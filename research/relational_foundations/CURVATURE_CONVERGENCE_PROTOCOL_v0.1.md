# LOOM 2226 — Relational Foundations
## Corrected-Curvature Convergence / Saturation Protocol v0.1

**Status:** PREREGISTERED BOUNDED METHOD CHECK — NON-CANON — NON-RUNTIME  
**Purpose:** Determine whether the weak locality-like corrected-curvature effect reported in PR #14 persists as the same chains are extended from `2N` to `5N` and `10N`, and characterize whether the recovered sampled-curvature Metropolis implementation is stable enough to serve as the baseline for the matter-induced Stage-A experiment.

## 1. Why this work package exists

The corrected-sign scaling experiment established a reproducible directional effect at `N=40,80`: the experimental `-alpha * curvature_sum` convention produced longer paths and smaller normalized-Laplacian spectral gaps than both the recovered historical sign and the null. It did **not** establish a non-expander phase.

A subsequent independent review correctly identified a remaining methodological question: PR #14 used only `2N` proposals. The observed difference could therefore be a short-chain transient rather than a stable property of the implemented dynamics.

There is an additional implementation-level limitation that must be explicit before anyone uses the word *equilibrium*: the recovered curvature action uses a sampled curvature estimator based on global `random.sample`. With `curvature_sample_edges=20`, repeated evaluations of the same graph need not return the same action. The existing chain therefore does **not** sample a rigorously fixed deterministic Boltzmann target in the ordinary Metropolis sense.

This work package does not silently repair that historical/reconstructed behavior. It measures the behavior we actually used.

## 2. Frozen experiment

Use only:

- `N = 80`
- random-regular degree `4`
- seeds `2226, 2227, 2228`
- temperature `T = 1.0`
- corrected curvature coefficient `alpha = 1.0`
- corrected sign `S_C = -alpha * curvature_sum`
- action curvature sample cap `20` edges
- matched null cell `S_0 = 0`
- checkpoints at `2N`, `5N`, `10N` proposals = `160`, `400`, `800`

No historical positive-curvature cell is needed here; its sign behavior is already established. No triangle term, matter term, coupling sweep, sign sweep, dimension target, or new graph action is allowed.

## 3. Trajectory-preservation rule

Diagnostics can consume random numbers through historical helper functions. Therefore checkpoint diagnostics **must not be evaluated during the MCMC trajectory**.

At each checkpoint the implementation shall:

1. save `G.copy()`;
2. save the current sampled action value;
3. save accepted/proposed counts;
4. continue the chain without calling graph diagnostics.

Only after the `10N` chain has completed may diagnostics be evaluated on the saved snapshots.

This prevents diagnostics from perturbing the global RNG state and changing the later trajectory.

## 4. Required output

For every seed, cell, and checkpoint report:

- checkpoint proposal count;
- `path_over_logN`;
- average shortest path;
- normalized-Laplacian spectral gap;
- diameter;
- clustering;
- triangle count;
- accepted moves;
- valid proposals;
- acceptance fraction;
- sampled current action at checkpoint;
- action-trace mean and standard deviation over the interval ending at that checkpoint;
- lag-1 action autocorrelation when numerically defined.

The action autocorrelation is descriptive only because the action estimator itself is stochastic.

## 5. Preregistered comparison

For each checkpoint, aggregate over the three seeds.

The corrected cell is directionally locality-like relative to null at a checkpoint only if:

- corrected mean `path_over_logN` > null mean `path_over_logN`; and
- corrected mean spectral gap < null mean spectral gap.

Classification:

- `DIRECTIONAL EFFECT PERSISTS THROUGH 10N` — the above relation holds at all three checkpoints.
- `DIRECTIONAL EFFECT NOT STABLE` — it fails at one or more checkpoints.

The surviving historical `path_over_logN > 1.3` reference gate is still reported but remains provisional and is not a convergence criterion.

## 6. Saturation language

Changes from `2N -> 5N -> 10N` may be described as **growing**, **roughly stable**, or **decaying** only in plain descriptive language.

Do **not** call an apparent plateau an equilibrium plateau without a deterministic target action plus appropriate mixing/autocorrelation evidence.

## 7. Methodological interpretation gate

This work package can answer:

> Does the previously observed corrected-curvature directional effect survive longer trajectories under the same recovered sampled-action implementation?

It cannot answer:

> Has the corrected-curvature ensemble reached equilibrium?

because the sampled action is stochastic under the present implementation.

If the directional effect vanishes or changes sign, curvature-alone is weakened further and should not be used as a trusted Stage-A baseline without revision.

If the directional effect persists, the next methodological decision is whether to qualify a deterministic/full-curvature bounded control before treating corrected curvature as an equilibrium comparator. Persistence alone does not authorize an equilibrium claim.

## 8. Runtime and source firewall

- Historical `rqo1_reconstruction.py` remains untouched.
- No Navigator/GIS/runtime imports.
- No production SQLite state.
- No canon, M1, M2, metric, Loom, or engineering changes.
- Research outputs remain under the relational-foundations research output root.

## 9. Hard stop

Do not add new action terms in this work package. Do not proceed to dimension, continuum, clock, M1, or M2 analysis from these results.
