# Phase 3B Underwriting Input Contract Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN CANDIDATE
**Date:** 2026-10-04
**Autonomous-policy authority:** NOT GRANTED

## Purpose

Prevent future underwriting policies from inventing economic inputs merely because a return calculation requires them.

The MVP underwriting interface requires five input kinds per project archetype:

1. PRICE
2. EXPLORATION_CAPEX
3. DEVELOPMENT_CAPEX
4. OPERATING_COST
5. LEAD_TIME

Every input carries:

- stable input id;
- archetype scope;
- value and unit;
- epistemic/status class;
- source or rationale reference;
- sensitivity range where characterized;
- optional validity interval.

UNKNOWN is explicit and may not carry a numeric value.

## Validation table

The initial table is:

`inputs/OFFWORLD_MVP_UNDERWRITING_VALIDATION_V0_1.json`.

It is deliberately labeled:

`PRE_CONTRACT_AUTHORED_SCENARIO / VALIDATION_ONLY_NOT_EMPIRICAL_NOT_PRODUCTION`.

The values exist only to exercise future policy mechanics. They are not empirical estimates and must not be promoted by repeated use.

## Production rule

A production-capable underwriting table must replace validation values with either:

- admitted evidence-derived inputs; or
- explicitly governed scenario-authorized inputs.

No policy may supply a fallback number when the table returns UNKNOWN.

## Current authored validation values

For `GENERIC_RESOURCE_PROJECT_MVP`:

| Kind | Value | Unit | Sensitivity |
| --- | ---: | --- | --- |
| PRICE | 20 | MODEL_CURRENCY_PER_RESOURCE_UNIT | 10–40 |
| EXPLORATION_CAPEX | 10 | MODEL_CURRENCY | 5–20 |
| DEVELOPMENT_CAPEX | 60 | MODEL_CURRENCY | 30–120 |
| OPERATING_COST | 4 | MODEL_CURRENCY_PER_RESOURCE_UNIT | 2–8 |
| LEAD_TIME | 2 | YEARS | 1–5 |

These are synthetic authored scenario values only.
