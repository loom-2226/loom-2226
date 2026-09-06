# LOOM 2226 — Corrected-Sign Scaling Protocol v0.1

**Status:** NON-CANON / NON-RUNTIME EXPERIMENT  
**Purpose:** Test whether the directional curvature-sign effect observed in the N=40 smoke experiment persists with a larger graph, an additional seed, and longer chains before any new action term is invented.

## Prior result being tested

The bounded sign-sensitivity experiment found that, at strengths 0.5 and 1.0, the experimental action

`S_experimental = -alpha * curvature_sum`

produced longer paths and smaller normalized-Laplacian spectral gaps than the recovered historical convention

`S_historical = +alpha * curvature_sum`.

Neither corrected-sign cell crossed the surviving historical `1.3 * log(N)` non-expander gate. The result therefore established sign sensitivity only, not emergent locality or geometry.

## Frozen follow-up cell

This experiment freezes `alpha = 1.0`, because it was already tested in the prior sign-sensitivity matrix and showed the larger matched sign separation there. This is a follow-up sensitivity choice, not a newly fitted optimum and not a claim that 1.0 is physically preferred.

No triangle term or other new action term is added.

## Matched scaling matrix

- sizes: `N = 40, 80`
- degree: `4`
- seeds: `2226, 2227, 2228`
- proposal steps: `2 * N`
  - N=40: 80 steps
  - N=80: 160 steps
- curvature sampling cap inside the action: `20` edges
- temperature: `1.0`
- strength: `alpha = 1.0`

At every `(N, seed)` run three matched cells:

1. null: `S = 0`
2. historical sign: `S = +alpha * curvature_sum`
3. experimental corrected sign: `S = -alpha * curvature_sum`

The historical reconstruction module remains unchanged.

## Primary questions

### Q1 — Does the sign-direction effect persist across N?

At each N, the corrected-sign cell must have both:

- larger mean `path_over_logN` than the historical-sign cell; and
- smaller mean spectral gap than the historical-sign cell.

This is a sign-sensitivity result only.

### Q2 — Does the corrected-sign cell beat the null in the locality direction?

At each N, compare corrected sign with null using the same two directional diagnostics:

- larger mean `path_over_logN`;
- smaller mean spectral gap.

This is more demanding than merely outperforming the historical sign.

### Q3 — Does anything cross the surviving historical gate?

Record whether every corrected-sign seed at a given N has

`path_over_logN > 1.3`.

The `1.3` threshold is retained only as a historical/provisional gate. It is not treated as a derived scaling law.

## Interpretation classes

The output may report independently:

- `sign_direction_persists_all_sizes`
- `corrected_beats_null_directionally_all_sizes`
- `corrected_crosses_gate_all_sizes_all_seeds`

Only the last item is a provisional non-expander candidate under the surviving historical gate. Even then, it is not an RQO-1 PASS and would require substantially longer-chain, larger-N, multi-seed validation plus independent dimension and pathology checks.

Failure to beat the null is scientifically useful: it means correcting the historical sign removes one confound but does not by itself generate locality.

## Hard stop

Do not add new curvature definitions, triangle/cycle rewards, causal orientation, internal clocks, target geometry, M1/M2 mechanisms, or canon implications in this experiment.