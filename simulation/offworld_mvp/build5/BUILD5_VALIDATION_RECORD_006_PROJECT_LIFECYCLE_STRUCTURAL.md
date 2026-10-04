# Build 5 Validation Record 006 — Project Development Lifecycle Test 006A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-project-lifecycle`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_006_PROJECT_LIFECYCLE_TEST006A.md`  
**Executable anchor:** `b8df4388b314ce9282aebbdd691ff7c4ec1424cd`

## 1. Result

Build 5 now executes the first governed project-development lifecycle after an autonomous sponsor chooses `DEVELOP`.

The verified causal slice is:

`Sponsor DEVELOP -> project DEVELOPMENT -> explicit staged construction plan -> persistent multi-year ConstructionWIP -> completion resolution -> OPERATING or FAILED`.

Construction remains a SYSTEM process. No new Agent role or company-specific runtime engine was introduced.

## 2. Development-plan contract

Test 006A introduces immutable:

- `ProjectDevelopmentPlan`;
- `DevelopmentStageRecord`;
- `DevelopmentResolutionRecord`;
- `DevelopmentStageOutcome`;
- `DevelopmentResolutionOutcome`.

The development plan identifies:

- project;
- persistent WIP identity;
- commissioned asset identity;
- supplier;
- asset location;
- required development cost;
- explicit stage schedule;
- completion year;
- commissioned capacity;
- source/rationale reference;
- plan version.

The plan validates that the explicit stage schedule reconciles exactly to required cost. There is no hidden default staging rule.

## 3. Existing WIP machinery reused

Test 006A reuses the Build 4 construction machinery rather than creating a parallel lifecycle accounting model.

Existing mechanics used include:

- `ConstructionWIP`;
- staged WIP expenditure;
- fixed-capital-formation records;
- supply/resource-allocation constraints;
- commissioning;
- productive assets;
- A1-A9 auditing;
- deterministic scheduler execution.

The existing `ConstructionWIP` contract is extended with explicit `written_off` state and:

`remaining_wip = accumulated_cost - commissioned - written_off`.

## 4. WIP write-off semantics

A failed development may destroy the remaining economic value of unfinished construction without reversing the cash transaction that originally paid for it.

The executable A5 identity is extended so:

`closing WIP = opening WIP + additions - commissioned - written_off`.

A write-off:

- does not refund project cash;
- does not create a reverse supplier payment;
- does not create a productive asset;
- remains explicitly visible in WIP/audit state.

## 5. Construction stage semantics

Each scheduled stage is indivisible for Test 006A.

A stage may produce:

- `SPENT`;
- `BLOCKED_PROJECT_CASH`;
- `BLOCKED_SUPPLY`.

A stage is spent only when:

- project status is `DEVELOPMENT`;
- year/amount are declared by the immutable development plan;
- stage has not already resolved;
- project cash covers the full stage;
- applicable supplier/resource-allocation capacity covers the full stage.

Blocked stages do not partially invent expenditure.

## 6. Completion semantics

At or after declared completion:

### OPERATING

`DEVELOPMENT -> OPERATING` is permitted only when all declared stages were spent and net WIP equals the full required development cost.

The SYSTEM then commissions the WIP into one PRODUCTIVE asset.

### FAILED

If declared completion arrives without the full construction requirement:

- project becomes `FAILED`;
- existing net construction WIP is explicitly written off;
- no productive asset is created;
- unspent project cash remains cash.

`FAILED` is therefore distinct from sponsor-controlled `ABANDONED`.

## 7. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`a2db979370a1a2a7b7d316aa0f2a775bf9f8c2872bc6433a6db9e3b2f5c911e8`

Git-object reconstructed source-tree SHA-256:

