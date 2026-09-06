# LOOM 2226 — RQO-1 Recovery Protocol v0.1

**Date:** 6 September 2026  
**Status:** HISTORICAL REPRODUCTION PROTOCOL — NON-CANON / NON-RUNTIME  
**Parent plan:** `research/rabbit_holes/LOOM_2226_Relational_Foundations_Independent_Work_Plan_v0.1.md`

## 1. Objective

Reconstruct and reproduce the earlier relational-graph experiment before designing any new microscopic model.

The recovered project record indicates two distinct historical states:

1. **AUIF-era result:** generic finite-degree relational graphs remained expander-like / nonlocal rather than developing robust manifold-like locality. Local short-cycle terms improved locality but risked putting the desired answer into the action. Adding an internal clock improved causal-looking structure without deriving general relativity.
2. **RQO-1 implementation:** a later, more explicit coordinate-free graph experiment used random-regular starting graphs, degree-preserving Metropolis rewiring, curvature and short-cycle terms, and multiple locality/dimension diagnostics. The known execution was only a small smoke test and is not a valid scientific failure of the full protocol.

This protocol treats the AUIF observation as a real historical negative result and RQO-1 as an unfinished experiment requiring reproduction.

## 2. Recovery order

Before changing model dynamics:

1. locate any surviving original Python, notebook, config, output CSV/JSON, plots, shell commands, or chat-export fragments;
2. preserve recovered originals byte-for-byte under `research/relational_foundations/recovered/`;
3. record source, date, filename, hash, and confidence in provenance;
4. reconstruct only missing glue needed to execute the historical model;
5. distinguish original code from reconstructed compatibility code in file headers and commit messages.

## 3. Historical model features to reproduce

The recovery target should reproduce, where supported by surviving material:

- finite-degree / random-regular graph initialization;
- no supplied Euclidean coordinates in candidate dynamics;
- degree-preserving edge rewiring;
- Metropolis-style acceptance;
- Ollivier–Ricci or equivalent graph-curvature observable/term used historically;
- triangle / short-cycle contribution where historically present;
- spectral dimension estimate;
- volume-growth / neighborhood-growth dimension estimate;
- shortest-path scaling;
- spectral gap / expansion proxy;
- clustering / cycle diagnostics;
- deterministic random seed capture;
- parameter-grid execution.

No undocumented term should be added merely because it makes the result more geometric.

## 4. Reproduction ladder

### R0 — Environment reproduction

Identify and pin the smallest independent research environment needed to execute the recovered model. Production Navigator/GIS dependencies are out of scope.

### R1 — Smoke-test reproduction

Reproduce the known small-run behavior as closely as possible, including the historical order of magnitude (`N≈40`, very small grid, tens of MCMC steps) if supported by recovered material.

**Purpose:** implementation equivalence only. A FAIL here is not a physics result.

### R2 — Diagnostic validation

Run controls to verify that the observable suite distinguishes:

- random regular / expander-like graphs;
- explicitly geometric positive controls;
- shuffled / degree-preserving nulls.

Dimension estimators must be treated as scale-dependent diagnostics, not truth labels.

### R3 — AUIF null reproduction

Run increasing-`N` generic finite-degree graph ensembles without explicit locality-promoting terms. Determine whether expander-like behavior persists under the recovered diagnostics.

### R4 — Historical term isolation

Run, where historically defined:

- curvature-only;
- triangle/short-cycle-only;
- combined action;
- relevant ablations.

The key question is not whether any term can create locality, but whether the mechanism does more than explicitly reward lattice-like local structure.

### R5 — Scaling and robustness

Only after R1–R4 are stable:

- increase `N` across a preregistered ladder;
- run multiple fixed seeds;
- increase MCMC / equilibration budget;
- estimate uncertainty across runs;
- record finite-size effects;
- compare all candidate runs against null and positive controls.

## 5. Decision criteria

### Historical result confirmed

Record **AUIF FAILURE CONFIRMED** if generic relational finite-degree ensembles remain robustly expander-like under increasing size and validated diagnostics.

### RQO-1 remains unresolved

Record **RQO-1 UNRESOLVED** if historical dynamics cannot be reconstructed faithfully enough, or computational scale remains inadequate.

### RQO-1 negative

Record **RQO-1 NEGATIVE** only if the intended experiment is run at defensible size, seed count and equilibration, and no robust non-expander manifold-like phase survives controls.

### RQO-1 interesting

Record **RQO-1 INTERESTING** only if locality and finite effective dimension appear over a nontrivial scale window, survive seed/size checks and null comparison, and are not attributable to a term equivalent to directly imposing target locality/dimension.

No outcome promotes LOOM canon.

## 6. Required outputs

Every reproduced run must emit machine-readable artifacts containing at minimum:

- git commit SHA;
- experiment/config version;
- Python/platform/dependency versions;
- seed;
- `N`, degree and parameter values;
- burn-in / step counts;
- acceptance rate;
- locality/expansion metrics;
- dimension estimates and scale windows;
- runtime;
- pass/fail labels derived from frozen criteria.

Charts are secondary; underlying tables are authoritative.

## 7. Stop rule

Do not design RQO-2 or add a new microscopic action until this recovery protocol produces a written verdict on what AUIF actually showed and what RQO-1 actually tested.
