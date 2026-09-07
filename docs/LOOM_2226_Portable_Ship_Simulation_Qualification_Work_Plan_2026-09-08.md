# LOOM 2226 — Portable Ship Simulation Qualification Work Plan

Date: 2026-09-08  
Status: **GOVERNING SUPPLEMENTAL WORK PLAN — planning branch**  
Parent governance:
- `docs/LOOM_2226_Navigator_GIS_HUD_Next_Phase_Work_Plan_2026-09-06.md`
- `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`

## 0. Authority and documentary-source rule

This plan governs the portable spacecraft-simulation qualification effort that must precede further Navigator/HUD physics integration.

**GitHub is documentary authority.** Any LOOM document, schema, code artifact, status claim, canon reference, work plan, or implementation note used to justify work under this plan must be fetched from live GitHub authority before reliance. Chat history and model memory may identify candidates to inspect, but they are not authority. If GitHub and chat differ, GitHub wins.

External simulator documentation, standards and scientific references must be independently sourced and recorded with provenance before they are used as qualification authority.

## 1. Purpose

Build and qualify a portable LOOM ship-simulation architecture in which one generic spacecraft physical model can:

1. drive independent six-degree-of-freedom flight-dynamics tests outside Navigator;
2. run its mandatory qualification suite locally on the Pixel without an LLM and without a network connection after dependencies/test data are installed;
3. reproduce a minimal, dimensionally faithful 3D spacecraft from the same structured physical authority;
4. emit a stable canonical vehicle-state product suitable for Navigator, HUD, GIS, campaign persistence and later GN&C;
5. support ordinary RCS and torch dynamics using ordinary force/torque accounting;
6. support `metricpy` as an explicitly speculative, separately qualified metric-regime propagator with governed entry/exit state continuity;
7. defer `loompy` until the Relational Foundations / physics-research workstream produces a governed Loom transition model.

## 2. Hard Navigator / HUD physics freeze

Navigator/GIS/HUD presentation work may preserve already-qualified foundations, but no new spacecraft-physics assumptions, vehicle-state reconstruction, maneuverability model, metric propagation rule, or ship-geometry authority may be introduced into those surfaces while this gate is open.

Navigator resumes physics-dependent implementation only after the exit gate in Section 12 is satisfied.

No UX surface owns physical truth.

## 3. Non-negotiable qualification rule: testing occurs outside the LLM

The LLM may design code, review results, explain failures and propose changes. It may not be the pass/fail authority.

Mandatory acceptance tests must be executable from repository code and data by a deterministic command on the Pixel.

Target operator experience:

```text
python verify_all.py
```

The runner must emit machine-readable and human-readable results, including actual numerical traces, tolerances, provenance and explicit PASS/FAIL outcomes.

Once required dependencies and frozen reference data are installed, mandatory qualification must not require:

- ChatGPT or another LLM;
- network access;
- a remote API;
- a desktop simulator;
- manual interpretation of graphs to decide PASS/FAIL.

Desktop/CI tools may generate or independently verify frozen reference vectors, but the Pixel must be able to rerun the acceptance suite against those governed artifacts.

## 4. Simulator-role architecture to qualify

The current candidate architecture is intentionally provisional until Phase 1 closes.

```text
LOOM SIMULATION EXECUTIVE
|
+-- ordinary dynamics
|   +-- portable 6DOF kernel
|   +-- RCS / attitude effectors
|   +-- torch force/torque + mass-flow model
|   +-- gravity/environment modules as required
|
+-- metricpy
|   +-- acquisition boundary
|   +-- metric-regime state
|   +-- governed metric propagator
|   +-- natural terminal 6D state
|   +-- residual / match qualification
|
+-- loompy [RESERVED / NOT IMPLEMENTED]
|
+-- canonical state-continuity contracts
```

Candidate external roles to evaluate include:

- NASA SimuPy Flight / NESC 6DOF cases — portable reference/harness candidate;
- Basilisk — spacecraft dynamics/GN&C hostile reference candidate;
- NASA JEOD + Trick — high-fidelity NASA hostile reference candidate;
- Tudat/TudatPy — astrodynamics/propagation hostile reference candidate;
- JSBSim where useful for independent 6DOF/control comparison;
- game/simulation architecture lessons from Children of a Dead Earth, Kerbal Space Program, Juno: New Origins and Elite Dangerous.

