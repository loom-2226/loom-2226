# LOOM 2226 — Generic Ship Physical Contract v0.1

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 2 CONTRACT — FEATURE BRANCH — NOT CANON  
**Branch:** `qualification/portable-ship-phase2-contract-2026-09-08`  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Prerequisite:** Phase 1 Pixel feasibility PASS recorded in `docs/LOOM_2226_Portable_Ship_Simulation_Phase1_Decision_2026-09-08.md`

---

## 1. Purpose

This contract defines the minimum generic physical authority required for any LOOM spacecraft class to participate in deterministic standalone flight-dynamics qualification, configuration/mass-property recomputation, docking/attachment geometry, low-detail deterministic 3D reconstruction, torch dynamics, and later `metricpy` regime-boundary qualification.

It is deliberately **not** a Wayfarer convenience schema and **not** a simulator API mirror.

The inclusion rule is the governing Phase 2 rule:

> **Structured physical authority contains every physical quantity required to propagate the vehicle's true translational or rotational state, resolve contact/proximity geometry, or determine whether a propulsion/configuration transition is physically admissible.**

This document defines semantics and invariants only. It does **not** authorize a production `LOOM_2226_SHIPCLASSES.sqlite3` database. Phase 3 will prototype a non-destructive Wayfarer-only SQLite implementation after this contract is accepted.

---

## 2. Authority chain

The physical-authority chain is:

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

Rules:

1. Class authority says what a spacecraft **is physically**.
2. Instance state says which mutable stores, attachments, configuration states and failures apply to one vehicle now.
3. Simulation derives current mass, center of mass, inertia, position, velocity, attitude and angular velocity.
4. Sensors/estimation may disagree with true state; they do not overwrite it.
5. Navigator/HUD/GIS render or consume authoritative outputs and own no spacecraft physics.
6. No external simulator owns LOOM ship SQL, campaign state, or contract semantics.

---

## 3. Coordinate and frame discipline

Every ship class shall define one explicit, immutable **body datum frame**.

Minimum body-frame definition:

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

The datum frame is geometric/configuration authority. It is **not** the instantaneous center-of-mass frame.

All component transforms, mass centroids, actuator locations, docking interfaces, render primitives and collision envelopes shall be expressed directly or transformably into this datum frame.

Dynamic center of mass shall be derived from current mass configuration and may migrate relative to the datum.

Attitude shall use an explicit convention. The Phase 1 kernel convention is acceptable as the initial ordinary-dynamics convention:

```text
q_BN = [w, x, y, z]
body → inertial rotation
omega_BN_B = body angular velocity relative to inertial, expressed in body coordinates
```

Any future contract serialization shall identify the frame/convention rather than relying on consumer assumptions.

---

## 4. Required class identity and version semantics

Each generic class/variant shall expose at minimum:

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

A physical-model version change is required whenever a change can alter propagated state, mass properties, collision/contact geometry, actuator forces/torques, configuration admissibility, or regime-boundary behavior.

Cosmetic-only presentation changes shall not create a new physical-model version.

---

## 5. Provenance and epistemic status

Every physical datum that is not purely derived shall carry source/provenance semantics.

Initial LOOM-compatible provenance/status vocabulary:

- `CANON`
- `DESIGN_BASELINE`
- `DERIVED`
- `LEGACY_COMPATIBLE`
- `VISUAL_REFERENCE`
- `OPEN`
- compound states such as `CANON_MASS_DESIGN_POSITION` where authority differs across dimensions of one modeled element

A physical solver may use lower-authority values for qualification only when the scenario explicitly admits them and reports their status. A renderer may display OPEN or VISUAL_REFERENCE geometry, but that geometry may not silently become collision, mass, inertia or actuator authority.

Derived quantities shall record the model/version and authoritative inputs from which they were computed.

---

## 6. Physical component contract

A spacecraft is decomposed into physical components. A component may contribute geometry, mass, actuation, attachment capability, consumables, thermal state or regime eligibility.

Minimum component semantics:

```text
component_id
parent_component_id optional
component_type
name
body_transform
configuration_membership
authority_status
provenance
```

`body_transform` shall include at least translation and orientation relative to the parent/body datum.

