# Build 5 Implementation Authorization 010 — Surplus / Return / Reinvestment / Distribution Test 010A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go surplus / return / reinvestment / financier-and-owner distributions.”  
**FRD mutation:** NOT AUTHORIZED FOR THIS TEST  
**Parent:** Build 5 Test 009A sale/revenue/market-clearing structural pass

## 1. Purpose

Implement the first bounded post-revenue project-cash allocation decision without collapsing financing claims, ownership claims, project reserve, local reinvestment, or owner distributions into one generic “profit” transfer.

The authorized causal slice is:

`project revenue -> project cash -> sponsor surplus-allocation decision -> reserve + financing return + local reinvestment + owner distribution -> reconciled financial state`.

## 2. Research intake standing

Advisory research inspected read-only:

- repository: `loom-2226/loom-research-lab`;
- commit: `a47d53ce1bd06453fe4d19eeab7abbc56f924527`;
- artifact: `projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md`;
- classification: `RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION`.

Useful research discipline admitted here:

- preserve ownership, capital outflow, capital return and realized transaction flows separately;
- preserve project/body provenance beneath later economic aggregation;
- do not feed same-period macro consequences backward into the originating period.

No research proposal becomes runtime authority merely by being adjacent to the FRD.

## 3. Core semantic distinction

Test 010A shall preserve:

`financing return claim != project ownership claim`.

Financing a project does not automatically make the financier an owner.

Owning a project does not automatically define a debt/financing return.

Any financier return entitlement must be separately declared and versioned.

Owner distribution shall be derived from the project's explicit ownership ledger.

## 4. Generic Agent architecture

The existing `PRIVATE_SPONSOR` remains the decision-bearing Agent.

No finance-company-specific, mining-company-specific, or dividend-specific Agent class may be introduced.

The sponsor shall use the established:

`AgentState -> DecisionSnapshot -> isolated policy -> immutable decision -> scheduled SYSTEM consequence`.

The settlement/distribution mechanism is a SYSTEM consequence.

## 5. Explicit financing-return claim

Test 010A shall introduce an immutable `FinancingReturnClaim` with at minimum:

- claim id;
- financier id;
- project id;
- destination account id;
- maximum return amount;
- source commitment ids;
- source/rationale reference;
- epistemic standing;
- version.

Remaining claim shall be derived from immutable claim amount minus prior qualified settlement records.

The claim shall not imply project ownership.

## 6. Structural fixture only

For Test 010A:

- next-cycle operating reserve requirement = `20 MODEL_CURRENCY`, derived from the already-authored Test 008A cycle cost;
- financing-return claim maximum = `30 MODEL_CURRENCY`;
- local-reinvestment requirement = `10 MODEL_CURRENCY`.

The `30` financing-return claim and `10` reinvestment requirement are TEST_ONLY structural fixtures.

They are not empirical financing terms, calibrated return expectations, legal entitlements, or policy baselines.

## 7. Required sponsor decision facts

The surplus-allocation snapshot shall admit exactly:

- `project.STATUS`;
- `project.CASH_BALANCE`;
- `project.RESERVE_REQUIREMENT`;
- `financing.RETURN_CLAIM_REMAINING`;
- `project.REINVESTMENT_REQUIREMENT`.

Required sponsor capability:

- `DISTRIBUTE_SURPLUS`.

Required sponsor objective:

- `RETURN`.

## 8. Bounded allocation policy

The bounded policy shall use no arbitrary profit threshold or payout percentage.

Given positive project cash:

1. reserve up to the admitted reserve requirement;
2. apply remaining cash to the separately declared financing-return claim;
3. apply remaining cash to the admitted local-reinvestment requirement;
4. distribute any remaining residual to project owners according to the ownership ledger.

Conceptually:

`cash = reserve + financier_return + local_reinvestment + owner_distribution`.

The policy determines category totals.

The SYSTEM validates claim identity, account identity, ownership and executable balances before moving money.

## 9. Owner distribution

Owner distribution shall be routed pro rata to current explicit project ownership shares.

For Test 010A, project `P` remains:

`SPN = 1.0`.

Therefore any owner distribution goes to the sponsor's own registered account.

This does not imply that all future projects have one owner.

## 10. Revenue remains project cash until allocation

