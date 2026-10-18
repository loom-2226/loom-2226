# Shared destination-state lattice: design only

**Status:** PROPOSED / NON-CANON / NON-RUNTIME / NOT IMPLEMENTED. Draft PR #427 only. No authority over frozen code or PRs #423–#426. Arm A remains stopped.

## Objective and boundary

Avoid fetching identical destination SPICE states for each departure. Build each qualified body's state array once on a shared quarter-day arrival lattice, then let geometry calculations and independent sponsor/vehicle/price evaluations read those immutable states. This is a **state cache**, not a geometry, price, admissibility, or mission cache. No SPK repacking or modification.

## 1. Authorship, hashes, identity

Author the future cache's time lattice in a small explicit **new experiment input** (not in the current state-probe config): UTC epoch anchor, `step_days=0.25`, inclusive first/last arrival epoch, endpoint inclusivity, source selection/coverage policy, and body-selection rule. Derive the bounds from the union of **all** authored coarse and permitted refinement departures and the authored 45–1400-day flight range; the final bounds and their derivation must be recorded. Do not silently infer a new grid from sponsor requests. Quarter-day arithmetic should use integer ticks from a UTC anchor, avoiding float date drift. A request off-lattice or outside bounds fails closed or requires a separately authored new cache; never round silently.

Canonicalize the authored input and SHA-256 it. The run identity includes its SHA-256, the resolved lattice bounds and tick count, body catalog/eligibility hash, all selected source and kernel SHA-256 values, reference frame, observer, aberration convention, SPICE implementation/version, and the existing experiment/solver/flight-grid identities. Cache output gets a separate content SHA-256. Changing a source or horizon changes the identity rather than mutating a previous run.

## 2. Cache key and rebuild

A state entry is keyed by `(body NAIF ID, integer lattice tick, source ephemeris ID + kernel SHA-256, source coverage identity, reference frame ECLIPJ2000, observer SUN/NAIF 10, aberration NONE, state algorithm/version)`. The enclosing cache/table is keyed by the lattice identity and ordered source manifest hash. Store six-component position (km) and velocity (km/s), not prices. An exact matching entry is reusable across departures, years, sponsors, and runs **only when the source identity and epoch semantics match**.

Rebuild the affected body's table when its kernel bytes/hash, source/coverage selection, time lattice, coordinate conventions, or state-computation version changes. Rebuild a newly required range or reject it; do not silently extend an existing hashed artifact. Changing sponsor, vehicle limits, price rate, departure cadence **within covered lattice bounds**, or economic model does **not** rebuild destination states. A change to departure dates that requires off-lattice arrivals does.

## 3. Independent direct-fetch validation

Before marking a completed body table usable, compare cached six-component states against fresh direct `spice.spkezr` lookups with the same loaded qualified kernel and frame/observer/aberration contract. Deterministic sample: read `design_validation.sample_divisor`, `design_validation.maximum_sample_count`, and `design_validation.mandatory_ticks` from the SHA-256-authored `state_probe_config.json`; take mandatory first/midpoint/last ticks plus every `max(1, floor((N-1)/sample_divisor))`th tick, sort/deduplicate, and if above the authored maximum preserve mandatory ticks and take the lowest-index remaining ticks up to that maximum. No validation values are embedded in the algorithm. Record selected ticks and count, max absolute component difference in km and km/s, and max Euclidean position and velocity vector difference, plus hashes and versions. Require finite values and **bitwise equality** for the same SPICE path initially; if actual measured differences disprove bitwise reproducibility, stop and author a justified tolerance before proceeding. **No measured max difference exists yet; validation has not run.** Never report zero as an observed result before executing the check.

## 4. Sponsor lookup

Sponsor intent -> authored departure, destination and vehicle -> qualified source and lattice identity -> compute integer arrival ticks for the authored flight-duration grid -> lookup destination six-vectors by tick; obtain the departure Earth state from the same qualified lattice when it falls within its coverage (otherwise from an equally identified direct state source) -> batched Lambert geometry -> vehicle-specific admissibility -> price/award. Missing tick, source seam, wrong hash, or unsupported origin returns an explicit unavailable state, not interpolation or a fabricated quote. Keep existing geometry fingerprint semantics, adding the state-table identity. Reuse the same destination table for every sponsor; do not make a sponsor-specific copy.

