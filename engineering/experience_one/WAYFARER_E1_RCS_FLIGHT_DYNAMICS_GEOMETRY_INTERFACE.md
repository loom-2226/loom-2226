# Wayfarer E1 RCS — Flight Dynamics and Geometry Interface

**Status:** E1 vehicle-level RCS architecture frozen with explicit component-installation holds  
**Purpose:** Single human-readable handoff for RCS geometry, flight dynamics, control/allocation requirements, sampled actuator-demand evidence, and unresolved physical-hardware interfaces.  
**Authority boundary:** This document consolidates governed/requalified E1 source artifacts. It does not promote unresolved component detail to canon or hardware certification. Campaign mutation: **ZERO**. LLM calculation authority: **ZERO**.

## 1. Interpretation and authority classes

RCS data in this interface belongs to four distinct classes and MUST NOT be conflated:

1. **Geometry authority** — 16 hardpoint coordinates, band/azimuth arrangement, ship-frame convention, and current point-clearance screens.
2. **Flight-model authority** — configuration-aware mass/CoM/inertia model, resultant force-vector model, wrench allocation, GNC, nominal/degraded limits, and qualified witness cases.
3. **Sampled demand evidence** — actuator commands observed in governed mount-resolved time-domain qualification. These are requirement evidence, not component certification.
4. **Unresolved physical hardware** — working fluid, exhaust velocity, actual MIB, valve dynamics, detailed vectoring mechanism response, nozzle/pod geometry, physical plume, thermal load, cycle life, local structure/reinforcement, and component installation release.

The precise freeze statement is:

> **The E1 RCS vehicle architecture is frozen with component-installation holds, and the tested rigid-body/GNC/allocation flight-dynamics envelope is qualified for its governed cases.**

This is not a claim that every Wayfarer RCS maneuver, configuration, disturbance, failure combination, docking/contact event, plume interaction, saturation history, flexible-body mode, or propellant state has been qualified.

## 2. Vehicle-level RCS specification

| Parameter | Current value / specification | Interpretation |
|---|---:|---|
| Architecture | `COMPOUND_COARSE_FINE_VECTORED_MOUNT` | Frozen vehicle architecture |
| Mount count | **16** | Four axial bands × four mounts |
| Axial bands | **4** | FORE, FORE_MID, RADIATOR_ROOT, AFT |
| Logical failure clusters | **A, B, C, D** | One mount from each band per cluster |
| Allocator mount force cap | **25,000 N** | Qualified allocation cap; not final certified thruster rating |
| Nominal translation requirement | **100,000 N** | Allocator requirement |
| One-cluster-out translation requirement | **75,000 N** | Degraded allocator requirement |
| Nominal pitch/yaw torque | **1,000,000 N·m** | Each axis |
| Nominal roll torque | **200,000 N·m** | — |
| One-cluster-out pitch/yaw torque | **750,000 N·m** | Each axis |
| One-cluster-out roll torque | **100,000 N·m** | — |
| Vector-cone basis | **45° recovered geometric cone** | Geometric/realizability basis; not physically certified actuator range |
| Allocator vector samples per mount | **5** | RADIAL_IN, AXIAL_PLUS, AXIAL_MINUS, TANGENT_PLUS, TANGENT_MINUS |
| Coarse actuation family | `ELECTRONICALLY_METERED_THROTTLEABLE_LIQUID_THRUSTER_FAMILY` | Architecture downselect; component not selected |
| Fine actuation family | `DEDICATED_FAST_PULSED_FINE_AUTHORITY_ELEMENT` | Architecture downselect; component not selected |
| Preferred vectoring | `INTERNAL_FLOW_VECTORING` | Architecture downselect |
| Vectoring reserve | Mechanical gimbal | Reserve architecture |
| Working fluid | **OPEN** | Not selected |
| Final RCS exhaust velocity | **OPEN** | Not selected |
| Hardware MIB | **OPEN** | Not certified |
| Valve response/bandwidth | **OPEN** | Not certified |
| Cycle life | **OPEN** | Not certified |
| Physical plume cone | **OPEN** | Not certified |
| Structural mount design/compliance | **OPEN** | Installation hold |
| Component installation release | **FALSE** | Vehicle architecture freeze does not release component installation |

