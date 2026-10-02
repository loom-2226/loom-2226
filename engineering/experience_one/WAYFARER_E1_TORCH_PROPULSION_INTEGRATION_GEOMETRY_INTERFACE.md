# Wayfarer E1 Torch — Propulsion, Integration and Geometry Interface

**Status:** E1 vehicle-level primary torch interface frozen with explicit technology and component-certification holds  
**Purpose:** Single human-readable handoff for primary propulsion performance, remass/feed requirements, energy and thermal interfaces, structural loads, vehicle geometry, operational constraints, visualization geometry, and unresolved physical-hardware interfaces.  
**Authority boundary:** This document consolidates governed and requalified E1 source artifacts through T5. It does not promote unresolved component physics or implementation detail to canon or hardware certification. Campaign mutation: **ZERO**. LLM calculation authority: **ZERO**.

## 1. Interpretation and authority classes

Torch information in this interface belongs to four distinct classes and MUST NOT be conflated:

1. **Vehicle-interface authority** — earned thrust modes, exhaust velocities, mass-flow requirements, remass accounting, operating-state rules, and vehicle-facing propulsion requirements.
2. **Interface geometry** — vehicle-relative stations, interfaces, thrust axis, and required load-path connectivity that downstream vehicle/visualization consumers may preserve deterministically.
3. **Candidate envelope geometry** — current non-governing packaging envelopes useful for integration and rendering, but not certified physical component dimensions.
4. **Unresolved physical hardware and source physics** — reactor/source realization, fusion gain, directed-energy coupling, radiation deposition, working-fluid species, feed hardware, magnetic-nozzle physics, physical plume, thermal lifetime, detailed thrust-frame structure, and other component-certification matters.

The precise freeze statement is:

> **The Wayfarer E1 primary torch vehicle interface is frozen as `E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD`.**

Wayfarer vehicle engineering may consume the frozen torch interface. This does **not** certify the reactor/source, magnetic nozzle, working-fluid/feed system, shadow shield, radiator system, thrust frame, physical plume, or associated propulsion hardware.

## 2. Vehicle-level primary propulsion specification

| Parameter | Current value / specification | Interpretation |
|---|---:|---|
| Architecture | `AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE` | Vehicle architecture |
| Primary torch count | **1** | Current authority |
| Main body length | **57 m** | Current E1 geometry basis |
| Main body diameter | **9 m** | Current E1 geometry basis |
| Wet mass | **1,158.5 t** | Governed E1 mass state |
| Dry mass | **858.5 t** | Governed E1 mass state |
| Normal torch remass | **250 t** | Available for normal torch operation |
| Protected water reserve | **50 t** | Not normal torch remass |
| Post-normal-remass mass | **908.5 t** | Vehicle state after normal-remass expenditure |
| Governed operating modes | **6** | ECON through LIMIT |
| Acceleration envelope | **0.30–7.5 g** | Governed requirement |
| Effective exhaust velocity envelope | **300–3,000 km/s** | Governed requirement |
| Mass-flow envelope | **1.1361004025–284.025100625 kg/s** | Derived requirement |
| Required mass-flow turndown | **250:1** | Feed-system requirement |
| High-drive reject interface | **900 K** | Thermal interface, not radiator certification |
| Radiator count | **4** | Current vehicle interface |
| Working-fluid species | **OPEN** | Not selected |
| Source architecture / realizability | **OPEN** | Not certified |
| Fusion gain / Q | **OPEN** | Not certified |
| Source specific power | **OPEN** | Not certified |
| Magnetic-nozzle efficiency | **OPEN** | Not certified |
| Physical plume geometry | **OPEN** | Not certified |
| Component hardware certification | **FALSE** | T5 authority boundary |

## 3. Governed operating modes

