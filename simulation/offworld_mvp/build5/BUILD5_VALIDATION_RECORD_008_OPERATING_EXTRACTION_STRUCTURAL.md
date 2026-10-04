# Build 5 Validation Record 008 — Operating / Extraction Test 008A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-operating-extraction`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_008_OPERATING_EXTRACTION_TEST008A.md`  
**Executable anchor:** `5534179000af4720469b57a02faf7763a874d160`

## 1. Result

Build 5 now implements the first bounded autonomous sponsor operating-cycle decision and governed physical extraction from an `OPERATING` project.

The verified causal chain is:

`OPERATING project -> sponsor operating decision -> operating-finance request if needed -> financier decision -> fresh sponsor decision -> OPEX spend -> WORLD_SIM extraction resolution -> realized resource depletion + offworld inventory`.

The sponsor remains the existing generic `PRIVATE_SPONSOR` Agent.

No mining-specific Agent engine was introduced.

## 2. Sponsor operating policy identity

Policy:

`SPONSOR_OPERATING_V1`

Semantic version:

`0.1`

Policy semantics:

`BOUNDED_OPERATING_CAPACITY_AND_WORKING_CAPITAL_V1`

Policy contract SHA-256:

`3036becca2f4ef5185dfb1f34c862808743ab0d7b9cb76c0c07804c6dd5c67ad`

Policy version:

`SPONSOR_OPERATING_V1:0.1:8d0ce3a30b855e3a629d03539ab4054ae563708ca1c898c046926547ec1165b5`

The policy contains no arbitrary numeric behavioral threshold.

## 3. Operating request/decision contract

Test 008A adds immutable:

- `OperatingCycleRequest`;
- `OperatingCycleDecision`;
- `OperatingCycleDecisionOutcome`;
- `OperatingCycleReasonCode`;
- `OperatingCostRecord`;
- `ExtractionResolutionRecord`.

Supported bounded outcomes are:

- `REQUEST_FINANCE`;
- `OPERATE`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

Required admitted facts are:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `asset.CAPACITY`;
- `underwriting.OPERATING_COST`.

Required belief/prior key:

- `resource_exists`.

## 4. Policy semantics

The bounded sponsor operating rule is:

- non-`OPERATING` project -> `DEFER`;
- missing relevant admitted observation -> `DEFER`;
- current resource belief <= sponsor prior -> `DEFER`;
- invalid/nonpositive productive capacity -> `DEFER`;
- missing class/objective/capability -> `DEFER`;
- UNKNOWN required fact -> `BLOCKED_UNKNOWN`;
- positive evidence + insufficient project cash -> `REQUEST_FINANCE` for exact operating-cash shortfall;
- positive evidence + sufficient cash + admitted `OPERATE` and `EXTRACT` capabilities -> `OPERATE`.

Planned quantity is the admitted productive-asset capacity.

Planned cycle cost is:

`planned quantity * admitted unit operating cost`.

## 5. Structural fixture

Test-only commissioned operating capacity:

`5 MODEL_RESOURCE_UNITS_PER_OPERATING_CYCLE`.

Carried Test-only operating cost:

`4 MODEL_CURRENCY_PER_RESOURCE_UNIT`.

Therefore:

`planned cycle cost = 5 * 4 = 20 MODEL_CURRENCY`.

The operating underwriting table preserves required standing:

`PRE_CONTRACT_AUTHORED_SCENARIO`.

Its Test 008A distinction is carried through table/source lineage, not by inventing a new epistemic-status label.

## 6. Working-capital recursion

After Test 006A construction:

- project state = `OPERATING`;
- productive asset exists;
- development cash has been fully spent;
- project cash = `0`;
- financier cash = `40`.

The first operating decision therefore returns:

`REQUEST_FINANCE 20`.

A later scheduled SYSTEM creates a formal Build 5 `FinancingRequest`:

`FINREQ-008A-OPERATING`.

Stage:

`OPERATING`.

Amount:

`20`.

The existing bounded financier policy then evaluates this request from its own admitted state.

Outcome in all qualification worlds:

`APPROVE 20`.

After disbursement:

- financier cash = `20`;
- project cash = `20`.

A fresh sponsor snapshot then produces:

`OPERATE`.

## 7. Operating-cost execution

