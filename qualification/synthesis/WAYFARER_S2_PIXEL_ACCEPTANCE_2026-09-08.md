# LOOM 2226 — Wayfarer S2 Pixel Offline Acceptance

**Date:** 2026-09-08  
**Classification:** ENGINEERING / RESEARCH / QUALIFICATION — NON-CANON — NON-PRODUCTION  
**S2 source commit tested:** `7cb1dc0ac20b4d518ec656c4b332bafd69c2014f`  
**Device:** Pixel 10 Pro / Android / Termux  
**Network state:** Wi-Fi OFF; mobile data OFF  

## Result

```text
WAYFARER_S2_OFFLINE_ACCEPTANCE = PASS
S2_COMMON_MODEL_COMPARISON = PASS
candidate_id = CAND-5719E3F3251DE6E25FDF
seed = 2226
baseline_relational_x_m = 26.0
baseline_launch_x_m = 21.8
baseline_tank_x_m = 25.0
generated_relational_x_m = 26.0
generated_launch_x_m = 21.75
generated_tank_x_m = 26.5
com_x_delta_m = 0.322270176952955
j4_delta_m = -1.5
j7_delta_m = 0.05000000000000071
flight_dynamics_authority = false
wayfarer_flight_inertia_qualified = false
canon_changed = false
production_shipclasses_changed = false
```

## Acceptance statement

The pinned S2 source commit executed successfully on the Pixel acceptance device with network connectivity disabled. The generated S1 candidate and the hand-authored Wayfarer baseline were compared under the same admitted S1 physical model, and the common-model comparison passed.

This closes the required Pixel/offline portability gate for Wayfarer S2.

## Authority firewall

This acceptance does **not** qualify full Wayfarer flight inertia and does not create flight-dynamics authority. It does not change canon and does not modify production SHIPCLASSES.

```text
S2_COMMON_MODEL_COMPARISON = PASS
PIXEL_OFFLINE = PASS
WAYFARER_FLIGHT_INERTIA = NOT QUALIFIED
FLIGHT_DYNAMICS_AUTHORITY = false
CANON = UNCHANGED
PRODUCTION SHIPCLASSES = UNCHANGED
```