No candidate is adopted merely because it is prestigious or mature. Pixel portability, reproducibility, licensing, numerical transparency and LOOM integration cost are explicit selection criteria.

## 5. Governing physical-authority split

The target authority chain is:

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

A separate generic ship-class SQLite database is the leading design candidate and must be prototyped before promotion. The filename `LOOM_2226_SHIPCLASSES.sqlite3` is provisional until schema design is governed.

Class authority describes what a spacecraft is physically. Campaign authority describes what a particular instance is doing now.

Derived current mass, center of mass and inertia should be recomputed from class definition plus mutable inventories/configuration wherever practical rather than independently authored.

## 6. Phase 1 — Simulator landscape decision and Pixel feasibility

### 6.1 Research and decision matrix

Perform a documented hostile comparison of candidate frameworks against at least:

- rigid-body 6DOF translation and rotation;
- dynamic mass, center of mass and full inertia tensor support;
- RCS/thruster force and torque application;
- actuator/control allocation and GN&C compatibility;
- orbital propagation and frame discipline;
- docking/rendezvous applicability;
- deterministic integration and test-vector reproducibility;
- extensibility for torch;
- clean separation for metric-regime propagation;
- Python/C++ dependencies;
- Android/Pixel/Pydroid viability;
- offline execution;
- runtime footprint;
- license and redistribution obligations;
- CI/headless execution;
- state-contract compatibility;
- maintainability for a zero-budget project.

Output must designate, with evidence:

- `PORTABLE_QUALIFICATION_KERNEL`
- `SPACECRAFT_HOSTILE_REFERENCE`
- `NASA_DEEP_REFERENCE`
- `ASTRODYNAMICS_REFERENCE`
- `LOOM_RUNTIME_STRATEGY`
- `GN&C_STRATEGY`
- `DO_NOT_REIMPLEMENT` boundaries.

### 6.2 Pixel proof

Before selecting a portable kernel, execute a real minimal 6DOF case on the Pixel.

Minimum proof:

1. required scientific-Python dependencies load locally;
2. the candidate reference/portable framework imports and runs, or a documented compatible portable subset is demonstrated;
3. free rigid-body/inertial propagation produces deterministic output;
4. a custom force/moment callback can be injected;
5. results can be written to local JSON/CSV;
6. the run can be repeated offline;
7. PASS/FAIL can be determined numerically by code.

If NASA SimuPy Flight cannot be made reliable on the Pixel without fragile native-build assumptions, it may remain a reference-vector generator while the portable LOOM runtime uses an independently implemented small kernel qualified against NASA/NESC and other external cases.

**Phase 1 gate:** do not design the generic ship schema around an unproven simulator API.

## 7. Phase 2 — Generic ship physical contract

Derive the minimum generic spacecraft model from simulator requirements rather than from Wayfarer-specific convenience.

The inclusion rule is:

> **Structured physical authority contains every physical quantity required to propagate the vehicle's true translational or rotational state, resolve contact/proximity geometry, or determine whether a propulsion/configuration transition is physically admissible.**

Minimum domains include:

- class/variant identity;
- explicit body datum frame and handedness;
- exterior dimensions and collision/bounding envelopes;
- physical components and body-frame transforms;
- mass elements and configuration dependencies;
- mutable consumable stores;
- total mass and center of mass derivation;
- full inertia tensor or equivalent principal-moment representation with orientation;
- force/torque-producing effectors with application point and direction;
- RCS layout and propellant source;
- torch application point, axis, thrust law, mass-flow law and control envelope;
- docking/attachment interfaces;
- simple render primitives/envelopes sufficient for deterministic low-detail 3D reconstruction;
- metric hardware/configuration state required by the qualified metric model;
- authority/status/provenance/version semantics.

Do not conflate the geometry datum frame with a dynamic center-of-mass frame.

## 8. Phase 3 — Prototype ship-class SQLite with Wayfarer only

Create a non-destructive prototype generic ship-class SQLite database containing only Wayfarer.

Do not migrate or delete the current Wayfarer geometry/engineering authority until compatibility has been demonstrated.

Candidate normalized domains include:

- `SHIP_CLASS`
- `SHIP_VARIANT`
- `BODY_FRAME`
- `PHYSICAL_COMPONENT`
- `COMPONENT_TRANSFORM`
- `GEOMETRY_PRIMITIVE`
- `COLLISION_ENVELOPE`
- `MASS_ELEMENT`
- `MASS_CONFIGURATION`
- `INERTIA_MODEL`
- `PROPELLANT_STORE`
- `FORCE_EFFECTOR`
- `ATTITUDE_ACTUATOR`
- `ATTACHMENT_INTERFACE`
- `DOCKING_INTERFACE`
- `TORCH_SYSTEM`
- `METRIC_SYSTEM`
- `AUTHORITY_PROVENANCE`

