# LOOM 2226 — Relational Foundations Historical Reconstruction v0.1

**Date:** 6 September 2026  
**Status:** RESEARCH PROVENANCE NOTE — NON-CANON — NON-RUNTIME  
**Purpose:** Recover and preserve the earlier relation-first / emergent-locality work before any new relational-foundations implementation begins.

---

## 1. Executive finding

The earlier work was more advanced than the current GitHub tree suggested.

The project did not merely discuss relational emergence conceptually. It previously built and smoke-tested a concrete first reopened experiment, **RQO-1 — Expander-Soup Avoidance Test**, together with a protocol and a Python reference implementation.

Recovered source artifacts from the project file archive:

- `RQO-1_protocol.md` — created 28 August 2026.
- `rqo1_experiment.py` — created 28 August 2026.
- `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf` — created 27/28 August 2026; preserves the earlier AUIF-v1 failure history and the rationale for RQO-1.

These files were not found in the current GitHub default-branch tree during the 6 September repository review. They therefore count as recovered project-history evidence rather than current repository authority.

---

## 2. What the historical record says happened

### 2.1 AUIF v1 — original failure

The earlier microscopic relation-first model started from sparse finite-degree relational graphs with no ordinary spatial embedding.

The key result was negative:

- generic sparse finite-degree graph ensembles tended toward random-regular / expander-like states;
- typical graph distances remained too short;
- locality did not emerge;
- low-dimensional manifold-like behavior was not obtained for free.

Project shorthand: **expander soup**.

The first major lesson was therefore:

> Relations first is not sufficient. Generic relations do not automatically produce useful locality.

### 2.2 Short-cycle intervention

The earlier work then added cycle-sensitive terms. These could produce a conditional low-dimensional/local phase, but the project correctly identified a methodological problem: rewarding short loops may simply encode the geometry we wanted into the action.

The preserved anti-soup rule is:

> desired geometry encoded in the Hamiltonian is not the same as geometry derived from the Hamiltonian.

### 2.3 Internal-clock intervention

An internal-clock constraint produced more promising long-wavelength Lorentzian-looking behavior and a causal cone.

The project stopped short of claiming success because this did **not** derive:

- Einstein field equations;
- Standard Model matter;
- a complete quantum theory;
- or a demonstrated GR/QFT infrared limit.

That stop decision remains valid.

---

## 3. Recovered RQO-1 experiment

The 28 August RQO-1 package was explicitly designed as a rerun of the AUIF-v1 failure with a sharper falsification gate.

### 3.1 Research question

Can a relation-first graph ensemble, with:

- no embedded coordinates;
- no target lattice;
- no hand-picked dimension;

produce a broad, stable, non-expander / locally low-dimensional phase under an independently motivated intrinsic graph action?

### 3.2 State and dynamics

The reference implementation used:

- a random-regular graph baseline;
- degree-preserving double-edge-swap proposals;
- Metropolis Monte Carlo evolution;
- fixed-degree graph topology as the microscopic state.

The tested action was:

```text
S(Gamma) = alpha * sum_(i,j in E) kappa(i,j) - beta * C3
```

where:

- `kappa(i,j)` is discrete Ollivier-Ricci curvature;
- `C3` is triangle / short-cycle count;
- `alpha=beta=0` is the negative-control expander ensemble.

The curvature implementation used lazy random-walk neighborhood measures and Wasserstein-1 distance solved through linear programming.

### 3.3 Diagnostics

The script measured:

- degree mean and variance;
- average shortest-path length;
- comparison against `log(N)` expander scaling;
- graph diameter;
- normalized spectral gap / algebraic connectivity;
- clustering coefficient;
- triangle count;
- spectral dimension from random-walk return probability;
- Hausdorff / volume-growth dimension;
- sampled mean Ollivier-Ricci curvature.

### 3.4 Parameter scan and robustness rule

The reference scan used a grid over `(alpha, beta)` with multiple independent seeds per cell.

