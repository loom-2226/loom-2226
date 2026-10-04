# Phase 3B Kernel Validation Record 010 — Build 5 Entry Gates G5-1 through G5-4

**Status:** PASS FOR BUILD-5 ENTRY GATES / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Development branch:** `offworld-mvp-phase3`
**Validated executable/documentation head:** `d78c7379d295b3f3cf25771f02a68e166a9ccdbb`
**Predecessor baseline:** `offworld-mvp-build4-mvp-r5-underwriting-accounting-2026-10-04`

## 1. Purpose

Close the four final Build 4 substrate/interface gates required before Build 5 may branch:

- G5-1 exact replay provenance;
- G5-2 explicit held-out/out-of-sample validation standing;
- G5-3 executable-schema to ODD drift detection;
- G5-4 immutable financing request/decision protocol with bounded outcomes and reason codes.

This record authorizes Build 4 closure and Build 5 branch creation only. It does not authorize autonomous policy behavior.

## 2. Regression result

Executed on `quantifactus` from a fresh Git archive of the complete `simulation/offworld_mvp/phase3b` tree.

The archive run was pinned with:

`LOOM_GIT_COMMIT=d78c7379d295b3f3cf25771f02a68e166a9ccdbb`.

Command:

`python3 -m unittest discover -s tests -v`

**92 tests executed; 92 passed.**

The complete suite includes all prior Build 2–4 / R1–R5 regression tests plus the four Build 5 entry-gate tests.

## 3. G5-1 — Replay provenance

Added:

- `offworld_kernel/provenance.py`;
- exact provenance fields in `ScheduledRunResult`;
- replay-manifest regression tests;
- `PHASE3B_REPLAY_PROVENANCE_CONTRACT_0_1.md`.

Every integrated scheduled run now carries:

- repository identity;
- exact 40-hex Git commit;
- SHA-256 of the executable `offworld_kernel` Python source tree;
- input snapshot ids;
- parameter-manifest ids;
- table-manifest ids;
- scheduler contract version;
- scheduler plan fingerprint;
- initial/final state fingerprints;
- execution/event-results fingerprint;
- provenance fingerprint;
- final result fingerprint.

Archive/export runs require exact `LOOM_GIT_COMMIT`; checkout runs may use `git rev-parse HEAD`.

The executable Python source-tree hash is not treated as a substitute for Git identity. Both are retained.

### Validation run example

For the scheduled payment fixture at validated head:

- Git commit: `d78c7379d295b3f3cf25771f02a68e166a9ccdbb`;
- executable code SHA-256: `41f266849d120cf0ff56c90e6054de9611ee1ff1a97f4fd4dc2a26aa2c7d9c6e`;
- input snapshot: `SYNTH_STRICT`;
- parameter manifest: `PARAMS_SHA256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`;
- table manifest: `NO_EXTERNAL_TABLES`;
- provenance fingerprint: `3b89be896c829229a39d2bdaa03c750295a425d46ec8c19dea7887de970a81da`;
- scheduler plan fingerprint: `a4adf7e46852e62aedc3e469505c5b96d31d723b068f9e85873efa0e77d11c40`;
- execution fingerprint: `7ecf47bc81f8cb8536140b82069a233dd26c686f18a983af2681bd0348ab419f`;
- final state fingerprint: `229190f7a904105eb7f8cac66ae5d083ef79d594872da9ffa12b2c95eb5c820b`;
- result fingerprint: `03393650317fafa4193b6f8c3e342674dd996ff53aee38b49359388fbb73237d`.

A future Build 5 run consuming the underwriting table must identify that table/version/fingerprint rather than use `NO_EXTERNAL_TABLES`.

## 4. G5-2 — Validation standing

`ValidationManifest` now carries explicit:

- calibration-set references;
- validation-set references;
- held-out set references;
- out-of-sample status;
- out-of-sample disclosure.

Statuses are:

- `NOT_APPLICABLE`;
- `IN_SAMPLE_ONLY`;
- `HELD_OUT`;
- `OUT_OF_SAMPLE`;
- `MIXED`.

Rules verified:

- `NOT_EMPIRICALLY_VALIDATED` must use `NOT_APPLICABLE`;
- empirical validation claims may not omit out-of-sample standing;
- held-out/out-of-sample/mixed claims require held-out references;
- empirical validation claims require an explicit disclosure;
- `VAL6_OUT_OF_SAMPLE` requires `OUT_OF_SAMPLE` or `MIXED`;
- calibration/validation target overlap still requires explicit disclosure.