Test 009A revenue shall remain in the project's cash account until Test 010A executes.

Sale shall not be retroactively changed to pay owners or financiers directly.

This preserves the causal sequence:

`buyer -> project revenue -> project allocation -> capital return / reinvestment / owner distribution`.

## 11. RICH qualification case

Test 009A leaves:

`project cash = 80`.

Test 010A structural allocation shall produce:

- reserve = `20`;
- financier return = `30`;
- local reinvestment = `10`;
- owner distribution = `20`.

After execution:

- project cash = `20`;
- financier account increases by `30`;
- local reinvestment account increases by `10`;
- sponsor owner account increases by `20`;
- financing-return claim remaining = `0`.

## 12. SPARSE qualification case

Test 009A leaves:

`project cash = 60`.

Test 010A structural allocation shall produce:

- reserve = `20`;
- financier return = `30`;
- local reinvestment = `10`;
- owner distribution = `0`.

Thus owner distribution is residual after the explicit reserve/claim/reinvestment sequence.

## 13. NULL qualification case

Test 009A leaves:

`project cash = 0`.

Expected sponsor outcome:

`DEFER / NO_DISTRIBUTABLE_CASH`.

No distribution transaction may occur.

## 14. Transaction semantics

Test 010A shall distinguish at least:

- `FINANCIER_RETURN`;
- `LOCAL_REINVESTMENT`;
- `OWNER_DISTRIBUTION`.

Reserve is retained project cash and requires no cash-transfer transaction.

Financier return and owner distribution may both physically return funds to an Earth account, but their economic/legal semantics must remain distinct in the ledger.

## 15. Distribution record

Every executed allocation shall record:

- year;
- project id;
- sponsor decision id;
- opening project cash;
- reserve;
- financier-return claim id and amount;
- local-reinvestment amount/account;
- owner-distribution total;
- per-owner allocation and transaction ids;
- closing project cash;
- all transaction ids;
- source lineage/version.

## 16. Required hostile/falsification tests

Test 010A shall verify at minimum:

1. policy evaluation alone mutates no money;
2. UNKNOWN reserve requirement blocks before worker;
3. UNKNOWN financing-return claim blocks before worker;
4. UNKNOWN reinvestment requirement blocks before worker;
5. no `DISTRIBUTE_SURPLUS` capability defers;
6. non-`OPERATING` project defers;
7. zero cash defers;
8. negative fixture values are rejected;
9. forged decision cannot distribute more than current project cash;
10. wrong financing-claim/project linkage is rejected;
11. wrong financier destination account is rejected;
12. financing return cannot exceed remaining claim;
13. owner distribution cannot bypass current ownership shares;
14. owner shares must still sum to one;
15. duplicate execution of one distribution decision is rejected;
16. distribution does not alter resource inventory or resource remaining;
17. distribution does not mutate project ownership;
18. A1–A9 remain satisfied;
19. deterministic replay is exact;
20. raw post-allocation account tampering remains epoch-detectable.

## 17. No debt/equity doctrine

Test 010A does not classify the Test 001 financier instrument as real-world debt, preferred equity, common equity, royalty finance, streaming finance, project finance, or any other legal structure.

The financing-return claim is a bounded structural abstraction proving that financier cash return can be represented separately from equity ownership.

## 18. No profitability claim

A RICH project returning cash does not establish profitability.

A single cycle does not include all lifecycle costs, taxes, transport, processing, maintenance, depreciation, closure, or opportunity cost.

Test 010A demonstrates cash-allocation mechanics only.

## 19. Explicitly outside scope

Test 010A does not authorize:

- empirical financing terms;
- interest-rate or IRR calibration;
- debt-service schedules;
- preferred/common equity waterfalls;
- royalties;
- taxes;
- carried interest;
- liquidation preference;
- dilution;
- new financing rounds;
- retained-earnings optimization;
- endogenous reinvestment opportunity search;
- repeated operating/sale cycles;
- country/macro feedback;
- FRD mutation.

## 20. Epistemic standing

Passing Test 010A establishes structural surplus allocation, return, reinvestment and owner-distribution mechanics only.

All Test 010A numeric allocation fixtures remain TEST_ONLY / NOT_CALIBRATED / NOT_POLICY_BASELINE.