The operating decision itself does not spend money.

A later scheduled `OPERATING_COST_SYSTEM` validates:

- project remains `OPERATING`;
- productive asset exists;
- asset belongs to project and node;
- planned quantity <= productive capacity;
- authorized OPEX reconciles with quantity * unit cost;
- project cash covers the full cycle;
- supplier allocation is available.

The successful structural operating cycle records:

- planned quantity = `5`;
- unit OPEX = `4`;
- total OPEX = `20`;
- transaction = `tx-000020`;
- purpose = `OPEX`;
- source = project cash;
- destination = Earth supplier.

After OPEX:

- project cash = `0`;
- Earth supplier cash = `90`.

No fixed capital is created by OPEX.

## 8. Physical extraction boundary

Only the later `EXTRACTION_RESOLUTION_SYSTEM` consults actual resource remaining.

The bounded structural rule is:

`actual_extracted = min(planned_quantity, resource.remaining)`.

WORLD_SIM then:

- decreases resource remaining by actual extracted;
- increases offworld resource inventory by exactly actual extracted;
- records planned vs actual output;
- records full/partial/zero-output result;
- preserves decision/OPEX causal lineage.

The sponsor policy does not receive resource remaining.

## 9. RICH full-output case

Universe:

`RICH_PUBLIC_3`.

Source observation:

`obs-000004 / POSITIVE`.

Sponsor resource belief:

`0.5`.

First operating decision:

`ODEC-504c6709d2db39c8aba8`

Outcome:

`REQUEST_FINANCE`

Requested operating finance:

`20`.

Financier decision:

`DEC-1ba36066e77050ad13f6 / APPROVE / 20`.

Second operating decision:

`ODEC-fac5202b22708ec85ad3`

Outcome:

`OPERATE`.

Planned quantity:

`5`.

Authorized OPEX:

`20`.

Realized extraction:

- resource before = `20`;
- planned = `5`;
- actual = `5`;
- resource after = `15`;
- inventory before = `0`;
- inventory after = `5`.

Result:

`FULL_OUTPUT`.

## 10. SPARSE under-production case

Universe:

`SPARSE_PUBLIC_1`.

Hidden/realized resource before operating cycle:

`3`.

Agent-visible operating state is otherwise equivalent to the RICH case.

The sponsor and financier decisions are identical:

- `ODEC-504c6709d2db39c8aba8 / REQUEST_FINANCE 20`;
- `DEC-1ba36066e77050ad13f6 / APPROVE 20`;
- `ODEC-fac5202b22708ec85ad3 / OPERATE / planned 5 / OPEX 20`.

Realized extraction:

- resource before = `3`;
- planned = `5`;
- actual = `3`;
- resource after = `0`;
- inventory before = `0`;
- inventory after = `3`.

Result:

`PARTIAL_OUTPUT`.

Thus productive capacity is an upper bound on attempted output, not a guarantee of physical supply.

## 11. NULL false-positive zero-output case

Universe:

`NULL_FP_1`.

Hidden/realized resource:

`0`.

The earlier legitimate remote false positive produces the same admitted positive information and sponsor belief used in the RICH/SPARSE cases.

Therefore the complete pre-extraction operating decision sequence is identical:

First operating decision:

`ODEC-504c6709d2db39c8aba8 / REQUEST_FINANCE 20`.

Financier:

`DEC-1ba36066e77050ad13f6 / APPROVE 20`.

Second operating decision:

`ODEC-fac5202b22708ec85ad3 / OPERATE / planned 5 / OPEX 20`.

The project spends the full authorized operating cost:

`20`.

Physical result:

- resource before = `0`;
- planned = `5`;
- actual = `0`;
- resource after = `0`;
- inventory before = `0`;
- inventory after = `0`.

Result:

`ZERO_OUTPUT`.

Project cash after the attempted cycle:

`0`.

Financier cash:

`20`.

Earth supplier cash:

`90`.

The project remains `OPERATING`; Test 008A does not automatically infer shutdown/failure from one zero-output cycle.

## 12. Hidden-world anti-cheating result

Across RICH, SPARSE and NULL qualification cases, before physical extraction the following are identical:

- sponsor operating-finance DecisionSnapshot;
- first sponsor operating decision;
- formal operating FinancingRequest;
- financier DecisionSnapshot;
- financier decision;
- post-finance sponsor DecisionSnapshot;
- second sponsor operating decision;
- planned quantity;
- authorized OPEX.

Only the WORLD_SIM extraction result diverges:

- RICH = `5`;
- SPARSE = `3`;
- NULL = `0`.

This structurally verifies that hidden resource quantity does not leak into sponsor or financier decisions.

## 13. OPEX treatment

Test 008A charges the full planned-cycle OPEX before physical recovery is known.

Therefore all three cases spend:

`20`.

This allows:

- full-output operation;
- economically inefficient under-production;
- complete operating loss with zero recovered material.

The rule is a structural abstraction only.

It is not an empirical claim that real extraction cost is fully fixed per nameplate-capacity cycle.

## 14. No revenue yet

Extraction increases offworld resource inventory.

It does not create revenue.

No `REVENUE` transaction is produced by Test 008A.

Sale remains a separate later action requiring a buyer/market-clearing account and explicit price/demand semantics under FRD §22.

## 15. Physical conservation

For every extraction resolution:

`resource_after = resource_before - actual_extracted`.

and:

`inventory_after = inventory_before + actual_extracted`.

Actual extracted quantity is always:

`0 <= actual_extracted <= planned_quantity <= productive_capacity`.

No negative resource stock is permitted.

## 16. Hostile execution boundaries

Focused tests verify that:

- a non-`OPERATING` project cannot execute an operating cycle;
- an asset belonging to the wrong project is rejected before spending;
- a forged plan above productive capacity is rejected before spending;
- missing `OPERATE`/`EXTRACT` capabilities prevents policy authorization;
- nonpositive evidence relative to sponsor prior defers operation;
- UNKNOWN operating cost blocks before worker execution;
- policy evaluation alone changes neither cash nor resource state;
- policy hostile-access probe exposes no hidden-world/runtime access.

## 17. Persistent-state hardening

Extraction makes offworld resource inventory decision-relevant persistent state.

Test 008A therefore extends the MVP decision-epoch fingerprint to serialize full current colony stock-flow state, including:

- population;
- cash;
- productive capital;
- infrastructure;
- resource inventory;
- import inventory;
- production capacity;
- operating need;
- subsidy;
- colony stage.

A hostile test demonstrates that raw mutation of extracted resource inventory between epochs is detected as persistent-state tampering.

Productive-asset capacity tampering between epochs is likewise detected.

## 18. Accounting

All operating qualification epochs preserve A1 through A9.

The operating-finance request epoch introduces no cash flow.

The operating-finance epoch uses the existing qualified commitment/disbursement path.

The operating/extraction epoch:

- records a double-sided OPEX payment;
- depletes physical resource only by actual extraction;
- creates equal offworld inventory;
- creates no revenue.

The NULL zero-output case still reconciles despite its full OPEX loss.

## 19. Eight-epoch RICH history

The RICH qualification case now spans eight persistent parent-linked epochs.

1. Publication  
   result: `15662a85308f985d19f04d7ae52b04c96cd96b365e3219ae783f6a9a5a4eee68`

2. Sponsor development-finance request  
   result: `d3d41924966cd81f8221d55d7c1686822ce098170c666f3673cf072717dfa19e`

3. Development financier approval/funding  
   result: `79818e8833c8a50d472287aa2b3e302d385eedd660e20d73306f7a89b7ac5c80`

4. Sponsor DEVELOP  
   result: `bee58c4835c44eee6a8dd900ebef1a6f59f34bcaf112da952a4ec88db63b038f`

5. Construction/commissioning  
   result: `0dea584d9de3afbfa4839f0e9178d2af9aabba2cac1ffc32462f0cd7599bb9c7`

6. Sponsor operating-finance request  
   result: `ea106a2fb544d3241180dc2e80052e7103f2b6cd24a84a92b9ddaa77fd34257d`

7. Operating financier approval/funding  
   result: `1623aa46de40c0af58055edb93c419b43df5d4558803473ba6b8691372eaeb7b`

8. Sponsor OPERATE -> OPEX -> extraction  
   result: `7f779de57c2dec38fa9de30698fbc1de95d9e020233f3850075cba958a719bed`

