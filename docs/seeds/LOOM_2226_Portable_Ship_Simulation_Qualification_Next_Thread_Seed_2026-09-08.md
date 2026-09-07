# LOOM 2226 — Portable Ship Simulation Qualification — Next Thread Seed

Date: 2026-09-08

## PURPOSE

Continue the portable spacecraft-simulation qualification effort as its own engineering thread.

This is primarily an ENGINEERING / QUALIFICATION thread.

Default classification:

- CLASS: ENGINEERING / QUALIFICATION
- GOVERNED BY LIVE GITHUB
- NOT CANON UNLESS EXPLICITLY PROMOTED
- NAVIGATOR PHYSICS WORK FROZEN UNTIL EXIT GATE

## HARD AUTHORITY RULE

GitHub outranks chat.

Before relying on any LOOM document, schema, code artifact, status claim, canon reference, work plan, refinement, or implementation note, fetch it from live GitHub authority. Chat history/model memory may identify what to look for, but is not documentary authority.

Repository: `loom-2226/loom-2226`

Planning branch:
`planning/navigator-gis-hud-next-phase-2026-09-06`

Primary governing plan for this thread:
`docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`

Parent governance:
`docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`
`docs/LOOM_2226_Navigator_GIS_HUD_Next_Phase_Work_Plan_2026-09-06.md`

Do not make direct changes to `main`.
Use governed feature branches and PRs.
Do not merge without explicit user authorization.

## CORE USER DECISION

All mandatory qualification testing must occur OUTSIDE the LLM.

The acceptance suite must be runnable locally on the user's Pixel, without an LLM and without network access after dependencies/reference data are installed.

Target operator experience:

```text
python verify_all.py
```

The code, not ChatGPT, determines PASS/FAIL.

## NAVIGATOR FREEZE

Navigator/GIS/HUD physics-dependent implementation is hard-frozen until the common ship simulation baseline is qualified.

Preserve existing accepted Navigator/GIS/HUD foundations, but do not introduce new spacecraft-physics assumptions, maneuverability shortcuts, vehicle-state reconstruction, metric propagation rules, or renderer-owned physical authority.

Formal resumption target:

> Navigator resumes only after one generic ship-class schema, instantiated by Wayfarer, passes independent portable 6DOF flight-dynamics qualification, torch and metric-regime continuity qualification, deterministic minimal-3D reconstruction, and exposes a stable canonical vehicle-state contract suitable for Navigator/HUD consumption.

## TARGET ARCHITECTURE

```text
CANON / approved design constraints
        ↓
GENERIC SHIP-CLASS PHYSICAL AUTHORITY
        ↓
CAMPAIGN SHIP INSTANCE STATE
        ↓
LOOM SIMULATION EXECUTIVE
        ↓
TRUE VEHICLE STATE
        ↓
SENSORS / ESTIMATION / GN&C
        ↓
NAVIGATOR / HUD / GIS / TELEMETRY
```

The simulation executive target is:

```text
LOOM SIMULATION EXECUTIVE
|
+-- ordinary dynamics
|   +-- portable 6DOF kernel
|   +-- RCS / attitude effectors
|   +-- torch force/torque + mass flow
|   +-- environment/gravity modules
|
+-- metricpy
|   +-- acquisition boundary
|   +-- metric-regime state
|   +-- governed propagation
|   +-- natural terminal 6D state
|   +-- residual/match qualification
|
+-- loompy [RESERVED / NOT IMPLEMENTED]
|
+-- state-continuity contracts
```

## CURRENT SIMULATOR RESEARCH POSITION

Do not treat this as final until Phase 1 evidence is completed.

Candidates to evaluate:

- NASA SimuPy Flight / NESC 6DOF cases — leading Pixel-portable reference/harness candidate;
- Basilisk — leading spacecraft/GN&C hostile-reference candidate;
- NASA JEOD + Trick — deep NASA hostile reference;
- Tudat/TudatPy — astrodynamics/propagation hostile reference;
- JSBSim — optional independent 6DOF/control comparator;
- game architecture lessons from Children of a Dead Earth, Kerbal Space Program, Juno: New Origins and Elite Dangerous.

The project should not reimplement mature external functionality merely for pride. Use external/open-source/reference engines where they improve evidence, but keep mandatory Pixel acceptance portable and deterministic.

## PHASE 1 — IMMEDIATE WORK

1. Fetch live governing work plan from GitHub.
2. Research candidate simulator frameworks deeply enough to establish actual architecture, dependencies, licensing, Android/Pydroid viability, reference-test availability and extension seams.
3. Produce a scored decision matrix covering at least:
   - 6DOF translation/rotation;
   - dynamic mass/CoM/inertia;
   - RCS/thruster force and torque;
   - GN&C/actuator support;
   - orbital/frame support;
   - deterministic testing;
   - torch extension;
   - metric separation;
   - Pixel/Pydroid portability;
   - offline execution;
   - licensing/redistribution;
   - runtime footprint;
   - CI/headless use;
   - maintainability for a zero-budget project.
4. Designate with evidence:
   - `PORTABLE_QUALIFICATION_KERNEL`
   - `SPACECRAFT_HOSTILE_REFERENCE`
   - `NASA_DEEP_REFERENCE`
   - `ASTRODYNAMICS_REFERENCE`
   - `LOOM_RUNTIME_STRATEGY`
   - `GN&C_STRATEGY`
   - `DO_NOT_REIMPLEMENT` boundaries.
