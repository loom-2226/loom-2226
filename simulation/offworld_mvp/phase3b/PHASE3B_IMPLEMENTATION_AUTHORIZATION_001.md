# Phase 3B Implementation Authorization 001

**Status:** AUTHORIZED / PRE-CONTRACT / SINGLE-AUTHORITY
**Scope:** Offworld MVP Phase 3B
**Authorization date:** 2026-10-04
**Authorizer:** project owner

## Decision

Phase 3B implementation authority is granted for the **executable state kernel and deterministic validation fixtures only**.

Full agent-engine implementation remains gated.

## Authorized work

This authorization permits implementation and deterministic testing of:

1. Phase 3B state objects and schemas;
2. identity, context and economic-node semantics;
3. accounts, transactions, commitments and project cash;
4. project, WIP, exploration-WIP, knowledge-asset and productive-asset state;
5. location-neutral FixedCapitalFormationEvent state and aggregation;
6. reference-versus-realized Earth accounting interfaces needed by the kernel;
7. event/transition processing and causal lineage;
8. conservation and accounting invariants;
9. deterministic keyed replay infrastructure needed by validation;
10. the required four-route capital-formation trace fixtures:
   - Earth -> offworld;
   - offworld local -> local;
   - offworld -> Earth supplier -> offworld asset;
   - offworld node A -> offworld node B;
11. deterministic ENCLAVE versus SETTLEMENT recursive-economy validation fixtures;
12. tests and diagnostic outputs required to falsify or verify the above mechanics.

## Explicitly not authorized

This authorization does **not** permit:

- full autonomous agent-engine implementation;
- LLM/runtime-agent decision authority;
- production simulation claims;
- promotion of PRE-CONTRACT material to Authority Contract v1 governed/qualified status;
- invention of missing empirical values;
- selecting a participating Earth economy by legacy default;
- treating Earth INVESTMENT_REAL_PROXY / GFCF as cash;
- replacing empirical UNKNOWN with scenario truth;
- silently changing the finalized financing/recursive-FCF semantics to make tests pass.

Deterministic scripted policies may be used only as validation drivers for the authorized kernel. They are not the full agent engine.

## Governing design

Implementation must conform to:

- PHASE3B_FINANCING_RECURSIVE_FCF_FINALIZED_CANDIDATE_0_1.md;
- PHASE3B_STATE_MODEL_WORKING_CANDIDATE_0_1.md as subsequently refined;
- PHASE3B_1_CONTEXT_IDENTITY_MODEL_CANDIDATE_0_1.md;
- PHASE3B_2_STATE_OBJECT_SCHEMAS_CANDIDATE_0_1.md;
- PHASE3B_3_TRANSITION_EVENT_MODEL_CANDIDATE_0_1.md;
- PHASE3B_4_CONSERVATION_ACCOUNTING_MODEL_CANDIDATE_0_1.md;
- MVP_ABSTRACTION_REGISTER_CANDIDATE_0_1.md as subsequently refined;
- OFFWORLD_MVP_GUIDING_FRD.md.

Where those artifacts conflict, implementation must stop and surface the conflict rather than choosing a convenient interpretation.

## Exit condition

This authorization does not itself close Phase 3B.

Before requesting authority for the full agent engine, the executable kernel must demonstrate deterministic replay and pass the authorized conservation, locality, reference/realized separation, information-firewall, four-route and recursive-economy validation fixtures.

Any failure is evidence about the design and must not be repaired by weakening an invariant without a new governed design decision.