## 3. Ship frame and exact hardpoint placement

The Wayfarer main body is represented with **X longitudinal along the ship axis**. RCS hardpoints lie at radius **4.5 m**, half the current 9 m main-body diameter. Positions below are ship-frame metres.

The recovered axial bands are:

| Band | X range (m) | Hardpoint X center (m) | Azimuths | Placement rationale |
|---|---:|---:|---|---|
| FORE | 5–8 | **6.5** | 0°, 90°, 180°, 270° | Forward hull |
| FORE_MID | 17–20 | **18.5** | 45°, 135°, 225°, 315° | Rotated off launch/docking cardinals |
| RADIATOR_ROOT | 35–38 | **36.5** | 45°, 135°, 225°, 315° | Rotated off cardinal radiator roots |
| AFT | 43–46 | **44.5** | 0°, 90°, 180°, 270° | Aft propulsion exterior candidate band |

Exact hardpoints:

| Mount | Band | Cluster | X (m) | Y (m) | Z (m) | Azimuth | Radius (m) |
|---|---|---|---:|---:|---:|---:|---:|
| RCS_FORE_1 | FORE | A | 6.5 | +4.500000 | 0.000000 | 0° | 4.5 |
| RCS_FORE_2 | FORE | B | 6.5 | 0.000000 | +4.500000 | 90° | 4.5 |
| RCS_FORE_3 | FORE | C | 6.5 | -4.500000 | 0.000000 | 180° | 4.5 |
| RCS_FORE_4 | FORE | D | 6.5 | 0.000000 | -4.500000 | 270° | 4.5 |
| RCS_FORE_MID_1 | FORE_MID | A | 18.5 | +3.181981 | +3.181981 | 45° | 4.5 |
| RCS_FORE_MID_2 | FORE_MID | B | 18.5 | -3.181981 | +3.181981 | 135° | 4.5 |
| RCS_FORE_MID_3 | FORE_MID | C | 18.5 | -3.181981 | -3.181981 | 225° | 4.5 |
| RCS_FORE_MID_4 | FORE_MID | D | 18.5 | +3.181981 | -3.181981 | 315° | 4.5 |
| RCS_RADIATOR_ROOT_1 | RADIATOR_ROOT | A | 36.5 | +3.181981 | +3.181981 | 45° | 4.5 |
| RCS_RADIATOR_ROOT_2 | RADIATOR_ROOT | B | 36.5 | -3.181981 | +3.181981 | 135° | 4.5 |
| RCS_RADIATOR_ROOT_3 | RADIATOR_ROOT | C | 36.5 | -3.181981 | -3.181981 | 225° | 4.5 |
| RCS_RADIATOR_ROOT_4 | RADIATOR_ROOT | D | 36.5 | +3.181981 | -3.181981 | 315° | 4.5 |
| RCS_AFT_1 | AFT | A | 44.5 | +4.500000 | 0.000000 | 0° | 4.5 |
| RCS_AFT_2 | AFT | B | 44.5 | 0.000000 | +4.500000 | 90° | 4.5 |
| RCS_AFT_3 | AFT | C | 44.5 | -4.500000 | 0.000000 | 180° | 4.5 |
| RCS_AFT_4 | AFT | D | 44.5 | 0.000000 | -4.500000 | 270° | 4.5 |

The ±3.181981 m coordinates are the 45° locations on a 4.5 m radius circle; source code remains authoritative for full floating-point reconstruction.

### 3.1 Failure-cluster topology

| Cluster | FORE | FORE_MID | RADIATOR_ROOT | AFT |
|---|---:|---:|---:|---:|
| A | 0° | 45° | 45° | 0° |
| B | 90° | 135° | 135° | 90° |
| C | 180° | 225° | 225° | 180° |
| D | 270° | 315° | 315° | 270° |

A one-cluster-out condition therefore removes four longitudinally distributed hardpoints rather than an entire ring.

