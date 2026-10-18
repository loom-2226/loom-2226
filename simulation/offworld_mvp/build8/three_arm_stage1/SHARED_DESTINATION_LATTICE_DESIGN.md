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

Before marking a completed body table usable, compare cached six-component states against fresh direct `spice.spkezr` lookups with the same loaded qualified kernel and frame/observer/aberration contract. Deterministic sample: unique sorted ticks comprising first, last, midpoint, and every `max(1, floor((N-1)/99))`th tick, capped to 101 total by taking the first 98 interior indices in ascending order if necessary. The rule is mechanical, not hand-picked, and includes both endpoints. Record selected ticks and count, max absolute component difference in km and km/s, and max Euclidean position and velocity vector difference, plus hashes and versions. Require finite values and **bitwise equality** for the same SPICE path initially; if actual measured differences disprove bitwise reproducibility, stop and author a justified tolerance before proceeding. **No measured max difference exists yet; validation has not run.** Never report zero as an observed result before executing the check.

## 4. Sponsor lookup

Sponsor intent -> authored departure, destination and vehicle -> qualified source and lattice identity -> compute integer arrival ticks for the authored flight-duration grid -> lookup destination six-vectors by tick; obtain the departure Earth state from the same qualified lattice when it falls within its coverage (otherwise from an equally identified direct state source) -> batched Lambert geometry -> vehicle-specific admissibility -> price/award. Missing tick, source seam, wrong hash, or unsupported origin returns an explicit unavailable state, not interpolation or a fabricated quote. Keep existing geometry fingerprint semantics, adding the state-table identity. Reuse the same destination table for every sponsor; do not make a sponsor-specific copy.

## 5. BENNU and slow-body build

Use an **explicit, separate, bounded offline build** on quantifactus, not on sponsor-query paths and not inside a live simulation tick. BENNU's qualified source is the unmodified 84,648,960-byte `bennu_sb-101955-118_long.bsp` (172,210 type-2 segments). AMUN uses `amun_2026_2251.bsp` (11 type-21 segments). Use the existing qualified direct SPICE path; no repacking, editing, or replacement of kernels. Build one body at a time, in contiguous tick chunks; write each finished chunk to a temporary content-hashed file, then atomically record a manifest with completed tick ranges, hashes, source/lattice identity and measured elapsed time. On restart verify those identities and hashes, resume only missing chunks. Publish a final immutable table only after all ticks and independent validation pass. A partial table is never sponsor-readable. A 120-second research-probe limit is **not** an authorized full-build timeout; the build must be separately authorized and bounded before execution.

BENNU measured 100-state warm throughput: 11.1336 s/100 = 0.111336 s/state; extrapolated 8,337 unique states ~= 928 s (~15.5 min) for one complete two-year lattice. Other 24 bodies' 1,000-state measurements were roughly 27–63 microseconds/state. **These are estimates, not measured build times**; chunk overhead, kernel loading, validation, storage and source seams add cost.

## 6. Full-horizon estimate, explicitly conditional

For authored 2026–2027 28-day coarse departures with final-year endpoint, 14 departures per year, 28 per body, 25 eligible bodies, 5,421 flight samples/departure: 700 coarse departures and 3,794,700 Lambert samples. The union of arrival epochs from 2026-01-01 through 2027-12-31 departures is `5,421 + (729 days * 4) = 8,337` unique quarter-day ticks **per body**, if source coverage permits the entire range. This corrects the earlier erroneous 1,720 count. Distinct state count across 25 bodies: 208,425. Current repeated per-departure requests would be 3,794,700 destination states.

Conditional cached-state build estimate: BENNU ~928 s using its 100-state rate; remaining 24 bodies combined ~6.2 s using their 1,000-state rates; warm Lambert solver ~4.2 s using ~0.006 s/5,421-sample call; **other geometry processing** ~28 s using ~0.04 s/departure * 700; total ~966 s (~16.1 minutes), excluding first-call JIT (~9 s), source loading, serialization, validation, disk I/O, checkpoint writes and scheduling overhead. With those costs, do not present 16.1 minutes as a committed wall-clock time. Additional daily refinement can add up to 27 dates per body-year (1,350 departures): ~54 s other processing + ~8 s solver, while arrival states remain on the same lattice and within the coarse horizon. Refinement may alter feasibility/quote results, not the cached ephemeris identity. This is a **planning estimate only**, not a benchmark or speedup claim.

## 7. Explicit exclusions

Do not cache price, monetary units, capital allocation, demand, sponsor decisions, vehicle limits, admissibility, propulsion assumptions, or a selected winning route as if they were ephemeris facts. Geometry can be separately keyed/reused only under its own full solver/flight-grid identity; it is not part of this proposal's destination-state table. Maintain direct-versus-propagated epistemic separation; a locally propagated non-navigation-grade source cannot substitute for BENNU's qualified direct source.

## 8. Coarse-versus-fine test

Use the **same validated destination lattice** and the same body/date/source, then evaluate (A) the authored PR #426 0.25-day flight-duration grid and (B) the `distance_research` body-dependent grid, provided each requested flight duration maps exactly to a lattice tick. If the fine/coarse step is off the quarter-day lattice, do **not** interpolate or quietly change either grid: stop and author a compatible comparison lattice, with a new hash and new state table. Select the comparison deterministically: lexicographically first `(body, year, departure)` among completed Arm A checkpoint rows with a non-null priced route and qualified source coverage for both grids. Record both sample counts, minimum admissible price, selected flight time, feasibility status, and solver time separately from cache hit/state build time. Do not choose by hand. For an independent check, repeat the comparison with fresh direct SPICE states for the same selected departure, without mutating the cached table. No comparison has been run under this design.

## Stop condition

This document authorizes **no** code change, cache build, kernel change, Arm A restart, frozen edit, or merge. Implement only after separately approving the authored lattice bounds, identity and build budget. A single qualified body table that validates and is reused across two departures would be the smallest meaningful first test.
