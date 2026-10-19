# Continuous-window sampling study proposal

**Status:** PROPOSAL ONLY / TEST_ONLY / NON-CANON / NON-RUNTIME. Draft PR #427. No runs authorized.

## Authored study configuration (values deliberately blank)

- `reference_departure_spacing_days`: **TBD (kT)**
- `reference_flight_step_days`: **TBD (kT)**
- `comparison_settings`: **TBD (kT)**; each entry has `departure_spacing_days` and `flight_step_days`
- `window_start`, `window_end`, flight minimum/maximum, eligible body selection and selected vehicle/mission pairs: reuse explicitly authored experiment inputs; no named exceptions

**Validation:** Departure dates must lie on whole UTC days; flight steps must be exact integer multiples of the source table's authored `0.25`-day tick. Reject incompatible/off-lattice requests with an explicit `NEW_TABLE_REQUIRED` outcome; do not round, interpolate, or silently rebuild. The existing table coverage must contain every requested departure/arrival tick; otherwise stop and request a separately authorized table.

## Method

Use **one continuous departure timeline** across the entire authored window, not independent yearly grids. Evaluate every eligible body across that timeline under the same sampling rule. Partition **reports** by departure calendar year only after computing results, retaining the common timeline and its identity. Do not manufacture year-end departure dates; year-edge flags remain diagnostics, not sampling rules.

Run the finest **authored** setting as the reference. For each coarser authored setting, compare every body-year and vehicle/mission pair to that reference: status disagreement (`INFEASIBLE`, `UNPRICED`, `PRICED_TEST_ONLY`, `PRICED`), price regret (coarse lowest price minus reference lowest price, only when both have comparable quotes), and shift in best departure date (signed days, only when both have comparable best dates). Report `NOT_COMPARABLE` instead of invented numeric regret when pricing statuses or calibrated metrics differ. Include runtime, departure count, flight-sample count and peak RSS. Keep the reference and comparisons on the same continuous window and lattice.

## Runtime basis (estimate, not benchmark)

Measured Arm A: **1,537 departures / 326.44 s = 0.2124 s per departure** at the existing 0.25-day flight step, including refinement/checkpoint work. For a 730-day authored window and 25 bodies, a first approximation is `25 × (1 + floor(729 / departure_spacing_days))` departures, with actual endpoints determined by the authored window. Scale compute by `new_departures / 1537` and `new_flight_samples / 5421` from the measured 45–1400-day, 0.25-day grid. The earlier approximate illustrations were 7-day/0.25-day ~9 minutes, 1-day/0.25-day ~65 minutes, 1-day/1-day ~16 minutes; they are not commitments, exclude table build/gate costs, and may not capture nonlinear solver and checkpoint effects.

**No numerical sampling values are authorized here.** A possible later choice is a 1-day/0.25-day reference with 7-day/0.25-day and 28-day/0.25-day comparisons, but kT must explicitly author values before any run. No automatic refinement beyond those settings. Stop and report any coverage or lattice conflict.