The nominal default grid preserved in the Python artifact was:

```text
alpha = [0.0, 0.5, 1.0, 2.0]
beta  = [0.0, 0.5, 1.0, 2.0]
seeds = [2226, 2227, 2228]
```

The script's reference run targeted approximately `N=200`, degree `4`, and several hundred MCMC steps, with comments noting intended scaling to larger N.

### 3.5 Historical pass/fail gate

A parameter cell counted as a non-expander candidate only when average shortest-path length exceeded `1.3 * log(N)` for **every seed** at that cell.

The scan only passed if at least three distinct `(alpha,beta)` cells qualified, preventing one isolated fine-tuned point from being treated as a phase.

This threshold was explicitly labelled provisional rather than theoretically derived.

### 3.6 Actual historical result recovered

The protocol records only a smoke test, not a full RQO-1 verdict.

The smoke test used approximately:

- `N=40`;
- two trial parameter cells;
- `30` MCMC steps.

It returned **FAIL**, but the protocol explicitly states that this run was far too small and short to mean anything either way.

Therefore the historical evidence does **not** support the statement that RQO-1 itself failed scientifically. It supports only:

1. AUIF v1 previously failed through expander soup;
2. RQO-1 was designed to re-test that failure more rigorously;
3. RQO-1 received a methodology smoke test;
4. no recovered artifact yet demonstrates that the full parameter scan was executed to a scientifically meaningful verdict.

---

## 4. Methodological weaknesses already identified in 2026

The protocol itself documented several limitations that must not be rediscovered as new findings:

1. **Scale:** N~40–200 smoke/reference runs are not enough to establish asymptotic phase behavior.
2. **Curvature cost:** exact Ollivier-Ricci evaluation is expensive; the MCMC action used sampled curvature at scale.
3. **Action noise:** Monte-Carlo curvature sampling introduces acceptance-noise that can move apparent phase boundaries.
4. **Pass thresholds:** `1.3 * log(N)` and the three-cell broad-region rule were placeholders, not rigorously derived.
5. **Target leakage:** the triangle term may reward precisely the local geometric structure the experiment claims to derive.
6. **Finite-dimension evidence:** leaving expander scaling is necessary but not sufficient; stable spectral and volume-growth dimension must survive increasing N and perturbation.

---

## 5. Consequence for the 6 September work plan

The project must **not** begin RF-WP1 from a blank implementation.

The correct next step is now designated **RF-WP0 — Historical Reproduction and Audit**.

RF-WP0 must:

1. preserve the recovered RQO-1 protocol and Python implementation as historical artifacts;
2. reproduce the historical smoke test from the recovered code without changing the model;
3. establish a clean standalone environment and exact dependency versions;
4. run unit checks on the recovered diagnostics and graph invariants;
5. identify any implementation defects separately from theory defects;
6. execute the intended RQO-1 grid at several N values only after reproduction succeeds;
7. replace the provisional expander cutoff with a defensible null-ensemble comparison before issuing a new scientific verdict;
8. explicitly compare curvature-only, triangle-only, curvature+triangle, and null action families so target-geometry leakage is visible;
9. produce one historical-reproduction memo before any new action family is invented.

The project shall not call the recovered RQO-1 result a PASS or FAIL until that reproduction/audit is complete.

---

## 6. Non-interference rule

This historical reconstruction remains confined to:

```text
research/relational_foundations/
```

It must not touch Navigator, Solar GIS, runtime, production SQLite databases, current canon, current governance, deployment paths, or production tests.

No Navigator/GIS release may depend on this work.

---

## 7. Current decision

**Status: CONTINUE TO RF-WP0 ONLY.**

The historical record is strong enough to justify reproduction, but not strong enough to justify new theory work yet.

The immediate question is no longer:

> Can relationships make a map?

It is now:

> Can we faithfully reproduce what we already did, establish exactly where AUIF v1 and RQO-1 actually stopped, and avoid solving the same problem twice?