Configuration membership shall allow a component to be present, absent, deployed, rotated, detached, docked, consumed, failed or otherwise transformed without rewriting the class definition.

One source transform shall feed both geometry and physical calculations wherever the component contributes to both. Duplicate renderer-only placement values are prohibited for physically meaningful components.

---

## 7. Geometry authority

The generic contract must support deterministic low-detail physical reconstruction without prescribing a final visual mesh format.

Required geometry domains:

```text
GEOMETRY_PRIMITIVE
COLLISION_ENVELOPE
SWEEP_ENVELOPE optional
CONTACT_SURFACE optional
```

Initial primitive support should be deliberately small and portable, for example:

- box
- cylinder
- capped cylinder
- sphere/ellipsoid
- cone/frustum
- convex polyhedron where necessary

Each primitive shall reference a governed component transform.

Collision/contact authority shall be separate from decorative/high-detail render geometry. A high-detail Blender mesh may be downstream but cannot silently redefine contact geometry.

Deployable hardware shall be able to expose state-dependent sweep envelopes for interference checks.

---

## 8. Mass-element contract

Mass is not a single authored ship-level number once the vehicle is configurable.

Each mass element shall expose at minimum:

```text
mass_element_id
component_id
mass_kind
reference_mass_kg
centroid_B_m[3]
configuration_rule
mutable_store_id optional
authority_status
provenance
```

Representative `mass_kind` values:

- fixed_structure
- equipment
- payload
- consumable
- propellant/remass
- attached_vehicle
- docked_external_mass
- reserve/uncertainty allowance where explicitly admitted

Ship total mass shall be recomputed from active/present elements plus current mutable stores.

A class-level dry/wet/reference mass may exist as a validation invariant, but it shall not replace element-level recomputation when element data are available.

---

## 9. Mutable stores and consumables

Consumable stores shall support at minimum:

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

The contract must allow one physical inventory to serve multiple operational labels without double-counting mass. For example, a working-fluid inventory may contain both protected reserve and remass-capable quantity.

Consumption shall change total mass and, where geometrically relevant, center of mass and inertia.

Store geometry/centroid behavior may initially use qualified approximations, but the approximation and its applicability shall be explicit.

---

## 10. Center-of-mass derivation

For active mass elements `i`, expressed in the body datum frame:

```text
M = Σ m_i
r_CoM = (Σ m_i r_i) / M
```

No independent authored `current_center_of_mass` value is authoritative if it can be derived from the current component/store configuration.

A reference CoM may be retained as a regression target.

Configuration transitions that add/remove/reposition mass shall trigger recomputation before ordinary dynamics resumes.

---

## 11. Inertia contract

The generic model shall support the **full inertia tensor about the current center of mass**, expressed in a declared frame.

Each physical contribution shall be representable by either:

1. a full local inertia tensor plus centroid and orientation; or
2. sufficient primitive/material assumptions to derive that tensor.

Combination shall use rigid-body tensor rotation and the parallel-axis theorem.

The derived current product shall expose:

```text
I_CoM_B =
[Ixx Ixy Ixz
 Iyx Iyy Iyz
 Izx Izy Izz]
```

Principal moments alone are insufficient unless their principal-axis orientation is also supplied.

The contract shall permit temporary design-baseline approximations, but approximate inertia may not be presented as canon merely because a simulator requires a number.

---

## 12. Force/moment effector contract

All ordinary propulsion and attitude systems shall cross one generic force/moment interface.

Minimum effector semantics:

```text
effector_id
component_id
effector_type
application_point_B_m[3]
direction_B_unit[3]
max_force_N
min_force_N optional
command_model
response_model
resource_store_id optional
mass_flow_model optional
gimbal_model optional
enabled_configuration_rule
authority_status
provenance
```

At runtime, each effector resolves to a body/inertial wrench according to the active state convention:

```text
force
application point
torque contribution
mass/resource flow
actuator state
```

The ordinary rigid-body plant consumes wrenches. It must not need to know whether a wrench came from RCS, a docking thruster, a tug, or the torch.

---

## 13. RCS / attitude-actuator requirements

RCS shall be modeled as physical effectors with explicit location and direction rather than abstract pitch/yaw/roll authority numbers.

The contract must support:

- individual thruster stations;
- grouped commands;
- asymmetric failures;
- dead-zone/interference rules;
- propellant/feed assignment;
- control allocation above the plant;
- resulting coupled translation and rotation.

A future GN&C layer may request desired force/torque. Allocation to available effectors is a separate auditable function and shall not be embedded invisibly in the rigid-body equations.

---

## 14. Torch contract

Torch is ordinary momentum-exchange propulsion.

Minimum torch semantics:

```text
torch_system_id
component_id
application_point_B_m[3]
nominal_axis_B_unit[3]
operating_modes
thrust_law
mass_flow_law
resource_store_id
gimbal_limits optional
thermal/configuration constraints
mutual-exclusion constraints
```

Runtime output shall expose at minimum:

```text
commanded mode/throttle
force vector
application point
torque contribution
mass/remass flow
gimbal/control state
constraint status
```

Torch shall never bypass ordinary momentum, mass-flow, center-of-mass or inertia accounting.

---

## 15. Docking and attachment contract

Docking/attachment interfaces shall be explicit physical objects.

Minimum semantics:

```text
interface_id
component_id
interface_type
pose_B
capture_geometry
hard_dock_geometry
allowed_mates
load/path limits optional
transfer_capabilities
state_machine
```

Representative states may include:

- FREE
- APPROACH
- SOFT_CAPTURE
- HARD_DOCKED

Attached vehicles/components that become dynamically part of the spacecraft shall enter the active mass, CoM and inertia solution through a governed transform.

Detachment shall remove them before post-separation propagation.

An attachment/configuration transition may invalidate a committed propulsion/metric solution and require recertification.

---

## 16. Configuration-state contract

Configuration is first-class physical state, not UI state.

Each configurable assembly shall have:

```text
configuration_domain_id
allowed_states
allowed_transitions
transition_preconditions
transition_effects
transition_duration optional
```

Transition effects may change:

- active geometry
- collision/sweep envelope
- component transform
- active mass elements
- consumable access
- actuator availability
- thermal capability
- docking compatibility
- torch eligibility
- metric eligibility/certification

Illegal transitions shall fail closed.

---

## 17. Metric-system class authority

`metricpy` is a separate propagation regime, not an ordinary force effector.

The class contract may contain hardware/configuration authority needed to determine metric eligibility, for example:

```text
metric_system_id
hardware membership
node/topology identifiers
Mc inventory/lot applicability
bank/thermal capability
allowed metric operating modes
configuration prerequisites
certification applicability keys
```

It shall **not** encode fictitious ordinary thrust for metric transit.

Required regime seam remains:

```text
ordinary 6D
→ METRIC_ACQUISITION
→ metric internal state
→ NATURAL terminal ordinary 6D
→ residual/match qualification
→ ordinary dynamics resumes
```

Metric-internal state shall use a separate typed contract when ordinary XYZ position/velocity are not physically defined by the governed model.

`loompy` remains RESERVED / NOT IMPLEMENTED. Any attempted Loom execution shall fail closed.

---

## 18. Environment and external-body separation

The ship physical contract shall not absorb orbital/environment models that belong outside the vehicle.

External environment supplies, as required:

- gravity/ephemeris/frame state
- atmosphere where applicable
- radiation/thermal environment
- contact/docking partner state
- metric certification environment

The vehicle supplies its own geometry, mass properties, effectors, configuration and eligibility constraints.

This preserves the Phase 1 `DO_NOT_REIMPLEMENT` boundary and avoids embedding Tudat/JEOD/Basilisk/SPICE object models into LOOM class authority.

---

## 19. Derived `VehicleTrueState`

The simulation executive shall be able to emit the following canonical semantic product:

```text
VehicleTrueState
- epoch
- reference_frame
- position
- velocity
- attitude
- angular_velocity
- mass
- center_of_mass
- inertia_tensor
- configuration_state
- consumable_state
- actuator_propulsion_state
- propulsion_regime
- provenance
- qualification_quality
```

This is a derived current-state product. It is not class-authority storage.

Minimum provenance/quality shall identify:

- class physical-model version
- instance-state version
- solver/kernel version
- environment/reference-data version
- qualification status
- degraded/approximate inputs where present

---

## 20. Required physical invariants

Any implementation of this contract shall enforce at least:

