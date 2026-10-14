# Scaled Flight-Time Search: measured Build 8 PR 2 evidence

**Non-canon, non-runtime, not a qualified mission-design or new scientific baseline.**
Authoritative parent: ad8625d1edd70b493d67c32688e158b91fcfcecc.

## Policy, horizons and evidence method

- Approved **starting** research fraction: MIN_USEFUL_FLIGHT_TIME_FRACTION = 0.005; named minimum MIN_USEFUL_FLIGHT_TIME_FLOOR_DAYS = 1.0. Rule: step = max(1 day, fraction × flight days).
- The caller MUST explicitly supply the initial flight-time bracket and maximum flight-time horizon. No maximum is chosen in code and no hidden limit or vehicle/price choice has been added.
- The six DATE-OF-DEPARTURE samples are: 2026-01-01, 2026-04-01, 2026-07-01, 2026-10-01, 2031-05-01, 2036-09-01.
- Six outer pairs: initial maximum = 0.5 × 365.25 × (outer heliocentric AU)^1.5, rounded outward to 30 days and floored at 3000 days, with **experiment-only** maximum search horizon = 1.25 × that initial bound, also rounded outward to 30 days. These are reported research inputs NOT runtime default horizons.
- Eight legacy inner pairs: research maximum 1400 days (same as existing inner research). All search starts at 45 days.
- 0.25-day dense reference versus the proportional-step grid. Existing 2026-held flat Build 7 CARGO_DELIVERY price rate is applied without change to the sum of two endpoint speeds. The diagnostic 10/20 km/s caps are measurement filters, not modified vehicle rows.
- Feasible dense islands are consecutive speed-admitted samples. A **material** island spans at least the useful difference at its midpoint; smaller islands remain in the evidence. For each island, compare lowest priced dense and scaled samples inside the dense island.

## Every pair: Jan 2026 sample sizes, six-date window recall and price drift

| Route | Dense / departure | Scaled / departure | 10-km/s material recall | 20-km/s material recall | Max abs price drift % |
|---|---:|---:|---:|---:|---:|
| JUPITER → SATURN | 26,701 | 861 | 7/7 | 7/7 | 0.010152 |
| JUPITER → URANUS | 78,421 | 1,076 | 9/9 | 12/12 | 0.015080 |
| SATURN → URANUS | 78,421 | 1,076 | 12/12 | 6/6 | 0.020402 |
| SATURN → NEPTUNE | 149,101 | 1,205 | 10/10 | 6/6 | 0.036152 |
| URANUS → NEPTUNE | 149,101 | 1,205 | 6/6 | 6/6 | 0.027879 |
| NEPTUNE → PLUTO | 192,421 | 1,256 | 6/6 | 6/6 | 0.457071 |
| CERES → EARTH | 5,421 | 547 | 8/8 | 37/37 | 1.467896 |
| CERES → MARS | 5,421 | 547 | 15/15 | 23/23 | 0.160230 |
| EARTH → CERES | 5,421 | 547 | 1/1 | 6/6 | 0.018436 |
| EARTH → MARS | 5,421 | 547 | 5/5 | 21/21 | 0.107104 |
| EARTH → MERCURY | 5,421 | 547 | 0/0 | 20/20 | 0.612793 |
| MARS → CERES | 5,421 | 547 | 8/8 | 12/12 | 0.003941 |
| MARS → EARTH | 5,421 | 547 | 13/13 | 36/36 | 0.462435 |
| MERCURY → EARTH | 5,421 | 547 | 0/0 | 7/7 | 0.002967 |

## Aggregate measurements

- All 84 route/date geometries: **4,323,924** dense solves versus **66,303** scaled unique sample times; **65.21×** fewer unique flight-time samples.
- Six outer pairs × six dates: 4,063,716 dense versus 40,047 scaled unique samples.
- Eight legacy pairs × six dates: 260,208 dense versus 26,256 scaled unique samples.
- **306 of 306** observed dense-reference islands detected, including 305 material and 1 below the proposed useful-width threshold. **Zero observed misses in this finite reference.** This metric means each dense island contained at least one speed-admitted scaled sample; it does **not** prove exact island-boundary reconstruction or that the scaled grid cannot merge nearby islands.
- Price drift across each of the 306 detected islands: median absolute **0.003168%**, P95 absolute **0.166170%**, largest absolute **1.467896%**.
- Worst drift: **Ceres → Earth, 2026-10-01, 20 km/s cap**, dense reference price **5.840473807829805** versus scaled **5.9262059158553955** model currency, a **+1.467896%** difference.
- Individual window ranges and both prices, including the one sub-useful-width island, are in [SCALED_FLIGHT_WINDOW_PRICE_DRIFT.csv](SCALED_FLIGHT_WINDOW_PRICE_DRIFT.csv).

## Every outer pair/date edge outcome

