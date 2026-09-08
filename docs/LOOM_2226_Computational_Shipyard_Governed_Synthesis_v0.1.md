# LOOM 2226 — Computational Shipyard Governed Synthesis v0.1

Status: ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION

## Architectural invariant

Computational Shipyard is a governed, hierarchical multidisciplinary design-synthesis system. It searches system architectures and physical topologies, evaluates coupled engineering disciplines at declared fidelity, explores nondominated configurations under manufacturing and institutional constraints, and compiles admitted design states into deterministic geometry.

The governed design state and its evidence are authoritative within their admitted scope. Geometry and visualization are derived artifacts.

**Geometry does not own the ship.**

Deleting a mesh or viewer must not delete engineering authority. A derived visual artifact must be reproducible from the governed state that produced it.

## v0.1 implemented stack

This research slice implements the first executable path from the existing deterministic Wayfarer `CandidateDesign` into a richer synthesized mesh:

`CandidateDesign -> DesignState -> PhysicalTopology -> PackagingState -> StructuralGraph -> GeometryPackage -> offline WebGL viewer`

It deliberately reuses the existing LOOM physical-design substrate. It does not create a parallel ship type or new physics solver.

### DesignState

`DesignState` projects active component instances and point masses from the existing candidate into explicit design nodes with positions and provenance. It records a hash of the source candidate snapshot.

The coupled engineering dependency graph is **OPEN in v0.1**. No fake MDAO graph is manufactured simply to make the architecture look complete.

Authority: `DESIGN_STATE_EVIDENCE_ONLY`.

### PhysicalTopology

`PhysicalTopology` is a separate representation from engineering dependency. v0.1 creates a deterministic coarse synthesis backbone at occupied x stations and attaches admitted source nodes to that backbone.

These edges are explicitly labelled `SYNTHESIS_BACKBONE_HYPOTHESIS` or `SYNTHESIS_ATTACHMENT_HYPOTHESIS`.

They are **not validated load paths** and do not imply structural adequacy.

Authority: `TOPOLOGY_HYPOTHESIS_ONLY`.

### PackagingState

Packaging preserves only admitted component geometry as spatial envelopes. Existing point masses do not silently acquire volume; each remains an OPEN item such as `NO_ADMITTED_VOLUME::<source>`.

Authority: `PACKAGING_HYPOTHESIS_ONLY`.

### StructuralGraph

The topology graph is converted into a coarse member network so that physical connectivity can be visualized and later refined.

The member radii in v0.1 are explicit synthesis/visualization parameters (`0.18 m` backbone and `0.10 m` attachment), not strength-derived sizing.

Structural qualification is hard-coded and validated as:

`NOT_STRUCTURALLY_QUALIFIED`

Authority: `STRUCTURAL_HYPOTHESIS_ONLY`.

### GeometryPackage

The geometry compiler converts admitted packaging envelopes, coarse structural members, and source nodes into deterministic triangle meshes. The browser receives vertices and triangle indices; it does not invent geometry.

Authority: `DERIVED_GEOMETRY_ONLY`.

## Three representations

The mature system keeps at least three representations distinct:

1. **Engineering dependency graph** — what depends mathematically or causally on what. v0.1 remains OPEN.
2. **Physical topology graph** — what is proposed to connect to what spatially or functionally.
3. **Spatial state / fields** — positions, envelopes, routes, keep-outs and eventually admitted continuous fields.

No edge type may silently substitute for another.

## Fidelity and authority

Future discipline results must carry declared fidelity and authority. Low-fidelity estimates may guide search but must not impersonate qualification evidence.

Planned fidelity bands include architecture estimate, configuration analysis, structural synthesis and later qualification-grade analysis. These names are architecture direction, not current qualification states.

## Manufacturing integration

Existing `manufacturing_functional_regions.py` remains the basis for explicit manufacturing capability and functional-region contracts. v0.1 does not yet use manufacturing capability to alter the synthesized topology. That is a next-layer integration, not a hidden bonus.

Manufacturing capability must constrain permitted design operations and geometry search space through governed adapters. It must never become a magic numeric bonus such as “yard X gets 20% stronger structures.”

## Designer / SOL integration

Designer and SOL remain supervisory agents around deterministic engineering machinery.

Designer may propose architecture/topology/search experiments. Deterministic synthesis and discipline evaluators produce candidates and evidence. SOL/Critic may critique architecture, maintainability, evidence gaps and institutional fit, but may not manufacture physical PASS states or close OPEN evidence.

## OpenMDAO position

LOOM adopts the **pattern** of replaceable coupled discipline models and hierarchical multidisciplinary optimization. OpenMDAO is not a required Pixel dependency in v0.1.

Discipline contracts should be independently callable first. A future OpenMDAO adapter may orchestrate those same contracts without changing their engineering semantics or evidence provenance.

## What v0.1 proves

- the existing Wayfarer candidate can become a governed DesignState;
- engineering state, topology and geometry can remain separate;
- missing volumes remain OPEN rather than being guessed;
- a physical topology hypothesis can compile into a visible structural scaffold;
- the scaffold can be rendered on the same offline Android/browser path;
- derived geometry remains non-canon and non-qualified.

## What v0.1 does not prove

- structural adequacy;
- load paths from FEA;
- thermal or radiation fields;
- maintenance clearance;
- pressure-vessel design;
- manufacturing feasibility;
- MDAO convergence;
- material optimization;
- flight inertia qualification;
- canon or production shipclass changes.

## Next implementation layers

1. typed physical interfaces and adjacency requirements on functional regions;
2. admitted packaging volumes for currently point-mass-only systems;
3. route and access constraints;
4. manufacturing-capability gating of topology and geometry operations;
5. coarse discipline interfaces with declared fidelity;
6. Pareto architecture/configuration search;
7. structural load cases and member sizing once admitted analysis exists;
8. topology refinement and graded material fields only after constitutive/manufacturing support exists.

The purpose of the sequence is to ensure that increasing geometric sophistication corresponds to increasing engineering evidence rather than aesthetic invention.