This prevents an in-sample fit from quietly acquiring out-of-sample language.

## 5. G5-3 — Executable-to-ODD drift detection

Added:

- `offworld_kernel/schema_registry.py`;
- a machine-readable registry embedded in `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`;
- `tests/test_odd_schema_drift.py`.

The registry covers the core runtime/interface dataclasses, including:

- Node / Account / Transaction / Commitment / Project / Asset;
- SystemState / AggregateState / EntityAssetRef / AgentState;
- ScenarioResource / Observation / ColonyState / PopulationLedger;
- DecisionSnapshot / PolicyContext;
- ScheduledEvent / CouplingSpec;
- UnderwritingInput / UnderwritingTable;
- ResolutionExposurePlan / ResolutionExposureRecord;
- FinancingRequest / FinancingDecision.

The test compares the executable dataclass field lists exactly against the ODD JSON block.

A registered field addition, removal or rename without an ODD update fails the regression suite.

The Build 5 financing fields are explicitly covered.

## 6. G5-4 — Financing request / decision protocol

Added:

- formal Build 5 fields/enums to `mvp_state.py`;
- `offworld_kernel/financing_protocol.py`;
- `PHASE3B_FINANCING_REQUEST_DECISION_PROTOCOL_0_1.md`;
- six protocol tests.

### Request contract

A Build 5 financing request requires:

- sponsor/project/year/stage;
- positive amount;
- unit/currency;
- disclosed observations;
- exact required underwriting keys.

The required underwriting keys are exactly:

- `underwriting.PRICE`;
- `underwriting.EXPLORATION_CAPEX`;
- `underwriting.DEVELOPMENT_CAPEX`;
- `underwriting.OPERATING_COST`;
- `underwriting.LEAD_TIME`.

### Decision outcomes

Allowed outcomes are exactly:

- `APPROVE`;
- `REJECT`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

A decision carries:

- financier id;
- amount/instrument;
- human-readable reason;
- machine reason code;
- unknown-input keys;
- pinned input-snapshot reference;
- policy version;
- decision version.

Rules verified:

- APPROVE requires positive funding and an instrument;
- approval may not exceed the request;
- all non-APPROVE outcomes carry zero funding;
- unknown required inputs cannot hide under REJECT/DEFER;
- required unknowns force `BLOCKED_UNKNOWN`;
- `BLOCKED_UNKNOWN` requires `BLOCKED_REQUIRED_INPUT_UNKNOWN` and explicit unknown keys.

The decision artifact does not mutate the world. Commitment/disbursement remains a later scheduler/kernel transition.

## 7. ODD / FRD / methodology updates

Updated:

- `OFFWORLD_MVP_GUIDING_FRD.md`;
- `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`;
- `PHASE3B_VERIFICATION_VALIDATION_UNCERTAINTY_PROTOCOL_0_1.md`.

Added:

- `PHASE3B_IMPLEMENTATION_AUTHORIZATION_003_BUILD5_GATE_CLOSURE.md`;
- `PHASE3B_REPLAY_PROVENANCE_CONTRACT_0_1.md`;
- `PHASE3B_FINANCING_REQUEST_DECISION_PROTOCOL_0_1.md`.

## 8. Gate determination

All four Build 5 entry gates pass at the stated verification level.

Therefore:

1. Build 4 may be formally closed and frozen;
2. a Build 5 branch may be created from that closed baseline;
3. autonomous policy behavior remains separately gated and is **not** authorized by this record.

## 9. Remaining Build 5 Test 001 requirements

The first autonomous financier experiment still requires a separate Build 5 implementation authorization and must demonstrate at minimum:

- immutable DecisionSnapshot-only policy input;
- deterministic replay by snapshot/request/policy/key;
- `BLOCKED_UNKNOWN` behavior;
- no direct world mutation by policy;
- NULL/SPARSE/RICH decision identity while admitted information is identical;
- controlled divergence only after admitted information differs;
- A1–A9 survival;
- full provenance including underwriting-table identity;
- counterfactual attribution to changed admitted inputs.

## 10. Standing

Build 4 remains:

- PRE-CONTRACT;
- SINGLE-AUTHORITY;
- NOT_EMPIRICALLY_VALIDATED.

The passed gates establish a verified substrate/interface baseline, not a validated civilization forecast.
