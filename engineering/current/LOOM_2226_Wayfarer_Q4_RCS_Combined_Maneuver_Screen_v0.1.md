# LOOM 2226 — Wayfarer Q4 RCS Combined-Maneuver Screen v0.1

**Status:** ENGINEERING SCREEN / NON-CANON  
**Date:** 2026-09-11  
**Parent:** Q4 RCS allocation/plume work on PR #96

## 0. Authority boundary

This screen does not alter CANON II and does not create flight-control authority. It reuses the existing Q4 mount layout, sampled vectoring model, 25 kN per-mount sizing cap, and bounded allocator to test representative *combined* force/torque requests.

The cases are engineering stress cases. They are not canonical maneuver requirements, Navigator commands, certified docking profiles, or guidance laws.

## 1. Why this screen exists

The prior Q4 allocator proved both signs of six pure wrench axes could be produced under nominal and one-cluster-out conditions. Pure-axis tests do not establish operational usefulness because real proximity maneuvers combine translation and attitude control.

The next question is therefore narrower and harder:

> Can the current actuator candidate produce representative coupled translation + torque requests without exceeding the same 25 kN per-mount cap?

## 2. Nominal combined cases

`src/wayfarer_rcs_combined_maneuvers.py` defines four representative bounded cases:

1. **DOCKING_CORRECTION** — low translation in multiple axes with simultaneous roll/pitch/yaw correction.
2. **COLLISION_AVOIDANCE_SIDESTEP_SLEW** — stronger lateral translation plus simultaneous reorientation.
3. **TORCH_AXIS_ACQUISITION** — small trim translation with dominant simultaneous pitch/yaw alignment torque.
4. **PROXIMITY_BRAKE_AND_ALIGN** — braking translation plus multi-axis attitude correction.

All requested components remain below the existing pure-axis Q4 nominal envelope. This module does not silently increase spacecraft authority.

## 3. One-cluster-out combined cases

For each failed logical cluster A, B, C, and D, the screen evaluates:

1. **ONE_CLUSTER_OUT_APPROACH_CORRECTION** — degraded multi-axis proximity correction.
2. **ONE_CLUSTER_OUT_ABORT_SIDESTEP** — degraded lateral abort translation with simultaneous attitude correction.

The four-cluster cross-strapped topology therefore receives eight degraded combined-wrench cases in total.

## 4. Validation result

GitHub Actions workflow **Wayfarer Q4 Python / run 3** passed on commit:

`ccebf0061b307c0adca594b13585c6ba282618bd`

The regression includes current Q4 mass-state, rigid-body, HUD attitude-envelope, RCS placement, RCS kinematic-control, bounded allocation, plume-screen, and combined-maneuver tests.

The combined-maneuver regression asserts:

- every nominal combined case passes the existing bounded allocator;
- every A/B/C/D one-cluster-out combined case passes;
- no case exceeds the 25 kN per-mount cap;
- each mission-relevant test contains at least four non-zero wrench components, preventing accidental regression to pure-axis testing;
- OPEN authority boundaries for closed-loop control, physical plume, structural loads, power/thermal duty, minimum impulse and docking-contact dynamics remain explicit.

**Disposition:** `PASS_COMBINED_WRENCH_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION`

## 5. What this earns

The current candidate is no longer supported only by geometric rank and isolated-axis force tests. Within the existing convexified sampled-vectoring model, it also survives a first representative set of coupled translation/attitude demands in nominal and one-cluster-out states.

This materially strengthens the case that 16 distributed 25 kN-class mounts are an operationally plausible architecture candidate.

## 6. What remains open

This does **not** qualify:

- exact simultaneous physical gimbal angles;
- arbitrary six-axis wrench feasibility over the full continuous envelope;
- transient actuator dynamics;
- minimum impulse bit / pulse modulation;
- exact plume half-angle or plume thermochemistry;
- final radiator plume clearance;
- structural mount and local hull loads;
- RCS working fluid or exhaust velocity;
- bus and thermal duty cycle;
- momentum-storage sizing and unload intervals;
- closed-loop guidance/control stability;
- docking contact dynamics.

## 7. Next engineering gate

The next useful Q4/Q5 step is to replace the convexified sampled-vector relaxation with a stricter simultaneous-gimbal allocation model and then couple the resulting actuator duty demand into Q5 power/thermal closure. If that stricter model materially reduces usable combined authority, the response is to revisit mount count, vectoring range, thrust class, or maneuver doctrine rather than weaken qualification gates.
