# Phase 3B Ensemble Reporting Guardrails 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / METHODOLOGY CANDIDATE
**Date:** 2026-10-04

## Decision

Ensemble generation does not imply probabilities.

The reporting layer distinguishes the meanings of spread by axis class:

- SCENARIO -> `SCENARIO_SPREAD_NOT_PROBABILITY`
- PARAMETER -> `PARAMETER_SENSITIVITY`
- UNCERTAINTY -> `UNCERTAINTY_SPREAD`
- STOCHASTIC_KEY -> `STOCHASTIC_VARIABILITY`

Spread across stochastic keys shall not be labeled epistemic uncertainty.

## Probability weighting

Probability-weighted summaries are forbidden unless a `ProbabilityWeightAuthority` is supplied with:

- an explicit authority reference;
- weights for exactly every included case;
- non-negative weights;
- weights summing to one.

There is no default equal-probability interpretation for scenarios.

## Mean-with-interval

Mean-with-interval reporting is forbidden without probability authority.

Even with authority, the method remains deliberately unimplemented until an interval semantics/method is separately selected. This prevents a mathematically convenient interval from silently becoming a probabilistic claim.

## Current status

The guardrails are executable in `offworld_kernel.ensemble.EnsembleReporter`.

They do not authorize probabilities for current LOOM scenarios.
