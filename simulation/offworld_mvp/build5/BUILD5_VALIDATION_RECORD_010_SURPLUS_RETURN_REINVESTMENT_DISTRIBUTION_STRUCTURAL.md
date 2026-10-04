# Build 5 Validation Record 010 — Surplus / Return / Reinvestment / Distribution Test 010A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Branch:** `offworld-mvp-build5-surplus-distribution`  
**Authorization:** `BUILD5_IMPLEMENTATION_AUTHORIZATION_010_SURPLUS_RETURN_REINVESTMENT_DISTRIBUTION_TEST010A.md`  
**Executable anchor:** `2fabe742840a042203fc1012aec3653ceccd5f8a`  
**FRD mutation:** NONE

## 1. Result

Build 5 now implements the first bounded post-revenue project-cash allocation cycle.

The verified causal chain is:

`project revenue -> project cash -> sponsor surplus-allocation decision -> retained reserve + financier return + local reinvestment + owner distribution -> reconciled closing cash`.

This closes the first structural capital loop from external financing through project operation and sale back into explicit capital return / reinvestment / ownership distribution.

## 2. Research intake standing

Advisory research inspected read-only:

- repository: `loom-2226/loom-research-lab`;
- commit: `a47d53ce1bd06453fe4d19eeab7abbc56f924527`;
- artifact: `projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md`;
- classification: `RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION`.

Useful research discipline admitted:

- ownership and capital-return flows remain separate;
- capital outflow, capital return and realized transaction flows remain explicit;
- provenance remains project/body/actor traceable beneath later aggregation;
- no same-period macro consequence is fed backward into the originating period.

No research proposal was promoted to FRD or empirical authority.

## 3. FRD preservation

Test 010A was implemented from parent Test 009A head:

`e1337ff77f3b14f4d8dc98445e51e92184e2afa5`.

Mechanical diff against:

`simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md`

returned:

`FRD_DIFF_LINES=0`.

The executable ODD was updated because the executable schema changed.

The FRD was not modified.

## 4. Core semantic separation

Test 010A formally distinguishes:

`financing return claim != project ownership claim`.

The private financier funded the project but does not become an owner merely because financing occurred.

Project `P` remains, in the qualification fixture:

`SPN = 1.0 ownership`.

The financier receives cash only through a separately declared `FinancingReturnClaim`.

Owner distribution is routed separately from project ownership.

## 5. Financing-return claim

The qualification claim is:

`FRC-010A-1`.

Fields:

- financier = `FIN`;
- project = `P`;
- destination account = `fin_funds`;
- maximum return amount = `30 MODEL_CURRENCY`;
- source commitments =
  - `C-SPONSOR-005A`;
  - `C-OPERATING-008A`;
- standing = `TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE`.

Claim SHA-256:

`d2c3f55672312975a801561d1161bf7540e0a75499b52e791286988b65f99799`.

The settlement SYSTEM requires cited commitments to exist, match the project/financier and contain actual disbursed capital.

A commitment with no disbursement cannot support a financier-return settlement.

## 6. Sponsor surplus policy identity

Policy:

`SPONSOR_SURPLUS_V1`.

Semantic version:

`0.1`.

Policy semantics:

`BOUNDED_RESERVE_FINANCIER_RETURN_REINVEST_OWNER_RESIDUAL_V1`.

Policy contract SHA-256:

`0669067ff6baa4a1553035580d2df1b91a5390b791b0fc1133f4bdce9e3d90d2`.

Policy version:

`SPONSOR_SURPLUS_V1:0.1:40de5d3d531777a73a540a9c29c4c7a0b85224a387b8725267c84dbc9d1c613e`.

The policy contains no arbitrary payout percentage or profit hurdle.

## 7. Decision contract

Test 010A adds immutable:

- `SurplusDistributionRequest`;
- `SurplusDistributionDecision`;
- `SurplusDistributionDecisionOutcome`;
- `SurplusDistributionReasonCode`;
- `FinancingReturnClaim`;
- `OwnerDistributionAllocation`;
- `SurplusDistributionRecord`.

