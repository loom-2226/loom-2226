# LOOM 2226 — Deterministic Corrected-Curvature Comparator Qualification Protocol v0.1

**Date:** 7 September 2026  
**Status:** PREREGISTERED RESEARCH PROTOCOL — NON-CANON — NON-RUNTIME  
**Parent plan:** `research/rabbit_holes/LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md` v0.4  
**Historical reconstruction:** MUST NOT be modified  
**Matter Stage A:** remains ON HOLD until this comparator verdict and the separate Stage-A instrumentation-validation gate are reviewed.

---

## 1. Question

Does the corrected-sign locality-like direction previously observed under the sampled-curvature dynamics persist when curvature energy is evaluated deterministically over **all graph edges**, so that the action is a fixed function of graph state and ordinary Metropolis interpretation is at least formally available?

This protocol does **not** test emergent geometry, continuum physics, M1, M2, chronology, or LOOM. It qualifies or demotes one candidate baseline comparator.

The prior result must be referred to as:

> **D-PROVISIONAL — sampling validity unconfirmed:** corrected-curvature locality-like direction persisted through 10N under sampled-action dynamics; equilibrium interpretation remains unqualified pending deterministic-action control.

---

## 2. Methodological debt being closed

The recovered curvature helper performs random edge sampling when `max_edges` is smaller than the graph edge count. The previous corrected-sign chains therefore evaluated a stochastic energy on repeated visits to the same graph state.

For this protocol:

`S_C(G) = -alpha * sum_{e in E(G)} kappa_OR(e)`

with:

- `alpha = 1.0`;
- lazy random-walk mass = inherited 0.5;
- all edges evaluated;
- no edge sampling in the action;
- `T = 1.0`;
- same degree-preserving connected double-edge-swap proposal family;
- no triangle, matter, path, gap, dimension, conductance, or other new action term.

Calling the historical helper with `max_edges=None` is permitted in the new module because that evaluates all edges. The historical reconstruction file itself remains immutable.

---

## 3. Frozen qualification design

### 3.1 Ensemble

- N = **40**
- degree = **4**
- simple connected undirected random-regular initial graphs
- independent seeds = **2226, 2227, 2228, 2229**
- cells:
  - `NULL`: `S_0 = 0`
  - `DETERMINISTIC_CORRECTED_CURVATURE`: `S_C = -1.0 * full_curvature_sum`

N=40 is deliberately selected before scientific output because full all-edge Ollivier-Ricci evaluation is substantially more expensive than the recovered 20-edge estimator. This is a comparator-qualification run, not a scaling claim.

### 3.2 Chain length and sampling

- proposals per chain = **200 = 5N**
- burn-in = **40 = 1N**
- post-burn diagnostic sample every **5 proposals**
- expected post-burn samples per chain = **32**
- four independent chains per cell

No chain length may be extended after looking at scientific direction. If the mixing gate fails, a longer-chain amendment must be written and committed before a rerun.

### 3.3 Recorded traces

For every chain record:

- deterministic action after each proposal;
- accepted moves;
- valid proposals;
- acceptance fraction;
- post-burn sampled `path_over_logN`;
- post-burn sampled normalized-Laplacian spectral gap;
- final graph metrics used in prior corrected-sign comparisons.

Diagnostics are not action terms.

---

## 4. Determinism contract

The corrected action must satisfy all of the following before a scientific run is allowed:

1. evaluating the same graph twice returns the same action to numerical tolerance;
2. changing Python's global random state does not change the full-curvature action;
3. the action equals `-1.0 * curvature_sum(G, max_edges=None)` on test graphs;
4. the historical `rqo1_reconstruction.py` remains unchanged;
5. no stochastic estimator is called by the corrected action path.

Failure of any item blocks the experiment.

---

## 5. Mixing / convergence qualification gate

This is a short computational qualification, so no single statistic is treated as proof of equilibrium. The following thresholds are frozen before output and are used only to determine whether the comparator is interpretable enough to proceed.

