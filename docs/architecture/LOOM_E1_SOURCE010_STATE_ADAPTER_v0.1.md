# LOOM E1 SOURCE-010 State Adapter v0.1

Status: E1-bounded runtime seam. Non-canon. No new flight-dynamics authority.

## Purpose

Reconnect Experience One metric-domain geometry to the ephemeris authority Navigator already uses for real Ceres→Neptune planning.

The Pixel diagnostics on PR #123 proved that WORLD SQLite `states` is not the major-body source for this flight: Ceres and Neptune each have zero rows there. Historical qualification on PR #98 already proved Navigator's route-scoped SOURCE-010 chain for `CERES -> NEPTUNE_SYSTEM`, consuming only BASE dependencies `CE` and `NE`.

This seam therefore adapts Navigator's already acquired, canonical-axis-qualified route rows into the shared `SpatialState` contract used by metric-domain hydration.

## Authority chain

Human/Mara intent
→ Navigator mission normalization
→ Navigator SOURCE-010 acquisition
→ Navigator canonical dependency index + axis qualification
→ Navigator `_route_rows_from_canonical`
→ `NavigatorSource010StateResolver`
→ shared `SpatialState`
→ E1 metric-domain hydration/checker.

Navigator remains the ephemeris and flight authority. The adapter does not fetch data itself and cannot independently certify arbitrary rows.

## Qualification conditions

The resolver fails closed unless:

- source authority is exactly `SOURCE-010`;
- Navigator axis qualification is `PASS`;
- the requested body was explicitly supplied with route rows;
- at least two finite Navigator rows exist;
- requested epoch lies inside the acquired canonical time axis.

Rows use Navigator's existing shape:

`[source_time, x_AU, y_AU, z_AU, vx_AU_day, vy_AU_day, vz_AU_day]`.

Exact grid epochs use the corresponding row directly. Between grid epochs, position and velocity are sampled by cubic Hermite interpolation using the row position/velocity pairs. Provenance explicitly identifies this operation; it is not represented as a new ephemeris source.

## E1 probe

`engineering/experience_one/qualification/e1_source010_state_probe.py` performs a read-only online probe at the earned E1 epochs:

- departure: Ceres at `2226-08-22T01:32:00Z`;
- arrival: Neptune at `2226-08-22T09:45:17.864616Z`.

It uses Navigator's own route-scoped acquisition and canonical row loader, and writes no campaign state.

Expected success outcome:

`next_action = CONNECT_E1_ROUTE_SAMPLES_TO_DOMAIN_HYDRATION`

## Deliberate non-scope

- no replacement ephemeris service;
- no SQLite major-body promotion;
- no generic Solar acquisition sweep;
- no domain-radius decision;
- no detour solver;
- no campaign mutation;
- no HUD/UI work;
- no Mara/LLM calculation, state, authorization, or execution authority.

The next E1 seam is not more ephemeris architecture. It is exposing honest Navigator spatial route samples/collapse geometry so the already-merged metric-domain hydrator can evaluate the actual Ceres→Neptune candidate.
