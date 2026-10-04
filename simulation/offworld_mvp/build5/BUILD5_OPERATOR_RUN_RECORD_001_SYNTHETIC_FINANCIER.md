# Build 5 Operator Run Record 001 — Synthetic Financier Scenario

**Classification:** OPERATOR-RUN SCENARIO RECORD  
**Status:** RECORDED / DESCRIPTIVE ONLY / NOT FORMAL TEST EVIDENCE  
**Date:** 2026-10-04  
**Operator execution host:** `quantifactus`  
**Branch:** `offworld-mvp-build5-autonomous-financier`  
**Executed Git commit:** `0553b11440f794da4c8c3fb1ad0dc3fe8c91653e`

## 1. Purpose

This record preserves the project owner's observed execution of the Build 5 Test 001 synthetic financier scenario.

It is intentionally **not** a formal qualification result and does not authorize or calibrate the numeric policy parameters used by the scenario.

The run demonstrates only that, under the declared synthetic inputs and executable state recorded below, the autonomous financier produced the observed decisions and scheduler-mediated state changes shown in this record.

This record must not be cited as evidence of:

- empirical finance calibration;
- real-world financier behavior;
- production forecast validity;
- policy-parameter authority;
- observation-model calibration;
- economic realism.

## 2. Operator-run authority boundary

The numeric inputs remained:

`TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE`

The operator did not grant them policy-baseline status by running the scenario.

This operator record is descriptive evidence of execution, not parameter authority.

## 3. Raw operator artifact

Raw output file on the operator host:

`/home/ubuntu/LOOM-output/BUILD5_TEST001_OPERATOR_RUN_001.txt`

Raw file line count:

`93`

Raw file SHA-256:

`d64745f215225c7b24374abd53a1b94e914118f316bee8edabfb8616240b5165`

## 4. Observed provenance

The operator run reported:

- executable source-tree SHA-256: `48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c`;
- reconstructed Git-object source-tree SHA-256: identical;
- linkage: `GIT_OBJECT_VERIFIED=True`;
- policy: `FINANCIER_SCREENING_V1`;
- policy manifest: `BUILD5_TEST001_SYNTHETIC_PARAMS_V0_1`;
- manifest status: `TEST_ONLY`;
- parameter-manifest SHA-256: `b4bf09605f4f48a07957b5bbf561ba33cf887ad2c0e68b3df722a9ef7f8de535`;
- policy version: `FINANCIER_SCREENING_V1:0.1:3014a328a26629fe635c4b19cbf63846fa8a3dd818cb3f21081ad7dc6626c9d9`;
- observation relation: `PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION`.

## 5. Observed execution

The operator observed:

- POSITIVE signal:
  - prior `0.20`;
  - posterior `0.5`;
  - outcome `APPROVE`;
  - reason `APPROVED_POLICY_RULE`;
  - amount `60`;
  - instrument `EQUITY`.

- NEGATIVE signal:
  - prior `0.20`;
  - posterior `0.05882352941176470588235294118`;
  - outcome `REJECT`;
  - reason `BELOW_RETURN`;
  - amount `0`.

- Integrated APPROVE fixture:
  - financier cash `40`;
  - project cash `60`;
  - commitment present;
  - commitment disbursed `60`;
  - A1-A9 all reported;
  - execution order `financier-decision,finance-execute`.

- Integrated REJECT fixture:
  - financier cash `100`;
  - project cash `0`;
  - no commitment;
  - A1-A9 all reported.

- Replay observation:
  - repeated APPROVE result fingerprint equality: `True`;
  - repeated APPROVE decision equality: `True`.

These are operator-observed scenario outputs under synthetic inputs. They are not empirical estimates.

## 6. Preserved raw output

