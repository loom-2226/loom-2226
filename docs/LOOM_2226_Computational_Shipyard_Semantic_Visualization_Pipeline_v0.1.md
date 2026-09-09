# LOOM 2226 — Computational Shipyard Semantic Visualization Pipeline v0.1

**Date:** 2026-09-09  
**Status:** ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION  
**Authority:** ARCHITECTURE / WORK-PLAN ONLY

## Purpose

Reframe Computational Shipyard visualization around the demonstrated Wayfarer pipeline:

`governed engineering state -> semantic engineering geometry -> minimal deterministic GLB -> deterministic reference views -> shipyard realization grammar -> AI visual realization`

The Shipyard is not required to generate presentation-quality finished spacecraft meshes. Its geometric responsibility is to produce deterministic, physically meaningful spatial representations sufficient for engineering reasoning, inspection, interaction, comparison and downstream visual conditioning.

## Governing principle

**MINIMAL 3D. MAXIMAL ENGINEERING SEMANTICS.**

The governed Design State and admitted engineering evidence remain authoritative. Geometry remains derived.

**Geometry does not own the ship.**

AI visual realization is explicitly non-authoritative and may not back-propagate unsupported engineering claims.

## Authority layers

### 1. Authoritative engineering state

Includes admitted requirements, calculations, dimensions, masses, placements, constraints, interfaces, statuses and provenance.

### 2. Derived engineering-traceable artifacts

Includes semantic geometry, GLB, deterministic reference renders and any structural graph derived by an admitted algorithm. Each artifact must be reproducible from its governed source state.

### 3. Non-authoritative visual realization

Includes AI-generated structural elaboration, surface detail, unspecified materials, invented conduits, local topology and hero imagery. These artifacts may inspire engineering questions but may not create engineering facts.

## Semantic geometry contract direction

Every generated object should eventually carry stable machine-readable identity sufficient to answer what it is, why it exists, where it came from and how downstream visualization may treat it.

Candidate fields, to be designed before freezing schema:

- `geometry_object_id`
- `source_design_state_id`
- `source_component_id`
- `semantic_class`
- `system_id`
- `function`
- `authority_status`
- `engineering_status`
- `geometry_role`
- `visual_mutability`
- `provenance_refs`

Candidate visual-mutability semantics include immutable shape/envelope/position, style elaboration allowed, non-authoritative proxy and analysis-only. These are architecture directions, not yet frozen enumerations.

## Minimal geometry scope

Prioritize geometry that supports engineering, interaction, simulation or conditioning value:

- pressure and habitable volumes;
- propellant tanks;
- cargo volumes;
- power/reactor/drive/nozzle envelopes;
- radiators and deployment envelopes;
- shielding regions;
- docking interfaces;
- thrust axis and center-of-mass representation;
- structural attachment points;
- justified major structural/load-path graph;
- service/maintenance clearances;
- thermal/radiation/shadow keep-outs;
- deployment/interference envelopes.

Do not add geometry solely to improve presentation quality.

## Work removed as required destinations

The following are no longer required Shipyard endpoints unless a later engineering, interaction, simulation or gameplay requirement justifies them:

- detailed procedural presentation hull generation;
- elaborate greeble systems;
- hand-authored surface detailing;
- production-quality procedural visual materials;
- native photorealistic rendering;
- Blender dependency;
- high-poly finished spacecraft meshes;
- decorative topology optimization;
- detailed structural filigree whose only purpose is appearance.

Existing working capabilities need not be deleted merely because they are no longer roadmap destinations.

## Work deferred

- high-resolution structural topology synthesis until admitted structural analysis requires it;
- graded-material spatial fields until constitutive and manufacturing models can consume them;
- detailed fluid/electrical/service routing until route feasibility requires it;
- detailed robotic maintenance motion planning until coarse access constraints are insufficient;
- PBR/Meshy-style textured 3D as optional downstream visualization.

## Deterministic reference rendering

A validated semantic GLB should eventually emit standardized deterministic views with fixed orientation, camera policy, focal length, scale and lighting. Candidate views include canonical fore and aft three-quarter views, port/starboard broadside, top, fore and aft.

Reference rendering is evidence/conditioning infrastructure, not cinematic rendering.