## 5. BENNU and slow-body build

Use an **explicit, separate, bounded offline build** on quantifactus, not on sponsor-query paths and not inside a live simulation tick. BENNU's qualified source is the unmodified 84,648,960-byte `bennu_sb-101955-118_long.bsp` (172,210 type-2 segments). AMUN uses `amun_2026_2251.bsp` (11 type-21 segments). Use the existing qualified direct SPICE path; no repacking, editing, or replacement of kernels. Build one body at a time, in contiguous tick chunks; write each finished chunk to a temporary content-hashed file, then atomically record a manifest with completed tick ranges, hashes, source/lattice identity and measured elapsed time. On restart verify those identities and hashes, resume only missing chunks. Publish a final immutable table only after all ticks and independent validation pass. A partial table is never sponsor-readable. A 120-second research-probe limit is **not** an authorized full-build timeout; the build must be separately authorized and bounded before execution.

BENNU measured 100-state warm throughput: 11.1336 s/100 = 0.111336 s/state; extrapolated 8,337 unique states ~= 928 s (~15.5 min) for one complete two-year lattice. Other 24 bodies' 1,000-state measurements were roughly 27–63 microseconds/state. **These are estimates, not measured build times**; chunk overhead, kernel loading, validation, storage and source seams add cost.

## 6. Authored experiment horizon (2026–2027): conditional estimate

**Scope clarification:** The *actual Stage 1 authored experiment* (`experiment.json`, `years: [2026, 2027]`) spans **2026–2027 only**. SPK coverage through 2251 is **not** an authored simulation horizon. A 2026–2250 run would require a new authored experiment and a separate estimate, not an implicit extension of Stage 1.

**Inputs:** 25 derived eligible bodies (assume the same set qualifies throughout); two authored years; `start_month_day=01-01`; `stride_days=28`; `include_last_day=true`; 14 departures per body-year; `flight_range_days=[45,1400]`; `flight_step_days=0.25`; 5,421 flight samples per departure; `daily_refinement=true`, `refinement_step_days=1`, `max_transition_brackets_per_body_year=1`. Rates from prior probes: BENNU warm 100-state 0.111336 s/state, other 24 bodies measured 1,000-state rates ~0.000027–0.000063 s/state; warm solver ~0.006 s/departure; other processing ~0.04 s/departure (see measured profile below). The departure count and maximum refinement count are **derived**, not new policy values.

**Coarse schedule:** 14 departures/year/body × 2 years × 25 bodies = **700 departures**, or **3,794,700 solver samples**. Jan 1 2026 to Dec 31 2027 spans 729 days: one shared arrival lattice has `5,421 + 729*4 = 8,337` distinct ticks per body, **208,425 body-state entries** for 25 bodies (subject to qualified source coverage). The uncached solver requests would fetch 3,794,700 destination states, including duplicates.

**Maximum permitted refinement:** One bracket of up to 28 days per body-year, with daily interior dates, adds **at most 27 departures/body-year**, or **1,350 departures** over 50 body-years. Thus the maximum **2,050 total departures** and **11,113,050 Lambert samples**. Refinement dates lie between coarse dates and therefore introduce **no additional distinct arrival ticks** on the shared 0.25-day lattice. Actual refinement count depends on observed feasibility transitions and may be zero. The cache must still check source coverage for every arrival.

**Estimated compute, excluding infrastructure:**

| Component | Coarse only | Coarse + maximum refinement |
|---|---:|---:|
| Destination-state build, BENNU | ~928 s | ~928 s |
| Destination-state build, other 24 combined | ~6.2 s | ~6.2 s |
| Warm Lambert solver (~0.006 s/departure) | ~4.2 s | ~12.3 s |
| Other geometry work (~0.04 s/departure) | ~28 s | ~82 s |
| **Subtotal, estimate** | **~966 s (16.1 min)** | **~1,029 s (17.2 min)** |

