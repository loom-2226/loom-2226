# Vehicle, mission and price-domain proposal

**Status:** PROPOSAL ONLY / TEST_ONLY / NON-CANON / NON-RUNTIME. Draft PR #427. No implemented changes, no authority over frozen PRs #423–#426.

## Goal

Replace experiment-wide 10 km/s departure and arrival thresholds with authored vehicle-class and mission-type rules, without changing the existing single geometry builder. Preserve the distinction between trajectory admissibility and price-model support.

## Authored inputs (proposed, not yet present)

`experiment.json` would name **lists** of `vehicle_class_ids` and `mission_type_ids`. Their definitions would be authored tables, included by content hash in the existing run identity. One result set per selected `(vehicle_class_id, mission_type_id)` pair; reports carry both IDs in every row, group, and result identity. The existing global keys remain historical inputs until a separately authorized implementation replaces them.

- **Vehicle-class table:** `class_id`, `departure_limit_km_s`, `arrival_limit_km_s`. Values are authored. No named body, year, or class in code.
- **Mission-type table:** `mission_type_id`, `arrival_limit_policy`, optional `mission_arrival_limit_km_s`, and `charged_speed_terms` (authored selection of `departure_vinf_km_s` and `arrival_vinf_km_s`). A flyby uses `arrival_limit_policy=NONE` and charges **departure only**; a rendezvous enforces the tighter applicable vehicle and mission arrival limits and charges whichever speed terms its authored rule specifies. No flyby braking charge is implied. Do not conflate a flyby encounter with a rendezvous.
- **Price-proxy table/config:** authored coefficient and optional calibrated minimum/maximum of the **charged speed metric** (not necessarily departure-plus-arrival). If bounds are absent, a numeric quote is **`PRICED_TEST_ONLY`**, visibly labeled as uncalibrated in every report, never plain `PRICED`. If calibrated bounds exist and the otherwise admissible trajectory falls outside them, it is `UNPRICED`, **not** `INFEASIBLE`. Do not extrapolate silently. An in-domain calibrated quote may use `PRICED` only with a supported calibration basis.

The current `price_rate_usd_millions_per_km_s` is a TEST_ONLY proxy, not an established calibration. The mission-specific charged terms and price domain must both be hashed inputs. A change to a limit, rule, coefficient, bound, or selected pair changes run identity.

## One builder and evaluator

Generate geometry once per body/date/flight grid, then evaluate each authored vehicle/mission pair against the **same** geometry. Apply flight-duration bounds and vehicle departure limit; apply arrival limit only if the authored mission policy requires it. Evaluate the mission-specific charged-speed metric; then check pricing calibration. Preserve both admissibility and pricing status independently, including a qualifying unpriced trajectory and its reason. Do not use a missing quote as evidence of physical infeasibility.

No class-specific, year-specific or destination-specific code branches. No additional fleet model, finance system, or builder implementation. **Stop** once a single evaluator can replay pair-specific results deterministically with complete hashes and correct `INFEASIBLE` / `UNPRICED` / `PRICED_TEST_ONLY` / supported `PRICED` distinctions.