## 4. Mount force-vector model

At each mount, with ship-frame hardpoint position `[x,y,z]`, define radial distance `r = sqrt(y²+z²)` and:

- outward = `[0, y/r, z/r]`
- inward = `[0, -y/r, -z/r]`
- tangent = `[0, -outward_z, outward_y]`
- axial = `[1,0,0]`

The allocator samples five unit resultant-force directions:

| Name | Construction | Meaning |
|---|---|---|
| `RADIAL_IN` | unit(inward) | Directly inward toward longitudinal axis |
| `AXIAL_PLUS` | unit(inward + axial) | 45° radial/+X edge |
| `AXIAL_MINUS` | unit(inward - axial) | 45° radial/-X edge |
| `TANGENT_PLUS` | unit(inward + tangent) | 45° radial/tangential edge |
| `TANGENT_MINUS` | unit(inward - tangent) | Opposite tangential edge |

For mount `i`:

`F_i = T_i * fhat_i`

`tau_i = (r_i - r_COM) × F_i`

The allocator solves the complete physical wrench `[Fx,Fy,Fz,Tx,Ty,Tz]`. CoM is taken from the current configuration-aware mass state rather than hard-coded.

The recovered Q4 result supporting a continuous circular 45° resultant-force cone is geometric/kinematic evidence. It does **not** certify a physical gimbal, internal-flow-vectoring mechanism, nozzle, actuator slew rate, or plume envelope.

## 5. Allocator numerical contract

| Parameter | Value | Meaning |
|---|---:|---|
| Per-mount force cap | **25,000 N** | Capped resultant force per hardpoint |
| Characteristic length | **20.0 m** | Numerical force/torque normalization parameter; not ship geometry |
| Maximum solver iterations | **1,500** | Allocation numerical parameter |
| Relative normalized residual gate | **1.0e-4** | Allocation acceptance gate |
| Logical clusters | A/B/C/D | Used for one-cluster-out qualification |

The allocator uses a per-mount capped-simplex constraint across sampled force directions. The total contribution of a mount cannot exceed its 25 kN cap.

## 6. Configuration-aware mass and inertia interface

The current principal E1 RCS qualification configuration is:

| State | Value |
|---|---:|
| Normal remass | **250 t** |
| Protected water | **50 t** |
| Planetary launch | **DOCKED** |
| Total modeled mass | **1,158.5 t** |
| Normal-remass depletion doctrine | `BALANCED_FOUR_TANK_DRAW` |

The model computes mass, center of mass, and a full symmetric 3×3 rigid-body inertia tensor from the governed engineering mass ledger plus explicit equivalent-shape assumptions. The current launch-docked configuration produces a small +Z CoM displacement because the 33 t planetary launch is represented at approximately `[21.8, 0, +5.2] m`.

**Do not treat a single printed CoM or inertia tensor as a permanent Wayfarer constant.** `build_mass_inertia_state(normal_remass_t, protected_water_t, launch_docked)` is the configuration-aware authority. Consumers requiring exact numerical CoM/tensor values MUST consume that source result for the actual flight configuration rather than copying a stale snapshot from this document.

The current model includes intrinsic equivalent-shape component inertia and parallel-axis contributions. Its explicitly open physics are:

- radiator deployed mass distribution;
- fluid slosh/free-surface dynamics;
- flexible-body modes;
- structural-FEA-grade mass distribution;
- moving internal masses beyond declared stores.

The model is therefore current rigid-body engineering authority for E1 RCS requalification, **not** FEA, slosh, or flexible-body authority.

## 7. Closed-loop GNC interface

Standalone finite-attitude GNC qualification uses:

| Parameter | Value |
|---|---:|
| Numerical integration timestep | **0.05 s** |
| Maximum simulation duration | **240 s** |
| Required in-gate hold | **2 s** |
| Attitude convergence gate | **0.25°** |
| Body-rate convergence gate | **0.05°/s** |
| Natural frequency | **0.12 rad/s** |
| Damping ratio | **0.90** |

These are controller/model qualification parameters. They do not independently certify physical actuator bandwidth.

