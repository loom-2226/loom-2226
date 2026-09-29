# LOOM 2226 — Wayfarer Q5 RCS Attitude Energy Bridge v0.1

**Status:** ENGINEERING_CANDIDATE_NON_CANON  
**Authority:** ENGINEERING_STUDY_NON_CANON  
**Date:** 2026-09-11

## Purpose

Convert the already-qualified Q4 finite-attitude timing envelope into bounded Q5 RCS energy / thermal screening without inventing maneuver timing.

## Inputs

- `engineering/current/wayfarer_q4_hud_attitude_envelope_v0.4.json`
- `src/wayfarer_rcs_allocation.py`
- `engineering/current/wayfarer_q5_power_thermal_envelope_v0.2.json`

The bridge is implemented in `src/wayfarer_q5_attitude_energy.py`.

## Earned timing basis

Q4 v0.4 already qualifies reference-wet-docked 90° and 180° roll / pitch / yaw transition times with an explicit 20% settle margin.

For the existing symmetric bang-bang timing model:

`powered_bang_bang_time = qualified_transition_time / 1.20`

The residual 20% remains settle margin and is **not** silently treated as full-thrust RCS firing.

This is a derivation from the existing Q4 model, not a new control-law or maneuver-duration assumption.

## Physical actuator demand

For each pure attitude axis, the bridge uses the physical resultant mount thrust reported by the Q4 allocator, not net translational force. For degraded control it conservatively selects the largest physical resultant demand across both torque signs and A/B/C/D single-cluster failures.

That retains torque-producing counter-thrust in the propulsion and thermal accounting.

## Q5 screening outputs

For each reference-wet-docked nominal and one-cluster-out 90° / 180° roll, pitch and yaw slew, the bridge derives:

- powered RCS duration;
- retained settle-margin duration;
- total physical resultant mount thrust;
- peak physical hardpoint utilization;
- candidate kinetic jet power for the existing 20 km/s and 50 km/s exhaust-velocity screens;
- candidate jet energy;
- conversion-waste-heat power and energy across the existing 0.90–0.95 efficiency screen;
- equivalent expelled mass from impulse / candidate exhaust velocity;
- gross conversion-heat fraction of the existing 50–60 GJ thermal-buffer screen.

No radiator rejection credit is applied to the transient comparison because radiator transient response and final physical geometry remain open.

## Result

The checked pure-attitude qualification set remains within the existing 50 GJ gross conversion-heat buffer screen under the candidate Q5 propulsion assumptions.

This is a bounded engineering result only. It does **not** establish final bus architecture, working fluid, radiator dynamics, or closed-loop control.

## Still open

- combined-maneuver duration;
- translation-maneuver duration;
- exact physical gimbal mechanism and slew dynamics;
- minimum impulse bit;
- RCS working fluid and final exhaust velocity;
- final conversion efficiency;
- radiator transient response and final radiator geometry;
- plume thermochemistry / finite plume cone;
- structural loads;
- closed-loop guidance and control;
- final docking-contact dynamics.

## Validation

Validated code/test head: `5aecbd98fd27063c5d5e7b4b352cc19e74f31627`

- WALTER / LOOM Gate run 190: **PASS**
- Wayfarer Q4 Python run 16: **PASS**

The actuator workflow explicitly includes `tests/test_wayfarer_q5_attitude_energy.py`.

## Disposition

Q5 remains `OPEN_BOUNDED`, but pure-attitude maneuver energy and gross conversion-heat screening are no longer timing-unknown at the reference wet/docked qualification state.

The next useful step is to earn translation and combined-maneuver timing from explicit displacement / relative-state / attitude histories, rather than assigning arbitrary durations to named maneuver cases.