**Not included:** first-call JIT (~9 s), kernel loading, source seams, source-specific changes in per-state cost, direct-fetch validation, state-table serialization and reads, geometry checkpoint writes, eligibility checks, sponsor-specific pricing/selection, and process startup. The 0.04 s is an earlier *approximate residual* and is not an independent constant; the read-only profile below shows that total measured non-bulk, non-solver geometry work can vary. Do not double count work that is inside the measured bulk state retrieval. These are **estimates, not full-run timings**, and assume that cached-array lookups are inexpensive.

**Read-only warm AMUN profile, 2026-01-29:** one `cProfile` run after a cold 2026-01-01 warm-up, 5,421 flight samples. Inclusive cumulative timings: geometry **0.279 s**; `_batch_states` **0.195 s**, including SPICE `str2et` **0.114 s** and `spkezr` **0.060 s**; `pareto_geometry` **0.029 s**; `_times` **0.008 s**; `_key` **0.005 s**. Geometry's own exclusive Python time was **0.025 s**. The remaining roughly **0.084 s** outside `_batch_states` includes Pareto pruning, key/grid generation, vector processing, and solver; nested cProfile totals must **not** be added together. The earlier ~0.04 s residual is therefore an optimistic planning input, not a demonstrated stable cost. No production change was made to profile it.

## 7. Explicit exclusions

Do not cache price, monetary units, capital allocation, demand, sponsor decisions, vehicle limits, admissibility, propulsion assumptions, or a selected winning route as if they were ephemeris facts. Geometry can be separately keyed/reused only under its own full solver/flight-grid identity; it is not part of this proposal's destination-state table. Maintain direct-versus-propagated epistemic separation; a locally propagated non-navigation-grade source cannot substitute for BENNU's qualified direct source.

## 8. All-body-year coarse-versus-fine sampling experiment

Compare **all eligible body-years in the authored 2026–2027 experiment**, not a selected body/date. Derive body eligibility from the same Stage 1 catalog, qualified sources, and assets; include explicit unsupported/unavailable outcomes. Use the same immutable validated state lattice for each compared sampling arm and the same source, pricing law and vehicle limits. This experiment tests **two independent resolution dimensions**: departure spacing and flight-duration step. Author every comparison value and rule in a separate hashed **future experiment config** before execution: year window, eligible-body selection, origin, coarse and fine departure strides, whether to include Dec 31, coarse and fine flight-duration steps, flight-duration bounds, refinement rule, price/vehicle limits, tie-breaking, and comparison metrics. The current authored 28-day departure stride and 0.25-day flight step provide the reference arm; **no finer alternative values have been authorized yet**. Do not invent them in this design.

Both arms must draw states from a lattice with a step compatible with **both** flight grids and their departure epochs. Off-lattice requests are rejected; no interpolation or silently modified grid. For each `(body, year)`, evaluate all authored departures under each arm, and record: (a) **price regret** = coarse minimum admissible price minus fine minimum admissible price in USD, with `NOT_COMPARABLE` if either arm has no feasible price; (b) **window shift** = signed days between each arm's earliest feasible departure (and separately report the shift in best-priced departure); (c) **feasibility disagreement** = whether the arms disagree on existence of any feasible departure within that body-year, plus the count of disagreements on shared departure dates; (d) **best departure changes** = boolean and the two dates, with ties resolved by earliest departure, then shortest flight duration, then stable body ID. Preserve both arms' best flight duration, price, sample count, runtime, and source/cache hashes. Compare all body-years, aggregate only after retaining individual results, and report unavailable cases rather than dropping them. A fine arm's better sampled minimum is not proof of the true continuous optimum. An independent direct-SPICE sample audit follows Section 3. No experiment is authorized or run by this design.

## Stop condition

This document authorizes **no** code change, cache build, kernel change, Arm A restart, frozen edit, or merge. Implement only after separately approving the authored lattice bounds, identity and build budget. A single qualified body table that validates and is reused across two departures would be the smallest meaningful first test.
