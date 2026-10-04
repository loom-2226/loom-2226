# BUILD 5 VALIDATION RECORD 014 — REPEATED ENTERPRISE STRUCTURAL

Status: **STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED**

## Authority

Parent Test 013 head: `871c5c56f8d76f7d4bdad700584d93b46eb6c3d8`  
Authorization commit: `acedf2a`  
Executable candidate: `d67f6794cd27acc5927ae93bfae35d98416b42f3`

The guiding FRD was not modified.

## Result

Test 014A closes the bounded repeated-enterprise lifecycle seam identified by the
FRD. The existing private sponsor can now review a completed operating/extraction
cycle from admitted realized output, continue an open venture after positive output,
or close the venture after zero output under a Test-only structural strategy.

The verified causal chain is:

`existing operating cycle -> WORLD_SIM realized output -> sponsor post-cycle review -> CONTINUE or CLOSE -> later existing operating/finance machinery`.

No second operating engine, financing engine, market, or surplus model was introduced.

## Reused machinery

Test 014A reuses unchanged:

- `SPONSOR_OPERATING_V1` for operating/working-capital choice;
- Test 008 OPEX execution and resource-bounded extraction;
- the existing bounded financier policy and disbursement machinery;
- Test 009 sale/market clearing;
- Test 010 surplus allocation and next-cycle operating reserve;
- persistent decision epochs, accounting identities and replay provenance.

Existing sponsor operating identity remains exactly:

`SPONSOR_OPERATING_V1:0.1:8d0ce3a30b855e3a629d03539ab4054ae563708ca1c898c046926547ec1165b5`

Contract SHA-256 remains:

`3036becca2f4ef5185dfb1f34c862808743ab0d7b9cb76c0c07804c6dd5c67ad`.

Existing surplus policy identity remains:

`SPONSOR_SURPLUS_V1:0.1:40de5d3d531777a73a540a9c29c4c7a0b85224a387b8725267c84dbc9d1c613e`

with contract SHA-256:

`0669067ff6baa4a1553035580d2df1b91a5390b791b0fc1133f4bdce9e3d90d2`.

## New sponsor review policy

Policy:

`SPONSOR_ENTERPRISE_REVIEW_V1`

Semantic version:

`0.1`

Policy version:

`SPONSOR_ENTERPRISE_REVIEW_V1:0.1:a7b06c8fa0a7f32cd7baf08aa65dbdad98b0666b60ffb0db9efc585b03f7be1f`

Contract SHA-256:

`96ea61485bd295e32fd7771abb6407af30a359fa8f47452061adafb555dd557c`

Required admitted facts are exactly:

- `project.STATUS`;
- `cycle.PLANNED_QUANTITY`;
- `cycle.ACTUAL_OUTPUT`.

The policy receives no hidden scenario-resource quantity or remaining-resource state.

## Test-only structural strategy

The bounded rule contains no authored numeric behavioral threshold:

- positive realized output -> `CONTINUE`;
- zero realized output -> `CLOSE`;
- non-`OPERATING` state or missing class/objective/capability -> `DEFER`;
- inconsistent output (`planned <= 0`, `actual < 0`, `actual > planned`) -> `DEFER`;
- UNKNOWN required input -> `BLOCKED_UNKNOWN` before worker execution.

This rule is **TEST_ONLY / NOT_POLICY_BASELINE / NOT_EMPIRICALLY_VALIDATED**. It is not
a claim that a real enterprise rationally closes after one zero-output cycle.

## World-side execution boundary

`CONTINUE` records the sponsor review and leaves project lifecycle state unchanged.

`CLOSE` is executable only if the kernel independently verifies:

- exact request/decision lineage;
- private-sponsor identity;
- project currently `OPERATING`;
- exact completed extraction-event lineage;
- realized output equals zero;
- sponsor has `CLOSE_PROJECT` capability;
- the extraction has not already been reviewed.

Only then does the executor perform:

`OPERATING -> CLOSED`.

The older generic `transition_project_status()` authorization was deliberately **not**
widened. Therefore Test 014A does not accidentally create a generic direct closure path.

There is no earned `CLOSED -> *` transition.

## Canonical RICH path

Initial hidden resource stock: `20` Test-only units.

The already-qualified Test 008/009/010 chain produces first-cycle output `5`, sale and
surplus allocation. Test 010 leaves project cash `20`, the exact next-cycle operating
reserve.

First review:

`5 / 5 -> CONTINUE`.

Second operating cycle, year 11:

- no new financing is created;
- retained project reserve `20` funds OPEX `20`;
- planned output = `5`;
- actual output = `5`;
- remaining hidden resource becomes `10`.

Second review:

`5 / 5 -> CONTINUE`.

After the retained reserve has been spent, project cash is `0`. The unchanged operating
policy then returns:

`REQUEST_FINANCE 20`.

The unchanged financier policy approves `20`; existing disbursement machinery restores
project cash to `20`.

Final canonical RICH state:

- project = `OPERATING`;
- realized outputs = `[5, 5]`;
- enterprise reviews = `[CONTINUE, CONTINUE]`;
- project cash = `20` after recapitalization;
- financier cash = `30`;
- decision epochs = `15`;
- economic transactions = `13`.

This proves both reserve-funded repetition and later recapitalization without adding a
new financing mechanism.

## Canonical SPARSE path

Initial hidden resource stock: `3` Test-only units.

First cycle:

`planned 5 -> actual 3 -> PARTIAL_OUTPUT`.

First review:

`3 > 0 -> CONTINUE`.

After sale/distribution, Test 010 again retains the exact `20` next-cycle reserve.
The second operating cycle therefore proceeds without synthetic new financing.

Second cycle:

`planned 5 -> actual 0 -> ZERO_OUTPUT`.

Second review:

`0 -> CLOSE`.

Final canonical SPARSE state:

- project = `CLOSED`;
- realized outputs = `[3, 0]`;
- enterprise reviews = `[CONTINUE, CLOSE]`;
- project cash = `0`;
- financier cash = `50`;
- decision epochs = `13`;
- economic transactions = `11`.

No recapitalization request occurs after closure.

## Canonical NULL path

Initial hidden resource stock: `0`.

The pre-review Agent decisions remain based on admitted positive evidence and therefore
the first operating cycle is still authorized and incurs the same Test 008 OPEX before
WORLD_SIM resolves truth.

First cycle:

`planned 5 -> actual 0 -> ZERO_OUTPUT`.

First review:

`0 -> CLOSE`.

Final canonical NULL state:

- project = `CLOSED`;
- realized outputs = `[0]`;
- enterprise reviews = `[CLOSE]`;
- no second operating cycle exists;
- project cash = `0`;
- financier cash = `20`;
- decision epochs = `11`;
- economic transactions = `7`.

## Epistemic boundary

The sponsor-review snapshot contains only project status, planned cycle quantity and
actual output from the completed extraction record.

Qualification explicitly verifies that neither `resource.REMAINING` nor scenario hidden
resource truth is admitted to review policy input.

RICH/SPARSE/NULL therefore diverge only after WORLD_SIM has produced different realized
outputs from the same previously admitted operating decision machinery.

## Hostile coverage

The 13 new Test 014 cases verify:

1. RICH reserve-funded repetition and later exact recapitalization;
2. SPARSE partial-output continuation followed by zero-output closure;
3. NULL immediate zero-output closure with no second cycle;
4. review input excludes hidden resource truth/remaining stock;
5. UNKNOWN actual output blocks before worker execution;
6. policy evaluation alone mutates no state;
7. missing `CLOSE_PROJECT` capability prevents closure;
8. forged CLOSE against positive output is rejected at execution;
9. forged CONTINUE against zero output is rejected at execution;
10. duplicate review of one extraction is rejected;
11. `CLOSED` causes later sponsor operating policy to defer on project state;
12. enterprise-review state tampering is detected at the next decision-epoch boundary;
13. complete RICH/SPARSE/NULL chains replay deterministically.

The execution record is included in methodology/decision-epoch fingerprints, so raw
review-record mutation cannot escape chain integrity checks.

## Focused qualification

Command:

`python3 -m unittest tests.test_odd_schema_drift tests.test_scheduled_runtime tests.test_build5_operating_extraction tests.test_build5_surplus_distribution tests.test_build5_repeated_enterprise`

Result on the committed candidate:

- 63 tests executed;
- 63 passed;
- 0 failures;
- 0 errors;
- runtime 198.799 s.

## Full governed regression

Command:

`python3 -m unittest discover -s tests`

Executed on candidate:

`d67f6794cd27acc5927ae93bfae35d98416b42f3`

Result:

- 308 tests executed;
- 308 passed;
- 0 failures;
- 0 errors;
- runtime 519.527 s.

All 295 tests from the Test 013 baseline remain present and pass; Test 014 adds 13.

## Executable provenance

Filesystem executable source-tree SHA-256:

`acfc3e862c0e7e063618c6d4d893525cbad2255507312d0b5b7460b96b89ffc1`

Git-object reconstructed executable source-tree SHA-256:

`acfc3e862c0e7e063618c6d4d893525cbad2255507312d0b5b7460b96b89ffc1`

Standing: `GIT_OBJECT_VERIFIED`.

## Size / bloat check

Executable Python package LOC (`offworld_kernel/**/*.py`):

- Test 013 parent: `10,128`;
- Test 014 candidate: `10,518`;
- net package growth: `390` lines (`3.85%`).

Of those 390 lines, `57` are the Test 014 fixture. Core package/policy integration grows
by approximately `333` lines.

The new machinery is limited to one sponsor review contract/policy, one execution record,
one validated executor, worker/runner integration and schema reconciliation. Existing
operating, finance, sale and surplus policies were not forked or semantically expanded.

## FRD / ODD standing

Guiding FRD diff from Test 013 parent: `0` lines.

The executable ODD is reconciled to `ODD_SCHEMA_REGISTRY_0_16` and records the newly
earned repeated-enterprise semantics and bounded `CLOSED` transition.

## Explicitly not earned

Test 014A does not earn:

- a calibrated closure strategy;
- maintenance or repair;
- asset replacement;
- workforce scheduling;
- bankruptcy/insolvency law;
- liquidation or salvage proceeds;
- reopening a closed venture;
- endogenous prices or demand;
- portfolio optimization across projects;
- endogenous R&D or technology choice;
- stochastic failure/closure behavior;
- a generalized corporate-management simulation.

## Conclusion

Test 014A structurally closes repeated operating-cycle lifecycle behavior for the strict
MVP: enterprises can persist through positive full/partial output, consume retained
next-cycle reserve, request recapitalization through the already-qualified finance seam,
and close through a separately governed sponsor decision after zero realized output.
