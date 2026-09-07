# LOOM 2226 — Generic Ship Physical Contract v0.2

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 2 HARDENED CONTRACT — FEATURE BRANCH — NOT CANON  
**Branch:** `qualification/portable-ship-phase2-contract-2026-09-08`  
**Supersedes for Phase-2 qualification:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_v0.1.md`  
**Hostile-review basis:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_Hostile_Review_2026-09-08.md`  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`

---

## 1. Purpose and inclusion rule

This contract defines the minimum generic physical authority required for a LOOM spacecraft class to support deterministic standalone flight dynamics, mass/CoM/inertia recomputation, contact/proximity geometry, docking/attachment, deterministic low-detail 3D reconstruction, ordinary RCS and torch dynamics, and later `metricpy` boundary qualification.

It is not a Wayfarer convenience schema and not a Basilisk/JEOD/Tudat/SimuPy API mirror.

> **Structured physical authority contains every physical quantity required to propagate the vehicle's true translational or rotational state, resolve contact/proximity geometry, or determine whether a propulsion/configuration transition is physically admissible.**

This document defines semantics and invariants. It does not authorize a production `LOOM_2226_SHIPCLASSES.sqlite3`; Phase 3 may only prototype a non-destructive Wayfarer-only SQLite after Phase 2 is accepted.

All solver-facing physical values are SI unless an ingestion field explicitly declares a source unit. Source units may be retained in provenance.

---

## 2. Authority chain

```text
CANON / approved design constraints
        ↓
GENERIC SHIP-CLASS PHYSICAL AUTHORITY
        ↓
CAMPAIGN SHIP INSTANCE STATE
        ↓
SIMULATION-DERIVED CURRENT TRUE STATE
        ↓
SENSORS / ESTIMATION / GN&C
        ↓