## 8. Mount-resolved coupled local-flight interface

The later coupled translation + full rigid-body rotation qualification places mount allocation inside the time-domain flight loop. Only allocator-achieved wrench advances vehicle state.

| Parameter | Nominal | One cluster failed |
|---|---:|---:|
| Force command limit | **100,000 N** | **75,000 N** |
| Roll torque limit | **200,000 N·m** | **100,000 N·m** |
| Pitch torque limit | **1,000,000 N·m** | **750,000 N·m** |
| Yaw torque limit | **1,000,000 N·m** | **750,000 N·m** |
| Numerical control/allocation cadence | **1.0 s** | **1.0 s** |
| Maximum qualification duration | **180 s** | **180 s** |
| Required terminal hold | **3 s** | **3 s** |
| Velocity convergence gate | **0.015 m/s** | **0.015 m/s** |
| Translation response rate | **0.16 s^-1** | **0.16 s^-1** |

The **1.0 s cadence is explicitly a numerical qualification cadence, not physical RCS hardware bandwidth**. The actuator contract in this qualification is continuous mount force vector; MIB, valve dynamics, vectoring dynamics, plume geometry, and structural compliance are not modeled.

### 8.1 Qualified mixed translation/attitude witness cases

| Case | Target velocity (m/s) | Attitude target | Failed cluster |
|---|---|---|---|
| `NOMINAL_MIXED_TRANSLATION_ATTITUDE` | `[+0.08,+0.25,-0.12]` | yaw +12° | none |
| `DEGRADED_MIXED_TRANSLATION_ATTITUDE_A` | `[+0.05,+0.18,+0.10]` | pitch +10° | A |
| `DEGRADED_MIXED_TRANSLATION_ATTITUDE_B` | `[+0.05,+0.18,+0.10]` | pitch +10° | B |
| `DEGRADED_MIXED_TRANSLATION_ATTITUDE_C` | `[+0.05,+0.18,+0.10]` | pitch +10° | C |
| `DEGRADED_MIXED_TRANSLATION_ATTITUDE_D` | `[+0.05,+0.18,+0.10]` | pitch +10° | D |

These are governed qualification witnesses, **not an exhaustive flight envelope**.

## 9. Sampled actuator-demand evidence

The qualified mount-resolved time-domain histories establish the following aggregate sampled demand evidence:

| Demand metric | Current result | Correct interpretation |
|---|---:|---|
| Maximum sampled mount thrust | **20,844.756650298394 N** | Highest observed mount demand in qualified traces |
| Allocator mount cap | **25,000 N** | Allocation ceiling, not certified component rating |
| Maximum sampled thrust step | **3,851.8896089839964 N/sample** | Demand history, not valve slew/bandwidth specification |
| Sampled exact-trace MIB upper bound | **9.281346527990696 N·s** | Upper bound for reproducing the sampled exact trace; **not hardware MIB** |
| Maximum sampled direction step | **27.725620059992647°** | Demand history |
| One-sample average direction-slew lower bound | **27.725620059992647°/s** | Requirement evidence; not certified vectoring slew capability |
| Gimbal/vectoring acceleration | **NOT DERIVED** | Open |
| Valve latency | **NOT DERIVED** | Open |
| Physical hardware MIB | **NOT DERIVED** | Open |

Transition metrics are grouped by **qualification case + mount ID**. Separate case clocks are not joined into artificial actuator transitions.

The model also derives on/off-transition counts from the traces. No aggregate count is frozen into this document because it is not required to define the current vehicle-level interface and should be regenerated from the governed trace if needed.

## 10. Clearance and integration state

