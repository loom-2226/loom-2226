# LOOM 2226 — Experience One End-to-End Flight Physics Objective v0.1

**Status:** ACTIVE ENGINEERING OBJECTIVE / NON-CANON DESIGN GOVERNANCE  
**Date:** 2026-09-15  
**Scope:** Experience One (E1), Wayfarer flight from astrodynamics scale through local flight and metric transition

## Purpose

E1 is not a 3D-ship preservation exercise and is not a renderer qualification exercise.

Its primary engineering objective is to demonstrate one continuous, governed spacecraft-flight stack in which the Wayfarer can be propagated, controlled and reviewed coherently across:

1. solar-system / interplanetary astrodynamics;
2. orbital and local-body dynamics;
3. conventional spacecraft translation and attitude control;
4. torch propulsion and remass/feed behavior;
5. metric-transition entry, transport and exit;
6. return to ordinary local-flight dynamics;
7. Navigator, Solar GIS and HUD presentation of the same authoritative state without changing physical authority.

The target quality bar is NASA-level astrodynamics and spacecraft-dynamics discipline for ordinary physics, with fictional propulsion/metric physics kept explicit, deterministic, internally self-consistent, fail-closed and provenance-governed.

## Priority hierarchy

When prior visualization, geometry, HUD, Shipyard, E1, or engineering artifacts conflict, E1 uses the following priority:

1. **Correct spacecraft dynamics and state continuity**
2. **Correct astrodynamics / orbital mechanics and reference-frame handling**
3. **Credible RCS / GNC / attitude and translation authority**
4. **Credible torch propulsion, remass, feed, thermal and structural interfaces**
5. **Internally consistent metric-transition physics and certification**
6. **Seamless cross-scale Navigator → GIS → metric-transition → HUD local-flight handoff**
7. **Geometry / layout / renderer continuity**
8. **Preservation of historical 3D appearance**

The previous 3D Wayfarer, HUD and Computational Shipyard work is therefore evidence and lineage, not a design veto.

## Wayfarer shape constraint

The existing Wayfarer general physical identity remains useful:

- approximately 57 m overall length;
- approximately 9 m nominal main-body diameter;
- long axial spacecraft architecture;
- forward crew / mission volume;
- central tanks / systems / structural spine;
- aft propulsion complex;
- overall visual identity recognizable as the Wayfarer.

These are broad design anchors, not authority for exact component placement.

E1 may change component stations, RCS mounts, radiator roots, tank arrangement details, internal equipment envelopes, thrust-frame details, metric-node placement, launch-bay packaging, docking geometry, or other design-baseline geometry where required to achieve a physically coherent spacecraft.

Any such change must preserve provenance and downstream recoverability.

## Baseline-to-E1 change rule

Any E1 change that differs materially from prior HUD / Wayfarer 3D / Computational Shipyard baselines must record:

- prior source artifact / branch / PR / commit where known;
- old assumption or geometry;
- new E1 assumption or geometry;
- reason for change;
- governing physics or qualification dependency that forced or justified it;
- affected downstream consumers;
- whether the prior consumer is now stale, compatible, or needs adaptation;
- whether the change is DESIGN_BASELINE, ENGINEERING_CANDIDATE, QUALIFIED_ENGINEERING, or CANON.

The purpose is not to preserve old layouts. The purpose is to make later HUD and Shipyard work resumable without reverse-engineering what E1 changed.

## E1 change ledger

Material divergences from prior HUD / Shipyard / 3D assumptions should be appended to an E1 change ledger using stable machine-readable fields wherever practical:

- `change_id`
- `e1_commit`
- `baseline_source`
- `baseline_ref`
- `baseline_value_or_geometry`
- `e1_value_or_geometry`
- `reason`
- `physics_dependency`
- `affected_consumers`
- `compatibility` = `COMPATIBLE | ADAPTATION_REQUIRED | STALE | SUPERSEDED`
- `authority_status`

A later HUD or Shipyard workstream should be able to traverse this ledger forward from its last known baseline rather than infer changes from visual diffs.

## Required downstream recovery path

When E1 stabilizes a physical change, the lineage record must identify expected adaptation points for:

- Wayfarer deterministic geometry source;
- semantic GLB / 3D derivatives;
- Computational Shipyard design ledger and geometry consumers;
- Solar GIS / HUD inspection geometry;
- local-flight attitude / plume / interference visualization;
- E1 containment / metric-boundary qualification;
- any mass / CoM / inertia consumers.

Derived presentation artifacts never outrank the authoritative physical model.

## End-to-end E1 physics stack

### A. Astrodynamics and reference frames

E1 must support deterministic, explicit frame/state transformations across at least:

- heliocentric / solar-system navigation context;
- body-centered inertial/orbital context;
- body-fixed context where required;
- spacecraft body frame;
- local flight / relative-navigation frame where required;
- metric-transition state representation.

No renderer or UI owns these transforms.

Frame changes must not silently teleport, rotate, accelerate, or reset the vehicle.