```text
LOOM 2226 — BUILD 5 TEST 001 OPERATOR RUN 001
CLASSIFICATION=OPERATOR_RUN_SCENARIO_RECORD
FORMAL_TEST_RESULT=NO
EMPIRICAL_CALIBRATION=NO
FORECAST_BASELINE=NO
PARAMETER_AUTHORITY=TEST_ONLY
GIT_BRANCH=offworld-mvp-build5-autonomous-financier
GIT_COMMIT=0553b11440f794da4c8c3fb1ad0dc3fe8c91653e
RUN_UTC=2026-10-04T03:41:17Z

=== PROVENANCE ===
CODE_TREE_SHA256=48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c
GIT_OBJECT_CODE_TREE_SHA256=48393762bf0f151c826e4734d9c8caf0e73a9205b27a20a19e311bba7202014c
GIT_OBJECT_VERIFIED=True
POLICY_ID=FINANCIER_SCREENING_V1
POLICY_MANIFEST_ID=BUILD5_TEST001_SYNTHETIC_PARAMS_V0_1
POLICY_MANIFEST_STATUS=TEST_ONLY
POLICY_MANIFEST_SHA256=b4bf09605f4f48a07957b5bbf561ba33cf887ad2c0e68b3df722a9ef7f8de535
POLICY_VERSION=FINANCIER_SCREENING_V1:0.1:3014a328a26629fe635c4b19cbf63846fa8a3dd818cb3f21081ad7dc6626c9d9
OBSERVATION_KNOWLEDGE_RELATION=PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION

=== DECLARED SYNTHETIC INPUTS ===
agent_detection_rate=0.80 UNIT=PROBABILITY STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE
agent_false_positive_rate=0.20 UNIT=PROBABILITY STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE
horizon_years=10 UNIT=YEARS STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE
hurdle_rate=0.20 UNIT=DIMENSIONLESS_ANNUAL_RATE STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE
max_concentration_fraction=0.80 UNIT=DIMENSIONLESS_SHARE STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE
normalized_throughput=10 UNIT=MODEL_RESOURCE_UNIT_PER_YEAR STATUS=TEST_ONLY AUTH_REF=TEST_ONLY:BUILD5_TEST001_SYNTHETIC_FIXTURE:NOT_POLICY_BASELINE

=== OBSERVED SIGNAL CASE: POSITIVE ===
PRIOR_RESOURCE_EXISTS=0.20
POSTERIOR_RESOURCE_EXISTS=0.5
OUTCOME=APPROVE
REASON_CODE=APPROVED_POLICY_RULE
APPROVED=True
AMOUNT=60
INSTRUMENT=EQUITY
DECISION_ID=DEC-fecd9c60404e753885ff
INPUT_SNAPSHOT_REF=decision-snapshot:1:6835b63c72041fc620c7f6eb72e12bdac3021f7042907daf8cf94756d783c4a2
WORKER_FINGERPRINT=27fb4e0acdf9ef1f87df06ce31832935d6ae208ab6962e9c678b78a90186da23

=== OBSERVED SIGNAL CASE: NEGATIVE ===
PRIOR_RESOURCE_EXISTS=0.20
POSTERIOR_RESOURCE_EXISTS=0.05882352941176470588235294118
OUTCOME=REJECT
REASON_CODE=BELOW_RETURN
APPROVED=False
AMOUNT=0
INSTRUMENT=
DECISION_ID=DEC-b8d89e68999eac1d37eb
INPUT_SNAPSHOT_REF=decision-snapshot:1:c1f79f7e4a0908a2604bc4b3fe25f3aeb906bc9290d5bfc9f672f423b5f7c710
WORKER_FINGERPRINT=d687a43f08b3e7d2d0c4a1138295d7442f0213807bef8399428912b46a51431f

=== OBSERVED INTEGRATED CASE: APPROVE_FIXTURE_RUN_1 ===
BELIEF_RESOURCE_EXISTS=0.50
OUTCOME=APPROVE
REASON_CODE=APPROVED_POLICY_RULE
FINANCIER_CASH=40
PROJECT_CASH=60
COMMITMENT_PRESENT=True
COMMITMENT_DISBURSED=60
ACCOUNTING_IDENTITIES=A1,A2,A3,A4,A5,A6,A7,A8,A9
EXECUTION_LOG=financier-decision,finance-execute
RESULT_FINGERPRINT=792bd1bd8a562d026912ce3677ef5ddde7ecbeebe091a2ce138eb8c85a740a0e

=== OBSERVED INTEGRATED CASE: REJECT_FIXTURE ===
BELIEF_RESOURCE_EXISTS=0.05
OUTCOME=REJECT
REASON_CODE=BELOW_RETURN
FINANCIER_CASH=100
PROJECT_CASH=0
COMMITMENT_PRESENT=False
ACCOUNTING_IDENTITIES=A1,A2,A3,A4,A5,A6,A7,A8,A9
EXECUTION_LOG=financier-decision,finance-execute
RESULT_FINGERPRINT=2d7df7388cf0cd549a4d78a71b13cf703384bfc67968fa95d74c17532693e6a1

=== OBSERVED INTEGRATED CASE: APPROVE_FIXTURE_RUN_2_REPLAY ===
BELIEF_RESOURCE_EXISTS=0.50
OUTCOME=APPROVE
REASON_CODE=APPROVED_POLICY_RULE
FINANCIER_CASH=40
PROJECT_CASH=60
COMMITMENT_PRESENT=True
COMMITMENT_DISBURSED=60
ACCOUNTING_IDENTITIES=A1,A2,A3,A4,A5,A6,A7,A8,A9
EXECUTION_LOG=financier-decision,finance-execute
RESULT_FINGERPRINT=792bd1bd8a562d026912ce3677ef5ddde7ecbeebe091a2ce138eb8c85a740a0e

=== OBSERVED REPLAY COMPARISON ===
RESULT_FINGERPRINT_EQUAL=True
DECISION_EQUAL=True

END_OF_OPERATOR_OBSERVATION
```

## 7. Standing

This record closes no empirical or parameter-calibration claim.

It may be referenced by the Build 5 structural validation record as operator-observed execution of the synthetic scenario.

Formal structural qualification remains grounded in the governed test suite and associated provenance checks, not in this operator-run output.