| Mode | Acceleration | Effective exhaust velocity | Initial axial thrust | Direct kinetic jet power |
|---|---:|---:|---:|---:|
| `ECON` | **0.30 g** | **3,000 km/s** | **3.408301 MN** | **5.112452 TW** |
| `CRUISE` | **1.0 g** | **2,000 km/s** | **11.361004 MN** | **11.361004 TW** |
| `EXPEDITE` | **2.0 g** | **1,000 km/s** | **22.722008 MN** | **11.361004 TW** |
| `FAST` | **3.0 g** | **700 km/s** | **34.083012 MN** | **11.929054 TW** |
| `HARD` | **5.0 g** | **450 km/s** | **56.805020 MN** | **12.781130 TW** |
| `LIMIT` | **7.5 g** | **300 km/s** | **85.207530 MN** | **12.781130 TW** |

These cards define required vehicle behavior. They do not establish how a physical fusion source, plasma system, feed system, or magnetic nozzle achieves it.

## 4. Remass and feed interface

The normal-remass flow envelope is approximately **1.1361004025 kg/s → 284.025100625 kg/s**, requiring approximately **250:1** turndown.

The **250 t normal-remass inventory** is the normal propulsion consumable. The **50 t protected water reserve is not normal torch remass** and MUST NOT be silently consumed by trajectory optimization, qualification, or mission planning.

Working-fluid identity, storage phase/density/tankage, CoM migration, thermal conditioning/ionization, feed hardware, response time, feed pressure, valves/pumps/injectors, fault isolation, species-dependent energy transfer, magnetization/gyradius, plasma detachment, divergence, interception, erosion/contamination and lifetime remain technology holds.

## 5. Energy accounting interface

The torch model maintains a strict firewall between:

- direct kinetic jet power;
- fusion/source output;
- external driver power;
- electrical load;
- intercepted/deposited energy;
- vehicle waste heat.

The governed mode cards imply approximately **5.1–12.8 TW of direct kinetic exhaust power**. This is not automatically reactor thermal output, fusion-source output, electrical-generation requirement, radiator load, or vehicle waste heat.

Source directed fraction, fusion gain/Q and source specific power remain open. Source output, driver power and source mass therefore remain unresolved unless explicit sensitivity inputs are supplied.

## 6. Thermal and deposition interface

The high-drive thermal rejection interface is **900 K** with **four radiators**. This does not certify torch radiator area.

Vehicle deposition fraction and radiator emissivity are unresolved. Required radiator area is calculated only when a physical deposition load and emissivity are explicitly supplied. The deposition partition must ultimately account for photons, neutrons/side reactions, magnet/nozzle interception, charged-particle leakage, secondary heating and mode dependence.

Thermal transport/plumbing, geometry/view factors/clearance, transient buffer credit, shield/magnet thermal lifetime and transient rejection duty remain open.

## 7. Source and shadow-shield interface

A directional shadow-shield function is required to protect occupied and sensitive forward ship systems. The model must eventually budget prompt photon transport, neutron and secondary transport, charged-particle leakage, scattering/streaming paths, activation/decay heat, and shield heating/rejection.

Shield materials and layering are **OPEN**. The current shield body is therefore an allocated candidate envelope, not a certified material stack.

## 8. Ship frame and detailed rendering geometry

The Wayfarer uses **X longitudinal along the ship axis**. The following geometry is the current rendering/integration basis:

| Region / interface | X range or station | Transverse basis | Authority |
|---|---:|---:|---|
| Shadow-shield envelope | **38–43 m** | **5.5 m working diameter** | `CANDIDATE_ENVELOPE_GEOMETRY` / `NON_GOVERNING_CANDIDATE` |
| Reactor/source + thrust-frame envelope | **43–50 m** | **4.25 m working transverse diameter** | `CANDIDATE_ENVELOPE_GEOMETRY` / `NON_GOVERNING_CANDIDATE` |
| Four-longeron thrust-frame convergence | **48–50 m** | connectivity requirement | `INTERFACE_GEOMETRY` |
| Magnetic-nozzle envelope | **50–57 m** | **6.0 m working aperture/support diameter** | `CANDIDATE_ENVELOPE_GEOMETRY` / `NON_GOVERNING_CANDIDATE` |
| Primary thrust/exhaust axis | vehicle centerline | +X reference | `INTERFACE_GEOMETRY` |

