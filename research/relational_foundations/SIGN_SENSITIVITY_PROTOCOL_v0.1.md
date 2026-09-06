# LOOM 2226 — Curvature Sign-Sensitivity Protocol v0.1

**Status:** NON-CANON / NON-RUNTIME EXPERIMENT  
**Purpose:** Test whether the recovered curvature-term sign is responsible for the R4 movement toward stronger expander behavior.

## Source boundary

The historical/reconstructed action remains frozen as:

`S_historical = +alpha * curvature_sum`

The experimental comparison is:

`S_experimental = -alpha * curvature_sum`

The minus-sign form is **not** historical reproduction. It is a new hypothesis motivated by the source audit.

## Matched smoke matrix

- `N = 40`
- degree `4`
- seeds `2226`, `2227`
- `30` proposal steps
- strengths `0.5`, `1.0`
- action curvature sampling cap `20` edges
- same random-regular initialization
- same degree-preserving connected double-edge-swap proposal
- same Metropolis temperature and acceptance
- same diagnostic implementation

Cells:

- null
- historical `+alpha * curvature_sum`
- experimental `-alpha * curvature_sum`

## Primary comparison

For each matched strength compare:

- mean path/log(N)
- normalized-Laplacian spectral gap
- historical sampled-curvature diagnostic field

The corrected-sign variant is directionally consistent with weaker expansion only if it has both:

1. longer mean path/log(N) than the historical-sign cell; and
2. smaller mean spectral gap than the historical-sign cell.

A **provisional corrected-sign candidate** additionally requires every seed to exceed the surviving historical path gate `1.3 * log(N)`.

## Interpretation

A directional reversal without gate crossing is useful evidence that the sign convention matters, but it is not evidence of emergent geometry.

A gate crossing is still not an RQO-1 PASS. It would only justify freezing that corrected-sign cell for increasing-N, longer-chain, multi-seed testing.

## Hard stop

Do not add triangle terms, new curvature definitions, causal orientation, internal clocks, target geometry, M1/M2 mechanisms, or canon implications in this experiment.