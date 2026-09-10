# LOOM 2226 — Wayfarer Q6 Navigator Mission Suite v0.2

**Status:** ENGINEERING QUALIFICATION / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Purpose

Convert Q6 from ideal rocket-equation screening into a direct consumer of Navigator route results without duplicating route physics.

Navigator already emits a route/plan result containing at least:

- `mass.departure_remass_t`
- `mass.planned_remass_used_t`
- `mass.planned_arrival_remass_t`
- `speeds.terminal_delta_v_km_s`
- `speeds.exhaust_velocity_km_s`
- `torch.burn_s`

Q6 therefore treats Navigator as the authoritative route solver and performs only qualification scoring against candidate dispatch inventories and reserve floors.

## 1. Authority rule

Do not infer route remass from straight-line distance, historical screenshots, or a duplicate trajectory approximation when Navigator can supply the plan result.

The qualification layer may:

1. validate mass arithmetic;
2. record route ordinary-state delta-v and burn metadata;
3. compare `planned_remass_used_t` against candidate dispatch inventories;
4. enforce a protected operational floor;
5. identify the worst-case route in the suite;
6. select the lowest candidate dispatch inventory that passes every required route.

It may not recompute or override Navigator trajectory physics.

## 2. Implemented adapter

`src/wayfarer_q6_navigator_adapter.py`

Consumes one Navigator result and reports:

- departure remass;
- remass used;
- arrival remass;
- fraction of departure remass consumed;
- reserve margin to a specified floor;
- pass/fail against the floor;
- Navigator mass-arithmetic residual;
- terminal delta-v;
- exhaust velocity;
- torch burn time.

## 3. Implemented suite scorer

`src/wayfarer_q6_suite.py`

Consumes a set of Navigator results and replays each route's computed remass demand against candidate dispatch loads.

Default candidate dispatch set:

- 100 t
- 150 t
- 200 t
- 250 t

The scorer returns:

- route count;
- maximum route remass demand;
- worst-case route ID;
- pass/fail by candidate dispatch inventory;
- minimum arrival remass by candidate;
- minimum reserve margin by candidate;
- the lowest candidate dispatch inventory that passes the entire supplied route set.

## 4. Required route suite

The Q6 qualification run remains:

- Earth ↔ Ceres;
- Mars ↔ Ceres;
- Mars ↔ Jupiter system;
- Ceres ↔ Neptune;
- outer-system expedition case;
- metric unavailable;
- endurance unavailable;
- torch unavailable where survivable;
- radiator degradation;
- one RCS cluster failed;
- low-remass reserve arrival;
- emergency high-g terminal correction.

Each route/result must carry a stable route/plan identifier and enough provenance to reproduce the Navigator preview.

## 5. Reserve-floor handling

The suite scorer accepts a protected operational remass floor independently from the separate protected life-support water reserve.

These concepts must not be silently conflated:

- `PROTECTED_WATER_RESERVE` is a ship resource / life-support cleanliness boundary;
- `OPERATIONAL_REMASS_FLOOR` is a dispatch/arrival propulsion reserve rule;
- `NORMAL_DISPATCH_REMASS` is the routine carried propulsion inventory.

Q7 will set the final values.

## 6. Current limitation

This repository-side session can inspect Navigator source and its output contract, but GitHub does not expose the mutable local Pixel runtime state or ephemeris cache required to regenerate every current route preview here.

Therefore v0.2 deliberately does **not** populate synthetic route numbers. The code path is now ready for direct use by the real Navigator runtime, and no historical route result is being promoted as a machine constant.

## 7. Q6 disposition

Q6.1 rocket-equation screening: **PASS**.

Q6.2 Navigator integration contract and suite scorer: **IMPLEMENTED / AWAITING FULL RUNTIME ROUTE SET**.

No dispatch inventory reduction is yet qualified.

The next authoritative step is to feed the required Navigator preview/plan results through `score_suite`, then carry the minimum-passing dispatch inventory plus margin into Q7 reserve doctrine.