For the corrected-curvature cell, after burn-in:

- at least **30 post-burn samples per chain** must be present;
- classical **split-R-hat <= 1.10** for deterministic action, `path_over_logN`, and spectral gap where the statistic is defined;
- pooled effective sample size estimate **>= 40** for deterministic action and **>= 40** for each of `path_over_logN` and spectral gap;
- no chain may have zero valid proposals;
- acceptance fraction is always reported; there is **no post-hoc acceptance cutoff** that converts a mixing failure into success.

If one or more R-hat/ESS conditions fail, the comparator verdict is `INCONCLUSIVE_MIXING` even if the directional effect looks favorable.

These are methodology thresholds, not physics/locality success thresholds. Failing them does not count as evidence for or against Relational Topography.

---

## 6. Directional comparator test

Only if the mixing gate passes, compare the post-burn cell means.

The previously observed direction is reproduced only if both hold:

- mean corrected `path_over_logN` > mean null `path_over_logN`;
- mean corrected spectral gap < mean null spectral gap.

The historical `1.3 * log(N)` gate is reference-only and is not a success criterion here.

No single seed may be removed. No coefficient may be tuned. No third diagnostic may be substituted after output if one of the two directions fails.

---

## 7. Frozen verdict taxonomy

Exactly one primary verdict must be emitted:

- `QUALIFIED_DIRECTION_PERSISTS`
  - determinism contract passes;
  - mixing/convergence gate passes;
  - both directional comparisons reproduce.

- `QUALIFIED_DIRECTION_DOES_NOT_PERSIST`
  - determinism contract passes;
  - mixing/convergence gate passes;
  - one or both directional comparisons fail.

- `INCONCLUSIVE_MIXING`
  - deterministic action is valid;
  - one or more preregistered R-hat/ESS/mixing requirements fail.

- `IMPLEMENTATION_OR_DETERMINISM_FAILURE`
  - determinism contract or required invariants fail.

- `COMPUTATIONALLY_INTRACTABLE`
  - frozen run cannot be completed on the qualification environment without changing the preregistered scale/length.

No verdict is an emergent-locality PASS.

---

## 8. Interpretation consequences

### If `QUALIFIED_DIRECTION_PERSISTS`

Corrected full curvature may be retained as the Stage-A comparator, with the exact qualification scope recorded. This does not establish a thermodynamic phase; it only closes the specific stochastic-action defect enough for the bounded Stage-A comparison.

### If `QUALIFIED_DIRECTION_DOES_NOT_PERSIST`

Demote corrected curvature as a Stage-A baseline. The earlier D-PROVISIONAL result remains a result about sampled-action trajectories only.

### If `INCONCLUSIVE_MIXING`

Do not run matter Stage A. Decide whether a preregistered longer-chain qualification is computationally justified. Directional output from the failed-mixing run is descriptive only.

### If implementation failure / intractability

Stop and document. Scale may only be reduced by a committed protocol amendment made before comparative scientific output is inspected.

---

## 9. Required tests before phone qualification

Before releasing the runner:

- unit test exact action determinism under changed random state;
- unit test exact action matches full historical curvature helper without editing it;
- unit test graph degree/connectivity invariants after accepted proposals;
- unit tests for split-R-hat and ESS helpers on synthetic converged and pathological traces;
- functional smoke test at very small N/steps;
- existing relational-foundations unit regression suite must pass.

Substantive implementation therefore requires unit + functional research tests before user qualification.

---

## 10. Runtime/canon/track firewalls

This protocol:

- touches research files only;
- does not fit canon, hidden topology, route times, ship constants, or Mc-299m;
- adds no Track-B gauge/moduli or chronology term to Track-A dynamics;
- does not alter the matter preregistration;
- does not alter historical RQO-1 reconstruction;
- cannot promote or demote M1/M2.

---

**Protocol frozen before deterministic-comparator scientific output.**
