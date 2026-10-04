# BUILD 6A IMPLEMENTATION AUTHORIZATION 001 — TEMPORAL MULTI-PROJECT TEST 001A

Status: AUTHORIZED / FRD-CONSISTENT EXPANSION / STRUCTURAL ONLY  
Parent frozen baseline: `build5-final-v1-2026-10-05` -> `014106ac05f762c29745271137d0a0389b6276b1`  
Branch: `offworld-mvp-build6a-temporal-multiproject`

## Purpose

Earn the first post-Build-5 expansion gate by proving that multiple candidate projects can
compete for one finite capital pool while authorized actions consume real elapsed simulation
time and complete asynchronously.

Build 6A is infrastructure/semantics, not a Solar-System forecast.

It SHALL NOT yet instantiate Moon, Mars, Ceres or Bennu, add pre-feasibility/feasibility
maturity, introduce stochastic schedule risk, add multiple economies, or alter the guiding
FRD.

## Governing FRD basis

Build 6A is bounded by existing FRD requirements:

- Section 18 capital origin / commitment / disbursement;
- Section 20 explicit project lifecycle;
- Section 27 causal events with explicit time;
- Section 28 deterministic keyed randomness;
- Section 30 conservation and epistemic invariants;
- Section 37 expansion gate `multiple projects`;
- Section 39 deterministic scheduler with explicit sub-period events and stable same-time
  ordering;
- Section 45 underwriting `LEAD_TIME` standing.

No FRD text mutation is authorized.

## Reuse-first rule

Build 6A MUST reuse the frozen Build 5 kernel, accounting, transaction ledger, scheduler,
decision snapshots, policy isolation, project registry/lifecycle, Agent accounts and replay
machinery.

No second ledger, second scheduler, second project-state model, second Agent architecture or
parallel financing system is authorized.

## New bounded temporal seam

A minimal typed time-bearing project activity representation may be added.

Required semantics:

```
AUTHORIZED
    -> WAITING_PREREQUISITES or WAITING_WINDOW when applicable
    -> ACTIVE
    -> COMPLETED | CANCELED | FAILED
```

For Test 001A only, fixed authored deterministic timestamps/durations are permitted.

At minimum an activity records:

- stable activity identity;
- project identity;
- activity type;
- authorizing Agent;
- authorization time;
- earliest admissible start;
- optional deterministic opportunity-window identity;
- actual start;
- deterministic planned completion;
- capital commitment amount;
- result type / completion lineage;
- status.

Authorization, start, completion and result admission are distinct facts.

An activity result SHALL NOT be visible to an Agent before completion/admission.

## Finite shared-capital seam

Test 001A SHALL contain at least two projects competing for the same sponsor capital pool.

The same money may not be committed simultaneously to two activities.

For the first structural slice:

- committed capital may be reserved at activity authorization;
- reservation reduces capital available for later project decisions;
- reservation is not itself expenditure or destruction of cash;
- explicit completion/cancellation settlement must reconcile the reservation;
- already-spent cash, if any, may not be resurrected by cancellation.

No bank, credit market, portfolio optimizer, dynamic interest rate, endogenous price or
additional financier policy is authorized.

## Multi-project decision seam

The existing sponsor/operator Agent may be reused across multiple projects.

One bounded Test-only selection policy may choose among formally proposed project activities
using only admitted project/activity facts and available sponsor capital.

For Test 001A the policy MUST be deliberately simple and non-empirical. It may rank candidates
only by an explicit authored priority and then by stable project identity, subject to:

- required inputs KNOWN;
- project eligible state;
- no conflicting active activity;
- sufficient uncommitted sponsor capital;
- valid opportunity timing.

This is `TEST_ONLY / NOT_POLICY_BASELINE / NOT_EMPIRICALLY_VALIDATED`.

No hidden resource truth, future completion result, future observation, or unadmitted project
state may influence selection.

## Deterministic event semantics

Time-bearing activity execution SHALL occur through the existing scheduled runtime.

The qualification must distinguish at least:

1. authorization/commitment;
2. activity start;
3. activity completion;
4. completion result/admission;
5. later decision opportunity.

Same-time ordering must be stable and explicit and must not depend on:

- Python dictionary/set ordering;
- database row order;
- thread timing;
- event insertion order where events are otherwise semantically unrelated.

No stochastic duration is authorized in Build 6A.

## Canonical structural fixture

At least three candidate projects SHALL exist to prove more than a binary special case.

The fixture should include:

- one project whose affordable activity starts immediately and completes later;
- one project that is otherwise eligible but cannot be authorized while capital is committed
  elsewhere;
- one project with an admissible future opportunity window, proving readiness is not the same
  as start.

After the first activity completes/releases or settles its commitment, a later decision epoch
must be able to authorize a previously capital-blocked project.

The fixture uses generic project IDs only. No Moon/Mars/Ceres/Bennu semantics are authorized
here.

## Forbidden

Build 6A does NOT authorize:

- named Solar targets;
- new Solar evidence;
- grade/tonnage/resource-assessment machinery;
- scoping/PFS/FS study maturity;
- stochastic delays or Monte Carlo schedule risk;
- launch-window calculation from SPICE/trajectory solvers;
- multiple Earth economies;
- new Agent classes;
- endogenous technology;
- detailed workforce/equipment/fleet capacity;
- detailed mine engineering;
- market-price endogeneity;
- autonomous portfolio optimization;
- FRD modification.

## Acceptance

Test 001A passes only if qualification demonstrates:

1. at least three projects coexist on one persistent kernel/world state;
2. at least two project activities draw against one finite sponsor capital pool;
3. capital committed to one active activity is unavailable to another;
4. commitment reservation and cash remain reconciled and are not double-counted as spend;
5. authorization, start, completion and information/result admission occur at distinct
   scheduler-valid moments where configured;
6. future completion/result state cannot influence the authorizing decision;
7. a future opportunity window can hold an otherwise-ready activity in a waiting state;
8. a completed/released commitment changes the later opportunity set without retroactive
   effects;
9. projects progress concurrently/asynchronously rather than through a single-project loop;
10. same-time events have deterministic stable ordering;
11. reordered candidate registration does not change the governed result;
12. deterministic replay remains exact;
13. direct/tampered mutation of activity or committed-capital state is detected or blocked
    under the governed runtime boundary;
14. existing Build 5 accounting, epistemic and conservation invariants remain satisfied;
15. ODD/schema reconciliation is updated for any executable state added;
16. focused unit/functional/hostile tests pass;
17. full governed regression passes before closure;
18. the guiding FRD is byte-unchanged relative to the Build 5 frozen baseline.

## Closure standing

Passing Build 6A earns only:

- deterministic time-bearing project activities;
- shared finite-capital competition across multiple projects;
- the FRD `multiple projects` expansion gate at structural standing.

It does not authorize Build 6B staged resource/project-study maturity or Build 6C
Moon/Mars/Ceres/Bennu execution. Those require separate authorization.
