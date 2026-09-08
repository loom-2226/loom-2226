# LOOM 2226 — Computational Shipyard Design Ledger v0.1

Status: ENGINEERING RESEARCH / NON-CANON / NON-PRODUCTION

## Purpose

Phase 1 adds persistent design-history evidence around the existing governed synthesis without changing engineering, canon, production, or flight-dynamics authority.

The architecture is:

`Git authority -> deterministic engineering/synthesis -> typed state/evidence -> SQLite design ledger -> derived geometry/viewer`

Git remains authoritative for code, schemas, protocols, qualification logic, and frozen research branches. SQLite is the persistent record of design runs, candidate/state genealogy, declared discipline results, dependency graphs, and derived-artifact hashes.

## Invariants

1. Geometry does not own the ship. The design state and supporting evidence are authoritative within their declared scope; geometry is derived.
2. Every discipline result declares model identity/version, fidelity class, assumptions hash, input hash, result hash, result status, provenance, and authority.
3. Fidelity does not imply authority. A higher-fidelity label cannot grant qualification, canon, production, or flight authority.
4. OPEN dependency edges remain OPEN. They may document expected feedback relationships but cannot be traversed as admitted coupled physics.
5. Admitted dependency cycles fail closed until an explicit coupled-solver/MDAO contract exists.
6. LLM Designer/Critic/SOL outputs remain proposal/critique evidence only and are not promoted by the ledger.
7. The ledger may persist a deterministic PASS only when the underlying deterministic evaluator produced it. It cannot create PASS by interpretation.

## Fidelity classes

- `L0_ANALYTIC`: low-cost analytic/estimate discipline model.
- `L1_DETERMINISTIC_REDUCED_ORDER`: deterministic reduced-order model with explicit assumptions and provenance.
- `L2_HIGHER_FIDELITY`: reserved for later admitted higher-fidelity models.
- `OPEN`: discipline/fidelity not yet admitted.

Wayfarer S1 is recorded as `L1_DETERMINISTIC_REDUCED_ORDER`; this does not alter its existing qualification scope.

## SQLite schema

The v0.1 ledger contains:

- `design_run`: one governed exploration/execution run.
- `design_state`: content-addressed state snapshots and parent relation.
- `discipline_result`: typed, fidelity-tagged deterministic evidence.
- `dependency_graph`: content-addressed engineering/synthesis dependency declaration.
- `derived_artifact`: hashes of derived geometry or later viewers/reports.
- `ledger_meta`: schema/version metadata.

The current Wayfarer Phase 1 fixture persists one run, one state, one S1 discipline result, one dependency graph, and one derived geometry artifact.

## Dependency graph v0.1

Admitted derivation chain:

`MISSION_REQUIREMENTS -> S1_LAYOUT_EVALUATION -> DESIGN_STATE`

`DESIGN_STATE -> PACKAGING`

`DESIGN_STATE -> PHYSICAL_TOPOLOGY -> STRUCTURAL_GRAPH`

`PACKAGING + STRUCTURAL_GRAPH -> GEOMETRY`

Explicit OPEN feedback:

`S1_LAYOUT_EVALUATION -> COUPLED_THERMAL_POWER_PROPULSION -> PACKAGING`

The coupled path is documentation only in v0.1. It is not an MDAO solve.

## What this does not do

- no architecture search;
- no Pareto/NSGA-II optimization;
- no OpenMDAO dependency;
- no thermal/power/propulsion coupled solve;
- no structural qualification;
- no promotion of the 15 Wayfarer OPEN point-mass volumes;
- no canon or production mutation;
- no flight-dynamics authority.

Those remain later work.
