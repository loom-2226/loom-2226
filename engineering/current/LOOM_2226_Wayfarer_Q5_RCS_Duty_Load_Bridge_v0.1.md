# LOOM 2226 — Wayfarer Q5 RCS Duty / Load Bridge v0.1

Status: **ENGINEERING_CANDIDATE_NON_CANON**  
Authority: **ENGINEERING STUDY / NON-CANON**  
Date: 2026-09-11

## Purpose

Bridge the now-realizable Q4 one-vector-per-hardpoint RCS demand into Q5 power/thermal screening without inventing hardware, bus, plume, propellant, or maneuver-duration authority.

## Implemented path

`Q4 bounded allocator -> physical resultant thrust per surviving hardpoint -> Q4 mission-relevant combined-wrench cases -> Q5 candidate exhaust-velocity/efficiency envelope -> jet-power and conversion-waste-heat screening`

The allocator now reports, for every screened case:

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

The bridge does **not** qualify or infer:

- maneuver duration;
- maneuver energy draw;
- thermal-buffer depletion;
- propellant consumption;
- working-fluid selection;
- electrical-bus source;
- physical radiator transient response;
- plume thermochemistry or plume half-angle;
- gimbal mechanism losses;
- structural heating;
- minimum impulse bit;
- closed-loop control.

Those remain open because the current sources do not earn them.

## Validation

Validated code/test head: `a4703635071bb1c76ed5d96c9b1e38ed1420ccf6`

- WALTER / LOOM Gate run 185: **PASS**
- Wayfarer Q4 Python run 12: **PASS**

The dedicated Python workflow now includes both the single-gimbal realizability regression and the Q5 RCS duty/load bridge regression.

## Disposition

**PASS AS A Q4 -> Q5 ENGINEERING BRIDGE; Q5 REMAINS OPEN_BOUNDED.**

The next earned step is to use mission duration/control-law timing once qualified to turn instantaneous power/waste-heat demand into energy, thermal-buffer and radiator transient requirements. Until duration authority exists, those quantities remain explicitly unavailable rather than guessed.
