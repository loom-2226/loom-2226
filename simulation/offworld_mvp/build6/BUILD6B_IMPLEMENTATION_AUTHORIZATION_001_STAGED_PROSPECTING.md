# BUILD 6B IMPLEMENTATION AUTHORIZATION 001 — STAGED PROSPECTING / PROJECT-STUDY MATURITY

Status: AUTHORIZED / FRD-CONSISTENT ELABORATION / STRUCTURAL ONLY

Parent frozen baseline:
`build6a-final-v1-2026-10-05`
-> `3f1e001fe28a9ee2f08f831f14362177fc9fb8a8`

Branch:
`offworld-mvp-build6b-staged-prospecting`

## Purpose

Earn the next bounded Offworld seam after Build 6A:

> project candidates may spend real finite capital on staged information acquisition and
> project studies, carry unfinished study work through elapsed time, convert completed useful
> work into knowledge, and advance through explicit evidence/study maturity only after an
> Agent reviews the admitted result.

Build 6B remains generic. It SHALL NOT instantiate Moon, Mars, Ceres or Bennu.

## Governing FRD basis

Build 6B elaborates existing FRD provisions for:

- exploration / observation;
- Project lifecycle `PROPOSED -> EXPLORING -> DEVELOPMENT`;
- explicit capital commitment and expenditure;
- knowledge assets and exploration WIP;
- deterministic scheduler-owned elapsed time;
- Agent-visible information separated from hidden WORLD_SIM truth;
- multiple-project competition earned by Build 6A.

No FRD text mutation is authorized.

## Reuse-first rule

Build 6B MUST reuse:

- Build 6A `ProjectActivity`, finite-capital reservation and scheduler semantics;
- the existing transaction ledger;
- existing `TxPurpose.EXPLORATION`;
- existing `AssetKind.EXPLORATION_WIP` and `AssetKind.KNOWLEDGE`;
- existing sponsor/account/project state;
- existing isolated policy worker and DecisionSnapshot architecture;
- existing project `ABANDONED` transition;
- existing replay/tamper/conservation machinery.

No second project lifecycle, accounting ledger, scheduler, Agent hierarchy or knowledge store
is authorized.

## Orthogonal study maturity

Build 6B may add a typed project-study maturity state separate from Project lifecycle.

Required ordered structural stages:

```
SCREENED
REMOTE_CHARACTERIZED
SURFACE_OR_SAMPLE_CHARACTERIZED
RESOURCE_ASSESSMENT
CONCEPT_SCOPING
PREFEASIBILITY
FEASIBILITY
DEVELOPMENT_READY
```

These are research-informed structural labels, not legal adoption of JORC/CIM/CRIRSCO
reporting standards.

A Project may remain `EXPLORING` while its study maturity advances.

`DEVELOPMENT_READY` does not itself transition the Project into `DEVELOPMENT`.

## Study plans and spending

A study/prospecting activity SHALL declare:

- project;
- required current maturity;
- maturity potentially earned on successful review;
- activity/result type;
- deterministic duration;
- authorized capital amount;
- supplier;
- result standing;
- lineage.

At activity start, the authorized amount may be spent through the existing ledger.

For the structural fixture the sponsor may fund the project directly:

`SPONSOR_FUNDS -> PROJECT_CASH -> SUPPLIER`

using existing `OTHER_INVESTMENT` then `EXPLORATION` purposes.

The expenditure MUST:

- reduce sponsor cash;
- not be refunded merely because the study later disappoints;
- create `EXPLORATION_WIP`;
- remain attributable to the project/activity.

Once spent, the same amount is no longer also counted as an unspent activity reservation.

## Completion / knowledge

On deterministic completion:

- useful completed study work may resolve `EXPLORATION_WIP -> KNOWLEDGE`;
- failed/unusable work may be written off;
- an explicit study result is created;
- the Agent may not see that result before admission.

Study result standing for Test 001A may be limited to:

- `SUPPORTS_ADVANCE`;
- `INSUFFICIENT`;
- `NEGATIVE`.

These are Test-only structural outcomes, not calibrated geology or economics.

## Sponsor study review

One bounded Test-only sponsor review policy may consume only admitted:

- project lifecycle state;
- current study maturity;
- completed study/result identity;
- study result standing;
- declared next maturity.

Structural rule:

- `SUPPORTS_ADVANCE -> ADVANCE`;
- `INSUFFICIENT -> DEFER`;
- `NEGATIVE -> ABANDON`;
- UNKNOWN required input -> `BLOCKED_UNKNOWN` before worker execution.

Standing:

`TEST_ONLY / NOT_POLICY_BASELINE / NOT_EMPIRICALLY_VALIDATED`.

No hidden resource truth, future study result, undeclared project economics or Technology
Timeline state may enter the policy.

## Execution boundary

SYSTEM execution must independently verify:

- exact decision/request/activity/study lineage;
- sponsor identity/capability;
- project currently eligible;
- activity completed;
- result admitted to the deciding Agent;
- maturity equals the study plan's required predecessor;
- no duplicate review;
- only the plan's declared next maturity may be earned.

`ABANDON` must reuse the existing governed Project transition.

No direct maturity jump is authorized.

## Canonical structural fixture

At least three generic projects SHALL compete under one sponsor.

The canonical fixture must demonstrate:

1. one project progresses through multiple consecutive study stages;
2. one project receives a negative admitted result and is abandoned with sunk spending;
3. one otherwise-valid project is temporarily deferred because finite capital was spent or
   remains committed elsewhere;
4. at least one study result is insufficient and therefore does not advance maturity;
5. later capital availability permits a previously deferred project to proceed;
6. study actions execute asynchronously and results arrive only after completion.

The fixture remains on generic Build-6A-style targets.

## Forbidden

Build 6B does NOT authorize:

- named Solar bodies;
- multiple bodies/resources;
- empirical resource inventories;
- JORC/CIM/CRIRSCO legal standing;
- calibrated PFS/FS costs or durations;
- endogenous value-of-information optimization;
- stochastic schedule delays;
- SPICE-derived launch windows;
- multiple economies;
- development construction;
- mine engineering;
- new Agent classes;
- endogenous technology or markets;
- FRD modification.

## Acceptance

Build 6B passes only if:

1. study maturity is orthogonal to Project lifecycle;
2. spending is real ledger expenditure, not mere reservation;
3. sponsor cash falls exactly by study spend;
4. spent capital cannot be double-used or refunded on negative result;
5. unfinished study is represented as exploration WIP;
6. completed useful study may become knowledge;
7. results remain unavailable before completion/admission;
8. review policy has no hidden-truth/future-result access;
9. SUPPORTS_ADVANCE advances exactly one declared maturity edge;
10. INSUFFICIENT does not advance;
11. NEGATIVE can abandon through existing lifecycle transition;
12. direct/skipped maturity advancement is blocked;
13. duplicate review is blocked;
14. multi-project capital competition remains causal;
15. deterministic replay remains exact;
16. tampering remains detectable;
17. ODD/schema reconciliation is complete;
18. focused/hostile tests pass;
19. full governed regression passes;
20. guiding FRD remains byte-unchanged.

## Closure standing

Passing Build 6B earns only staged generic prospecting / project-study maturity and real
study expenditure.

It does not authorize named Moon/Mars/Ceres/Bennu execution. That remains a separately
governed Build 6C expansion.
