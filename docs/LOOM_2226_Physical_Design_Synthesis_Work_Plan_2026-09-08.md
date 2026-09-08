# LOOM 2226 — Physical Design Synthesis Work Plan

**Date:** 2026-09-08  
**Status:** ENGINEERING / RESEARCH — NON-CANON — NON-PRODUCTION — NEW WORKSTREAM  
**Branch:** `research/physical-design-synthesis-wayfarer-s1-2026-09-08`  
**Frozen parent:** `qualification/portable-ship-phase5-dynamics-2026-09-08` at commit `1d8ef6a20427dbfc7b6b38596824abcf8e6afd2d`  
**Primary first test vehicle:** reference courier **Wayfarer**

---

## 1. Purpose

Develop a generic, deterministic, physically grounded design-synthesis framework that can procedurally generate and evaluate spacecraft from component parts and design requirements, with the framework deliberately structured so that later domains can include orbitals and industrial/surface facilities without rewriting the core architecture.

This workstream exists because the current Wayfarer qualification path exposed a structural limitation in the hand-authored design: mass and CoM are governed, but complete centroidal inertia is not. Rather than force geometric assumptions backward onto a manually placed mass ledger, this workstream tests whether physical arrangement can instead be generated upstream and then made authoritative for geometry, mass properties, inertia, dynamics and later industrial production.

The immediate research question is deliberately narrow:

> Can LOOM deterministically generate a legal Wayfarer-class physical arrangement from governed requirements and component constraints, while deriving mass, CoM, geometry and inertia from the generated arrangement itself?

If the answer is no, the frozen Phase-5C manual inertia plan remains available as the fallback path.

---

## 2. Hard freeze / authority boundary

The existing Phase-5 qualification branch is frozen at:

```text
1d8ef6a20427dbfc7b6b38596824abcf8e6afd2d
qualification: define Phase 5C Wayfarer inertia authority plan
```

No further work in this synthesis workstream may mutate that branch.

The following remain true:

- Phase 5A portable mechanics is PASSED on Pixel/offline.
- Phase 5B inertia audit is PASSED on Pixel/offline.
- Full Wayfarer rotational 6DOF remains fail-closed with `WAYFARER_INERTIA_OPEN_NOT_QUALIFIED`.
- The Phase-5C manual candidate inertia plan remains preserved but paused as a fallback.
- Production SHIPCLASSES is untouched.
- Navigator/GIS/HUD physics-dependent work remains hard frozen.
- No merge is authorized by this work plan.

This synthesis workstream is research/engineering only until a separate qualification gate explicitly promotes any generated design into physical authority.

---

## 3. Core architecture

The framework shall be generic and domain-neutral at its center.

```text
TECHNOLOGY / INDUSTRIAL CONTEXT
            ↓
COMPONENT / MODULE LIBRARY
            ↓
DESIGN REQUIREMENTS
            ↓
DESIGN GRAMMAR
            ↓
TOPOLOGY + PLACEMENT SYNTHESIZER
            ↓
CANDIDATE PHYSICAL DESIGN
            ↓
PHYSICAL EVALUATOR
            ↓
SELECTED DESIGN AUTHORITY
            ↓
SHIPCLASS / ORBITALCLASS / FACILITYCLASS
            ↓
INSTANCE STATE
            ↓
DYNAMICS / DAMAGE / LOGISTICS / GAME
```

The optimizer shall generate physical arrangements, not hand-authored game statistics.

Derived game/simulation behavior must flow from generated physical authority.

---

## 4. Domain-neutral core objects

The core framework shall be designed around objects such as:

- `PhysicalComponentType`
- `PhysicalComponentInstance`
- `ConnectionPort`
- `MountRule`
- `DesignVariable`
- `HardConstraint`
- `SoftConstraint`
- `ObjectiveTerm`
- `DesignGrammar`
- `CandidateTopology`
- `CandidatePlacement`
- `CandidateDesign`
- `EvaluationResult`
- `DesignAuthorityRecord`
- `TechnologyContext`
- `IndustrialContext`