5. Build a tiny Pixel proof before designing ship SQL around any external simulator API.
6. Pixel proof must show:
   - scientific-Python dependencies import;
   - candidate kernel/reference subset executes;
   - free rigid-body/inertial case produces deterministic output;
   - custom force/moment injection works;
   - JSON/CSV trace output works;
   - rerun works offline;
   - numerical PASS/FAIL is code-determined.
7. If SimuPy Flight itself proves fragile on Android, retain its/NESC outputs as frozen reference vectors and use a smaller LOOM-owned portable kernel qualified against them.

## GENERIC SHIP SQL DIRECTION

A separate generic ship-class SQLite database is the leading candidate.
Provisional name:
`LOOM_2226_SHIPCLASSES.sqlite3`

Do not treat the filename or schema as final until governed.

Wayfarer is the first/reference implementation, not the schema definition.

Class authority answers:
“What is a Wayfarer-class ship physically?”

Campaign ship state answers:
“What is this particular ship doing now?”

The generic physical model must ultimately include every physical quantity needed to propagate translational/rotational state, resolve contact/proximity geometry, or determine propulsion/configuration admissibility.

Important domains:
- body datum frame;
- physical components and transforms;
- simple geometry/collision envelopes;
- mass elements;
- mutable inventories;
- CoM;
- full inertia tensor;
- RCS/effectors with application points/directions/thrust;
- torch force/torque/mass-flow model;
- docking/attachment interfaces;
- configuration states;
- metric hardware/state inputs;
- authority/provenance/status.

Do not conflate geometry datum frame with dynamic CoM frame.

## SAME-AUTHORITY 3D RULE

The same structured numeric physical authority should feed both dynamics and minimal 3D reconstruction.

Critical qualification:

> Move/change one component/configuration in physical authority and verify both rendered geometry and mass-property/dynamics consequences change consistently from the same source.

No renderer-only duplicate numeric geometry.

## TORCH

Torch remains ordinary force/torque propulsion for dynamics accounting.
It must not bypass Newtonian rigid-body accounting.

Required model concepts include:
- force vector;
- application point;
- torque;
- mass/remass flow;
- control/gimbal state where applicable;
- governed engineering limits;
- deterministic telemetry.

## METRICPY

`metricpy` is INCLUDED in this qualification program.

It is a separate metric-regime propagator, not a fictitious giant ordinary thruster.

Required seam:

```text
ordinary 6D state
→ METRIC_ACQUISITION
→ metricpy
→ NATURAL terminal ordinary 6D state
→ explicit residual / match qualification
→ ordinary dynamics resumes
```

Do not invent ordinary XYZ occupancy during relational metric transit.

Metric qualification means deterministic conformity to the governed LOOM metric model, path dependence, accounting, transition semantics, admissibility, residual handling and regression vectors. It does NOT mean empirical validation of speculative physics.

## LOOMPY

`loompy` is OUT OF SCOPE FOR IMPLEMENTATION.

It is reserved until the Relational Foundations / physics-research workstream produces a governed Loom transition model with explicit state variables, admissibility, boundary semantics, invariants/accounting and testable outputs.

Attempted Loom execution must fail closed as NOT IMPLEMENTED / NOT QUALIFIED.

No placeholder `loompy` may silently establish physics.

## QUALIFICATION PHILOSOPHY

Use three levels where practical:

1. analytic invariants/known solutions;
2. published/frozen external reference vectors, including NASA/NESC where appropriate;
3. hostile cross-engine comparison using Basilisk/JEOD/Tudat or other qualified references on supported machines/CI.

Pixel does not need every hostile reference engine installed. It must be able to rerun LOOM acceptance against governed frozen reference artifacts.

Reference vectors must retain source tool/version, scenario, units/frames, integrator/settings, generation date, license/provenance, tolerances and hash.

## TESTING DISCIPLINE

- unit regression before sending new Python;
- substantive functional changes: unit + functional qualification;
- full end-to-end regression before production/runtime promotion;
- deterministic tests;
- Pixel mandatory for portable acceptance;
- Windows/desktop/CI hostile checks supplement Pixel; they do not replace it;
- do not use manual graph inspection as pass/fail authority.

## WAYFARER AUTHORITY

Before relying on any Wayfarer dimensions, masses, component positions or engineering classifications, fetch the live GitHub sources.

Likely relevant files must be rediscovered/fetched live, including current Wayfarer geometry seed/compiler, physical-baseline bridge, tests and canon/candidate engineering documentation.

Do not silently invent missing inertia tensors, RCS layouts, thrust values or other dynamics data. Missing values must remain missing/open or be introduced through governed candidate/design work with provenance.

## NON-NEGOTIABLES

1. Testing authority is executable code/data, not LLM assertion.
2. Mandatory qualification runs on Pixel offline after setup.
3. GitHub documentary authority outranks chat/memory.
4. Do not break the accepted campaign authority chain.
5. Do not break the damn game.
6. No arbitrary physical `maneuverability` stat; derive it from mass properties/effectors.
7. One shared numeric source feeds dynamics and minimal geometry where appropriate.
8. Ordinary/torch physics and speculative metric physics remain explicitly separated.
9. Metric transit does not fabricate ordinary-space occupancy.
10. `loompy` waits for physics-research governance.
11. No merge without explicit user authorization.

## FIRST CONCRETE EXIT TARGET

Before moving deeper into schema work, prove on the Pixel that a deterministic external-to-LLM 6DOF test harness can run locally and accept a custom force/moment model.

Then freeze the simulator-role decision in Git and proceed to generic ship physical-contract design.