### B. Ordinary orbital and local flight

Ordinary-space propagation should use established spacecraft-dynamics practice wherever physics is non-fictional, including as applicable:

- state vectors with explicit epoch and frame;
- N-body / central-body gravity model appropriate to fidelity level;
- body harmonics / rotation / ephemeris where material;
- finite burns rather than UI-derived impulses where finite burn duration matters;
- mass depletion and configuration state;
- attitude kinematics/dynamics;
- translational/rotational coupling where required;
- event-driven transitions between regimes;
- uncertainty / provenance sufficient to know what has and has not been qualified.

### C. RCS / GNC

E1 must make the Wayfarer controllable in ordinary space rather than merely geometrically plausible.

Required closure includes:

- qualified configuration-aware mass and inertia state;
- RCS station/mount geometry;
- force and torque authority;
- allocation / controllability;
- degraded / one-cluster-out behavior where required;
- minimum-impulse / actuator dynamics where material;
- plume and keep-out geometry;
- launch, docking, radiator and torch interference;
- structural mount/load constraints;
- closed-loop attitude / translation behavior at the fidelity needed for E1 maneuvers.

Recovered HUD/Q4/Q5 RCS work is candidate evidence only until revalidated against the current vehicle.

### D. Torch propulsion

Torch propulsion is fictional in mechanism but must behave as an engineered momentum-exchange propulsion system at the spacecraft level.

E1 requires coherent interfaces for:

- thrust magnitude and direction;
- throttle/mode behavior;
- exhaust velocity / remass flow relationship;
- mass depletion;
- feed architecture and transient supply;
- inlet/interface requirements;
- thermal burden;
- thrust-frame / structural load path;
- nozzle / plume exclusion geometry;
- attitude-control interaction;
- burn-to-coast / coast-to-burn transitions.

Fictional core physics does not excuse inconsistent mechanics at its interfaces.

### E. Metric transition

Metric transport is a separate regime from torch flight.

E1 must model an explicit transition contract including:

- pre-transition ordinary-space state;
- vessel configuration eligibility;
- node / array / domain readiness;
- local geometry / causal / matter / thermal / control certification channels;
- certified translation-domain boundary and vessel membership;
- transition initiation;
- metric transport state;
- exit / collapse / re-entry into ordinary dynamics;
- post-transition position, velocity/momentum, attitude/configuration semantics;
- failure / hold / derate / collapse behavior.

Metric transport may use fictional relational physics, but every state transition must be deterministic and auditable.

### F. Cross-scale continuity

The central E1 demonstration is that the same governed spacecraft can move seamlessly through:

`Navigator / system scale`
→ `orbital/body approach`
→ `local flight / maneuvering`
→ `metric transition`
→ `metric transport`
→ `ordinary-space re-entry`
→ `local HUD flight`

Solar GIS and HUD are consumers of authoritative state, not alternative simulators.

A scale change or presentation handoff must not create a second position, velocity, attitude, propulsion, timeline, or campaign truth.

## Authority separation

- Python / deterministic runtime: calculation and physical state authority.
- Navigator: governed navigation / route realization authority within its defined contract.
- GIS / HUD / browser: presentation, intent and review only unless a separately governed input contract explicitly says otherwise.
- LLM: interpretation and engineering assistance only; calculation/state/execution authority ZERO.

## Current E1 use of prior work

The following prior work may accelerate E1 but is explicitly replaceable:

- Wayfarer 3D geometry and semantic GLB derivatives;
- prior Computational Shipyard component placements;
- prior HUD attitude-envelope assumptions;
- recovered RCS 16-hardpoint candidate;
- prior torch/remass architecture studies;
- current 13×16 metric-node design baseline.

They survive only where they remain compatible with the end-to-end E1 physics objective.

## Definition of success

E1 succeeds when one Wayfarer mission can be replayed from authoritative inputs with deterministic state continuity such that:

- Navigator-scale trajectory and orbital/local-flight state agree;
- the spacecraft has credible ordinary-space translation and attitude authority;
- torch burns change momentum and mass consistently;
- metric entry/transport/exit obey the governed metric contract;
- configuration, mass, CoM, inertia and subsystem state evolve consistently;
- HUD and GIS can display the same state at appropriate scales without changing it;
- no hidden hand-authored state jump is needed to move between system, orbital, metric and local-flight regimes;
- provenance shows exactly where fictional physics begins and what empirical/classical mechanics remains conventional;
- prior HUD/Shipyard work can later be resumed using the recorded baseline-to-E1 change ledger rather than rediscovered manually.

## Non-goals

E1 does not require preserving the existing 3D Wayfarer exactly.
E1 does not require completing the full Computational Shipyard.
E1 does not require final production-quality HUD visuals.
E1 does not require detailed Loom/interstellar hardware certification.
E1 does not promote design-baseline geometry to canon merely because it enables a demonstration.

The governing exercise is **one scientifically disciplined, continuous spacecraft flight model across scale and propulsion regime boundaries**.