Required admitted facts:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `project.RESERVE_REQUIREMENT`;
- `financing.RETURN_CLAIM_REMAINING`;
- `project.REINVESTMENT_REQUIREMENT`.

Supported outcomes:

- `DISTRIBUTE`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

## 8. Structural allocation rule

For positive project cash, the bounded policy applies cash in this order:

1. retain reserve up to the admitted reserve requirement;
2. satisfy the separately declared financing-return claim from remaining cash;
3. satisfy the admitted local-reinvestment requirement from remaining cash;
4. classify any remaining residual as owner distribution.

Identity:

`opening_project_cash = reserve + financier_return + local_reinvestment + owner_distribution`.

Closing project cash must equal retained reserve.

## 9. Reserve basis

The Test 010A reserve requirement is not an independent new authored number.

It is derived from the already-authorized Test 008A operating fixture:

- productive capacity = `5`;
- unit operating cost = `4`.

Therefore:

`next-cycle operating reserve requirement = 5 * 4 = 20 MODEL_CURRENCY`.

This is still a structural Test-only operating-cost basis, not empirical mining calibration.

## 10. New Test-only allocation fixtures

Test 010A adds only:

- financing-return claim maximum = `30 MODEL_CURRENCY`;
- local-reinvestment requirement = `10 MODEL_CURRENCY`.

These values are structural fixtures.

They do not represent empirical debt terms, expected returns, dividend policy, calibrated reinvestment behavior or a production baseline.

## 11. Transaction semantics

Test 010A adds distinct transaction purposes:

- `FINANCIER_RETURN`;
- `OWNER_DISTRIBUTION`.

It reuses:

- `LOCAL_REINVESTMENT`.

Retained reserve creates no transfer transaction; it remains in project cash.

This prevents physical destination from erasing economic meaning.

Both financier return and owner distribution may flow to Earth-located accounts, but the ledger preserves why each transfer occurred.

## 12. RICH qualification case

Prior Test 009A state:

- sale revenue = `80`;
- project cash = `80`;
- financier cash after prior project funding = `20`;
- sponsor cash = `0`;
- local reinvestment cash = `0`.

Surplus decision:

`DDEC-c2ad9f7d2f3fc1bd005f`.

Outcome:

`DISTRIBUTE`.

Allocation:

- reserve = `20`;
- financier return = `30`;
- local reinvestment = `10`;
- owner distribution = `20`.

Settlement transactions:

- financier return = `tx-000025`;
- local reinvestment = `tx-000026`;
- owner distribution = `tx-000027`.

Closing state:

- project cash = `20`;
- financier cash = `50`;
- local reinvestment cash = `10`;
- sponsor cash = `20`;
- financing-return claim remaining = `0`;
- project ownership remains `SPN:1`.

Resource state remains:

- resource remaining = `15`;
- local resource inventory = `1`.

## 13. SPARSE qualification case

Prior Test 009A state:

- sale revenue = `60`;
- project cash = `60`.

Surplus decision:

`DDEC-3cd167efced719ab6a48`.

Outcome:

`DISTRIBUTE`.

Allocation:

- reserve = `20`;
- financier return = `30`;
- local reinvestment = `10`;
- owner distribution = `0`.

Closing state:

- project cash = `20`;
- financier cash = `50`;
- local reinvestment cash = `10`;
- sponsor cash = `0`;
- financing-return claim remaining = `0`;
- ownership remains `SPN:1`.

The sponsor receives no owner payout because no residual remains after the explicit priority sequence.

## 14. NULL qualification case

Prior Test 009A state:

- sale revenue = `0`;
- project cash = `0`.

Surplus decision:

`DDEC-df3005d1d9ccf339d7c8`.

Outcome:

`DEFER`.

Reason:

`NO_DISTRIBUTABLE_CASH`.

Allocation:

- reserve = `0`;
- financier return = `0`;
- local reinvestment = `0`;
- owner distribution = `0`.

Closing state:

- project cash = `0`;
- financier cash = `20`;
- local reinvestment cash = `0`;
- sponsor cash = `0`;
- financing-return claim remaining = `30`.

Thus a financing-return claim does not create cash or guarantee repayment.

## 15. Financier versus owner identity test

A hostile/structural fixture changes project ownership before the epoch chain to:

- `SPN = 0.5`;
- `FIN = 0.5`.

The RICH owner residual remains:

`20`.

The SYSTEM routes it pro rata:

- `SPN owner distribution = 10`;
- `FIN owner distribution = 10`.

The financier simultaneously receives:

- `30` under `FINANCIER_RETURN`;
- `10` under `OWNER_DISTRIBUTION`.

These remain separate ledger semantics despite sharing the same recipient entity/account.

This demonstrates that a single institution can hold multiple economic roles without collapsing those roles.

## 16. Owner-routing rule

The sponsor policy decides only the aggregate owner-distribution amount.

It does not choose recipients.

The SYSTEM reads the current explicit project ownership ledger and routes owner distribution pro rata.

Owner shares must reconcile to exactly one.

No owner distribution may bypass or overwrite project ownership.

## 17. A6 extension

The executable A6 accounting check now validates both:

- legacy `SurplusDecompositionRecord`;
- new `SurplusDistributionRecord`.

For Test 010A:

`80 = 20 + 30 + 10 + 20` in RICH.

`60 = 20 + 30 + 10 + 0` in SPARSE.

The distribution record additionally requires:

`closing_project_cash = reserve`.

Owner-allocation amounts must sum to total owner distribution.

## 18. Hostile execution boundaries

Focused tests verify:

- policy evaluation alone changes no cash;
- UNKNOWN reserve blocks before worker;
- UNKNOWN financing-return claim blocks before worker;
- UNKNOWN reinvestment requirement blocks before worker;
- missing `DISTRIBUTE_SURPLUS` capability defers;
- non-`OPERATING` project defers;
- zero project cash defers;
- negative allocation input is rejected by the isolated worker;
- forged total allocation above current project cash is rejected;
- claim/project mismatch is rejected;
- financier destination-account ownership mismatch is rejected;
- financing return above remaining claim is rejected;
- invalid ownership shares are rejected;
- duplicate execution of one distribution decision is rejected;
- claim settlement without actual disbursed financing is rejected.

## 19. Physical-state isolation

Surplus allocation does not alter:

- hidden/realized resource remaining;
- local resource inventory;
- Earth market resource inventory.

Focused tests capture those values before distribution and verify exact equality afterward.

Financial allocation therefore cannot create, destroy, extract or sell resource.

## 20. Persistent-state tamper protection

All cash accounts participate in the persistent decision-epoch state fingerprint.

After a completed Test 010A distribution epoch, raw mutation of project cash causes the next decision-epoch boundary to reject state as tampered.

The distribution claim and distribution records also participate in the methodology fingerprint.

## 21. Deterministic replay

Repeated complete RICH, SPARSE and NULL chains reproduce exactly:

- all ten decision-epoch records;
- surplus DecisionSnapshot;
- surplus decision;
- financing-return settlement;
- local reinvestment settlement;
- owner allocations;
- closing account balances;
- remaining financing-return claim;
- final methodology fingerprint.

Replay is exact.

## 22. Ten-epoch causal history

The qualification chain is now:

1. public observation publication;
2. sponsor development-finance request;
3. financier development funding;
4. sponsor DEVELOP;
5. construction / commissioning;
6. sponsor operating-finance request;
7. financier operating funding;
8. sponsor OPERATE -> OPEX -> extraction;
9. sponsor sale -> market clearing -> project revenue;
10. sponsor surplus allocation -> financier return / local reinvestment / owner distribution.

Final tenth-epoch result fingerprints:

- RICH = `aaf1cbe6bbe66a6f1d4209c8cf33fdec4b624bf8c85a4879942090c1477b0554`;
- SPARSE = `6bd431e015a96b33ccdee232e41dc13bf497dd6b93cff78bb56f1c25485880c5`;
- NULL = `a70be65fd182de37ffee29924902412111495c195c45572e587ec0d537f313ae`.