The core may understand geometry, transforms, graphs, constraints, scores and physical evaluators, but shall not hard-code concepts such as `ship`, `orbital`, `torch` or `spin habitat`.

Those belong in domain adapters.

---

## 5. Planned domain adapters

### 5.1 Ship domain — ACTIVE FIRST DOMAIN

Ship-specific semantics may include:

- thrust axis;
- propulsion alignment;
- acceleration load direction;
- tank/feed placement;
- RCS/control authority;
- docking approach volumes;
- launch/extraction corridors;
- crew/service access;
- radiator deployment clearance;
- forward/aft radiation separation;
- variable stores and detachable vehicles.

### 5.2 Orbital domain — RESERVED / DESIGN FOR NOW

The core must remain compatible with future orbital semantics such as:

- spin/non-spin sections;
- artificial-gravity radius and stress;
- non-spinning docking hubs;
- station-keeping;
- solar exposure;
- radiator shadowing;
- cargo traffic paths;
- industrial/habitation separation;
- large truss networks;
- module additions over time.

No orbital implementation is authorized in the first synthesis increment.

### 5.3 Surface / industrial facility domain — RESERVED

The architecture shall avoid choices that would make later facility synthesis impossible, but no surface-facility implementation is currently in scope.

---

## 6. Component library contract

Each component type should be able to expose, where physically meaningful:

```text
identity / class
technology prerequisites
manufacturer / industrial prerequisites
mass model
geometry / physical envelope
centroidal inertia model
mount points
allowed orientations
structural interfaces
power ports and power demand/supply
thermal generation / rejection requirements
fluid ports / feed dependencies
data/control links
crew/service access envelope
radiation source / shielding requirements
clearance / keep-out volumes
failure / detach state
cost / material / manufacturing demand
provenance / authority status
```

Not every component must implement every field.

Missing fields must remain explicit rather than silently defaulting to invented physics.

---

## 7. Design requirements contract

A design request shall describe what must be achieved, not manually place every component.

A requirement may include:

- required component inventory;
- minimum/maximum capacity;
- crew;
- payload;
- endurance;
- acceleration envelope;
- delta-v / working-fluid allocation;
- power requirement;
- thermal rejection requirement;
- docking interfaces;
- launch capability;
- envelope limits;
- safety margins;
- redundancy;
- technology limits;
- industrial/manufacturing limits;
- cost / mass / performance objectives.

The first Wayfarer test shall use the existing governed/candidate inventory and constraints rather than inventing a new ship specification.

---

## 8. Design grammar

A domain grammar encodes physically meaningful structural doctrine that should not be rediscovered by blind random search.

For the first Wayfarer experiment, candidate grammar constraints may include:

- one axial primary torch / nozzle system;
- aft propulsion region;
- inhabited volume forward of primary reactor/torch machinery;
- shielding between hazardous aft machinery and inhabited volume where required by existing authority;
- four major working-fluid/remass tanks in quadrature;
- four principal longerons;
- four radiator assemblies;
- semi-recessed integrated planetary-access launch bay;
- launch extraction corridor on the governed +Z side;
- docking/service side on -Z;
- structural connectivity between major masses and primary thrust load path;
- no collisions between physical envelopes;
- no use of OPEN radiator-panel or docking dimensions as hidden physical truth.

Grammar constraints must be explicitly sourced or explicitly marked as candidate engineering assumptions.

---

## 9. Search / optimization strategy

The portable LOOM runtime shall not initially depend on OpenMDAO, HEEDS, ModelCenter or another heavyweight optimization framework.

The first solver shall be LOOM-owned, deterministic and transparent.

Initial admissible methods include:

- deterministic constructive placement;
- heuristic ordering;
- bounded hill climbing;
- simulated annealing with deterministic RNG seed;
- beam search;
- deterministic genetic/evolutionary search if all randomness is seeded and serialized.

The optimizer must be replaceable behind a stable solver interface.

A future desktop/reference adapter may use OpenMDAO or another heavyweight framework as hostile/reference optimization, just as Basilisk/JEOD/Tudat are used as hostile/reference systems for dynamics.

---

## 10. Candidate physical evaluator