`a2db979370a1a2a7b7d316aa0f2a775bf9f8c2872bc6433a6db9e3b2f5c911e8`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 8. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`

Result at the executable anchor:

**169 tests executed; 169 passed in 44.406 seconds.**

The preceding sponsor/operator baseline contained 157 tests.

Test 006A adds 12 focused lifecycle tests.

## 9. Successful RICH lifecycle

Fixture:

`RICH_PUBLIC_3`

The pre-existing Agent chain produces:

- public observation = `POSITIVE`;
- sponsor belief = `0.50`;
- sponsor `REQUEST_FINANCE`;
- financier `APPROVE`;
- project cash = `60`;
- sponsor `DEVELOP`;
- project status = `DEVELOPMENT`.

The Test 006A development plan then executes:

### Year 6

Declared stage:

`30`

Outcome:

`SPENT`

Transaction:

`tx-000011`

### Year 7

Declared stage:

`30`

Outcome:

`SPENT`

Transaction:

`tx-000014`

### Year 8 completion

Accumulated WIP:

`60`

Commissioned:

`60`

Written off:

`0`

Remaining WIP:

`0`

Resolution:

`OPERATING`

Commissioned asset:

`MINE-P`

Asset kind:

`PRODUCTIVE`

Book value:

`60`

Structural capacity:

`10`

Final project cash:

`0`

Earth supplier cash after exploration plus construction:

`70`

Hidden resource remaining:

`20`

A1 through A9 all pass.

## 10. Financing-origin lineage

Both development fixed-capital-formation records preserve:

- financing origin = `EARTH:X`;
- supplier node = `EARTH:X`;
- asset node = `OFF:T1`.

Thus offworld project cash is not incorrectly treated as the economic origin of the development financing merely because the funds passed through the project's cash account.

## 11. Causal lineage

The successful lifecycle preserves:

`SponsorProjectDecision(DEVELOP)`

-> governed project transition event `PROPOSED -> DEVELOPMENT`

-> year-6 and year-7 construction-stage events

-> completion/commissioning event

-> `OPERATING`.

Construction stages carry the governed DEVELOPMENT transition as a parent.

The completion event carries all stage-event ids as parents.

## 12. Construction-failure lifecycle

Failure fixture uses the same positive information, financing and sponsor DEVELOPMENT path.

The difference is a declared Test-only Earth resource-allocation ceiling in year 7.

### Year 6

Declared stage:

`30`

Outcome:

`SPENT`

### Year 7

Declared stage:

`30`

Available Earth allocation capacity:

`20`

Outcome:

`BLOCKED_SUPPLY`

Reason:

`EARTH_RESOURCE_ALLOCATION_CAPACITY`

No year-7 construction transaction is created.

No partial 20-unit expenditure occurs.

### Year 8 completion

Accumulated WIP:

`30`

Commissioned:

`0`

Written off:

`30`

Remaining WIP:

`0`

Resolution:

`FAILED`

Productive asset:

none

Final project cash:

`30`

Earth supplier cash after exploration plus successful year-6 construction:

`40`

A1 through A9 all pass.

## 13. Write-off is not a cash refund

The failed fixture contains exactly `30` of development CAPEX.

No transaction returns the written-off value from the supplier to the project.

The project therefore retains only the unspent `30` cash.

The spent `30` remains a historical financial expenditure while its unfinished WIP economic value is written off.

## 14. Hidden-world independence

Construction execution does not query hidden resource quantity.

A second success fixture uses:

`NULL_FP_1`

with hidden resource remaining:

`0`.

Because the earlier WORLD_SIM observation is a legitimate false positive, the sponsor/financier chain reaches DEVELOPMENT.

With construction inputs identical to the successful RICH case, the lifecycle result is also identical:

- year 6 = `SPENT 30`;
- year 7 = `SPENT 30`;
- WIP = `60`;
- commission = `60`;
- productive asset book value = `60`;
- capacity = `10`;
- project state = `OPERATING`.

Hidden resource remains:

`0`.

This is intentional.

`OPERATING` in Test 006A means the constructed productive facility exists and has been commissioned. It does not mean the hidden deposit exists or that later extraction will succeed.

## 15. Persistent five-epoch chain

The successful RICH case now runs as one persistent five-epoch history.

### Epoch 1 — publication

Result fingerprint:

`41555bc2a25997ac24028f3a6f29bc6a19de5bdd347a14b603af365fc8cd4efd`

### Epoch 2 — sponsor requests financing

Parent:

Epoch 1 result

Result fingerprint:

`989a8cb1bcc077c6a7dd39ef1eaf19403a12adbb54f8835bdc99504908e5a588`

### Epoch 3 — financier approval/funding

Parent:

Epoch 2 result

Result fingerprint:

`5ca7219dbb93576fb7295f4cada02203feea3d3731f3065582986f72090244f6`

### Epoch 4 — sponsor enters DEVELOPMENT

Parent:

Epoch 3 result

Result fingerprint:

`5ecde79c1289a135c4ac2ecf109ada0ded8c2c5c786d33920cfca1cb58eafff7`

### Epoch 5 — staged construction and completion

Parent:

Epoch 4 result

Result fingerprint:

`eb53758eca60d1c1b45d08e8602e69327541b7d3bc223e583fffb103e1858403`

Every parent link matches the immediately prior epoch result.

## 16. Failure-chain epoch result

The constrained-supply failure case retains the same five-epoch causal form.

Its final construction/lifecycle epoch result fingerprint is:

`dc421c36204378937a4146b3f3009e06f573cc959f25316f1c14987588f00de6`

Final state:

- project = `FAILED`;
- project cash = `30`;
- WIP remaining = `0`;
- WIP written off = `30`;
- productive asset = none.

## 17. Decision-epoch tamper protection

Lifecycle plan and WIP state participate in the persistent methodology fingerprint.

Hostile tests demonstrate that:

- raw replacement of the immutable development plan between epochs; or
- raw mutation of completed WIP state

causes the next decision-epoch boundary check to fail.

Direct lifecycle-mutator calls between epochs are also rejected by the existing guarded-method runtime.

## 18. Existing accounting/resource-allocation integration

Earth-supplied WIP expenditure now uses the existing Earth resource-allocation reservation/spend mechanism.

For successful Earth-supplied construction:

- declared capacity must exist;
- the exact stage is reserved;
- the exact reserved amount is spent;
- Earth qualifying supplied expenditure is updated;
- terrestrial FCF displacement bookkeeping is updated;
- fixed-capital formation preserves financing/supplier/asset locations.

Offworld-supplied WIP continues to use existing local supply-capacity enforcement.

## 19. Parameter standing

The structural fixture uses existing Test-only underwriting inputs:

- development cost = `60 MODEL_CURRENCY`;
- lead time = `2 YEARS`.

Test 006A adds an explicit authored stage schedule:

- year 6 = `30`;
- year 7 = `30`;
- completion = year 8.

Structural commissioned capacity:

`10`.

Success-case Earth stage ceilings are sufficient for both stages.

Failure-case year-7 ceiling:

`20`.

These are structural fixtures only.

They are not empirical offworld construction costs, schedules, capacities, supply constraints or success probabilities.

Test 006A introduces no construction-success probability.

## 20. Not yet earned

Test 006A does not establish:

- autonomous sponsor choice during active DEVELOPMENT;
- surface prospecting;
- EXPLORING-stage entry mechanics;
- geology-dependent construction;
- autonomous extraction;
- production/operating-cost execution;
- sales;
- surplus distribution;
- sponsor response after FAILED;
- CLOSED semantics;
- repair/expansion;
- transport/technology economics;
- empirical construction calibration;
- settlement dynamics;
- production forecasting.

## 21. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC EXPLORER TEST 002A: STRUCTURAL PASS;
- PUBLICATION / CROSS-AGENT TEST 002B: STRUCTURAL PASS;
- GOVERNED DECISION-EPOCH RUNTIME TEST 004: STRUCTURAL PASS;
- PRIVATE SPONSOR/OPERATOR TEST 005A: STRUCTURAL PASS;
- PROJECT DEVELOPMENT LIFECYCLE TEST 006A: STRUCTURAL PASS;
- EXPLICIT DEVELOPMENT PLAN: PASS;
- STAGED MULTI-YEAR CONSTRUCTION WIP: PASS;
- EARTH FINANCING-ORIGIN PRESERVATION: PASS;
- DEVELOPMENT -> OPERATING AFTER FULL COMMISSIONING: PASS;
- DEVELOPMENT -> FAILED AFTER INCOMPLETE CONSTRUCTION: PASS;
- EXPLICIT WIP WRITE-OFF: PASS;
- UNFINISHED-VALUE LOSS WITHOUT CASH REVERSAL: PASS;
- CONSTRUCTION HIDDEN-RESOURCE INDEPENDENCE: PASS;
- NULL FALSE-POSITIVE -> SUCCESSFUL CONSTRUCTION: PASS;
- LIFECYCLE DECISION/EVENT LINEAGE: PASS;
- A1-A9: PASS;
- CHAINED DETERMINISTIC REPLAY: PASS;
- COMPLETE FRD PROJECT LIFECYCLE: NOT YET EARNED;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
