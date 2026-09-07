# LOOM 2226 — Generic Ship Physical Contract — Hostile Review

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — HOSTILE REVIEW — FEATURE BRANCH — NOT CANON  
**Branch:** `qualification/portable-ship-phase2-contract-2026-09-08`  
**Reviewed artifact:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_v0.1.md`  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`

---

## 1. Review question

Does v0.1 contain enough generic physical semantics to support the governed Phase-5 standalone known-answer suite, the existing Wayfarer mass/configuration authority, deterministic low-detail 3D reconstruction, later torch and metric-regime continuity work, without locking LOOM to a simulator API or silently inventing missing physics?

**Verdict:** **NO-GO AS WRITTEN / REPAIRABLE.**

The contract is structurally sound and preserves the correct authority boundaries, but several dynamics-critical semantics remain underspecified. Those omissions are cheap to repair now and expensive after SQL/schema commitment.

This is not a rejection of the architecture. It is a requirement to harden the contract before Phase 2 closes.

---

## 2. What survives hostile review

The following v0.1 decisions are retained:

- immutable body datum frame distinct from moving center of mass;
- class authority separated from instance state and derived true state;
- component transforms as shared physical/render authority;
- element-level mass accounting rather than one authored ship mass;
- overlapping operational labels must not double-count a physical store;
- full inertia tensor support;
- explicit physical RCS locations/directions rather than abstract pitch/yaw/roll ratings;
- control allocation separated from plant equations;
- torch treated as ordinary momentum-exchange propulsion;
- docking/attachment as explicit physical state;
- configuration as first-class physical state;
- `metricpy` as a separate propagation regime rather than an ordinary force effector;
- `loompy` fail-closed;
- external environment kept outside the vehicle class model;
- `VehicleTrueState` as a derived product;
- provenance/status cannot be silently promoted;
- external frameworks do not own LOOM SQL or state contracts.

These are compatible with the live Wayfarer authority and the Phase-1 simulator-role decision.

---

## 3. Critical finding H1 — wrench semantics are not yet mechanically closed

v0.1 provides force, application point and torque contribution, but does not make the torque resolution rule explicit.

For an effector force `F_B` applied at datum-frame point `r_app_B`, with current center of mass `r_CoM_B`, the ordinary rigid-body moment contribution must be resolved as:

```text
r_rel_B = r_app_B - r_CoM_B

tau_B = cross(r_rel_B, F_B) + tau_intrinsic_B
```

where `tau_intrinsic_B` permits a physically modeled pure couple or actuator-internal moment.

Required repair:

- distinguish force vector from intrinsic couple;
- define frame of each vector explicitly;
- torque arm is always relative to the **current** CoM, never silently relative to datum origin;
- gimballed effectors resolve direction before wrench construction;
- all ordinary effectors combine through the same wrench accumulator.

Why this matters: Phase-5 offset-thruster, pitch/yaw/roll and combined-6DOF tests cannot be unambiguously implemented without it.

---

## 4. Critical finding H2 — time integration and mass-property update ordering are underspecified

Phase 5 explicitly includes propellant/remass depletion, CoM migration and inertia migration. v0.1 says these values change, but not when they are recomputed relative to force evaluation and integration.

Required repair:

A deterministic simulation step must expose a governed update sequence equivalent to:

```text
1. resolve active configuration at step/substep time
2. resolve mutable-store quantities
3. compute current total mass / CoM / inertia
4. resolve actuator command and actuator state
5. resolve force, intrinsic moment and mass/resource flow
6. propagate ordinary translational/rotational state
7. integrate store depletion / actuator internal state consistently with the chosen integrator
8. recompute mass properties before the next force evaluation
9. validate bounds / transition events
```

For multistage integrators, stage evaluations must use stage-consistent mass/store state rather than freezing initial-step mass while consuming propellant in a separate afterthought.

Why this matters: a constant-force test can pass while a depletion test is physically wrong.

---

## 5. Critical finding H3 — variable-mass propulsion requires an explicit modeling boundary

The contract must prevent accidental double counting between:

- thrust already representing exhaust momentum flux; and
- generic variable-mass terms added independently by the rigid-body plant.

Required repair:

For rocket/torch/RCS effectors, the effector model owns the exhaust momentum exchange represented by its thrust law. The rigid-body plant consumes the resulting external wrench and current mass properties; it must not add a second `v_rel * dm/dt` term unless a separately governed efflux model explicitly requires it.

Store depletion remains independently integrated for mass-property evolution.

