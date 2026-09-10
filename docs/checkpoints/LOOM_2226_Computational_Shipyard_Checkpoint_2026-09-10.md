# LOOM 2226 — Computational Shipyard Checkpoint — 2026-09-10

Status: ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION

Branch at checkpoint:
`research/computational-shipyard-integrated-vehicle-pipeline-v0.1-2026-09-09`

Branch head before checkpoint commit:
`3c99e6d39a3b1e50599b1ef6ae8a14afc4ee3723`

## Program goalposts

The Computational Shipyard now has two explicit downstream acceptance targets derived from one governed design state:

1. **Navigator / HUD physical vehicle** — usable by real astrodynamics and propulsion logic, with declared authority per field.
2. **Visualization vehicle** — deterministic semantic geometry / GLB that can be inspected in-browser and handed to yard-specific AI visual realization without visual output becoming engineering truth.

The project invariant remains:

**Geometry does not own the ship.**

Authoritative engineering state, provenance, and admitted constraints outrank derived geometry and imagery.

## Visualization architecture — current frozen-enough state

The visualization lane has been materially simplified around:

`Design State -> semantic geometry -> deterministic GLB -> SQLite visual library -> browser inspection -> realization packet -> yard-specific AI visualization`

Principle:

**MINIMAL 3D. MAXIMAL ENGINEERING SEMANTICS.**

Current capabilities on the active branch include:

- deterministic semantic GLB generation;
- GLB-native browser viewer;
- Android/Pixel localhost launchers;
- WebGL2 preference with WebGL1 + `OES_element_index_uint` compatibility for older uint32-index GLBs;
- whole-GLB storage in the Shipyard SQLite visual library;
- side-by-side preservation of authority-distinct assets such as `GOVERNED_SEMANTIC`, `VISUAL_REFERENCE`, and `EXTERNAL_FIXTURE`;
- the richer legacy `wayfarer_test.glb` successfully imported and displayed from SQLite as a non-authoritative visual reference;
- ASTERIA / KELDRIN / SHIKARI / TASCHEN structured visual grammars;
- deterministic realization packets binding source GLB hash + yard grammar + component map + standard reference-view definitions;
- a visual workspace capable of storing non-authoritative realized images back into SQLite with provenance.

The local viewer cannot directly call ChatGPT's built-in image generator; an external API/provider bridge would be required for one-button generation. That bridge is intentionally deferred while we pivot back to shipbuilding.

## Legacy Wayfarer GLB role

`wayfarer_test.glb` is retained as a visualization regression/reference fixture only. It is useful because it contains meaningful named nodes such as pressure hull, tanks, longerons, technical core, radiators, reactor/torch envelope, nozzle, docking collar, and launch systems.

It MUST NOT outrank the current governed engineering state.

## Generative Shipyard — current state

The project has now pivoted from visualization back to iterative shipbuilding.

The governed synthesis baseline still separates:

1. engineering dependency graph;
2. physical topology graph;
3. spatial state / fields.

The first bounded generative foundation is implemented and exercised. It introduces a governed architecture/search layer that preserves OPEN state and model-adequacy limits rather than inventing missing physics.

A first bounded Wayfarer family test has run successfully under CI:

- 10 candidate outcomes;
- 6 survived the current screen;
- 4 were rejected by adequate current models;
- 4 remained on the current Pareto frontier;
- experiment deterministic;
- no flight-dynamics authority;
- no canon change;
- no production shipclass change.

This is a research-level screen only, not final optimization or qualification.

## Candidate archive and campaign path

The active branch includes a persistent campaign path that:

- runs the bounded Wayfarer configuration experiment;
- archives candidate lineage/results into the Shipyard SQLite;
- compiles surviving candidates into governed semantic GLBs;
- inserts those GLBs into the visual library;
- evaluates current vehicle-dynamics differentiation;
- exposes a Pixel launcher:
  `deploy/android/LOOM_Shipyard_Build_Campaign.py`.

The campaign report explicitly states the current physical limitation:

`TRANSLATIONAL_MISSION_BEHAVIOR_NOT_YET_DIFFERENTIATED; CURRENT_ADMITTED_DOMAIN_CHANGES_PACKAGING_ONLY`

That is the next meaningful blocker.

## Current physical-design baseline

The existing Wayfarer S1 substrate remains deliberately conservative:

- `CandidateDesign` / component instances / point masses / keep-outs;
- exact mass and CoM accounting within admitted inputs;
- centroidal inertia only where geometry is actually admitted;
- collision checks for supported primitive geometry;
- hard constraints and objective terms;
- flight authority explicitly false.

Current S1 search still varies a narrow domain:

- fixed relational-plant x station in this slice;
- launch x station;
- tank common x station.

This is sufficient to test deterministic search/provenance mechanics but is not yet enough to create materially different Navigator mission behavior.

## Immediate next work

Priority now moves to the actual shipbuilder rather than additional viewer polish.

### 1. Vehicle Dynamics Contract

Create a typed, authority-aware contract between Shipyard and Navigator/HUD. Candidate fields include:

- ship/candidate/design-state identity and hashes;
- dry mass / wet mass / current mass;
- center of mass;
- inertia tensor only when qualified;
- remass inventory and depletion state;
- Torch thrust / acceleration / exhaust-velocity envelopes by admitted mode;
- configuration state and propulsion eligibility;
- docking / deployment constraints;
- Metric and Loom capability/state as separate governed mechanisms;
- uncertainty / adequacy / provenance per field.

No current coarse geometry may silently become flight-inertia authority.

### 2. Expand Architecture Domain only where evidence exists

Move beyond packaging-only variation with bounded choices that can affect mission performance. Candidate future choices include, only when supported by admitted models:

- structural organization;
- remass/tank architecture;
- radiator arrangement;
- power/thermal packaging;
- docking / attachment configuration;
- propulsion/remass operational architecture;
- service/redundancy doctrine;
- manufacturing-constrained topology.

Do not invent values merely to create variation.

### 3. Executable discipline graph

Turn current discipline contracts into causal/evaluable propagation:

`architecture -> mass <-> packaging <-> thermal <-> power <-> propulsion <-> structure <-> shielding <-> maintenance/manufacturing`

Missing admitted physics must BLOCK or remain OPEN.

### 4. Navigator mission evaluator

Once the Vehicle Dynamics Contract contains admitted translationally relevant differences, use Navigator as a real design evaluator:

- ordinary Torch astrodynamics and finite-burn behavior;
- remass consumption;
- arrival/braking/capture behavior;
- configuration eligibility;
- Metric and Loom handled by their own governed models rather than fake thrust.

Mission performance belongs inside the candidate loop.

### 5. Pareto / lineage loop

Retain nondominated candidates and trace:

- parent candidate;
- mutation / architecture choice;
- changed inputs;
- model adequacy used for rejection;
- rejection reason;
- surviving objectives;
- downstream Navigator and visualization artifacts.

Rule retained:

**No candidate may be eliminated by a model that is not adequate for the reason it is being eliminated.**

## Acceptance milestones

### M1 — One ship closes

One governed Wayfarer can:

- produce a physics-consumable Navigator/HUD contract;
- run through real admitted astrodynamics/propulsion behavior;
- emit semantic GLB;
- display on Pixel;
- emit yard-specific realization packets.

### M2 — Ships vary

Multiple governed Wayfarer candidates differ in both:

- mission-relevant Navigator behavior; and
- semantic spatial geometry.

### M3 — Ships evolve

The Shipyard iteratively searches architecture space, rejects candidates for traceable engineering reasons, retains a robust Pareto frontier, and automatically produces Navigator + visualization outputs for survivors.

## Explicitly deferred

- OpenAI API bridge for one-button image generation;
- photorealistic native rendering;
- detailed procedural hull/greeble work;
- decorative high-poly geometry;
- component-level GLB decomposition unless needed for actual engineering/reuse;
- topology optimization performed only for appearance;
- structural qualification before admitted analysis exists;
- any mutation of canon/production authority from research results.

## Validation at pre-checkpoint head

At `3c99e6d39a3b1e50599b1ef6ae8a14afc4ee3723`, the following CI workflows were green:

- LOOM Shipyard GLB Native Viewer;
- LOOM Shipyard Semantic GLB v0.1;
- LOOM Shipyard Spatial Rule Contract R2A;
- LOOM Shipyard Candidate Archive;
- LOOM Shipyard Semantic 3D Builder Smoke;
- LOOM Shipyard Minimum Spatial Validation R2;
- LOOM Shipyard Visual Workspace;
- LOOM Shipyard Visual Grammar;
- LOOM Generative Shipyard Foundation;
- LOOM Python Regression.

This checkpoint is a research-state preservation marker only. It does not merge, promote, canonize, or qualify any Shipyard result.