1. total mass is positive;
2. all active stores satisfy `0 ≤ quantity ≤ capacity`;
3. no resource is double-counted across overlapping operational categories;
4. center of mass is derived from active mass contributions;
5. inertia is symmetric within numerical tolerance and positive-definite for a valid rigid body;
6. all physically relevant transforms resolve into the declared body datum frame;
7. actuator directions are normalized or normalized deterministically by the loader;
8. force/torque application points and configuration state are explicit;
9. removed/detached components contribute neither geometry nor mass/inertia after transition completion unless modeled as a separate body;
10. renderer geometry used for physical interference derives from the same governed transform/configuration data as dynamics;
11. ordinary propulsion cannot execute through the metric regime boundary without an explicit regime transition;
12. metric execution cannot masquerade as an ordinary wrench;
13. Loom execution fails closed;
14. provenance/status is never silently promoted by a consumer.

---

## 21. Validation contract for Phase 3+

A concrete ship-class implementation must be able to answer deterministically:

```text
resolve_active_components(instance_state)
resolve_geometry(instance_state)
resolve_collision_envelopes(instance_state)
resolve_mass_elements(instance_state)
compute_total_mass(instance_state)
compute_center_of_mass(instance_state)
compute_inertia_tensor(instance_state)
resolve_effectors(instance_state)
validate_configuration_transition(from_state, to_state)
resolve_attachment_mass_properties(instance_state)
resolve_torch_capability(instance_state)
resolve_metric_eligibility(instance_state, certification_context)
```

Names are semantic, not mandatory Python API names.

Phase 3 SQLite is successful only if it can support these operations without embedding simulator-specific object layouts into the schema.

---

## 22. Wayfarer compatibility constraints already identified from live authority

Wayfarer is **not** the source of this generic contract, but the contract must be capable of representing its existing authority without destructive loss.

Live GitHub sources establish, among other things:

- immutable geometric datum convention currently used by Wayfarer: X forward→aft, bow x=0 m, aft permanent structure x=57 m, +Z launch side, -Z docking side;
- approximately 57 m × 9 m reference body;
- four major tanks, four principal longerons, four major deployable radiator assemblies, one axial torch/nozzle;
- explicit launch `DOCKED / ABSENT` state affecting mass distribution;
- current 858.5 t dry / 1,158.5 t wet reference values;
- 300 t working-fluid/water inventory containing the normal 250 t remass allocation rather than adding to it;
- current design-ledger CoM values and a nonzero lateral launch contribution;
- explicit launch/radiator/docking/torch configuration vocabularies;
- geometry pipeline in which SQL parameters feed a deterministic compiler and downstream viewer/Blender products;
- provenance states including CANON, DESIGN_BASELINE, DERIVED, OPEN and mixed-authority values;
- current Wayfarer geometry seed already separates parameter authority from a mass-element ledger.

These are compatibility inputs for later Phase 3 mapping, not generic-schema shortcuts.

---

## 23. Explicitly unresolved for this contract

Phase 2 does not choose:

- final SQLite table names;
- row-vs-JSON storage strategy for tensors/transforms;
- a final unit library;
- a final serialization schema for `VehicleTrueState`;
- exact RCS station count for Wayfarer;
- exact Wayfarer inertia tensor;
- final tank-shell/slosh model;
- final radiator deployment topology;
- final collision solver;
- final docking contact dynamics;
- high-order flexible-body dynamics;
- full thermal simulation;
- metric constitutive calibration beyond existing governed interfaces;
- any Loom propagation implementation.

These must remain explicit rather than being accidentally fixed by Phase 3 database convenience.

---

## 24. Phase 2 gate

Phase 2 passes when this generic semantic contract is reviewed against:

1. the Phase 1 portable-kernel/runtime strategy;
2. the governing qualification work plan;
3. existing Wayfarer canon/engineering authority for non-destructive representability;
4. the required standalone known-answer tests planned for Phase 5;
5. the same-authority 3D rule;
6. torch ordinary-wrench accounting;
7. metric regime separation;
8. fail-closed Loom reservation.

Only after Phase 2 is accepted should Phase 3 create a **Wayfarer-only, non-destructive prototype** ship-class SQLite implementation.

Navigator/GIS/HUD physics-dependent work remains frozen.

No merge is authorized by this document.