NAVIGATOR / HUD / GIS / TELEMETRY
```

Class authority defines what a spacecraft is physically. Instance state selects mutable stores, attachments, configuration and failures. Simulation derives current true state. Sensors/estimation may disagree with true state but do not overwrite it. Navigator/HUD/GIS own no spacecraft physics. External simulators own neither LOOM SQL nor campaign state.

---

## 3. Identity, version and provenance

Every class/variant exposes at least:

```text
ship_class_id
ship_class_name
variant_id
contract_version
physical_model_version
authority_status
valid_from
valid_until optional
provenance_set_id
```

A new physical-model version is required when a change can alter propagated state, mass properties, collision/contact geometry, actuator force/torque, configuration admissibility or regime-boundary behavior. Cosmetic-only rendering changes do not require a physical-model version change.

Initial status vocabulary remains compatible with existing LOOM practice:

```text
CANON
DESIGN_BASELINE
DERIVED
LEGACY_COMPATIBLE
VISUAL_REFERENCE
OPEN
compound status such as CANON_MASS_DESIGN_POSITION
```

No consumer may silently promote provenance. Derived quantities identify model/version and input lineage. A lower-authority datum may be used only when the scenario admits it and reports the degradation.

---

## 4. Body datum and frame discipline

Every class defines one immutable geometric body datum frame:

```text
frame_id
origin_definition
axis_x_definition
axis_y_definition
axis_z_definition
handedness
linear_unit
angular_unit
```

The body datum is not the instantaneous CoM frame. All physical poses must resolve into it.

Initial ordinary-dynamics convention:

```text
q_BN = [w,x,y,z]     # body -> inertial
omega_BN_B           # body angular velocity relative to inertial, expressed in body
```

A serialized true state must identify separately, even if some fields alias the same frame:

```text
translational_reference_frame
velocity_expression_frame
attitude_from_frame
attitude_to_frame
angular_velocity_expression_frame
```

No frame may be inferred merely from field name.

---

## 5. Component hierarchy and transform composition

A spacecraft is decomposed into physical components:

```text
component_id
parent_component_id optional
component_type
name
local_transform
configuration_membership
authority_status
provenance
```

`local_transform` is a rigid translation + orientation relative to the parent component or body datum.

Every physical pose must resolve through a unique acyclic parent chain into the body datum frame. Loaders must reject missing parents, transform cycles, ambiguous multiple-parent physical ownership, invalid/non-rigid transforms, NaN and infinity.

State-dependent transforms are resolved **before** geometry, mass centroid, inertia and actuator application-point calculations.

The same governed component transform feeds all physical consumers. A launch/radiator/engine position used by rendering may not differ from the transform used by mass or dynamics unless the alternate geometry is explicitly nonphysical visual reference.

---

## 6. Geometry, collision, contact and sweep authority

The contract supports deterministic low-detail reconstruction using a small portable primitive vocabulary such as:

```text
box
cylinder
capped_cylinder
sphere_or_ellipsoid
cone_or_frustum
convex_polyhedron where necessary
```

Each primitive exposes:

```text
primitive_id
component_id
primitive_type
dimensions
local_pose or inherited component pose
physical_role
configuration_rule
authority_status
provenance
```

`physical_role` may include one or more of:

```text
render
collision
contact
mass_approximation
sweep
```

Collision/contact authority is distinct from decorative/high-detail mesh authority. Render-only geometry cannot silently enter mass, collision or interference calculations. If a primitive derives mass/inertia, its mass/density relationship must be explicit.

Deployables may expose state-dependent sweep envelopes. For kinematic transitions, intermediate geometry must be resolvable.

---

## 7. Mass elements

Every active mass contribution is explicit:

```text
mass_element_id
component_id
mass_kind
reference_mass_kg
centroid_local_m[3]
local_inertia_tensor optional
inertia_reference_point
inertia_frame
primitive_mass_model optional
configuration_rule
mutable_store_id optional
authority_status
provenance
```

Representative kinds include fixed structure, equipment, payload, consumable, propellant/remass, attached vehicle, docked external mass, and explicit reserve/uncertainty allowance.

A centroid plus scalar mass is insufficient to derive finite-size inertia unless an explicit primitive/material approximation is selected.

Class dry/wet/reference masses may exist as regression invariants but do not replace element-level recomputation when element data exist.

---

## 8. Mutable stores, overlapping labels and fill models

A store exposes:

```text
store_id
component_id
substance_or_resource
capacity_kg
current_quantity_kg
minimum_protected_quantity_kg optional
centroid_model
inertia_model
feed_connections
usage_constraints
```

One physical inventory may serve multiple operational labels without double-counting. A protected reserve is a constraint on one store, not a second mass bucket.

`centroid_model` / `inertia_model` are executable typed semantics, initially supporting at least:

```text
FIXED_CENTROID_SCALED_MASS
PRIMITIVE_FILL_MODEL
TABULATED_QUANTITY_MODEL
VERSIONED_CUSTOM_MODEL
```

Quasi-static fill geometry is distinct from dynamic slosh. Slosh, if later admitted, is explicit internal dynamic state rather than a hidden centroid formula.

All stores enforce `0 <= quantity <= capacity`. An effector cannot consume below a protected minimum unless the scenario explicitly authorizes reserve use.

---

## 9. Total mass, CoM and inertia

For current active contributions expressed in body datum coordinates:

```text
M = Σ m_i
r_CoM = (Σ m_i r_i) / M
```

Current CoM is derived; an independently authored current CoM is never physical authority when derivation is possible.

Each local inertia contribution must identify its reference point and frame. Combination requires:

1. resolve component orientation into body frame;
2. rotate local tensor into body coordinates;
3. translate it to the current composite CoM using the parallel-axis theorem;
4. sum all active contributions.

The final `I_CoM_B` is symmetric within tolerance and positive-definite for a valid rigid body.

```text
I_CoM_B =
[Ixx Ixy Ixz
 Iyx Iyy Iyz
 Izx Izy Izz]