| Interface | State |
|---|---|
| Launch-bay hardpoint **point** clearance | **PASS** |
| Docking-collar hardpoint **point** clearance | **PASS** |
| Radiator-root cardinal azimuth separation | **PASS** |
| Finite physical plume cone | **OPEN / NOT INVENTED** |
| Deployed radiator/plume sweep clearance | **OPEN** |
| Physical hardpoint/nozzle extent beyond skin | **NOT MODELED** |
| Mount load path/local reinforcement | **OPEN / INSTALLATION HOLD** |
| Working fluid/cycle/exhaust velocity/thermal load | **OPEN / INSTALLATION HOLD** |
| MIB/valve response/duty/total impulse/cycle life | **OPEN / INSTALLATION HOLD** |
| Vectoring dynamic response/life | **OPEN / INSTALLATION HOLD** |
| Component installation release | **FALSE** |
| Torch engineering may proceed | **TRUE**, carrying these holds as integration constraints |

The five explicit #203 component-installation holds are:

1. `PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP`
2. `WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD`
3. `MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE`
4. `VECTORING_DYNAMIC_RESPONSE_AND_LIFE`
5. `MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT`

## 11. What a flight-dynamics consumer may and may not assume

### May consume as current E1 authority

- exact 16 hardpoint positions and cluster topology;
- configuration-aware mass, CoM, and rigid-body inertia model;
- resultant mount-force geometry and `r × F` wrench construction;
- 25 kN/mount allocation cap;
- nominal and one-cluster-out vehicle wrench requirements;
- current bounded allocator and its numerical acceptance contract;
- current closed-loop GNC model parameters;
- current mount-resolved coupled local-flight model;
- the five qualified mixed translation/attitude witness cases;
- sampled actuator-demand evidence with its stated epistemic limits;
- current point-clearance and azimuth-separation screens.

### MUST NOT assume as solved/certified

- a specific RCS propellant or working fluid;
- RCS Isp/final exhaust velocity or physical propellant consumption;
- final pod/nozzle dimensions or mass;
- physical nozzle zero-angle/mechanism geometry from the mathematical force cone;
- actual minimum impulse bit;
- valve latency, bandwidth, response curve, or cycle life;
- vectoring/gimbal acceleration, settling, dynamic bandwidth, or life;
- finite plume geometry or plume impingement clearance;
- radiator plume interaction/transients;
- local structural reinforcement, compliance, or FEA-qualified mount loads;
- slosh/free-surface effects;
- flexible-body modes;
- docking/contact dynamics;
- exhaustive mission-wide saturation/failure coverage.

The engineering mass ledger contains a **25 t `rcs_docking_service` category**. This is a ledger category and MUST NOT be interpreted as the mass of the sixteen RCS thruster assemblies.

## 12. Primary governed source lineage

This interface consolidates, but does not replace, the executable authority in:

- `src/wayfarer_recovered_rcs_candidate.py`
- `src/wayfarer_mass_inertia_authority.py`
- `src/wayfarer_rcs_mount_allocator.py`
- `src/wayfarer_rcs_closed_loop_gnc.py`
- `src/wayfarer_rcs_coupled_local_flight.py`
- `src/wayfarer_rcs_time_domain_mount_coupling.py`
- `src/wayfarer_rcs_actuator_requirement_envelope.py`
- `src/wayfarer_rcs_coarse_fine_authority_envelope.py`
- `src/wayfarer_rcs_physical_requirement_envelope.py`
- `src/wayfarer_rcs_physical_architecture_trade.py`
- governed RCS technology downselect artifact(s)
- `src/wayfarer_rcs_installation_feasibility.py`

Historical geometry lineage includes recovered PR #96; current E1 qualification/recovery lineage proceeds through PRs #184–#203. PR #203 freezes the **vehicle-level architecture with component-installation holds** and authorizes torch engineering to begin with those holds carried forward.

## 13. Handoff rule

For visualization/GLB, Navigator, future six-DOF simulation, or torch integration:

- hardpoint **placement** may be deterministic from this interface/source geometry;
- mount force/wrench behavior may use the governed flight-model interfaces above;
- unresolved component bodies should remain explicit proxy/envelope geometry;
- no physical plume, propellant consumption, actuator latency/quantization, structural compliance, or final pod dimensions should be invented merely to complete a simulation or render.

When a configuration-dependent numerical snapshot (especially CoM or inertia tensor) is required, generate it from the governed executable mass/inertia authority for that exact configuration rather than copying a historical number.
