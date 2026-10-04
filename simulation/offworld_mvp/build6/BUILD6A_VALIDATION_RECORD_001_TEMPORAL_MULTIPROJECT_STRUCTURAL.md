# BUILD 6A VALIDATION RECORD 001 — TEMPORAL MULTI-PROJECT STRUCTURAL

Status: **STRUCTURAL PASS / FRD-CONSISTENT EXPANSION / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED**

## Authority

Frozen Build 5 parent tag: build5-final-v1-2026-10-05  
Parent commit: 014106ac05f762c29745271137d0a0389b6276b1  
Authorization commit: 1900197525c6c12605aef5d6cef0bc9574e0467f  
Executable/ODD qualification candidate: 5c3b4c8919aaab719606bcefdcd9c9bccf1f76b3  
Branch: offworld-mvp-build6a-temporal-multiproject

Authorization:
simulation/offworld_mvp/build6/BUILD6A_IMPLEMENTATION_AUTHORIZATION_001_TEMPORAL_MULTIPROJECT_TEST001A.md

The guiding FRD is byte-unchanged relative to the frozen Build 5 tag.

## Purpose

Build 6A earns the first post-Build-5 expansion seam: multiple candidate projects may
coexist and compete for one finite sponsor capital pool while authorized project activities
take explicit deterministic simulation time, may wait for a future opportunity window,
complete asynchronously, and reveal results only after completion/admission.

This is structural infrastructure. It is not a 2026-2041 forecast and does not instantiate
Moon, Mars, Ceres, Bennu or any other named Solar target.

## Result

Test 001A structurally passes.

The new causal seam is:

Agent portfolio decision -> capital reservation -> activity authorization -> optional wait ->
activity start -> elapsed time -> completion -> result admission -> later Agent decision.

The implementation preserves the existing boundary:

Agent decides -> SYSTEM validates/executes -> realized state changes.

No activity policy receives hidden resource truth, future activity result, world random
state, kernel/scheduler access, or unadmitted project state.

## Reused machinery

Build 6A reuses the frozen Build 5 kernel, ScheduledSimulationRuntime, deterministic
scheduler, persistent decision epochs, immutable DecisionSnapshot / isolated worker
architecture, Agent/account/project registries, causal-event/replay provenance machinery,
and existing accounting/conservation/epistemic invariants.

No second scheduler, ledger, Agent hierarchy, financing engine or project lifecycle was
introduced.

## New typed activity state

ProjectActivity supports:

- PROPOSED
- AUTHORIZED
- WAITING_PREREQUISITES
- WAITING_WINDOW
- ACTIVE
- COMPLETED
- CANCELED
- FAILED

Each activity carries stable project/actor identity, activity type, authored priority,
earliest start, deterministic duration, capital commitment, optional opportunity window,
authorization/start/completion timestamps, result type/reference, and authorization lineage.

Authorization, start, completion and information admission are distinct causal transitions.

## Capital reservation semantics

For authorized/waiting/active activity state:

available sponsor capital = sponsor account cash - active activity reservations.

Reservation reduces later decision capacity but is not expenditure, does not transfer or
destroy cash, and releases when an activity completes or is canceled.

The canonical sponsor starts with 100 model-currency units.

## Bounded portfolio policy

Policy: SPONSOR_PORTFOLIO_V1  
Semantic version: 0.1  
Policy version:
SPONSOR_PORTFOLIO_V1:0.1:d525074793f0795afc6f5f3cc5ef2eecbdbe97048555b819dc6eb82c937495aa

Contract SHA-256:
6d371b27928cae41c0b165e9ba3f11084a65ce5e78d4f010a6815e9994418720

Standing: TEST_ONLY / NOT_POLICY_BASELINE / NOT_EMPIRICALLY_VALIDATED.

The policy sees only admitted available capital, project identity/status, activity status,
commitment, authored priority and window-validity facts. It requires PRIVATE_SPONSOR,
RETURN objective and AUTHORIZE_ACTIVITY capability.

Eligible affordable candidates are ordered by:

priority -> stable project id -> stable activity id.

There is no hidden resource input and no empirical behavioral threshold.

## Canonical structural fixture

All projects remain on the same generic offworld target.

| Activity | Project | Priority | Commitment | Earliest | Duration | Window |
|---|---|---:|---:|---:|---:|---|
| ACT-A | P-A | 1 | 60 | 1 | 2 | none |
| ACT-B | P-B | 3 | 60 | 1 | 4 | none |
| ACT-C | P-C | 2 | 30 | 1 | 1 | 4.0-4.5 |

Canonical history:

- t=1: ACT-A authorized for 60 and starts; available capital = 40.
- t=1.1: ACT-C authorized for 30 but enters WAITING_WINDOW; available = 10.
- t=1.2: ACT-B is DEFER / INSUFFICIENT_AVAILABLE_CAPITAL.
- while ACT-A is ACTIVE, no ACT-A result exists in sponsor information.
- t=3: ACT-A completes and its 60 reservation releases.
- t=3.05: INFO:ACT-A:RESULT is admitted.
- available capital is now 70 because ACT-C still reserves 30.
- t=3.1: ACT-B is authorized for 60 and starts; available = 10.
- t=4: ACT-C starts inside its window while ACT-B remains ACTIVE.
- t=5 / 5.05: ACT-C completes / result admitted; available = 40.
- t=7.1 / 7.15: ACT-B completes / result admitted; available = 100.