All existing Wayfarer documentary/numerical inputs used in this migration must be fetched from live GitHub before reliance.

## 9. Phase 4 — Wayfarer compatibility and 3D sniff qualification

The generic model must reproduce the existing qualified/candidate Wayfarer physical baseline without silently promoting lower-authority fields.

At minimum compare:

- 57 m overall length;
- principal body dimensions;
- dry and wet mass;
- launch present/absent mass states;
- center of mass results available from the current model;
- tanks and major component placement;
- docking and launch-side semantics;
- radiator/configuration geometry;
- propulsion and relational-plant regions;
- status/provenance classifications.

The same generic physical model must deterministically generate a crude but dimensionally faithful 3D Wayfarer.

Critical coupled test:

> Change one governed component transform/configuration in the prototype input and verify that both its rendered geometry and its physical mass-property contribution change consistently from the same source data.

No hand-authored renderer-only numerical geometry is allowed to pass this gate.

## 10. Phase 5 — Standalone flight-dynamics qualification harness

Build the flight-dynamics harness completely outside Navigator/HUD/GIS.

Input:

```text
ship-class physical model
+ mutable ship-instance state
+ initial 6D state
+ command/effector sequence
+ environment definition
```

Output must include, as applicable:

- epoch;
- position and velocity;
- attitude and angular velocity;
- mass;
- center of mass;
- inertia tensor;
- forces and torques;
- actuator state;
- consumable state;
- configuration state;
- propulsion regime;
- qualification provenance.

Initial known-answer tests:

1. zero-force inertial coast;
2. single axial thruster;
3. offset thruster producing coupled translation/rotation;
4. symmetric thruster pair producing near-pure rotation;
5. commanded pitch maneuver;
6. commanded yaw maneuver;
7. commanded roll maneuver;
8. combined 6DOF maneuver;
9. propellant/remass depletion;
10. center-of-mass migration;
11. inertia migration;
12. detachable launch/configuration transition.

Use analytic solutions where possible and independent external reference vectors where appropriate.

## 11. Phase 6 — Torch and `metricpy`

### 11.1 Torch

Torch remains ordinary force/torque propulsion for dynamics accounting.

The torch model must expose at minimum:

- commanded operating mode/throttle;
- force vector;
- application point;
- torque contribution;
- mass/remass flow;
- gimbal/control state where applicable;
- engineering constraints required by the governed Wayfarer torch model;
- deterministic telemetry/state products.

Torch must not bypass ordinary rigid-body momentum accounting.

### 11.2 `metricpy`

`metricpy` is a separate regime propagator, not a fictitious giant thruster.

Required seam:

```text
ordinary 6D state
    ↓
METRIC_ACQUISITION boundary
    ↓
metricpy relational / metric state propagation
    ↓
NATURAL terminal ordinary 6D state
    ↓
explicit residual / terminal-match qualification
    ↓
ordinary dynamics resumes
```

Metric transit must not invent ordinary XYZ occupancy where the governed model defines relational/non-ordinary transit.

Metric qualification does **not** claim empirical validation. It may qualify only the governed model's deterministic equations, path dependence, accounting, boundary semantics, residual handling, admissibility rules, regression vectors and state continuity.

Current qualified/guided metric engineering and state-continuity contracts remain controlling unless deliberately changed through governed physics work.

### 11.3 `loompy` reservation

`loompy` is explicitly out of scope for this work plan's implementation and qualification baseline.

Attempted Loom execution must fail closed as not implemented/not qualified.

`loompy` may enter implementation only after the Relational Foundations / physics-research workstream produces a governed Loom transition model with explicit:

- state variables;
- admissibility conditions;
- transition semantics;
- boundary state requirements;
- invariants/accounting rules;
- deterministic/testable outputs.

No placeholder implementation may silently establish Loom physics.

## 12. Navigator-resumption exit gate

Navigator/HUD physics-dependent work resumes only after all of the following are true:

1. a generic ship-class physical contract has been defined and versioned;
2. Wayfarer is instantiated through that generic contract without destructive loss of existing authority/provenance;
3. the mandatory standalone 6DOF suite runs on the Pixel outside the LLM and passes defined tolerances;
4. ordinary LOOM runtime results are checked against independent analytic, NASA/NESC and/or frozen hostile-reference vectors as appropriate;
5. torch propagation passes standalone force/torque/mass-flow qualification;
6. `metricpy` passes deterministic regime-boundary/state-continuity qualification without claiming empirical validation;
7. a minimal 3D Wayfarer is reconstructed deterministically from the same structured physical authority;
8. configuration/mass changes affect both dynamics and 3D representation consistently;
9. a stable canonical `VehicleTrueState` contract is available for downstream clients;
10. the accepted campaign authority chain remains unbroken;
11. `loompy` remains fail-closed unless separately admitted by governed physics research.

Formal gate statement:

> **Navigator resumes only after one generic ship-class schema, instantiated by Wayfarer, passes independent portable 6DOF flight-dynamics qualification, torch and metric-regime continuity qualification, deterministic minimal-3D reconstruction, and exposes a stable canonical vehicle-state contract suitable for Navigator/HUD consumption.**

## 13. Canonical vehicle-state target

The exact schema will be designed under this work plan, but the target semantic product is:

```text
VehicleTrueState
- epoch
- reference frame
- position
- velocity
- attitude
- angular velocity
- mass
- center of mass
- inertia tensor
- configuration state
- consumable state
- actuator/propulsion state
- propulsion regime
- provenance
- qualification/quality
```

Metric-internal state must be represented by a separate typed contract and not overloaded into ordinary `position`/`velocity` fields when those quantities are not physically defined by the governed model.

## 14. Qualification evidence and repository layout target

Preferred conceptual layout:

```text
qualification/
  scenarios/
    rigid_body/
    rcs/
    torch/
    metric/
  reference/
    analytic/
    nasa_nesc/
    basilisk/
    jeod/
    tudat/
  output/
  verify_all.py
```

Exact paths may change to follow repository conventions.

Every frozen external reference vector must record, where available:

- generating source/tool;
- exact version/commit;
- scenario and initial conditions;
- units and frame conventions;
- integrator/timestep/settings;
- generation date;
- license/provenance;
- expected tolerances;
- hash of the reference artifact.

## 15. Testing discipline

- Run unit regression before delivering any new Python artifact.
- For substantive functional changes, run both unit regression and functional qualification.
- Run full end-to-end regression before promotion into production/runtime authority.
- Maintain deterministic test seeds where stochastic sensor/error models are later introduced.
- Cross-platform parity means semantic/numerical parity, not identical rendering.
- Pixel qualification is mandatory for the portable acceptance path.
- Desktop/CI hostile-reference generation is supplemental, not a substitute for Pixel acceptance.

## 16. Immediate execution order

1. Phase 1 research matrix and license/dependency review.
2. Phase 1 Pixel dependency/import proof.
3. Minimal free-body 6DOF Pixel run.
4. Custom force/moment Pixel run.
5. Freeze simulator-role decision with evidence.
6. Fetch and map current Wayfarer Git authority.
7. Define generic ship physical contract.
8. Prototype ship-class SQLite with Wayfarer only.
9. Compatibility + minimal-3D qualification.
10. Standalone RCS/6DOF qualification harness.
11. Torch integration and qualification.
12. `metricpy` implementation/qualification against governed metric contracts.
13. Freeze canonical vehicle-state contract.
14. Reassess Navigator-resumption gate.

## 17. Non-negotiable rules

1. **Testing authority is executable code/data, not an LLM assertion.**
2. **Mandatory qualification must run on the Pixel offline after setup.**
3. **Do not design around an external simulator that cannot support the portable acceptance path.**
4. **Do not silently invent Wayfarer physical values.**
5. **Do not store arbitrary game-stat `maneuverability` as physical authority; derive behavior from mass properties and effectors.**
6. **One numeric physical source feeds dynamics and minimal geometry wherever the quantity is shared.**
7. **Torch participates in ordinary force/torque/mass accounting.**
8. **Metric remains explicitly speculative and separately qualified.**
9. **No invented ordinary-space occupancy during metric transit.**
10. **`loompy` is not implemented until governed physics research earns it.**
11. **Navigator/HUD/GIS consume canonical state; they do not reconstruct physical truth.**
12. **GitHub documentary authority outranks chat and memory.**
13. **Do not break the damn game.**
