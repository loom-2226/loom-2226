# BUILD 5 COMPACTION AUTHORIZATION R1

Status: AUTHORIZED REFACTOR / ZERO FEATURE EXPANSION  
Parent: `4447f068bb25c06d395708d7991e803c5f5c8830`  
Branch: `offworld-mvp-build5-compaction-r1`

## Purpose

Reduce duplicated Build 5 execution/policy plumbing before any Test 013 feature work.
This pass earns no new simulation behavior, science, policy, transport capability, or
FRD meaning.

## Invariants

The refactor MUST preserve:

- all Test 001-012 observable behavior;
- all request/decision/record schemas and wire payloads;
- policy source files, contracts, policy IDs, semantic versions, and policy hashes;
- deterministic decision IDs and replay behavior;
- accounting and population conservation;
- Test 012 transport dimensions, qualification, departure, transit, and arrival semantics;
- historical Test 011 direct-settlement behavior;
- UNKNOWN gating and hostile-test behavior;
- the guiding FRD unchanged.

## Allowed changes

- consolidate repeated policy-runner metadata/hash plumbing behind internal helpers;
- consolidate repeated public-settlement execution validation behind internal helpers;
- remove dead/redundant internal code where tests prove equivalence;
- add narrowly targeted tests only if needed to prove refactor equivalence.

## Forbidden changes

No new Agent type, policy, economic mechanism, transport mechanic, technology mechanic,
state variable, stochastic behavior, fleet/ship model, R&D model, Earth coupling, or
qualification claim. No edits to frozen Build 4 artifacts or the guiding FRD.

## Acceptance

Compaction passes only if:

1. focused Test 011/012 and schema-drift tests pass;
2. the full governed unit suite passes;
3. policy identities before/after are byte-for-byte identical;
4. Test 012 canonical outputs before/after are behaviorally identical;
5. executable Python LOC does not increase;
6. final diff contains no FRD mutation.

A smaller codebase is desirable; semantic stability is mandatory.
