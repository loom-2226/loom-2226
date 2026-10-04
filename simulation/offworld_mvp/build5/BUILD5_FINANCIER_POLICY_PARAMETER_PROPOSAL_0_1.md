# Build 5 Financier Policy Parameter Proposal 0.1

**Status:** SUPERSEDED FOR TEST 001 CLOSURE / NOT AUTHORIZED / TEST-ONLY VALUES
**Date:** 2026-10-04

This document formerly isolated a possible human-authority decision for Build 5 Test 001. That closure approach was superseded on 2026-10-04 by the decision to keep the synthetic values un-authorized and record an operator-observed scenario instead.

The implementation already uses the following values as synthetic verification fixtures. They are proposed as the initial **MVP validation-policy baseline**, not as empirical estimates of real financiers or real offworld projects.

| Parameter | Proposed value | Unit | Sensitivity range | Local perturbation |
| --- | ---: | --- | --- | ---: |
| hurdle_rate | 0.20 | DIMENSIONLESS_ANNUAL_RATE | 0.05–0.40 | 0.01 |
| horizon_years | 10 | YEARS | 5–20 | 1 |
| agent_detection_rate | 0.80 | PROBABILITY | 0.60–0.95 | 0.02 |
| agent_false_positive_rate | 0.20 | PROBABILITY | 0.05–0.40 | 0.02 |
| normalized_throughput | 10 | MODEL_RESOURCE_UNIT_PER_YEAR | 5–20 | 1 |
| max_concentration_fraction | 0.80 | DIMENSIONLESS_SHARE | 0.50–1.00 | 0.05 |

Observation-model relation proposed for Test 001:

`PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION`.

Under that assumption, the Agent's 0.80 detection rate and 0.20 false-positive rate equal the world fixture's rates. The Agent therefore knows the likelihood model exactly but does not know hidden truth.

## Semantic caveat

`FINANCIER_SCREENING_V1` is a verification policy, not a calibrated investment model.

Its return measure is explicitly:

`MVP_VALIDATION_RETURN_PROXY_V1`.

`normalized_throughput` exists to make the price/opex/capital screening calculation dimensionally coherent. It is not an empirical production-capacity estimate.

`max_concentration_fraction` exists to exercise the CONCENTRATION branch. It is not claimed to represent a real institutional portfolio limit.

Authorizing this proposal would authorize these numbers **only for the Build 5 Test 001 MVP validation policy**. It would not promote them to empirical truth or production calibration.


## Supersession note

Build 5 Test 001 structural closure no longer depends on authorizing this parameter proposal.

The synthetic values remain `TEST_ONLY / NOT_POLICY_BASELINE` and were used only in an operator-observed scenario preserved in:

`BUILD5_OPERATOR_RUN_RECORD_001_SYNTHETIC_FINANCIER.md`

This proposal remains in repository history for provenance. It is not an active authorization request and must not be interpreted as a policy baseline.