Each epoch's parent result equals the immediately prior epoch result.

## 20. SPARSE and NULL terminal epoch fingerprints

SPARSE final operating/extraction epoch:

`90acd5120b6083198b71fbefe607c2e07d5cd817c7558deee80027b20124a26b`.

NULL final operating/extraction epoch:

`d8c793f56fb43fb6b7a282448ad4744ed9e189811316ba0ffe6a09f1c5fcd579`.

Their earlier epoch result fingerprints differ because hidden scenario state remains part of WORLD_SIM persistent state, while Agent decision artifacts remain identical where admitted information is identical.

## 21. Deterministic replay

Repeated full RICH, SPARSE and NULL chains reproduce:

- all eight decision-epoch records;
- sponsor operating-finance decision;
- formal operating FinancingRequest;
- financier decision;
- sponsor OPERATE decision;
- OperatingCostRecord;
- ExtractionResolutionRecord;
- final methodology fingerprint.

Replay is exact.

## 22. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`9810734af1dcd388784dea848cfff5fea33e28745b58cf3fcfc68a9c0d62d9b3`

Git-object reconstructed source-tree SHA-256:

`9810734af1dcd388784dea848cfff5fea33e28745b58cf3fcfc68a9c0d62d9b3`

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 23. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`.

Result at the executable anchor:

**200 tests executed; 200 passed in 95.363 seconds.**

The preceding surface-prospecting baseline contained 183 tests.

Test 008A contributes 17 focused operating/extraction tests.

## 24. Parameter standing

Test 008A uses structural authored values only:

- commissioned productive capacity = `5`;
- operating cost = `4 MODEL_CURRENCY_PER_RESOURCE_UNIT`;
- full cycle OPEX = `20`.

The existing financing policy parameters remain Test-only / not policy baseline.

No Test 008A value is promoted to empirical mining performance, calibrated cost, forecast throughput or reserve estimate.

## 25. Not yet earned

Test 008A does not establish:

- sale/revenue;
- market demand clearing;
- transport cost;
- energy submodel;
- extraction grade/quality;
- sponsor response to observed zero/partial production;
- repeated operating cycles;
- repair/maintenance;
- shutdown/CLOSED;
- debt service;
- dividends/equity distributions;
- surplus disposition;
- reinvestment;
- empirical mining calibration;
- settlement effects;
- production forecasting.

## 26. Standing

Current earned standing:

- PRIVATE FINANCIER AGENT TEST 001: STRUCTURAL PASS;
- PUBLIC EXPLORER REMOTE TEST 002A: STRUCTURAL PASS;
- PUBLICATION / CROSS-AGENT TEST 002B: STRUCTURAL PASS;
- GOVERNED DECISION-EPOCH RUNTIME TEST 004: STRUCTURAL PASS;
- PRIVATE SPONSOR/OPERATOR TEST 005A: STRUCTURAL PASS;
- PROJECT DEVELOPMENT LIFECYCLE TEST 006A: STRUCTURAL PASS;
- SURFACE PROSPECTING TEST 007A: STRUCTURAL PASS;
- OPERATING / EXTRACTION TEST 008A: STRUCTURAL PASS;
- OPERATING WORKING-CAPITAL REQUEST: PASS;
- RECURSIVE FINANCIER RESPONSE: PASS;
- FRESH POST-FINANCE OPERATING DECISION: PASS;
- OPEX LEDGERING: PASS;
- PRODUCTIVE-CAPACITY CEILING: PASS;
- WORLD_SIM RESOURCE-BOUNDED EXTRACTION: PASS;
- FULL / PARTIAL / ZERO OUTPUT DIVERGENCE: PASS;
- RESOURCE -> INVENTORY CONSERVATION: PASS;
- NULL ZERO-OUTPUT OPEX LOSS: PASS;
- HIDDEN-WORLD PRE-EXTRACTION DECISION EQUIVALENCE: PASS;
- COLONY INVENTORY EPOCH-TAMPER DETECTION: PASS;
- A1-A9: PASS;
- CHAINED DETERMINISTIC REPLAY: PASS;
- SALES / REVENUE: UNEARNED;
- EMPIRICAL VALIDATION: UNEARNED;
- PRODUCTION FORECAST STATUS: UNEARNED.