Every candidate design must be independently evaluated from its actual arrangement.

The evaluator shall eventually be able to produce:

- total mass;
- center of mass;
- full inertia tensor;
- principal axes/eigenvalues;
- geometry extents;
- collision and clearance checks;
- structural connectivity;
- thrust-axis / propulsion alignment;
- tank symmetry / store placement;
- connection-graph validity;
- plumbing / feed-path length surrogates;
- power-path length / capacity surrogates;
- thermal adjacency / rejection surrogates;
- radiation separation surrogates;
- docking clearance;
- launch extraction clearance;
- control-authority burden;
- provenance and unresolved-physics fraction.

A candidate with unresolved mandatory physics shall be rejected or explicitly marked non-authoritative; it shall not be silently patched.

---

## 11. Determinism and provenance

Every generated design must be reproducible from explicit inputs.

At minimum record:

```text
design_id
solver_name
solver_version
seed
component_library_version
technology_context_version
industrial_context_version
requirements_hash
grammar_hash
objective_weights
selected component inventory
selected transforms/topology
candidate score
constraint results
provenance map
```

Same executable + same inputs + same seed must reproduce byte-equivalent canonical design output on the target platform where practical.

---

## 12. Relationship to existing SHIPCLASSES work

The existing prototype SHIPCLASSES schema remains useful as a downstream physical-authority representation.

The synthesis framework shall not rewrite production SHIPCLASSES directly.

Instead:

```text
SYNTHESIS CANDIDATE
      ↓
qualification export / adapter
      ↓
SHIPCLASSES-compatible physical design snapshot
      ↓
existing mass / geometry / dynamics evaluators
```

The first experiment may use a qualification-only candidate schema if necessary, provided all generated outputs can later be projected into the generic physical contract without Wayfarer-specific hard-coding.

---

# PART II — WAYFARER FIRST TEST

## 13. Why Wayfarer is the first test

Wayfarer is ideal because:

1. its mass ledger is already explicit;
2. its wet/dry mass and CoM have already been qualified;
3. its major topology is partially governed;
4. its deterministic geometry pipeline already exists;
5. its current hand-authored layout provides a useful baseline;
6. current Phase 5 exposes exactly the missing quantity the new framework should solve upstream: physically defensible inertia.

The objective is not to replace Wayfarer canon in the first experiment.

The objective is to determine whether a generated physical arrangement can reproduce a legal Wayfarer-like vehicle and automatically close more of the physical-authority chain.

---

## 14. S0 — Freeze and extraction

**Goal:** Convert existing Wayfarer authority into machine-readable synthesis inputs without altering it.

Deliverables:

- frozen source manifest from current canon, geometry seed, Phase-3 seed, Phase-4 geometry overlay and Phase-5 status;
- classification of every source field as `CANON`, `DESIGN_BASELINE`, `DERIVED`, `OPEN`, or `QUALIFICATION_ONLY`;
- extraction of current component inventory, masses, existing centroids, known envelopes and topology constraints;
- explicit list of fields that must *not* be optimized in S1.

Acceptance:

- extraction reproduces current wet/dry mass exactly;
- extraction reproduces current DOCKED/ABSENT CoM exactly;
- no source mutation;
- no OPEN dimensions promoted.

---

## 15. S1 — Procedural Wayfarer layout feasibility

**Goal:** Prove that a deterministic portable solver can generate at least one legal Wayfarer-class arrangement from constraints rather than from the current full list of hand-authored transforms.

### 15.1 Fixed in S1

Keep fixed initially:

- overall ship-length reference and nominal main-body diameter;
- forward pressure-hull region;
- axial torch/nozzle topology;
- major aft propulsion region;
- four-tank topology;
- four-longeron topology;
- four-radiator topology/count;
- integrated launch requirement;
- +Z launch side and -Z docking side;
- current component mass ledger;
- current total 300 t working-fluid/water accounting;
- current launch mass/state semantics.

### 15.2 Candidate variables in S1

Allow controlled movement or grouping of selected components such as:

- relational plant longitudinal placement within an admissible region;
- electrical systems placement;
- avionics/sensors/comms placement;
- mission/courier systems placement;
- RCS/docking/service allowance placement;
- protected-water placement if an admissible containing region can be defined without inventing geometry;
- engineering-reserve placement as an explicitly abstract balance term only if justified;
- launch longitudinal station within governed bay reservation;
- common longitudinal placement of the four-tank cluster while preserving quadrature geometry and aggregate inventory.

S1 may further reduce this list if authority is insufficient.

### 15.3 S1 hard constraints

At minimum:

- no collision among admitted physical envelopes;
- all components remain inside or explicitly attached to the admitted ship envelope;
- canonical component counts remain correct;
- launch extraction path remains legal;
- propulsion remains axially aligned;
- tank quadrature remains preserved;
- mass ledger remains exact;
- working-fluid/water accounting remains exact;
- prohibited/open geometry remains unused;
- required structural/functional adjacency rules remain satisfied.

### 15.4 S1 objectives

Initial objective vector should be intentionally small and inspectable. Candidate terms:

- minimize transverse CoM offset;
- keep longitudinal CoM within an admissible target band;
- minimize selected principal inertias / control burden subject to stability/physicality;
- minimize first-order feed/plumbing distance;
- minimize major electrical interconnect distance;
- minimize radiation/thermal penalties;
- minimize unused or conflicting envelope volume.

No single scalar objective should silently collapse materially different tradeoffs without preserving component scores.

### 15.5 S1 required output

The selected candidate shall emit:

- complete component transform list for every admitted component;
- physical geometry/equivalent-body mapping used for mass properties;
- exact mass;
- exact CoM;
- full candidate inertia tensor;
- principal inertias/axes;
- all hard-constraint results;
- full objective breakdown;
- source/provenance classification per input and derived field;
- deterministic seed and hashes;
- qualification-only SHIPCLASSES-compatible projection;
- minimal 3D output compatible with the existing geometry-viewer direction.

### 15.6 S1 success criterion

S1 passes only if all of the following are true:

1. at least one candidate is generated from solver decisions rather than simply replaying the current full transform list;
2. all hard constraints pass;
3. mass accounting exactly matches the existing qualified Wayfarer ledger;
4. candidate mass properties are derivable from admitted component geometry/distribution with no hidden OPEN values;
5. candidate full inertia is symmetric positive definite;
6. the same inputs/seed produce the same selected candidate deterministically;
7. the process remains portable enough to run on Pixel after setup;
8. the generated design is clearly marked `QUALIFICATION_CANDIDATE`, not canon or production authority.

S1 does **not** require the generated design to outperform the current Wayfarer.

---

## 16. S2 — Compare generated candidate to hand-authored Wayfarer

If S1 passes, compare:

```text
HAND-AUTHORED WAYFARER BASELINE
vs
GENERATED WAYFARER CANDIDATE(S)
```

Report differences in:

- component positions;
- CoM;
- inertia;
- principal axes;
- envelope use;
- feed/power path surrogates;
- thermal/radiation penalties;
- launch/docking clearances;
- control burden;
- unresolved assumptions.

No generated arrangement may replace governing Wayfarer design without explicit later governance action.

---

## 17. S3 — External hostile/reference optimizer

If S1/S2 are promising, formulate the same reduced design problem in an external multidisciplinary optimization framework such as OpenMDAO or an equivalent reference tool.

Purpose:

- test whether the LOOM portable solver finds comparable legal solutions;
- expose weak objective scaling / search stagnation / hidden local minima;
- validate constraint implementation;
- establish frozen hostile/reference vectors or candidate outputs.

The external optimizer is not a runtime dependency.

---

## 18. S4 — Second ship class generalization test

Only after S1–S3 are credible, test a second vehicle whose layout is not already embodied in Wayfarer transforms.

Preferred candidate:

```text
small interplanetary tug
```

The test must reuse the same core component, constraint, evaluation and optimization interfaces.

If the second ship requires a separate bespoke solver, the generic architecture has failed.

---

## 19. S5 — Industrial-generation seam

After at least two ship-class designs can be generated, add a non-gameplay industrial context that limits the admissible component library and objective weighting by:

- technology availability;
- materials;
- yard envelope/capacity;
- manufacturing precision;
- energy capacity;
- workforce/automation capability;
- cost/capital constraints;
- manufacturer doctrine.

The first industrial test shall demonstrate that the same mission/class requirement can produce two different legal designs under two different industrial contexts.

This is the seam by which later economic/history simulation can produce design families.

---

## 20. S6 — Orbital readiness gate

Before implementing an orbital generator, prove that the core design framework does not assume ship-only concepts.

A readiness audit shall demonstrate that:

- topology and placement engine is domain-neutral;
- geometry supports branching/truss/module architectures, not only axial hulls;
- constraints can express spin-axis and non-spin-section relationships;
- objectives can be domain-injected;
- component library supports stationary facilities and rotating assemblies;
- selected design authority can represent non-vehicle facilities.

Only after this gate may the first orbital feasibility experiment begin.

---

## 21. Testing / qualification discipline

The existing LOOM testing discipline remains in force:

- unit regression before distributing new Python;
- unit + functional testing for substantive changes;
- full end-to-end regression before any production promotion;
- Pixel execution mandatory for portable acceptance;
- offline repeat mandatory for final portable acceptance;
- executable code/data, not ChatGPT, determines PASS/FAIL;
- failures and repairs remain part of qualification evidence.

For synthesis specifically, add:

- deterministic replay tests;
- constraint-injection tests;
- deliberately impossible-design tests that must fail closed;
- solver-seed reproducibility tests;
- objective-component regression tests;
- independent mass/CoM/inertia recomputation outside the optimizer;
- mutation tests proving the evaluator rejects physically invalid candidates.

---

## 22. Immediate first coding increment

The first executable increment should be intentionally small.

Create a new qualification/research package, provisionally:

```text
qualification/synthesis/
    contracts.py
    wayfarer_inputs.py
    evaluator.py
    solver_s1.py
    verify_s1.py
    tests/
```

Initial code should implement only:

1. typed component/constraint/candidate contracts;
2. extraction of frozen Wayfarer S1 inputs;
3. deterministic candidate representation;
4. exact mass/CoM evaluator;
5. a minimal admitted centroidal-inertia/equivalent-shape evaluator;
6. collision/region checks sufficient for the reduced S1 problem;
7. one transparent deterministic placement/search strategy;
8. structured PASS/FAIL output with hashes and provenance.

Do not add industrial generation, orbitals, detailed thermal analysis, finite-element structure, ML or procedural aesthetics in the first coding increment.

---

## 23. First decision gate

After S1, stop and decide among three outcomes.

### A. S1 strong success

Generated arrangement is legal, deterministic and physically coherent.

Then:

- continue S2/S3;
- consider making generated physical authority the preferred path for new ship classes;
- preserve hand-authored Wayfarer as comparison/reference until separately governed.

### B. S1 partial success

Architecture works but optimizer/search or missing component authority is weak.

Then:

- improve component library or search method;
- do not yet alter Phase-5 qualification path.

### C. S1 failure

Core requirements cannot be met without uncontrolled assumptions or unacceptable complexity.

Then:

- freeze synthesis experiment;
- return to preserved Phase-5C manual Wayfarer inertia plan.

This workstream must earn its continuation.

---

## 24. Gate state at work-plan creation

```text
PHASE 5A: PASSED / FROZEN
PHASE 5B: PASSED / FROZEN
PHASE 5C-M MANUAL INERTIA PATH: PRESERVED / PAUSED
PHYSICAL DESIGN SYNTHESIS: OPEN RESEARCH
WAYFARER S1: NOT YET IMPLEMENTED
ORBITAL SYNTHESIS: RESERVED / NOT IMPLEMENTED
INDUSTRIAL GENERATION: RESERVED / NOT IMPLEMENTED
NAVIGATOR/GIS/HUD PHYSICS WORK: FROZEN
PRODUCTION SHIPCLASSES: UNCHANGED
MERGE: NOT AUTHORIZED
```

---

**END — LOOM 2226 PHYSICAL DESIGN SYNTHESIS WORK PLAN**