For each date a cell gives the **10-km/s / 20-km/s** actual opt-in result: O = FLIGHT_RANGE_OPEN_EDGE, B = EXTENDED_BOUNDED, U = UNKNOWN_FLIGHT_RANGE.
| Route | 2026-01-01 | 2026-04-01 | 2026-07-01 | 2026-10-01 | 2031-05-01 | 2036-09-01 |
|---|---|---|---|---|---|---|
| JUPITER → SATURN | O/O | O/O | O/O | O/O | B/O | O/O |
| JUPITER → URANUS | O/O | O/O | O/O | O/O | B/O | O/O |
| SATURN → URANUS | O/O | O/O | O/O | O/O | O/O | O/O |
| SATURN → NEPTUNE | O/O | O/O | O/O | O/O | O/O | O/O |
| URANUS → NEPTUNE | O/O | O/O | O/O | O/O | O/O | O/O |
| NEPTUNE → PLUTO | O/O | O/O | O/O | O/O | O/O | O/O |

- All 72 actual opt-in outer searches: **70 OPEN**, **2 EXTENDED_BOUNDED**, **0 UNKNOWN**.
- An initial closed boundary does not exclude a later disconnected feasible island. Therefore the opt-in run extends deterministically to the caller-authored horizon, recording whether each extension was caused by a feasible edge or by the need to examine later potential windows.
- OPEN does **not** certify a globally cheapest route. Every outer run status, actual solves, dates, horizon, source constraints and summary bytes is in [SCALED_FLIGHT_OUTER_EDGE_STATUS.csv](SCALED_FLIGHT_OUTER_EDGE_STATUS.csv).

## Example storage: real Neptune → Pluto

- On 2026-01-01, with **visible test-only** initial range 45–38520 days, maximum 48150 days and 10/10-km/s research limit, the actual opt-in search returned **FLIGHT_RANGE_OPEN_EDGE**.
- **1,256 unique grid samples**, **2,467 actual Lambert solves** including the deterministic re-scan on extension, **1,683 bytes** of complete summary JSON, and **zero persistent geometry-cache files**.
- Dense 0.25-day reference across 45–48150 days uses **192,421 samples** and formerly retained about **16.6 MB** of trajectory JSON for this route. The new summary stores a source-sensitive grid fingerprint, horizon, extension history, window boundaries, best *sampled* candidates and result fingerprint, not the full trajectory arrays.
- The three CSV files in this report contain small **fixed research evidence only**; none is a runtime geometry warehouse.
- Across all 72 actual outer-search calls at the two stated endpoint thresholds, there were **157,002 actual Lambert solves** (including re-scans on deterministic extension). Mean serialized summary size **1,729 bytes**, maximum **1,910 bytes**. These are measured values in SCALED_FLIGHT_OUTER_EDGE_STATUS.csv, not estimates.

## Historical replay, scientific limits and non-qualification

- Historical daily and distance_research sampling and all their geometry-cache keys are untouched. The eight legacy routes must reproduce the pre-change compact JSON and SHA-256s **byte-identically**. No original pin may be repinned.
- The scaled strategy is opt-in through lookup. Both resolution constants and the explicit horizon appear in search metadata and fingerprints. Geometry identity has no vehicle or price field; the **filtered result** appropriately records its endpoint caps.
- Source coverage and contiguous SPICE kernel object availability are checked before scanning; crossing into propagated/missing coverage returns UNKNOWN_FLIGHT_RANGE. If the final requested horizon remains feasible, the result is FLIGHT_RANGE_OPEN_EDGE rather than a completed cheapest or complete range.
- Searched transfer family: **IZZO2015_M0_PROGRADE_LOW_PATH_HELIOCENTRIC**, zero revolution, impulsive heliocentric two-body.
- **Not searched:** multi-revolution Lambert, gravity assists, low-thrust, torch or metric drives, and moon-local transfer legs.
- These finite sparse departure epochs, two diagnostic caps, 0.25-day reference and incomplete outer-range boundaries cannot prove continuous 100% recall, a globally cheapest flight or physical infeasibility of unsearched transfers. The 70 open outer cases are unresolved, not qualification passes.

## Measurement files (small tabular evidence, not trajectory caches)

- [SCALED_FLIGHT_CASE_MEASUREMENTS.csv](SCALED_FLIGHT_CASE_MEASUREMENTS.csv): 168 per-cap rows covering 84 route/date cases.
- [SCALED_FLIGHT_WINDOW_PRICE_DRIFT.csv](SCALED_FLIGHT_WINDOW_PRICE_DRIFT.csv): 306 per-window dense versus scaled cheapest-price comparisons.
- [SCALED_FLIGHT_OUTER_EDGE_STATUS.csv](SCALED_FLIGHT_OUTER_EDGE_STATUS.csv): 72 actual opt-in outer-scan statuses, solve totals and serialized summary sizes.

**Review-only, non-runtime. No merge.**
