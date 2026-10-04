# Phase 3B MVP Hardening Items 1–4 Decision 001

**Status:** ACCEPTED IMPLEMENTATION DECISION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Autonomous-policy authority:** NOT GRANTED

This pass implements the four prerequisites selected after Resolution-Invariance R4.

## 1. Underwriting input authority layer

The first policy may not invent PRICE, EXPLORATION_CAPEX, DEVELOPMENT_CAPEX, OPERATING_COST or LEAD_TIME.

The validation table is explicitly synthetic/authored and PRE-CONTRACT. It exists to exercise interfaces, not to calibrate real economics.

## 2. Ensemble reporting guardrails

Scenario sampling carries no implicit probability. Stochastic-key spread is variability. Weighted summaries require explicit probability authority.

## 3. Scheduler-valid A1–A9 property verification

The exact A1–A9 identities from the supplied financing v2 architecture are executable.

A seeded state-aware SYSTEM validation driver generates valid scheduled transitions. A fresh accounting snapshot is taken before every transition and all nine identities are checked after every transition.

The validation driver is not an autonomous Agent policy.

## 4. Accounting/time edge cases

The pass adds:

- explicit reconciliation of signed Earth-boundary mirror state to both account delta and transaction-ledger delta;
- genuine staged WIP: year-2 spend, year-3 spend, year-4 commissioning, year-5 nonzero depreciation;
- a multi-rate synchronization fixture combining day-scale mission observations, quarterly finance and annual Earth-system cadence.

## Non-claims

This pass does not:

- empirically validate underwriting values;
- authorize a financier policy;
- assign probabilities to scenarios;
- claim exhaustive A5 exploration/knowledge property coverage;
- claim the scheduler is a continuous-time physics engine.
