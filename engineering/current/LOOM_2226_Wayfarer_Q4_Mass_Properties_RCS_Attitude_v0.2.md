# LOOM 2226 — Wayfarer Q4 Mass Properties, RCS & Attitude v0.2

**Status:** ENGINEERING STUDY / NON-CANON  
**Date:** 2026-09-11  
**Parent:** `LOOM_2226_Wayfarer_Flight_System_Qualification_Plan_v0.1.md`

## 0. Authority boundary

This study does not alter CANON II. It replaces no current Navigator handling value. It derives a conservative maneuver-sizing envelope from the current Wayfarer mass ledger and geometry while explicitly preserving uncertainty in subsystem intrinsic inertia.

## 1. Mass-state anchors

Current engineering/canon inputs used here:

- dry mass: 858.5 t;
- reference wet mass: 1,158.5 t;
- normal remass: 250 t centered near x=25 m in the current geometry compiler;
- protected water: 50 t centered near x=12.5 m;
- docked launch: 33 t at approximately x=21.8 m, z=+5.2 m;
- ship length: 57 m;
- nominal body diameter: 9 m.

The existing centroid ledger gives approximately:

- docked dry CoM x = 27.99 m, z = +0.20 m;
- docked wet CoM x = 26.68 m, z = +0.15 m.

## 2. Inertia truth boundary

The repository currently contains subsystem masses and centroids but does not contain final intrinsic inertia tensors for most subsystems. Therefore two deliberately different models are retained:

### Q4-L lower-fidelity centroid model

Treat each subsystem mass as concentrated at its current centroid and apply only the parallel-axis term.

For the reference wet state this yields approximately:

- pitch/yaw transverse inertia: 1.35–1.36 × 10^8 kg m²;
- roll inertia from centroid offsets alone: ~8.7 × 10^5 kg m².

The roll value is physically incomplete because it omits the intrinsic radial distribution of almost the entire ship.

### Q4-U conservative whole-body sizing model

Treat the 1,158.5 t reference wet vehicle as a homogeneous 57 m × 9 m cylinder solely for conservative actuator sizing.

This gives approximately:

- pitch/yaw inertia: 3.20 × 10^8 kg m²;
- roll inertia: 1.17 × 10^7 kg m².

This is not a claim that Wayfarer is a homogeneous cylinder. It is a conservative engineering surrogate until component shape tensors are available.

### Working design envelope

For pitch/yaw actuator sizing use:

`I_transverse_design = 3.2e8 kg m²`

with the centroid-only 1.35e8 kg m² result retained as the lower-fidelity bound.

No final actuator canon may be promoted until the geometry compiler emits intrinsic component inertias.

## 3. RCS architecture candidate

Wayfarer should not use the main torch for routine docking, station keeping or ordinary attitude control.

Candidate architecture:

- distributed high-authority plasma/electrothermal RCS at the existing fore/mid/aft station bands;
- internal momentum-storage devices for fine pointing and low-disturbance attitude maintenance;
- RCS for translation, rapid slew and momentum unloading;
- symmetric opposing pairs wherever geometry permits;
- explicit +Z launch-bay plume/dead-zone protection.

Exact thruster count remains OPEN. A practical installation range to test is 16–24 externally mounted/vectorable units distributed across the four existing station bands.

## 4. High-authority RCS sizing point

Retain the current candidate individual-thruster class:

`F_thruster,max = 25 kN`

This is a sizing point, not a canon lock.

### Translation authority

Representative aggregate commands:

- precision docking/close approach: 10–25 kN total, deeply throttled/pulsed;
- normal translation: ~100 kN total;
- collision-avoidance / abort translation: ~200 kN total where plume geometry permits.

At 1,158.5 t wet mass:

- 10 kN -> 0.00863 m/s² = 0.00088 g;
- 25 kN -> 0.0216 m/s² = 0.00220 g;
- 100 kN -> 0.0863 m/s² = 0.00880 g;
- 200 kN -> 0.1726 m/s² = 0.0176 g.

This provides centimetre/second-class precision through short impulses while retaining meaningful emergency translation without torch ignition.

## 5. Pitch/yaw torque authority

A fore/aft opposed pair separated by about 40 m gives an effective single-thruster moment arm near 20 m about the ship CoM.

Two 25 kN thrusters in a pure couple therefore provide approximately:

`tau = 2 * 25,000 N * 20 m = 1.0 MN m`

Against the conservative transverse design inertia:

`alpha = tau / I = 0.003125 rad/s² = 0.179 deg/s²`

Against the centroid-only lower-fidelity inertia the same couple would produce ~0.42 deg/s². The conservative value governs sizing.

## 6. Slew envelope

For a symmetric accelerate/decelerate rest-to-rest maneuver with no rate cap, using the conservative 1 MN m / 3.2e8 kg m² case:

- 30° slew: ~25.9 s ideal;
- 90° slew: ~44.8 s ideal;
- 180° slew: ~63.4 s ideal.

Operational commands must add rate caps, structural/crew constraints and settling time. Therefore the candidate handling doctrine should target approximately:

- fine-pointing corrections: internal momentum system, sub-degree, low disturbance;
- normal 90° vehicle reorientation: ~50–70 s including settle margin;
- normal 180° reversal: ~70–100 s including settle margin;
- emergency slew: higher multi-pair torque may be authorized, but must be separately power/thermal qualified.

This is intentionally not fighter-like handling.

## 7. Roll control

Roll inertia is much lower than pitch/yaw because the ship is long and comparatively narrow. Roll authority should therefore be rate-limited by structure, plumbing, deployed radiator state, docking configuration and crew/loose-object constraints rather than by raw thruster torque alone.

Do not preserve the old MVP roll-rate figure merely because the actuator could exceed it. Final roll limits should be operational constraints derived after radiator and launch interference modeling.

## 8. RCS working-fluid optionality

Q4 does not yet freeze an RCS propellant. The maneuvering system should preferentially share a qualified torch/utility feed where practical, but should not be forced to do so if minimum-impulse-bit, storage, contamination or power efficiency favor a dedicated clean feed.

Candidate RCS feed classes to carry into Q5:

- water/steam/plasma utility feed;
- nitrogen or argon clean plasma feed;
- other feed only if it materially improves minimum impulse bit or hardware lifetime.

## 9. Power coupling deferred to Q5

A 25 kN plasma thruster can imply hundreds of MW to GW of directed exhaust power depending on exhaust velocity. Therefore Q4 qualifies force/torque geometry only. Q5 must choose the RCS exhaust-velocity/power point and prove bus and thermal closure.

No RCS thrust rating is final until Q5 closes.

## 10. Q4 disposition after v0.2

### Supported now

- preserve distributed RCS architecture;
- preserve internal momentum storage for fine attitude control;
- retain 25 kN per-thruster as the current high-authority sizing point;
- use 3.2e8 kg m² as conservative pitch/yaw design inertia pending component tensors;
- size normal translation around 100 kN aggregate and abort translation around 200 kN aggregate;
- target roughly minute-class large-angle reorientation rather than fighter-like slew.

### Still open

1. intrinsic inertia tensors by major component;
2. exact thruster count and nozzle directions;
3. minimum impulse bit;
4. final nominal/emergency angular-rate caps;
5. RCS exhaust velocity and working fluid;
6. power/thermal duty limits;
7. radiator-deployed and launch-extraction interference matrices;
8. one-cluster-out controllability.

**Q4 remains OPEN, but its force/torque sizing envelope is now sufficiently bounded to proceed into Q5.**
