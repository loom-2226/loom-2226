# LOOM 2226 — Manufacturing Capability and Functional Regions v0.1

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION

## Purpose

Extend the Computational Shipyard without replacing its existing deterministic engineering substrate.

The existing `IndustrialContext` remains the coarse governed source for technology, material availability, manufacturing capability, suppliers, prohibitions, economics, and provenance. This v0.1 layer adds a narrower representation for future fabrication capabilities and for multifunctional ship regions.

It does **not** add new physics, a material-performance model, a manufacturing solver, structural qualification, flight-dynamics authority, canon changes, or production shipclasses.

## Why this exists

A 2226 shipyard should not be forced to think exclusively in a 2026 assembly ontology of discrete brackets, tanks, pipes, buses, manifolds, and supports.

The research direction motivating this layer is co-design of geometry, material system, manufacturing process, sensing, inspection, repair, thermal routing, fluid routing, electrical routing, and load path. A future ship region may perform several of those functions simultaneously.

The representation must nevertheless preserve LOOM's engineering firewall. Describing a multifunctional region does not prove that it can exist or satisfy a requirement.

## Continuity rule

This layer wraps existing authority rather than creating a parallel engineering system:

`IndustrialContext`
→ `ManufacturingCapabilityContext`
→ `FunctionalRegion` proposal/decomposition
→ existing or future governed deterministic synthesis/evaluation

`ManufacturingCapabilityContext.industrial_context_hash` is mandatory so a manufacturing context cannot silently detach itself from the existing governed industrial context.

## ManufacturingCapabilityContext

A manufacturing context records explicit capability facts only.

Material systems carry:
- material-system ID;
- `AVAILABLE`, `UNAVAILABLE`, or `OPEN` status;
- manufacturing class;
- feedstock classes;
- provenance.

Processes carry:
- process ID and status;
- manufacturing class;
- maximum build envelope where known;
- minimum feature scale where known;
- explicit support / non-support / OPEN for material grading, multimaterial fabrication, embedded channels, embedded sensing, and in-situ heat treatment;
- inspection resolution where known;
- repair processes;
- certified process families;
- explicit precision-cost class;
- provenance.

Manufacturing classes are deliberately coarse:
- `BULK_CONSTRUCTION`
- `PRECISION_STRUCTURAL`
- `EXOTIC_FUNCTIONAL`

They are taxonomy, not performance multipliers.

There is no rule such as `PRECISION_STRUCTURAL = stronger`, `EXOTIC_FUNCTIONAL = lighter`, or `BULK_CONSTRUCTION = cheap`. Any such relationship requires a governed model or explicit data.

## FunctionalRegion

A functional region is a design decomposition object, not a qualified part.

It can express:
- required functions;
- mechanical/load interfaces;
- thermal interfaces;
- fluid interfaces;
- electrical interfaces;
- pressure-boundary role;
- candidate governed material-system IDs;
- candidate governed manufacturing-process IDs;
- repairability requirement;
- inspection requirement;
- replaceable interfaces;
- embedded sensing requirement;
- provenance.

Example conceptually:

`AFT-MULTIFUNCTION-001`
may be required to carry primary thrust load, support remass tanks, route coolant, and route power while exposing explicit interfaces to the thrust frame, tank cluster, coolant loop, and power bus.

That statement does not imply that one printed lattice can actually satisfy those obligations. Deterministic engineering must decide that later.

## OPEN behavior

A region may reference a material system or process whose governed status is `OPEN`.

This is intentional. The object is a candidate/decomposition record and may express an experiment involving an unresolved capability.

The OPEN status is preserved exactly. This layer contains no mechanism that promotes it to AVAILABLE or converts it into engineering PASS.

Unknown material-system or process IDs fail closed.

## Precision-cost rule

Geometric complexity and manufacturing cost must not be conflated.

LOOM may eventually model a future in which complex geometry is relatively cheap while purity, defect control, inspection resolution, process certification, dopants, functional microstructure, or other precision requirements remain expensive.

v0.1 therefore stores `precision_cost_class` as explicit governed data. It does not derive cost from geometry or manufacturing class.

## Authority firewall

`ManufacturingCapabilityContext.authority_status = MANUFACTURING_CONTEXT_ONLY`

`FunctionalRegion.authority_status = FUNCTIONAL_DECOMPOSITION_ONLY`

Neither object may claim:
- physical PASS/FAIL;
- structural qualification;
- thermal qualification;
- mass or inertia authority;
- flight-dynamics authority;
- requirement closure;
- canon authority;
- production shipclass authority.

Authority escalation fails closed.

## Relationship to Wayfarer

No current Wayfarer solver, adapter, evaluator, candidate representation, mutation executor, evidence package, or SOL/Critic contract is replaced or modified by v0.1.

The current Wayfarer vertical slice remains:

existing solver
→ `CandidateDesign`
→ proposal
→ admitted mutation executor
→ `CandidateDesign`
→ existing deterministic Wayfarer evaluation
→ evidence
→ architectural review / Critic

A future experiment may attach one or more `FunctionalRegion` records to a proposal as research context. That future integration must not bypass the existing deterministic evaluation chain.

## Next research step

After this contract passes regression, the next intended experiment is the first real model-permutation Designer ↔ SOL study using the same deterministic Wayfarer backend. Models may reason over manufacturing capability and functional-region context, but they still may propose only admitted mutations and may not claim engineering authority.
