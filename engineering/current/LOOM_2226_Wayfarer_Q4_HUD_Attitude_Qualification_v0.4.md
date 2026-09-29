# LOOM 2226 — Wayfarer Q4 HUD Attitude Qualification v0.4

**Status:** QUALIFIED FOR HUD FINITE-ATTITUDE ENVELOPE / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Q4_Mass_Properties_RCS_Attitude_v0.2.md`

## 0. Decision

Q4 is sufficiently closed for the existing HUD/local-flight qualification slice to replace its instantaneous-attitude assumption with a finite Wayfarer attitude-transition envelope.

This is **not** final actuator canon and is **not** operational closed-loop flight-control authority.

## 1. What changed

The previous Q4-U whole-body homogeneous-cylinder surrogate was intentionally conservative. v0.4 now assembles a bounded rigid-body approximation from the current Wayfarer mass ledger plus governed geometry envelopes.

The model restores:

- four off-axis remass tanks at their current radial stations;
- intrinsic cylindrical inertia for major axial subsystem envelopes;
- box inertia for the docked planetary launch;
- parallel-axis terms about the actual state-dependent vehicle CoM;
- balanced four-tank depletion;
- launch DOCKED versus ABSENT states.

Composite subsystem shapes that remain underdetermined use explicit bounded envelopes rather than zero intrinsic inertia.

## 2. Reference wet/docked state

At 250 t normal remass + 50 t protected water + 33 t docked launch:

- mass = **1,158.5 t**;
- CoM ≈ **[26.6767, 0.0, +0.1481] m**;
- roll inertia Ixx ≈ **9.11×10^6 kg m²**;
- pitch inertia Iyy ≈ **1.972×10^8 kg m²**;
- yaw inertia Izz ≈ **1.963×10^8 kg m²**.

The earlier 3.2×10^8 kg m² homogeneous-cylinder transverse value remains useful as a conservative bounding check, but it is no longer the preferred HUD transition model.

## 3. Other qualified HUD mass states

### Reference wet / launch absent

- mass = **1,125.5 t**;
- CoM ≈ **[26.8196, 0, 0] m**;
- Ixx ≈ **8.17×10^6 kg m²**;
- Iyy = Izz ≈ **1.952×10^8 kg m²**.

### Normal remass depleted / launch docked

- mass = **908.5 t**;
- CoM ≈ **[27.1380, 0, +0.1889] m**;
- Ixx ≈ **7.00×10^6 kg m²**;
- Iyy ≈ **1.912×10^8 kg m²**;
- Izz ≈ **1.903×10^8 kg m²**.

### Normal remass depleted / launch absent

- mass = **875.5 t**;
- CoM ≈ **[27.3392, 0, 0] m**;
- Ixx ≈ **6.07×10^6 kg m²**;
- Iyy = Izz ≈ **1.890×10^8 kg m²**.

The weak transverse-inertia dependence on remass depletion is physically useful: large-angle pitch/yaw handling does not change dramatically across the normal dispatch envelope.

## 4. RCS attitude authority

Retain the current engineering candidate:

- 25 kN individual high-authority unit;
- ~40 m fore/aft opposed-pair separation;
- nominal pitch/yaw couple ≈ **1.0 MN m**;
- nominal roll couple ≈ **0.20 MN m**;
- nominal aggregate translation ≈ **100 kN**.

For the reference wet/docked state, with a 20% settle margin applied to the ideal symmetric accelerate/decelerate solution:

### Nominal

- pitch 90° ≈ **42.2 s**;
- pitch 180° ≈ **59.7 s**;
- yaw 90° ≈ **42.2 s**;
- roll 90° ≈ **20.3 s**;
- roll 180° ≈ **28.7 s**.

These are envelope transition times, not guidance-law predictions.

## 5. One-cluster-out qualification

For a conservative one-cluster-out case, v0.4 assumes cross-strapped surviving clusters retain:

- 75% of nominal pitch/yaw couple: **0.75 MN m**;
- 50% of nominal roll couple: **0.10 MN m**;
- 75% of normal translation: **75 kN**.

Under that case the reference wet/docked vehicle retains all three attitude axes plus translation.

Representative finite transitions become:

- pitch 90° ≈ **48.8 s**;
- pitch 180° ≈ **69.0 s**;
- yaw 90° ≈ **48.7 s**;
- roll 90° ≈ **28.7 s**;
- roll 180° ≈ **40.6 s**.

This closes the HUD requirement to distinguish nominal from degraded finite attitude authority. It does not claim that every physically possible arbitrary cluster installation satisfies this result; the installation must preserve the distributed/cross-strapped topology assumed here.

## 6. HUD authority boundary

The HUD may now consume this envelope to present and simulate:

- finite attitude-transition state;
- commanded-axis/angle transition duration;
- nominal versus one-cluster-out degraded timing;
- attitude transition before accelerate–flip–brake phases;
- explicit qualification provenance.

The HUD may **not** infer:

- final thruster coordinates or plume cones;
- structural load limits;
- high-rate slew with deployed radiators;
- closed-loop pointing error/settling precision;
- docking contact dynamics;
- final certified guidance/control law.

Python remains numerical authority; browser/render code remains presentation only.

## 7. Q4 disposition

For the narrow downstream need that froze HUD PR #92:

**Q4-HUD ATTITUDE ENVELOPE: QUALIFIED**

For final spacecraft engineering/canon:

**Q4 FULL ACTUATOR / STRUCTURE / CONTROL QUALIFICATION: OPEN**

Remaining full-Q4 items are installation-level plume/interference geometry, structural torque limits, deployed-radiator limits, minimum impulse behavior, and closed-loop control qualification. None of those is required to eliminate the HUD's current instantaneous-attitude abstraction, provided the HUD labels this authority correctly.