## 23. Accounting

A1 through A9 pass in the RICH, SPARSE and NULL distribution epochs.

The RICH distribution epoch creates three distinct transfers totaling `60`, while `20` remains in project cash as reserve.

The SPARSE distribution epoch creates two transfers totaling `40`, while `20` remains in project cash and no owner distribution occurs.

The NULL epoch creates no distribution transfer.

## 24. Executable identity

Executable `offworld_kernel` source-tree SHA-256:

`e2cdd2a3b31be34a208dec730a081a872c50053a8cd633be4065e9da18e29916`.

Git-object reconstructed source-tree SHA-256:

`e2cdd2a3b31be34a208dec730a081a872c50053a8cd633be4065e9da18e29916`.

Commit/code linkage:

`GIT_OBJECT_VERIFIED`.

## 25. Regression result

The governed kernel suite was executed from:

`simulation/offworld_mvp/phase3b/kernel`

using:

`python3 -m unittest discover -s tests`.

Result at executable anchor:

**244 tests executed; 244 passed in 218.343 seconds.**

The Test 009A baseline contained 221 tests.

Test 010A contributes 23 focused surplus/distribution tests.

## 26. ODD standing

The executable ODD schema registry now includes:

- surplus distribution request/decision;
- distribution outcomes/reason codes;
- financing-return claim;
- owner distribution allocation;
- surplus distribution record;
- new transaction semantics;
- associated unit contracts.

The ODD narrative records the financing-return-versus-ownership separation and SYSTEM-mediated routing.

The FRD remains unchanged.

## 27. What Test 010A does not mean

The structural financier-return claim is not a statement that the Test 001 financing instrument is:

- debt;
- preferred equity;
- common equity;
- royalty finance;
- streaming finance;
- convertible finance;
- secured project debt;
- unsecured lending.

The owner residual is not a calibrated dividend policy.

The local reinvestment requirement is not a forecast of optimal reinvestment.

The operating reserve is a structural next-cycle fixture.

## 28. Not yet earned

Test 010A does not establish:

- interest;
- amortizing debt service;
- IRR;
- hurdle-rate calibration;
- taxes;
- royalties;
- preferred/common waterfalls;
- dilution;
- new financing rounds;
- retained-earnings optimization;
- endogenous reinvestment opportunities;
- repeated operating/sale/distribution cycles;
- shutdown/closure;
- empirical financing calibration;
- long-run profitability;
- economic forecast validity.

## 29. Standing

Current earned standing:

- SALE / REVENUE / MARKET CLEARING TEST 009A: STRUCTURAL PASS;
- SURPLUS / RETURN / REINVESTMENT / DISTRIBUTION TEST 010A: STRUCTURAL PASS;
- FINANCING RETURN CLAIM SEPARATE FROM OWNERSHIP: PASS;
- CLAIM REQUIRES ACTUAL DISBURSED FINANCING LINEAGE: PASS;
- OPERATING RESERVE RETENTION: PASS;
- FINANCIER RETURN: PASS;
- LOCAL REINVESTMENT: PASS;
- OWNER RESIDUAL DISTRIBUTION: PASS;
- PRO-RATA OWNER ROUTING: PASS;
- DISTINCT FINANCIER_RETURN / OWNER_DISTRIBUTION SEMANTICS: PASS;
- ZERO-CASH CLAIM DOES NOT CREATE REPAYMENT: PASS;
- A6 SURPLUS DECOMPOSITION: PASS;
- A1-A9: PASS;
- PHYSICAL RESOURCE ISOLATION: PASS;
- CHAINED DETERMINISTIC REPLAY: PASS;
- FRD MUTATION: NONE;
- EMPIRICAL FINANCING TERMS: UNEARNED;
- REPEATED CASH-CYCLE POLICY: UNEARNED;
- PROFITABILITY / FORECAST STATUS: UNEARNED.