A future semantic reference board may combine rendered geometry, orientation, scale, design-state hash and compact system legend.

## Shipyard realization grammar

Shipyard identity remains separate from physical truth. Institutional context may carry construction environment, robotic fabrication/assembly capability, manufacturing processes, material families, structural doctrine, module doctrine, maintenance doctrine, redundancy doctrine, precision-cost tolerance, geometric-complexity tolerance, certification culture and historical lineage.

Culture must not become a hidden physics modifier.

The demonstrated Wayfarer visual experiment established four provisional realization languages from one coarse engineering baseline:

- **ASTERIA** — topology/generative structural language, branching load paths, minimum-mass integration, additive/parametric expression;
- **KELDRIN** — rectilinear trusses, standardized modules, rugged industrial construction, explicit serviceability;
- **SHIKARI** — consolidated structural architecture, low part count, integrated composite expression, performance/mass emphasis;
- **TASCHEN** — redundant framing, accessible machinery, modular replacement, expedition/field-repair emphasis.

These are provisional visual/manufacturing grammars, not engineering claims about unmodeled structure.

## Revised phased work plan

### R0 — Visualization authority contract

Freeze the distinction among governed engineering state, semantic GLB, deterministic reference render and non-authoritative AI realization. Preserve the no-back-propagation rule.

### R1 — Semantic Geometry Contract

Add stable machine-readable component/system/function/provenance/status identity to generated engineering geometry. Design the schema before freezing enumerations. Preserve current geometry and engineering behavior while adding semantics.

### R2 — Minimum Spatial Validation

Define deterministic geometry-sensitive checks needed before a GLB is suitable for downstream realization. Initial candidates: bounding validity, admitted containment, collision, declared clearance, thrust-axis consistency, plume keep-out, radiator deployment interference, docking access, service-access envelopes, major attachment consistency and explicit preservation of OPEN spatial items.

No missing physical model may be invented merely to complete this gate.

### R3 — Deterministic Reference Renderer

Produce reproducible standard reference views from semantic GLB. Rendering should remain lightweight and Pixel/browser compatible where practical.

### R4 — Shipyard Realization Grammar Contract

Represent manufacturing/engineering visual language as structured institutional context rather than free aesthetic adjectives. Generate downstream realization instructions from governed geometry plus yard grammar.

### R5 — Wayfarer End-to-End Visual Acceptance

Run one governed Wayfarer state through semantic geometry, spatial validation, deterministic GLB, interactive browser inspection, deterministic reference views and the four provisional shipyard realization grammars. Generated imagery remains non-authoritative.

### R6 — Restrained Interactive Inspection

Prioritize component selection, semantic labels, system filtering, hide/show, translucent envelopes, keep-outs, center of mass, thrust axis, structural graph, OPEN-state display and candidate comparison. Deprioritize cinematic shaders, fake wear, greebles and decorative rendering.

### R7 — Return effort to generative engineering

After visual pipeline acceptance, freeze visualization unless a demonstrated deficiency requires more work. Concentrate Shipyard development on architecture representation/search, model adequacy, uncertainty, executable coupled discipline graphs, materials/fabrication, construction environment, robotics, manufacturing feasibility, robustness and Pareto diversity.

## Geometry admission rule

> A geometric detail must justify its existence by engineering, interaction, simulation or conditioning value. Visual richness alone is insufficient.

## AI realization rule

> AI realization may add visual complexity only within freedoms left unconstrained by the governed engineering model. Generated detail remains non-authoritative unless separately admitted through engineering process.

## Relationship to existing governed synthesis

This reframe preserves the existing separation among engineering dependency graph, physical topology graph and spatial state/fields. It preserves Design State authority, OPEN handling, deterministic provenance, manufacturing adapters, discipline contracts and future architecture/MDAO work.

It changes the visualization endpoint: increasing engineering evidence may justify richer geometry, but presentation-quality geometry is no longer a required Shipyard destination.

## Classification

```text
ENGINEERING_RESEARCH
NON_CANON
NON_PRODUCTION
NO_FLIGHT_DYNAMICS_AUTHORITY
NO_STRUCTURAL_QUALIFICATION
AI_VISUAL_REALIZATION_NON_AUTHORITATIVE
```