The governing load-path concept is:

`FOUR_MAIN_LONGERONS_CONVERGE_TO_ONE_AFT_THRUST_FRAME_AND_ONE_AXIAL_NOZZLE`

These dimensions support deterministic integration and rendering. They MUST NOT be interpreted as certified reactor outer mold lines, shield thickness, magnet-coil topology, nozzle field geometry, or final hardware dimensions.

## 9. Structural interface

The primary structural interface is `FOUR_LONGERON_AXIAL_THRUST_FRAME_INTERFACE`.

The known quasi-static initial axial load envelope runs from **3.408301 MN (ECON)** to **85.207530 MN (LIMIT)**. `LIMIT` is the governing known axial load before unearned design factors.

Structural design factor, dynamic amplification, nozzle side load, fatigue spectrum, local stress/reinforcement, detailed thrust-frame geometry and FEA-qualified installation remain open.

## 10. Magnetic-nozzle interface

The vehicle requires one aft axial magnetic-nozzle function compatible with the governed thrust and remass-flow envelope.

Nozzle efficiency, field topology/strength, coil geometry/stress, working-fluid magnetization, gyroradius, plasma expansion, detachment, divergence, wall/coil interception, erosion/contamination and lifetime remain unresolved.

The **6.0 m aperture/support diameter and x=50–57 m envelope are candidate packaging geometry**, not a certified physical nozzle design.

## 11. Physical plume and external-clearance interface

No physical torch plume has been earned. Therefore:

- plume half-angle: **OPEN**;
- plume length: **OPEN**;
- clearance margin: **OPEN**;
- mode-dependent divergence/density: **OPEN**;
- detachment/backflow: **OPEN**;
- surface interception/deposition: **OPEN**.

Future clearance must include external vehicle hardware, including **radiators deployed and stowed**, RCS installations, docking/launch interfaces and other appendages.

An authoritative GLB MUST NOT fabricate a plume cone. It may include a metadata-only unresolved plume interface or clearly non-authoritative visualization aid.

## 12. Operational interface

Torch operation and high-metric thermal/field operation are mutually exclusive.

`NO_TORCH_OPERATION_DURING_HIGH_METRIC_THERMAL_OR_FIELD_OPERATION`

Additional exclusions are:

- `NO_NORMAL_TORCH_CONSUMPTION_OF_PROTECTED_WATER_RESERVE`
- `NO_COMPONENT_GEOMETRY_FREEZE_FROM_CANDIDATE_PACKAGING`
- `NO_EXTERNAL_HARDWARE_FREEZE_BEFORE_PHYSICAL_PLUME_CLEARANCE`

Transition preconditions remain open pending feed, field, thermal and attitude dynamics. Safe-shutdown/fault-isolation dynamics and RCS/torch mutual plume interaction remain open.

## 13. RCS integration holds carried forward

The primary propulsion interface carries the existing RCS installation holds:

1. `PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP`
2. `WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD`
3. `MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE`
4. `VECTORING_DYNAMIC_RESPONSE_AND_LIFE`
5. `MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT`

Torch geometry MUST NOT silently invalidate qualified RCS hardpoint placement.

## 14. Standalone GLB / Computational Shipyard representation

A standalone torch GLB may be detailed at the **engineering-interface/envelope level**. It may contain:

- shadow-shield candidate envelope;
- reactor/source candidate envelope;
- four-longeron convergence representation;
- aft thrust-frame interface;
- magnetic-nozzle candidate envelope;
- explicit interface planes/stations;
- primary thrust-axis reference;
- mode-card, thrust, jet-power and remass metadata;
- explicit technology-hold metadata;
- an unresolved plume metadata node with no fabricated cone.

