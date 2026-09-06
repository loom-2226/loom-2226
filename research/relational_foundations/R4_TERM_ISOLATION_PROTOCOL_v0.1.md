# LOOM 2226 — R4 Historical Term-Isolation Protocol v0.1

**Status:** NON-CANON / NON-RUNTIME RESEARCH  
**Purpose:** Isolate the two recovered RQO-1 action terms before any new action family is proposed.

## Question

Does either recovered term — sampled Ollivier–Ricci curvature or triangle/short-cycle bias — move the coordinate-free degree-4 ensemble away from the reproduced AUIF expander null, and does the combination do more than either component alone?

R4 is an attribution experiment, not a final RQO-1 verdict.

## Frozen mechanics

- no supplied Euclidean coordinates or target manifold;
- random-regular initial graph, degree 4;
- recovered connected degree-preserving double-edge-swap proposals;
- recovered Metropolis acceptance rule;
- recovered action convention `S = alpha * curvature_sum - beta * triangle_count`;
- recovered diagnostics and provisional non-expander path gate `mean shortest path > 1.3 * log(N)`.

No new physics term is permitted in R4.

## Qualification matrix

Pixel qualification intentionally remains smoke-scale so curvature LP cost cannot obscure basic attribution:

- `N = 40`;
- `seeds = 2226, 2227`;
- `30` Metropolis proposal steps per run;
- strengths `0.5` and `1.0`;
- action cells:
  - null `(alpha=0, beta=0)`;
  - curvature-only `(0.5,0)`, `(1.0,0)`;
  - triangle-only `(0,0.5)`, `(0,1.0)`;
  - combined `(0.5,0.5)`, `(1.0,1.0)`.

For phone qualification, curvature evaluation inside the MCMC action is capped at 20 sampled edges. Final diagnostics retain the reconstructed diagnostic implementation. This computational cap is recorded in output and means R4 qualification is **not** a claim of exact historical parameter reproduction.

## Attribution outputs

For every action cell and seed record:

- mean shortest path and path/log(N);
- diameter;
- normalized-Laplacian spectral gap;
- clustering;
- triangle count;
- sampled mean Ollivier–Ricci curvature;
- final action.

Aggregate by cell and report deltas against the null mean. For matched strengths, also report whether the combined cell exceeds the curvature-only and triangle-only path-ratio means.

## Interpretation gates

A cell is a **provisional non-expander candidate** only when every seed for that cell crosses the surviving `1.3 * log(N)` path gate.

R4 does not declare an RQO-1 PASS even if a cell crosses. Any candidate must survive R5 increasing-N, longer-chain, multi-seed robustness and diagnostic cross-checks.

Because this qualification is only `N=40`, two seeds, and 30 steps, ordinary stochastic differences from the null are reported descriptively but are **not** labeled a demonstrated term effect. The classifier therefore has only two scientific categories:

1. **NO GATE CROSSING** — no non-null cell crosses the historical non-expander gate across all seeds. Deltas remain descriptive only.
2. **PROVISIONAL CANDIDATE** — at least one cell crosses the historical gate across all R4 seeds; freeze that recovered cell and proceed to R5 without changing the action.

No new effect-size threshold is invented in R4.

## Hard stop

Do not introduce a new action, causal orientation, internal clock, M1/M2 mechanism, or canon implication during R4. If R4 produces a candidate, the next step is R5 robustness of that same recovered action family.