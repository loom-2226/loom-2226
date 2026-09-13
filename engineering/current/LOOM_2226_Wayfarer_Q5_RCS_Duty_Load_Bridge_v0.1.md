# LOOM 2226 — Wayfarer Q5 RCS Duty / Load Bridge v0.1

Status: **ENGINEERING_CANDIDATE_NON_CANON**  
Authority: **ENGINEERING STUDY / NON-CANON**  
Date: 2026-09-11

## Purpose

Bridge the now-realizable Q4 one-vector-per-hardpoint RCS demand into Q5 power/thermal screening without inventing hardware, bus, plume, propellant, or maneuver-duration authority.

## Implemented path

`Q4 bounded allocator -> physical resultant thrust per surviving hardpoint -> Q4 mission-relevant combined-wrench cases -> Q5 candidate exhaust-velocity/efficiency envelope -> jet-power and conversion-waste-heat screening`

The allocator reports, for every screened case:

- one resultant commanded force vector per surviving hardpoint;
- resultant thrust per hardpoint;
- physical hardpoint utilization relative to the existing 25 kN cap;
- total resultant mount thrust across the vehicle.

This total is deliberately **not** replaced by net translational force. Counter-thrust used to generate torque therefore remains visible in propulsion/power demand.

## Q5 screening assumptions consumed, not created here

From `wayfarer_q5_power_thermal_envelope_v0.2.json`:

- lead RCS exhaust velocity candidate: 20 km/s;
- alternate RCS exhaust velocity candidate: 50 km/s;
- conversion-efficiency screening band: 0.90–0.95;
- duty class: `BOUNDED_SHORT_DUTY`;
- physical radiator geometry: OPEN;
- Q5 qualification: `OPEN_BOUNDED`.

For each Q4 combined maneuver case, the bridge derives:

- kinetic jet power using `P_jet = 0.5 F v_e`;
- conversion waste heat across the existing efficiency screening band;
- active/firing mount count;
- peak physical mount utilization.

## Explicit non-results

The combined-wrench suite still does **not** contain earned maneuver duration. Therefore this bridge does not qualify or infer:

- combined-maneuver energy draw;
- combined-maneuver thermal-buffer depletion;
- combined-maneuver propellant consumption;
- working-fluid selection;
- electrical-bus source;
- physical radiator transient response;
- plume thermochemistry or plume half-angle;
- gimbal mechanism losses;
- structural heating;
- minimum impulse bit;
- closed-loop control.

Those remain open because the current combined-maneuver sources do not earn them.

Pure-attitude 90° / 180° timing is now handled separately by `LOOM_2226_Wayfarer_Q5_RCS_Attitude_Energy_Bridge_v0.1.md`, which consumes the already-qualified Q4 finite-attitude timing envelope without assigning arbitrary durations to the combined cases.

## Validation

Original instantaneous-duty code/test head: `a4703635071bb1c76ed5d96c9b1e38ed1420ccf6`

- WALTER / LOOM Gate run 185: **PASS**
- Wayfarer Q4 Python run 12: **PASS**

The later attitude-energy bridge is separately validated at head `5aecbd98fd27063c5d5e7b4b352cc19e74f31627` by WALTER run 190 and Wayfarer Q4 Python run 16.

## Disposition

**PASS AS A Q4 -> Q5 INSTANTANEOUS-DUTY BRIDGE; Q5 REMAINS OPEN_BOUNDED.**

Combined and translational energy closure still requires earned displacement / attitude histories and timing rather than named-case duration guesses.