It MUST NOT claim or imply an earned detailed design for reactor internals, shield material stack, feed machinery/plumbing topology, magnet winding topology, plasma field shape, nozzle throat/exit physics, physical plume, or detailed local thrust-frame structure.

The standalone geometry is intended to be deterministically placeable back into the Wayfarer GLB using the same ship-frame X stations.

## 15. T5 component-certification holds

T5 carries these explicit holds:

1. `SOURCE_REACTOR_REALIZABILITY`
2. `DIRECTED_ENERGY_REMASS_COUPLING_PARTITION`
3. `RADIATION_AND_PARTICLE_DEPOSITION`
4. `WORKING_FLUID_STORAGE_FEED_IMPLEMENTATION`
5. `MAGNETIC_NOZZLE_PHYSICS_AND_LIFETIME`
6. `SHIELD_MAGNET_THERMAL_LIFETIME`
7. `THRUST_FRAME_DYNAMICS_LOCAL_LOAD_AND_FATIGUE`
8. `PHYSICAL_PLUME_EXTERNAL_HARDWARE_CLEARANCE`
9. `RCS_INTEGRATION`

These do not block use of the frozen E1 vehicle interface. They block unsupported promotion to certified physical hardware.

## 16. What downstream consumers may and may not assume

### May consume as current E1 authority

- the six governed torch mode cards;
- normal-remass and protected-water accounting;
- exact mode mass-flow, exhaust-velocity, thrust and kinetic-jet-power behavior from executable authority;
- the 250:1 feed turndown requirement;
- energy-accounting separation;
- the 900 K / four-radiator thermal interface without assuming a torch radiator area;
- the four-longeron primary load-path requirement;
- the candidate aft packaging geometry with its explicit non-governing status;
- torch/high-metric mutual exclusion;
- technology holds;
- deterministic interface/envelope geometry for GLB and Computational Shipyard use.

### MUST NOT assume solved/certified

- fusion architecture or reactor realizability;
- Q, source directed fraction, source specific power, source mass or driver power;
- working-fluid species or physical feed implementation;
- nozzle efficiency or magnetic field topology;
- plasma detachment/divergence/interception;
- physical plume geometry;
- radiation/deposition fractions;
- shield composition/layering;
- torch-derived radiator area;
- final reactor/nozzle/shield dimensions;
- thrust-frame FEA, fatigue life or local reinforcement;
- component thermal lifetime;
- final RCS/torch plume interaction;
- propulsion component installation release.

## 17. Primary governed source lineage

This handoff consolidates but does not replace executable authority in the E1 torch closure sequence:

- T1 — `src/wayfarer_e1_torch_interface.py`
- T2 — `src/wayfarer_e1_torch_energy_thermal.py`
- T3 — `src/wayfarer_e1_torch_remass_feed_nozzle.py`
- T4 — `src/wayfarer_e1_torch_structural_plume_ops.py`
- T5 — `src/wayfarer_e1_torch_integrated_qualification.py`
- underlying packaging/structural authority — `src/wayfarer_torch_thermal_shield_thrust_frame_envelope.py`

T5 closes the vehicle-facing interface with **zero `OPEN_BLOCKING_E1` items** while retaining explicit component-certification holds.

## 18. Handoff rule

For Computational Shipyard, GLB visualization, Navigator, mission planning, structural integration, thermal integration or subsequent E1 engineering:

- consume governed torch performance directly;
- preserve normal-remass/protected-water accounting;
- preserve interface geometry and load-path connectivity;
- label candidate packaging as non-governing candidate geometry;
- propagate all technology holds downstream;
- do not invent physical plume, reactor architecture, working-fluid species, shield implementation, magnetic-nozzle internals, feed topology or detailed component structure merely to complete a render.

The frozen interface answers:

> **What must Wayfarer provide to, receive from, reserve for, and structurally accommodate around its primary propulsion system?**

It deliberately does not claim to answer:

> **Exactly how does a physically certified 2226 fusion torch work internally?**