Any future moving-internal-mass/slosh/jet-damping model must enter as an explicit state/effect model rather than being smuggled into generic mass loss.

---

## 6. Critical finding H4 — component transform semantics need a compositional rule

v0.1 allows parent components but does not explicitly require deterministic transform composition through the hierarchy.

Required repair:

Every physical pose must resolve through a unique acyclic parent chain into the body datum frame. The loader must reject:

- transform cycles;
- missing parents;
- ambiguous multiple parents;
- invalid/non-rigid orientation transforms.

State-dependent transforms must be resolved before geometry, mass centroid, inertia and effector application-point calculations.

Why this matters: the same launch/radiator transform must move rendering, collision geometry, mass centroid and actuator geometry together.

---

## 7. Critical finding H5 — inertia contributions need explicit local reference semantics

v0.1 correctly requires full tensors, but Phase-3 storage could still become ambiguous unless each contributed tensor identifies:

```text
local_inertia_tensor
inertia_reference_point
inertia_frame
centroid
orientation_to_body
```

Required repair:

- define whether each tensor is about its own centroid or another declared point;
- rotate local tensor into body coordinates;
- translate to current composite CoM using the parallel-axis theorem;
- require symmetric positive-semidefinite individual contributions where physically appropriate;
- require positive-definite final rigid-body tensor.

A centroid plus mass alone is not enough to calculate finite-size inertia unless a primitive/material approximation is explicitly selected.

---

## 8. Critical finding H6 — mutable-store centroid/inertia behavior must be executable, not prose-only

The Wayfarer has four major working-fluid/remass tanks and Phase 5 explicitly requires CoM and inertia migration.

Required repair:

`centroid_model` and `inertia_model` need typed semantics, at minimum supporting:

- fixed centroid / fixed-shape scaled mass approximation;
- primitive fill model;
- tabulated quantity-to-centroid/inertia model;
- externally qualified/custom model identified by version.

The contract should not mandate fluid slosh physics now, but must distinguish **quasi-static fill geometry** from dynamic slosh.

Dynamic slosh, if ever admitted, belongs as explicit internal dynamic state and not as a hidden centroid formula.

---

## 9. Critical finding H7 — actuator command/state semantics are too abstract for deterministic tests

`command_model` and `response_model` exist but lack minimum contract semantics.

Required repair:

At minimum an actuator must state:

```text
command_domain
command_units
command_limits
response_type
response_parameters/version
latency/deadtime if nonzero
rise/fall or first-order dynamics if modeled
minimum impulse bit / pulse rule if modeled
failure_state
```

A simple ideal actuator remains valid and should be explicitly representable.

Why this matters: tests must know whether a command means instantaneous force, throttle fraction, valve pulse, desired wrench or another quantity.

---

## 10. Major finding H8 — feed/resource connectivity needs fail-closed semantics

The contract names feed connections but does not yet say what happens when a requested effector has no admissible feed path or would violate protected reserve.

Required repair:

- an effector must resolve an admissible source store before producing resource-consuming thrust;
- feed isolation/failure may disable effectors;
- protected reserve is a constraint, not a second mass bucket;
- resource exhaustion during a step produces a deterministic cutoff/event, not negative quantity;
- mass flow cannot consume below an admitted minimum unless the scenario explicitly authorizes reserve use.

---

## 11. Major finding H9 — configuration transitions need intermediate-state semantics

v0.1 supports transition duration but leaves unclear whether the vehicle jumps from old to new geometry/mass state or occupies a physical intermediate state.

Required repair:

Each transition must declare one of:

- `ATOMIC`: state changes at one event epoch;
- `KINEMATIC`: transform/configuration evolves continuously by a governed transition model;
- `EXTERNAL_SEQUENCE`: transition is represented by an explicit command/state sequence outside the class record.

For `KINEMATIC`, intermediate geometry, mass, CoM/inertia and sweep envelope must be physically resolvable.

This matters for launch extraction, radiator deployment and docking capture.

---

## 12. Major finding H10 — attachment aggregation needs recursive composite-body rules

v0.1 correctly says a hard-docked body enters mass/CoM/inertia. The algorithmic semantic should be explicit.

Required repair:

A dynamically rigid attachment shall contribute:

- attached-body mass;
- attached-body CoM transformed through docking pose;
- attached-body inertia rotated into host body frame and translated by parallel-axis theorem;
- attached geometry/contact envelopes where applicable;
- attached effectors only when control/power/resource semantics explicitly permit them.

The composite must reject recursive attachment cycles.

Soft capture need not automatically imply one rigid body; the state machine must declare when rigid-body aggregation begins.

