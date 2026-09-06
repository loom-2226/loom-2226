# RQO-1 Historical Source Note v0.1

**Status:** NON-CANON / NON-RUNTIME / HISTORICAL RESEARCH RECONSTRUCTION  
**Date:** 6 September 2026

## Recovery result

The project File Library contains two surviving 28 August 2026 source artifacts:

- `rqo1_experiment.py`
- `RQO-1_protocol.md`

These materially improve the earlier reconstruction. The implementation itself survives in the File Library even though it was not present in the current Git repository.

This repository note records what those sources actually establish. It does **not** claim a byte-for-byte archive of the File Library objects; a byte-preserved copy should be added later if the original file bytes are exported directly.

## Recovered experiment contract

The RQO-1 question was whether a relation-first graph ensemble, with no embedded coordinates, target lattice, or hand-picked dimension, could develop a stable broad non-expander / locally low-dimensional phase.

The implementation used:

- random-regular graphs as the null/baseline starting ensemble;
- fixed degree under evolution;
- Metropolis Monte Carlo;
- degree-preserving double-edge-swap proposals;
- action

  `S(Gamma) = alpha * sum_(i,j in E) kappa(i,j) - beta * C3`

  where `kappa` is Ollivier-Ricci curvature and `C3` is triangle count;
- lazy random-walk measures with idle mass 0.5;
- Wasserstein-1 distance solved by linear programming;
- curvature sampling during MCMC for tractability;
- multiple `(alpha, beta)` cells and independent seeds.

Recovered default reference scan values from the original script:

- `N = 200`
- average degree `4`
- script entry point `n_steps = 300`
- alpha grid `[0.0, 0.5, 1.0, 2.0]`
- beta grid `[0.0, 0.5, 1.0, 2.0]`
- seeds `[2226, 2227, 2228]`
- curvature sample size `60` edges

## Recovered diagnostics

The original implementation calculated:

- degree mean and variance;
- average shortest-path length;
- `log(N)` comparison;
- diameter;
- normalized-Laplacian spectral gap;
- average clustering coefficient;
- triangle count;
- spectral dimension from random-walk return probability;
- Hausdorff / volume-growth dimension;
- sampled mean Ollivier-Ricci curvature.

The broader hypotheses document also proposed Cheeger/expansion diagnostics, finite perturbation robustness, and a Hessian/fluctuation spectrum. Those were proposed RQO-1 metrics but are **not present in the recovered Python implementation** and must not be retroactively described as executed.

## Recovered provisional gate

The implementation classified a cell as a non-expander candidate when every tested seed satisfied:

`average_shortest_path > 1.3 * log(N)`

A scan passed only if at least three distinct `(alpha, beta)` cells qualified.

The protocol explicitly labels both `1.3 * log(N)` and the three-cell threshold as placeholders requiring stronger statistical justification before a rigorous scientific verdict.

## Historical result status

The protocol states that the smoke-tested run used approximately `N=40`, only two trial cells, and 30 MCMC steps, and returned FAIL. It also explicitly states that this was far too small and short to count as a scientific RQO-1 result.

The exact two historical trial cells and their complete output are not specified in the surviving protocol text currently available to this reconstruction. Therefore this repository must not invent them.

The actual prior negative result remains the earlier AUIF-v1 lesson documented in the hypotheses paper:

- generic sparse finite-degree relation-first graphs tended toward random-regular / expander-like states (`expander soup`);
- cycle-sensitive terms could produce conditional locality but risked encoding the desired geometry in the Hamiltonian;
- an internal clock improved Lorentzian-looking causal behavior but did not derive GR;
- the correct project decision was to stop.

## Reconstruction discipline

The new implementation lane therefore separates three things:

1. **Historical source contract** — what the surviving 2026 source says.
2. **Diagnostic controls** — modern tests that establish whether our measurement code can distinguish obvious graph classes.
3. **New experiment runs** — only after the first two are qualified.

No historical parameter or output may be silently filled in from memory. Unknown means unknown.
