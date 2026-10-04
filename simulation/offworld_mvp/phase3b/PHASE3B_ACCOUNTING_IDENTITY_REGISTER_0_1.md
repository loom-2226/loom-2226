# Phase 3B Accounting Identity Register 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / EXECUTABLE IDENTITY REGISTER
**Date:** 2026-10-04
**Source basis:** supplied `Offworld Financing Agent — v2 Architecture.md`, §8 Revised accounting identities

The A-statements below are accounting or physical identities and must hold exactly. The M-statements in the source architecture are model rules, not accounting identities.

## A1 — Transaction balance and locality

Every transaction has one amount debited at source and the same amount credited at destination, with both economic locations recorded.

## A2 — Account roll-forward

`Balance_k(t+1) = Balance_k(t) + inflows_k(t) - outflows_k(t)`

for every account k.

## A3 — Commitment ledger

`Outstanding_f = Committed_f - Disbursed_f - Lapsed_f`

for every commitment/financier relation.

## A4 — Project cash

`Cash_j(t+1) = Cash_j(t) + Disbursed + Revenue + LocalSales - Spend - OperatingCost - Disposed`.

Executable checking uses the project cash account and the complete transaction ledger so held cash is preserved exactly.

## A5 — WIP, exploration, knowledge and productive assets

`WIP(t+1) = WIP(t) + CapexSpend - Capitalized - WriteOff`

`ExplWIP(t+1) = ExplWIP(t) + ExplorationSpend - ToKnowledge - WriteOff`

`Knowledge(t+1) = Knowledge(t) + ToKnowledge - Amortized - WriteOff`

`Asset(t+1) = (1-delta) * Asset(t) + Capitalized - WriteOff`.

Current generative A1–A9 coverage exercises construction WIP/capitalization/productive depreciation. Existing exploration fixtures separately exercise exploration-WIP to knowledge/writeoff. The property result must not be read as exhaustive coverage of every A5 sub-lane.

## A6 — Surplus decomposition

`Surplus = Reserve + LocalReinvest + sum(ReturnToEarth + LocalRetention + OtherInvestment)`.

A `SurplusDecompositionRecord` is now explicit and validates exact exhaustiveness.

## A7 — Ownership

Owner shares of each project sum to 1.

## A8 — Revenue payer

Every REVENUE transaction has a payer account: an Earth boundary or a local buyer.

The current executable check admits an Earth-boundary payer or a payer at the same economic node as the revenue recipient.

## A9 — Physical stock

`Stock(t+1) = Stock(t) - Extracted(t)`

in the world module only.

## Executable checker

`offworld_kernel.accounting.AccountingIdentityAuditor` implements A1–A9.

`AccountingPeriodSnapshot` pins the pre-transition state. The scheduler-valid generative fixture takes a fresh snapshot before every transition and evaluates all nine identities immediately after the transition.

The checker is a verification mechanism. Passing it is not empirical validation.
