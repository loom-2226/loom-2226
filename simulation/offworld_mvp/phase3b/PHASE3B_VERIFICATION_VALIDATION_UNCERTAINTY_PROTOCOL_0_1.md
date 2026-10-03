# Phase 3B Verification, Validation and Uncertainty Protocol 0.1

**Status:** METHODOLOGY CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY

## 1. Core distinction

LOOM shall not use passing software tests as evidence that simulated civilization trajectories are empirically valid.

The methodology distinguishes:

- **verification:** implementation matches declared model/rules;
- **validation:** model behavior is adequate for a stated real-world or scientific purpose;
- **calibration:** parameter estimation/selection against declared targets/data;
- **sensitivity analysis:** response to parameter/model/initial-state variation;
- **uncertainty analysis:** propagation and attribution of characterized uncertainty;
- **scenario exploration:** conditional trajectories under authored assumptions.

## 2. Verification ladder

V1 schema/type validation.
V2 local transition pre/postconditions.
V3 conservation/invariant tests.
V4 deterministic replay.
V5 coupling/scheduler tests.
V6 metamorphic/property tests.
V7 cross-implementation or independent calculation where practical.

A result may pass verification and still have no empirical validation standing.

## 3. Validation ladder

When applicable and data exist:

VAL1 face/domain review.
VAL2 component empirical comparison.
VAL3 stylized-pattern comparison.
VAL4 historical/backcast trajectory test.
VAL5 cross-sectional/cross-case comparison.
VAL6 out-of-sample or withheld-period test.
VAL7 policy/decision-use validation for the intended question.

Not every subsystem can reach every level. Missing validation must be disclosed, not converted into a zero-risk claim.

## 4. Calibration rules

Calibration targets, periods and loss/fit metrics are declared before evaluating calibration success where practical.

Parameters fitted to a target cannot validate against that same target without disclosure.

Scenario stipulations are not calibrated parameters unless explicitly treated as such.

## 5. Sensitivity

Each consequential authored parameter must eventually be classified as:

- fixed by evidence/standard;
- calibrated;
- scenario axis;
- nuisance/uncertainty axis;
- validation-only fixture value.

Sensitivity should include local perturbation for debugging and global/ensemble exploration for interaction/nonlinearity where consequential.

## 6. Uncertainty

Preserve:

- characterized empirical uncertainty;
- model/structural uncertainty;
- parameter uncertainty;
- scenario uncertainty;
- stochastic variability;
- uncharacterized uncertainty.

Scenario probabilities are not implied merely because scenarios are sampled.

## 7. Long-horizon rule

Outputs toward 2226 are conditional scenario trajectories, not point forecasts, unless a later governed forecasting claim earns that status.

The long-horizon analysis layer shall emphasize ensembles, robustness, divergence drivers, thresholds and causal explanation rather than a single privileged future.

## 8. Model comparison

Competing submodels may be run side by side. A fit advantage on one metric does not silently promote one model to universal authority.

## 9. Validation manifests

A run/report intended for interpretation carries:

- verified components/tests;
- validation level by subsystem;
- calibration targets used;
- uncertainty axes varied;
- scenario assumptions;
- coverage/limitations;
- known unvalidated mechanisms.

## 10. Current standing

Build 4-derived work has strong kernel verification for selected accounting, ownership, replay and epistemic invariants.

It does not yet have empirical behavioral validation for financing decisions, migration, settlement formation, production, prices, resource economics or long-run civilization development.
