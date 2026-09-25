# LOOM 2226 — Wayfarer Q4 RCS / Attitude Sizing v0.1

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Authority boundary

This study does not alter CANON II. It derives a first actuator-sizing envelope from the current Wayfarer mass and geometry baselines and explicitly marks where intrinsic subsystem inertia remains unresolved.

## 1. Current physical anchors

Use the current reference spacecraft values:

- wet mass: 1,158.5 t;
- dry mass: 858.5 t;
- length: 57 m;
- main body diameter: 9 m;
- four major working-fluid/remass tanks centered around the thrust axis;
- integrated 33 t planetary launch offset on +Z in the docked state;
- current candidate RCS station bands at x≈5–8, 17–20, 35–38 and 43–46 m.

The repository already computes current CoM states. Existing candidate values are approximately x=27.99 m dry and x=26.68 m wet, with a small +Z offset when the launch is docked.

## 2. Inertia fidelity rule

The current mass ledger gives subsystem masses and centroids, but most subsystems do not yet carry validated intrinsic inertia tensors. Therefore two different quantities must remain separate:

1. **centroid point-mass tensor** — computable now, useful as a lower-fidelity lower bound;
2. **full rigid-body tensor** — requires intrinsic shape inertia for major distributed masses and is the only quantity eligible for final actuator canon.

No Q4 number derived from centroid-only inertia is eligible for promotion as a final Wayfarer slew constant.

## 3. Reference geometric envelope

A homogeneous 57 m × 9 m cylinder at 1,158.5 t provides a useful order-of-magnitude comparison envelope, not a literal ship model:

- axial/roll inertia Ixx ≈ 1.17×10^7 kg·m²;
- pitch/yaw inertia Iyy≈Izz ≈ 3.20×10^8 kg·m².

The real ship will differ because its mass is strongly nonuniform along x and because the launch, tanks, radiators and aft machinery are distributed asymmetrically.

## 4. Candidate RCS architecture to size

Do not use the main torch for ordinary docking or fine translation.

Candidate architecture:

- four axial RCS station bands retained;
- distributed, throttleable high-power plasma/electric thruster clusters;
- nominal individual high-authority thruster class: **25 kN candidate**;
- opposing pairs used for pure torque;
- multiple thrusters combined for translation;
- internal momentum storage handles fine pointing and routine attitude control;
- external RCS performs momentum unload, coarse slew, rapid slew and translation.

The 25 kN value is an engineering sizing point only.

## 5. Translation sizing

At 1,158.5 t wet mass:

- 25 kN total -> 0.0216 m/s²;
- 50 kN total -> 0.0432 m/s²;
- 100 kN total -> 0.0863 m/s²;
- 200 kN total -> 0.173 m/s².

For docking, full thrust is unnecessary. Deep throttling plus pulse/impulse control is required. A 100 kN aggregate translation capability gives substantial collision-avoidance authority while remaining tiny compared with torch acceleration.

Candidate operating doctrine to test:

- FINE: sub-kN effective commanded thrust via throttling/pulsing;
- DOCK: 5–25 kN aggregate typical;
- MANEUVER: 25–100 kN aggregate;
- ABORT: up to 200 kN aggregate where plume geometry permits.

## 6. Pitch/yaw torque sizing

With fore/aft stations separated by roughly 40 m, one opposed 25 kN pair can generate approximately:

`tau ≈ F × separation ≈ 25,000 × 40 ≈ 1.0 MN·m`

Using the homogeneous-cylinder pitch/yaw reference inertia (~3.20×10^8 kg·m²):

- angular acceleration ≈ 0.00313 rad/s² ≈ 0.179 deg/s²;
- ideal bang-bang 90° rest-to-rest slew ≈ 44.8 s;
- ideal bang-bang 180° rest-to-rest slew ≈ 63.4 s.

Two simultaneous couples roughly halve inertia-normalized slew time by √2, yielding ~31.7 s for 90° and ~44.8 s for 180° before rate limits/settling margins.

These are sizing results, not final crewed maneuver limits.

## 7. Roll torque sizing

Roll uses transverse lever arms near the ~4.5 m body radius rather than the long fore/aft separation. A 25 kN opposed pair across an effective ~8 m diameter provides about 0.2 MN·m.

Against the simple-cylinder axial inertia (~1.17×10^7 kg·m²):

- angular acceleration ≈ 0.0171 rad/s² ≈ 0.98 deg/s²;
- ideal bang-bang 90° roll ≈ 19.2 s;
- ideal bang-bang 180° roll ≈ 27.1 s.

Again, full rigid-body inertia and plume constraints must be substituted before qualification.

## 8. Candidate handling doctrine emerging

The existing MVP envelope of degree-per-second attitude rates should not be treated as hardware truth. A more physically grounded hierarchy is:

- **fine pointing:** internal momentum storage / precision actuators;
- **normal slew:** low duty external torque plus internal momentum system;
- **rapid slew:** distributed RCS couples;
- **translation/docking:** throttleable distributed RCS;
- **large ordinary-space Δv:** axial torch only.

This produces a spacecraft that behaves like a large rigid vehicle rather than a fighter.

## 9. Key unresolved inputs

Q4 cannot close until the following are supplied or derived:

1. intrinsic inertia tensors for habitat/armor, tanks, radiator assemblies, relational plant, aft propulsion and launch;
2. remass free-surface/slosh treatment or baffled-tank equivalent;
3. actual candidate thruster plume cones and +Z launch-extraction dead wedge;
4. thruster minimum stable thrust / minimum impulse bit;
5. RCS working-fluid choice and exhaust velocity;
6. internal momentum-storage capacity and unload interval;
7. structural torque limits and crew comfort/operational slew-rate caps.

## 10. Q4 v0.1 disposition

**Architecture candidate retained:** internal momentum storage + distributed high-authority plasma RCS.

**Candidate high-authority thruster unit:** 25 kN class.

**Candidate aggregate translation authority:** 100 kN normal maneuver, up to 200 kN abort.

**Candidate pitch/yaw couple:** ~1 MN·m per fore/aft opposed pair at ~40 m separation.

**Q4 status:** OPEN, but actuator scale is now bounded well enough to proceed into full mass-property closure and Q5 thermal/power sizing.
