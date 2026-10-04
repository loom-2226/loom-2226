# Phase 3B Kernel Validation Record 009 — Underwriting Inputs, Ensemble Guardrails, A1–A9 Property Verification, and Edge Hardening

**Status:** PASS FOR AUTONOMOUS-POLICY PRE-GATE ITEMS 1–4 / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Development branch:** `offworld-mvp-phase3`
**Validated branch head before this record:** `29a76b11b9fa384102100c7b54e04782f75c373d`
**Predecessor baseline:** `offworld-mvp-build4-mvp-r4-resolution-invariance-2026-10-04`

## 1. Purpose

Implement the next four prerequisites selected before any autonomous underwriting policy:

1. authored underwriting input contract/table;
2. ensemble-reporting guardrails;
3. scheduler-valid property verification of A1–A9 after every generated transition;
4. boundary, staged-WIP, and genuine multi-rate edge hardening.

Autonomous-policy authority remains closed.

## 2. Full regression result

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**80 tests executed; 80 passed.**

## 3. Underwriting input contract

Added:

- `PHASE3B_UNDERWRITING_INPUT_CONTRACT_CANDIDATE_0_1.md`;
- `inputs/OFFWORLD_MVP_UNDERWRITING_VALIDATION_V0_1.json`;
- `offworld_kernel/underwriting.py`;
- underwriting contract tests.

The minimum required input kinds are:

- PRICE;
- EXPLORATION_CAPEX;
- DEVELOPMENT_CAPEX;
- OPERATING_COST;
- LEAD_TIME.

Each executable input carries:

- stable id;
- archetype;
- value/unit;
- status;
- source/rationale reference;
- sensitivity range;
- optional validity interval.

UNKNOWN is explicit and may not carry a number.

### Validation-only table

For `GENERIC_RESOURCE_PROJECT_MVP`, the current table contains:

- PRICE = 20 MODEL_CURRENCY_PER_RESOURCE_UNIT, sensitivity 10–40;
- EXPLORATION_CAPEX = 10 MODEL_CURRENCY, sensitivity 5–20;
- DEVELOPMENT_CAPEX = 60 MODEL_CURRENCY, sensitivity 30–120;
- OPERATING_COST = 4 MODEL_CURRENCY_PER_RESOURCE_UNIT, sensitivity 2–8;
- LEAD_TIME = 2 YEARS, sensitivity 1–5.

All five are explicitly:

`AUTHORED_SCENARIO / PRE_CONTRACT_AUTHORED_SCENARIO / VALIDATION_ONLY_NOT_EMPIRICAL_NOT_PRODUCTION`.

They are not empirical estimates and shall not be promoted by repeated use.

Underwriting table fingerprint:

`7b4f93a0518b333af8c23fa272f57e73b47d0cb842a8907cade5cd18e61fab07`.

The table can be converted into admitted immutable DecisionSnapshot facts, preserving value, source/rationale, and unit. This provides a policy-input route without allowing policy-local fallback numbers.

## 4. Ensemble reporting guardrails

Added executable `EnsembleReporter` semantics.

Spread meaning is now tied to axis class:

- SCENARIO -> `SCENARIO_SPREAD_NOT_PROBABILITY`;
- PARAMETER -> `PARAMETER_SENSITIVITY`;
- UNCERTAINTY -> `UNCERTAINTY_SPREAD`;
- STOCHASTIC_KEY -> `STOCHASTIC_VARIABILITY`.

A stochastic-key example with values 1 and 3 reports:

- minimum 1;
- maximum 3;
- meaning `STOCHASTIC_VARIABILITY`;
- `probability_weighted = false`.

Probability-weighted mean requires an explicit `ProbabilityWeightAuthority` that:

- names an authority reference;
- covers exactly all included cases;
- has no negative weights;
- sums to one.

No default equal-probability interpretation exists.

Mean-with-interval is rejected without explicit probability authority and remains deliberately unimplemented even with authority until interval semantics are separately governed.

## 5. A1–A9 identity basis

The executable identity register preserves the supplied financing-v2 definitions:

- A1 transaction debit/credit and locations;
- A2 account roll-forward;
- A3 commitment outstanding = committed - disbursed - lapsed;
- A4 project-cash roll-forward including cash held between disbursement and spending;
- A5 WIP/exploration-WIP/knowledge/productive-asset roll-forwards;
- A6 exhaustive surplus decomposition;
- A7 project owner shares sum to one;
- A8 every revenue has an Earth-boundary or local-buyer payer;
- A9 physical stock closes as opening stock minus extraction.

Added:

`PHASE3B_ACCOUNTING_IDENTITY_REGISTER_0_1.md`

and executable:

`offworld_kernel.accounting.AccountingIdentityAuditor`.

## 6. Scheduler-valid property verification

A deterministic seeded validation SYSTEM now generates transitions from the set valid in current state and executes them through the sealed scheduler runtime.

Before every generated transition:

`AccountingPeriodSnapshot.capture(...)`

pins the applicable state.

Immediately after every transition:

`AccountingIdentityAuditor.check_all()`

checks A1 through A9.

The suite runs:

- 20 independent deterministic seeds;
- 80 scheduled transitions per seed;
- **1,600 scheduler-valid generated transitions**;
- **14,400 A-identity evaluations**.

Observed action coverage across the 1,600 transitions:

- commission: 20;
- depreciation: 183;
- disburse: 233;
- extract: 256;
- lapse: 232;
- sell/revenue: 182;
- surplus decomposition: 211;
- WIP spend: 46;
- no-op valid steps: 237.

The suite asserts that all material action families above occur across the seeded sample.

Identical seed + steps replays to identical action sequence, identity results, and scheduled-run fingerprint.

### A5 scope caveat

The generative property fixture exercises construction WIP, capitalization and productive depreciation.

Exploration-WIP -> knowledge/writeoff remains covered by dedicated Build 3 fixtures rather than by this random generator. Therefore the result is not claimed as exhaustive property coverage of every A5 sub-lane.

## 7. A6 surplus decomposition

Added explicit `SurplusDecompositionRecord`.

For each recorded surplus:

`Surplus = Reserve + LocalReinvest + ReturnToEarth + LocalRetention + OtherInvestment`.

The record rejects negative components and non-exhaustive decomposition.

Non-reserve dispositions create explicit transactions. Reserve remains in project cash.

## 8. Signed Earth-boundary reconciliation

Build 4 now records each Earth-boundary account's opening balance.

Generic transfers update the signed boundary mirror when a boundary account is source or destination. Explicit boundary purchase continues to support a negative signed position.

The invariant now requires, for each Earth boundary:

`account_balance - opening_balance = transaction_inflows - transaction_outflows = boundary_net`.

Validation case:

- boundary purchase: -100;
- return to boundary: +30;
- closing account position: **-70**;
- mirror position: **-70**;
- transaction-ledger net: **-70**.

Deliberately changing only the mirror to -69 causes invariant failure.

## 9. True staged multi-year WIP

The strengthened fixture now performs:

- year 2: WIP spend 20;
- year 3: additional WIP spend 30;
- year 4: commission the same WIP identity at 50;
- year 5: depreciate productive asset by 10%.

Observed states:

- y2: accumulated 20, commissioned 0;
- y3: accumulated 50, commissioned 0;
- y4: accumulated 50, commissioned 50, productive book value 50;
- y5: productive book value **45.00**.

FCF events preserve the same WIP identity across both formation years:

- y2 = 20;
- y3 = 30.

This is a genuine staged construction test, not merely two expenditures in the same year.

## 10. Genuine multi-rate synchronization

The scheduler fixture now combines three distinct cadences:

- day-scale mission observation;
- quarterly financing;
- annual Earth-system update.

Events are inserted in reverse order to prevent insertion order from supplying semantics.

Observed execution order:

1. mission-day30;
2. finance-q1;
3. finance-q2;
4. mission-day200;
5. finance-q3;
6. earth-annual;
7. mission-day365;
8. finance-q4.

Observed project-cash state at synchronization points:

- day 30: 0;
- after Q1: 1;
- after Q2: 2;
- day 200: 2;
- after Q3: 3;
- annual Earth event at t=1.0: 3;
- day-365 observation at t=1.0: 3;
- Q4 financing at t=1.0: 4.

At the shared t=1.0 timestamp, phase semantics therefore produce:

`EXOGENOUS_INPUTS -> OBSERVATION -> COMMITMENT_DISBURSEMENT`.

Multi-rate scheduled result fingerprint:

`e370db953d33036c41f1fce0337501b06fadf20d7ba7333cdd2a914357b08e43`.

This validates scheduler synchronization semantics across the three cadences. It is not a claim of continuous-time physical fidelity.

## 11. Documentation

Added:

- `PHASE3B_UNDERWRITING_INPUT_CONTRACT_CANDIDATE_0_1.md`;
- `PHASE3B_ENSEMBLE_REPORTING_GUARDRAILS_0_1.md`;
- `PHASE3B_ACCOUNTING_IDENTITY_REGISTER_0_1.md`;
- `PHASE3B_MVP_HARDENING_ITEMS_1_4_DECISION_001.md`.

Updated:

- `OFFWORLD_MVP_GUIDING_FRD.md`;
- `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`.

## 12. Remaining autonomous-policy blockers

Items 1–4 requested in this pass are implemented at the stated verification level.

Still open before autonomous-policy authorization:

1. held-out/out-of-sample disclosure in validation manifests;
2. full code/Git hash in replay manifests;
3. schema-to-ODD drift checking;
4. defining the first autonomous underwriting request/decision schema and reason codes, including `BLOCKED_UNKNOWN`;
5. replacing validation-only underwriting numbers with evidence-derived or explicitly governed production scenario inputs before any production claim;
6. broader A5 generative coverage if exploration/knowledge transitions are brought into the first autonomous vertical slice.

## 13. Result

The first underwriting policy can no longer legitimately invent its price, capex, opex or lead time; ensemble reports cannot silently manufacture probabilities; all nine financing-v2 identities are checked after every transition in a seeded scheduler-valid stress suite; and the three accounting/time edge cases raised in review now have executable regression tests.

**Autonomous-policy authority remains closed.**
