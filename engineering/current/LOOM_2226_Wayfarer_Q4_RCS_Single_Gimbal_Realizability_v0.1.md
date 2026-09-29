# LOOM 2226 — Wayfarer Q4 RCS Single-Gimbal Realizability v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** Wayfarer flight-system qualification PR #96

## 1. Question

The prior Q4 bounded allocator represented each RCS hardpoint by non-negative thrust weights on five sampled directions inside a 45° vectoring envelope. That representation was deliberately conservative, but it left an important question open: does a passing allocation require a physically impossible interpretation in which one hardpoint fires several nozzle directions simultaneously?

## 2. Result

No, provided the candidate actuator is continuously vectorable anywhere inside the assumed 45° circular force cone.

For one mount at fixed position `r`, sampled force contributions `F_i` combine linearly:

`F = sum(F_i)`

Torque is also linear at a common origin:

`sum(r × F_i) = r × sum(F_i) = r × F`

Therefore the sampled-channel contributions at one hardpoint can be replaced by one resultant force vector at that same hardpoint without changing the spacecraft wrench.

The 45° circular cone is convex because its half-angle is below 90°. Every sampled direction used by the allocator lies inside that cone. Any non-negative weighted resultant therefore also lies inside the continuous cone.

Finally:

`|sum(F_i)| <= sum(|F_i|)`

so collapsing the sampled solution cannot increase the required mount thrust above the existing 25 kN summed-channel cap.

## 3. Engineering implication

This removes a false concern in the earlier wording. The sampled allocator is not relying on five simultaneous physical nozzles at one mount. Any feasible sampled allocation can be represented by one simultaneous gimbal direction and one thrust magnitude per active hardpoint, under the continuous-45° assumption.

The sampled model is actually conservative in direction coverage: it searches the convex hull of five directions, which is a subset of the full continuous 45° cone.

## 4. Validation

Implementation:

- `src/wayfarer_rcs_gimbal_realizability.py`
- `tests/test_wayfarer_rcs_gimbal_realizability.py`

The regression checks:

- every sampled direction lies inside the assumed continuous cone;
- representative positive sampled mixtures collapse to one direction inside the cone;
- resultant thrust never exceeds summed sampled thrust or the 25 kN mount cap;
- single-channel collapse reproduces the sampled direction exactly;
- engineering/non-canon authority boundaries remain explicit.

Validation head: `e460c3d07d851b82e81ddd38146254317747a8ba`

- Wayfarer Q4 Python run 6: **PASS**
- WALTER / LOOM Gate run 178: **PASS**

## 5. What remains OPEN

This result does **not** qualify:

- physical gimbal mechanism;
- gimbal slew rate or acceleration;
- minimum impulse bit;
- working fluid or RCS exhaust velocity;
- physical plume half-angle or thermochemistry;
- final radiator finite-cone clearance;
- structural mount/load qualification;
- Q5 electrical/thermal duty;
- closed-loop guidance/control;
- docking contact dynamics.

## 6. Disposition

**PASS — SINGLE-GIMBAL REALIZABILITY UNDER THE CONTINUOUS 45° ENGINEERING ASSUMPTION.**

This closes the narrow mathematical gap between the sampled allocator and a one-vector-per-hardpoint actuator command. It does not close full Q4 actuator hardware qualification.
