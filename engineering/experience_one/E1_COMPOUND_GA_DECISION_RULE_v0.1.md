# Experience One — Compound Geometric Admissibility Decision Rule v0.1

**Class:** ENGINEERING QUALIFICATION SUPPORT  
**Date:** 14 September 2026  
**Scope:** SUPPORTS_E1 only  
**Status:** NON-CANON / NON-RUNTIME-POLICY

## Purpose

Qualify a deterministic decision rule for Compound Geometric Admissibility using the evidence classes already earned in the E1 Neptune chain, without inventing scalar scores, weights, compensation, or numerical thresholds that have not been physically qualified.

## Decision rule

The rule is a fail-closed three-state conjunction across required axes:

- any qualified `HARD_FAIL` -> `INADMISSIBLE`;
- no hard fail but one or more `UNRESOLVED_REQUIRED` -> `INDETERMINATE_NOT_CERTIFIABLE`;
- all required axes satisfied -> `ADMISSIBLE`.

Unknown is neither zero nor pass. Unknown is also not automatically a physical failure.

No cross-axis compensation is allowed. A strong result on one axis cannot erase missing or adverse evidence on another axis.

## Current E1 Neptune evaluation

The decision rule itself can be qualified even though the current Neptune endpoint is not yet certifiable under that rule.

Current axis disposition:

- local geometry: qualified J2-corrected local tidal reference exists, but no governed geometry admissibility criterion/bound yet;
- local stress-energy: qualified non-material standard-GR screen;
- causal structure: ordinary standard-GR horizon-like pathology is non-material, but Loom-specific metric-domain causal structure remains unresolved;
- domain size: configuration-bound meaning is qualified, numerical translation-domain geometry remains unresolved;
- Loom coherence: model form is qualified, scenario acceptance criterion remains unresolved;
- lattice coherence: model form is qualified, scenario acceptance criterion remains unresolved.

Therefore the current decision is:

`INDETERMINATE_NOT_CERTIFIABLE`

This does **not** reject the earned E1 operational handoff. It means the newly formalized GA rule is not yet entitled to certify it as a general physical admissibility result.

## Authority boundary

No runtime policy is bound. No campaign state is mutated. No endpoint is moved. No LLM receives calculation authority. No unresolved axis is silently promoted to satisfied.

## Next bounded question

Qualify the minimum scenario-specific acceptance evidence needed to move the remaining required axes from `UNRESOLVED_REQUIRED` to a certifiable disposition without reopening broad foundational research.