---

## 13. Major finding H11 — geometry primitives need minimum physical parameter semantics

The primitive vocabulary is adequate, but Phase 3 must not invent incompatible meanings per consumer.

Required repair:

Each primitive must define:

```text
primitive_type
dimensions
local_pose/component transform
physical_role = render | collision | contact | mass-approximation | multiple
state/configuration rule
authority/provenance
```

If a primitive is used to derive inertia, its density/mass assignment relationship must be explicit. Render-only primitives remain forbidden from silently entering mass/collision calculations.

---

## 14. Major finding H12 — event semantics are required for depletion and detachment tests

Phase-5 known-answer cases include depletion and detachable-launch/configuration transitions. Determinism requires event behavior.

Required repair:

The simulation executive contract must support event epochs for at least:

- store reaches protected/zero quantity;
- actuator enable/disable boundary;
- configuration transition completion;
- attachment/detachment;
- propulsion regime entry/exit.

The solver must not step through a discontinuity and merely clamp afterward if doing so materially changes state. Event handling may initially be simple step subdivision/root-bracketing, but behavior and tolerance must be governed.

---

## 15. Major finding H13 — reference-frame labeling in `VehicleTrueState` needs stronger typing

One `reference_frame` string is not sufficient long term because position/velocity and attitude may reference different frame relationships.

Required repair:

Semantic state should distinguish at least:

```text
translational_reference_frame
attitude_from_frame
attitude_to_frame/body_frame
velocity_expression_frame
angular_velocity_expression_frame
```

A compact implementation may alias these where conventions coincide, but serialization must not depend on implicit assumptions.

This is especially important when ordinary state crosses the metric boundary and later when docking/local frames are used.

---

## 16. Major finding H14 — units and numerical validity need contract-level enforcement

The current examples imply SI but do not universally require it.

Required repair:

Internal physical contract values shall use SI unless a field explicitly declares another unit at an ingestion boundary. Canon/source units may be retained in provenance, but solver-facing normalized values are SI.

Reject NaN, infinity and physically invalid negative quantities unless a field explicitly permits signed values.

Direction vectors and quaternions shall be normalized within declared tolerance or fail/normalize deterministically according to loader policy.

---

## 17. Test-coverage attack against Phase-5 suite

| Governed Phase-5 case | v0.1 status | Hostile-review result |
|---|---|---|
| zero-force inertial coast | adequate | PASS conceptually |
| single axial thruster | mostly adequate | requires H1/H7 |
| offset thruster, coupled translation/rotation | incomplete | requires H1 |
| symmetric pair, near-pure rotation | incomplete | requires H1 + deterministic allocation/commands |
| commanded pitch | incomplete | requires H7 |
| commanded yaw | incomplete | requires H7 |
| commanded roll | incomplete | requires H7 |
| combined 6DOF | incomplete | requires H1/H7 |
| propellant/remass depletion | incomplete | requires H2/H3/H8/H12 |
| CoM migration | partially adequate | requires H2/H6 |
| inertia migration | partially adequate | requires H2/H5/H6 |
| detachable launch/configuration transition | incomplete | requires H4/H9/H10/H12 |

Therefore v0.1 should not be frozen as the Phase-2 contract yet.

---

## 18. Wayfarer compatibility attack

Live Wayfarer authority exposes several useful stress cases:

- the body datum is not the CoM;
- the 33 t docked planetary launch is laterally offset and materially changes CoM;
- launch `DOCKED/ABSENT` is physically meaningful;
- four tanks carry a shared working-fluid/remass inventory;
- 250 t normal remass is contained within 300 t total working-fluid/water mass;
- protected water is an operational reserve within that inventory, not additional mass;
- RCS layout remains open and therefore must not be fabricated merely to satisfy the simulator;
- radiator deployment geometry is configuration-dependent and remains partly open;
- metric and torch configurations have mutual-exclusion constraints;
- lower-authority design positions coexist with canon masses.

The generic contract can represent all of these, provided H1-H14 are repaired before schema implementation.

---

## 19. Required disposition

**Phase 2 remains OPEN.**

Required next action:

1. issue a hardened contract revision incorporating H1-H14;
2. explicitly map each Phase-5 known-answer case to contract fields/semantics;
3. rerun this hostile review against the hardened revision;
4. only then mark Phase 2 PASSED and permit Phase 3 Wayfarer-only SQLite prototyping.

No production SHIPCLASSES database is authorized by this review.

Navigator/GIS/HUD physics-dependent implementation remains frozen.

No merge is authorized.