Terminal state:

- ACT-A = COMPLETED
- ACT-B = COMPLETED
- ACT-C = COMPLETED
- sponsor cash = 100
- uncommitted sponsor capital = 100
- activity-fixture economic transactions = 0
- all three result references admitted
- persistent decision epochs = 10

Zero transactions is intentional: Build 6A qualifies reservation and elapsed-time semantics,
not prospecting/study expenditure.

## Opportunity-window and information semantics

Authorization does not imply immediate activity start. The executor rejects a start outside
the declared window.

Build 6A does not compute windows from ephemerides or trajectory mechanics; Test 001A uses an
authored deterministic window to prove the temporal interface.

Completion and information admission are separate. A result cannot be admitted before
completion.

## Cancellation semantics

The hostile cancellation case proves that canceling an authorized but unspent activity
releases its reservation, does not increase sponsor cash, and emits no synthetic financial
transaction.

Actual sunk prospecting/study expenditure is not yet modeled.

## Deterministic ordering and replay

Equal-time events retain the existing scheduler order key, not insertion order. Reversing
insertion of evt-a / evt-z still executes evt-a -> evt-z.

The complete canonical multi-epoch history is executed twice with identical epoch/result
fingerprints and terminal persistent-state fingerprint.

## Hostile / focused coverage

Eight Build 6A cases verify:

1. canonical three-project asynchronous history, finite capital and replay;
2. candidate registration/order does not change stable project selection;
3. required UNKNOWN input gives BLOCKED_UNKNOWN before worker execution;
4. start before an authored opportunity window is rejected;
5. cancellation releases reservation without creating cash/transactions;
6. raw activity-state mutation is detected by decision-epoch fingerprint;
7. equal-time ordering is stable and insertion-order independent;
8. portfolio policy source passes sandbox/source-safety and stable identity checks.

## Focused qualification

Command:
python3 -m unittest tests.test_odd_schema_drift tests.test_build6a_temporal_multiproject

Result: 10/10 passed in 7.848 s.

Broader scheduler/runtime/firewall regression:

python3 -m unittest tests.test_scheduler tests.test_scheduled_runtime tests.test_policy_firewall tests.test_build5_policy_runner tests.test_build5_decision_epochs tests.test_build5_project_lifecycle tests.test_build5_integrated_qualification tests.test_build6a_temporal_multiproject tests.test_odd_schema_drift

Result: 61/61 passed in 87.851 s; wall time 88.17 s.

## Full governed regression

Command:
python3 -m unittest discover -s tests

Executed on candidate 5c3b4c8919aaab719606bcefdcd9c9bccf1f76b3.

Result:

- 319 tests
- 319 passed
- 0 failures
- 0 errors
- runtime 589.539 s
- wall time 589.89 s

All 311 frozen Build 5 tests remain present and pass. Build 6A adds eight tests.

## Executable provenance

Filesystem source-tree SHA-256:
22be5b0dd41f2772591363fd1adcb25d8bc9827caaaa0b7df9a63ee0b5a130e8

Git-object reconstructed source-tree SHA-256:
22be5b0dd41f2772591363fd1adcb25d8bc9827caaaa0b7df9a63ee0b5a130e8

Standing: GIT_OBJECT_VERIFIED.

## Size / bloat check

Executable offworld_kernel Python LOC:

- frozen Build 5: 10,515
- Build 6A candidate: 11,278
- net: +763 lines (7.26%)

This includes typed activity/portfolio contracts, one bounded policy, worker/runner
integration, generic fixture, guarded execution/invariants and schema registration.
The test module is excluded.

No Build 5 economic engine or policy was forked.

## FRD / ODD standing

Guiding FRD diff from frozen Build 5: 0 lines.

Executable ODD registry: ODD_SCHEMA_REGISTRY_0_17.

Build 6A is therefore an implementation/elaboration of existing FRD temporal, scheduler,
capital and multiple-project requirements, not an FRD expansion.

## Explicitly not earned

Build 6A does not earn:

- named Solar targets;
- multiple bodies/resources;
- multiple economies;
- empirical prospecting cost or lead-time calibration;
- grade/tonnage/resource-assessment state;
- scoping, pre-feasibility or feasibility maturity;
- development-readiness criteria;
- stochastic delays or correlated schedule risk;
- SPICE/trajectory-derived launch windows;
- shared spacecraft/fleet/launch/workforce/equipment/power capacity;
- actual prospecting/study expenditure in this reservation-only fixture;
- autonomous portfolio optimization;
- endogenous technology or prices/demand;
- any empirical forecast claim.

## Conclusion

Build 6A structurally earns deterministic time-bearing multi-project competition under
finite capital.

Committing capital to one project changes the opportunity set for the others; activities may
wait and execute concurrently; information arrives only after completion; later decisions
see the changed opportunity set; and the history remains deterministic, replayable,
epistemically bounded and tamper-detecting.

The appropriate next separately authorized slice is Build 6B: staged prospecting /
resource-assessment / project-study maturity, before named Moon/Mars/Ceres/Bennu portfolio
execution.