```

Configuration, store quantity and attachment changes trigger recomputation before the next ordinary force evaluation.

---

## 10. Ordinary force/moment effector contract

All ordinary propulsion/attitude systems cross one generic wrench interface.

An effector defines at least:

```text
effector_id
component_id
effector_type
application_point_local_m[3]
direction_local_unit[3]
max_force_N
min_force_N optional
intrinsic_moment_model optional
command_model
response_model
resource_store_id optional
mass_flow_model optional
gimbal_model optional
enabled_configuration_rule
authority_status
provenance
```

After transforms and gimbal state are resolved, each effector produces a force `F_B`, application point `r_app_B`, optional intrinsic couple `tau_intrinsic_B`, resource flow and actuator state.

The moment delivered to the rigid-body plant is explicitly:

```text
r_rel_B = r_app_B - r_CoM_B
tau_B = cross(r_rel_B, F_B) + tau_intrinsic_B
```

Torque arm is always relative to the **current CoM**, not silently the body datum origin.

The plant sums ordinary wrenches from RCS, docking thrusters, tugs, torch and other admitted ordinary effectors without needing effector-specific equations.

---

## 11. Actuator command and response semantics

Every commanded effector declares at least:

```text
command_domain
command_units
command_limits
response_type
response_parameters_or_version
latency_or_deadtime if nonzero
rise_fall_or_first_order_dynamics if modeled
minimum_impulse_bit_or_pulse_rule if modeled
failure_state
```

An ideal instantaneous actuator is explicitly representable. A command must never be ambiguous between throttle fraction, force, valve pulse, desired wrench or another quantity.

GN&C may request desired force/torque, but allocation to individual effectors is a separate auditable layer above the plant.

---

## 12. RCS and attitude control

RCS authority is physical nozzle/station authority, not abstract pitch/yaw/roll ratings.

The model supports individual stations, command groups, asymmetric failures, dead zones/interference, feed assignment, minimum impulse behavior where applicable, and resulting coupled translation/rotation.

No exact Wayfarer RCS layout may be invented merely because the simulator wants one; OPEN remains OPEN until governed engineering supplies it.

---

## 13. Resource/feed and cutoff semantics

A resource-consuming effector must resolve an admissible source store before producing thrust.

Feed isolation/failure may disable an effector. Resource exhaustion or protected-reserve boundary during a step produces a deterministic event/cutoff; quantity must not become negative and later be clamped as an afterthought.

For rocket/RCS/torch models, the effector thrust law owns the exhaust momentum exchange represented by thrust. The generic rigid-body plant must not add a second `v_rel * dm/dt` momentum term unless a separately governed efflux model explicitly requires one.

Store depletion is still integrated for evolving mass/CoM/inertia.

---

## 14. Deterministic integration/update ordering

A simulation evaluation must be semantically equivalent to:

```text
1. resolve configuration at evaluation time
2. resolve mutable-store state
3. compute mass / CoM / inertia
4. resolve command and actuator internal state
5. resolve force, intrinsic moment and resource flow
6. evaluate translational/rotational derivatives
7. integrate ordinary state, stores and actuator internal state consistently
8. recompute mass properties before the next derivative evaluation
9. enforce bounds and process transition/depletion events
```

For RK or other multistage methods, stage evaluations use stage-consistent store/mass/actuator state. Propellant may not be consumed only after a whole step while force stages use stale initial mass.

Integrator choice/timestep is qualification configuration, not class authority.

---

## 15. Event semantics

The executive supports deterministic event epochs for at least:

```text
store reaches protected or zero quantity
actuator enable/disable boundary
configuration transition completion
attachment/detachment
propulsion regime entry/exit
```

A solver must not step materially through a discontinuity and merely clamp afterward. Initial implementations may use step subdivision or root bracketing, but event tolerance and behavior are qualification-controlled and reproducible.

---

## 16. Torch

Torch remains ordinary momentum-exchange propulsion.

Class authority includes at least:

```text
torch_system_id
component_id
application_point_local_m[3]
nominal_axis_local_unit[3]
operating_modes
thrust_law
mass_flow_law
resource_store_id
gimbal_limits optional
thermal_configuration_constraints
mutual_exclusion_constraints
```

Runtime output includes commanded mode/throttle, force vector, application point, torque, remass flow, gimbal/control state and constraint status.

Torch cannot bypass ordinary momentum, mass-flow, CoM or inertia accounting.

---

## 17. Configuration state and transitions

Each configurable assembly defines:

```text
configuration_domain_id
allowed_states
allowed_transitions
transition_preconditions
transition_effects
transition_mode
transition_duration optional
transition_model_version optional
```

`transition_mode` is one of:

```text
ATOMIC
KINEMATIC
EXTERNAL_SEQUENCE
```

`ATOMIC` changes state at one event epoch. `KINEMATIC` resolves intermediate transform/geometry/mass properties over time. `EXTERNAL_SEQUENCE` delegates to an explicit command/state sequence while preserving the same physical outputs.

Transition effects may change geometry, sweep envelope, transforms, active mass, consumable access, actuator availability, thermal capability, docking compatibility, torch eligibility and metric eligibility. Illegal transitions fail closed.

---

## 18. Docking and attachment aggregation

A docking/attachment interface exposes:

```text
interface_id
component_id
interface_type
pose_B
capture_geometry
hard_dock_geometry
allowed_mates
load_limits optional
transfer_capabilities
state_machine
```

Representative states may include FREE, APPROACH, SOFT_CAPTURE and HARD_DOCKED.

The state machine declares when rigid-body aggregation begins; SOFT_CAPTURE does not automatically imply one rigid body.

A rigidly attached child body contributes recursively through the governed docking transform:

- mass;
- transformed CoM;
- inertia rotated into host body frame and translated by parallel-axis theorem;
- physical geometry/contact envelopes;
- effectors only when control/power/feed semantics explicitly permit them.

Attachment cycles are invalid. Detachment removes the child from the composite before post-separation propagation and creates a separately propagated body if required.

---

## 19. Environment separation

The ship contract does not absorb external orbital/environment object models.

External environment provides as required gravity/ephemeris/frame state, atmosphere, radiation/thermal conditions, docking-partner state and metric-certification environment. The ship provides geometry, mass properties, effectors, configuration and eligibility constraints.

This preserves the Phase-1 `DO_NOT_REIMPLEMENT` boundary.

---

## 20. Metric system and regime boundary

`metricpy` is a separate propagation regime, not an ordinary effector.

Class authority may contain hardware/configuration eligibility keys such as hardware membership, node/topology IDs, Mc lot applicability, bank/thermal capability, allowed metric modes, configuration prerequisites and certification applicability identifiers.

It shall not encode fictitious ordinary thrust.

Required seam:

```text
ordinary 6D
→ METRIC_ACQUISITION
→ metric internal state
→ NATURAL terminal ordinary 6D
→ residual/match qualification
→ ordinary dynamics resumes
```

Metric internal state is a separate typed contract where ordinary XYZ is not defined by the governed model. Ordinary entry/exit states must retain explicit frame semantics.

`loompy` remains RESERVED / NOT IMPLEMENTED and attempted execution fails closed.

---

## 21. Derived VehicleTrueState

The simulation executive emits a derived semantic product containing at least:

```text
VehicleTrueState
- epoch
- translational_reference_frame
- position
- velocity
- velocity_expression_frame
- attitude
- attitude_from_frame
- attitude_to_frame
- angular_velocity
- angular_velocity_expression_frame
- mass
- center_of_mass_B
- inertia_tensor_CoM_B
- configuration_state
- consumable_state
- actuator_propulsion_state
- propulsion_regime
- provenance
- qualification_quality
```

Minimum provenance identifies class physical-model version, instance-state version, solver/kernel version, environment/reference-data version, qualification status, and degraded/approximate inputs.

This is current derived truth, not class-authority storage.

---

## 22. Numerical and physical invariants

Any implementation enforces at least:

1. positive total mass;
2. finite numerical values; no unadmitted NaN/infinity;
3. `0 <= store quantity <= capacity`;
4. protected reserve enforced as constraint rather than duplicate mass;
5. no resource double counting;
6. CoM derived from active contributions;
7. inertia symmetric within tolerance and final rigid-body tensor positive-definite;
8. transform hierarchy acyclic and resolvable to body datum;
9. direction vectors/quaternions normalized within declared policy/tolerance;
10. wrench arm resolved relative to current CoM;
11. detached/absent components contribute no post-transition mass/inertia/physical geometry unless separately propagated;
12. physical render/interference geometry uses the same governed transforms as dynamics;
13. ordinary propulsion cannot execute across the metric boundary without explicit transition;
14. metric cannot masquerade as ordinary wrench;
15. Loom execution fails closed;
16. provenance/status cannot be silently promoted;
17. event processing prevents negative stores and post-hoc discontinuity clamping where state would materially differ.

---

## 23. Required deterministic resolver semantics for Phase 3+

A concrete implementation must be able to answer deterministically, names non-binding:

```text
resolve_active_components(instance_state)
resolve_component_transforms(instance_state)
resolve_geometry(instance_state)
resolve_collision_envelopes(instance_state)
resolve_sweep_envelopes(instance_state, transition_state)
resolve_mass_elements(instance_state)
resolve_mutable_store_mass_properties(instance_state)
compute_total_mass(instance_state)
compute_center_of_mass(instance_state)
compute_inertia_tensor(instance_state)
resolve_effectors(instance_state)
resolve_wrench(effector_state, current_mass_properties)
resolve_resource_flow(effector_state, instance_state)
validate_configuration_transition(from_state, to_state)
resolve_transition_state(epoch)
resolve_attachment_mass_properties(instance_state)
resolve_torch_capability(instance_state)
resolve_metric_eligibility(instance_state, certification_context)
```

Phase-3 SQL succeeds only if these semantics can be supported without embedding an external simulator object graph.

---

## 24. Mapping to governed Phase-5 known-answer suite

| Phase-5 case | Required contract semantics |
|---|---|
| zero-force inertial coast | frame/state convention, positive mass/inertia |
| single axial thruster | effector command, wrench, resource feed |
| offset thruster coupled translation/rotation | current-CoM moment arm + full inertia |
| symmetric pair near-pure rotation | multiple explicit effectors + wrench sum |
| commanded pitch | actuator command/response + allocation above plant |
| commanded yaw | actuator command/response + allocation above plant |
| commanded roll | actuator command/response + allocation above plant |
| combined 6DOF | full wrench accumulator + rotational/translational plant |
| propellant/remass depletion | store flow + event cutoff + stage-consistent mass |
| CoM migration | executable fill/centroid model + recomputation ordering |
| inertia migration | executable inertia model + tensor combination |
| detachable launch/configuration transition | transform hierarchy + transition mode + attachment aggregation + event semantics |

No Phase-5 case requires simulator-specific class fields.

---

## 25. Wayfarer compatibility constraints from live authority

The contract can represent the currently documented Wayfarer without promoting open design details:

- body datum X forward-to-aft, bow `x=0`, aft permanent structure `x=57 m`, +Z launch side, -Z docking side;
- ~57 m x 9 m reference body;
- four major tanks, four principal longerons, four major radiators and one axial torch/nozzle topology;
- 858.5 t dry reference, 1,158.5 t wet reference;
- 300 t total working-fluid/water inventory containing 250 t normal remass and 50 t protected reserve, not three additive buckets;
- ~88 t unified relational plant;
- 33 t working planetary-launch mass with design-baseline offset and explicit DOCKED/ABSENT physical effect;
- lower-authority component positions may coexist with higher-authority masses through explicit provenance;
- radiator STOWED/DEPLOYING/DEPLOYED and launch DOCKED/EXTRACTING/ABSENT can be represented without assuming final geometry;
- torch/metric mutual-exclusion constraints can be represented;
- exact RCS count/layout remains OPEN and is not fabricated by this contract.

Wayfarer remains a compatibility test, not the source of generic semantics.

---

## 26. Phase-2 closure criteria

Phase 2 may be marked PASSED only when:

1. hostile-review findings H1-H14 are represented in the contract;
2. every governed Phase-5 known-answer case maps to explicit contract semantics without simulator-specific fields;
3. Wayfarer live authority can be represented without destructive loss or silent promotion of OPEN/design-baseline values;
4. the contract still preserves external-environment and metric-regime separation;
5. no production database has been prematurely adopted.

If accepted, Phase 3 is authorized only as a **non-destructive Wayfarer-only prototype** of the generic physical contract.

Navigator/GIS/HUD physics-dependent implementation remains frozen until the full later exit gate passes.

No merge is authorized by this document.
