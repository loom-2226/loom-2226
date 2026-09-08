# LOOM 2226 Computational Shipyard — Basic Python Continuity v0.1

Status: ENGINEERING_RESEARCH / NON_CANON / NON_PRODUCTION

## Purpose

The Computational Shipyard agent architecture does not replace the existing deterministic physical-design Python. It is an orchestration and proposal layer around that substrate.

The preserved baseline includes, at minimum:

- `qualification/synthesis/physical_design_core.py`
- `qualification/synthesis/physical_design_search.py`
- `qualification/synthesis/wayfarer_s1_solver.py`
- `qualification/synthesis/wayfarer_s1_adapter.py`
- existing Wayfarer synthesis and functional regression tests.

## Continuity rule

Designer output remains `PROPOSAL_ONLY`. A proposal may be converted into a derived candidate only through an admitted mutation executor. The executor must return the existing `CandidateDesign` type rather than inventing a parallel agent-native physical representation.

The derived candidate is then evaluated by the same deterministic engineering functions and search/evaluation machinery already used by the non-agent path.

Therefore the intended chain is:

`BASIC DETERMINISTIC PYTHON -> CandidateDesign -> Designer proposal -> admitted mutation executor -> CandidateDesign -> BASIC DETERMINISTIC PYTHON EVALUATION -> evidence -> Critic/SOL`

The Designer and Critic do not become evaluators.

## Mutation v0.1 boundary

The initial executor admits only:

- `SET_INSTANCE_TRANSLATION`
- `SET_INSTANCE_ACTIVE`

Both operate on existing `PhysicalComponentInstance` records. Unknown targets, unknown operations, malformed JSON payloads, and attempts to smuggle additional fields fail closed.

No operation exists for engineering PASS/FAIL, flight-dynamics authority, canon state, production shipclass state, mass authority, geometry admission, or requirement closure.

## Compatibility requirement

Regression must demonstrate that an executor-produced child candidate can be passed directly to an existing core engineering function without an adapter. v0.1 uses `evaluate_mass_inertia()` as that continuity check.

Later topology, sizing, component replacement, rotation, and multiplicity mutations may be admitted only as typed operations with deterministic validation and corresponding regression against the basic Python substrate.

## Authority

Mutation execution authority is `CANDIDATE_DERIVATION_ONLY`.

It does not establish physical feasibility. It does not confer flight-dynamics authority. It does not mutate canon or production shipclasses.
