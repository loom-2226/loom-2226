# LOOM 2226 — Relational Foundations
## Matter-Induced Locality Protocol v0.1

**Status:** PREREGISTERED EXPERIMENT DESIGN — NON-CANON — NON-RUNTIME  
**Code status:** NOT YET IMPLEMENTED  
**Purpose:** Test whether a coordinate-free Gaussian-matter determinant term can push a random-regular relational ensemble away from expander behavior without directly encoding a target geometry.

## 1. Research question

Does the induced effective action of a massless Gaussian scalar field on a dynamical graph produce a robust locality-like phase, either alone or in combination with the already-qualified corrected curvature sign, without generating only trivial bottlenecks or near-tree pathologies?

## 2. Frozen graph ensemble and moves

Use the existing RQO-1 graph machinery unless a technical defect is discovered before implementation:

- simple connected undirected graph;
- random-regular initialization;
- degree = 4;
- degree-preserving connected double-edge swaps;
- Metropolis acceptance;
- temperature `T = 1.0`;
- no embedded coordinates;
- no target lattice or hand-picked dimension.

The historical reconstruction module must remain untouched.

## 3. Frozen action cells

For a connected graph `G`, define

```text
Gamma_matter(G) = 0.5 * log det' L_G
```

with the constant Laplacian zero mode omitted.

Use four cells only:

```text
NULL:
    S_0 = 0

CORRECTED_CURVATURE:
    S_C = -1.0 * curvature_sum

MATTER_ONLY:
    S_M = +1.0 * Gamma_matter

COMBINED:
    S_CM = -1.0 * curvature_sum + 1.0 * Gamma_matter
```

The coefficients are fixed at unity for the first experiment. There is no sign scan and no coupling scan. `+Gamma_matter` is the Gaussian-induced sign; it is not selected from observed graph behavior.

The corrected curvature action uses the already-qualified experimental sign and must remain clearly labeled as non-historical.

## 4. Numerical definition of `log det' L`

Implementation must compute the nonzero eigenvalues of the symmetric combinatorial Laplacian and evaluate

```text
log det' L = sum_i log(lambda_i), lambda_i > tolerance.
```

For connected graphs exactly one eigenvalue should be numerically zero. The implementation must fail closed if the zero-mode count is inconsistent with connectivity or if a retained eigenvalue is non-positive beyond numerical tolerance.

For validation, at small `N` the numerical result must agree with Kirchhoff's matrix-tree theorem:

```text
log det' L = log N + log tau(G)
```

within an explicit numerical tolerance.

No spectral-gap or dimension diagnostic may be reused inside the action.

## 5. Stage A — phone qualification matrix

First implementation/qualification is intentionally modest:

- `N = 40`
- degree `4`
- seeds `2226, 2227, 2228`
- proposals `2 * N = 80`
- curvature action sample cap `20` edges, matching the recently qualified phone-scale corrected-sign follow-up
- four frozen action cells above

This is a smoke/qualification experiment, not an RQO-1 verdict.

If Stage A exhibits an obvious numerical or structural pathology, stop and diagnose before any scaling run.

## 6. Required diagnostics

Preserve the existing diagnostics where valid and add explicit pathology diagnostics. Minimum output per run:

- degree mean / variance;
- average shortest path;
- `path_over_logN`;
- diameter;
- normalized Laplacian spectral gap;
- clustering;
- triangle count;
- bridge count;
- articulation-point count;
- edge connectivity;
- node connectivity where tractable;
- size of largest component after removal of the single most damaging edge or articulation point, if one exists;
- `log_det_prime_laplacian`;
- `log_spanning_tree_count = log_det_prime_laplacian - log N`;
- final action value;
- acceptance fraction.

Existing spectral-dimension and volume-growth diagnostics may be recorded as descriptive measurements if computationally practical, but they are not Stage-A pass criteria.

## 7. Preregistered comparisons

For each seed compare:

### Matter effect versus null

Matter-only is directionally locality-like only if the aggregate result has:

- larger mean `path_over_logN` than null; and
- smaller mean spectral gap than null.

### Combined effect versus corrected curvature

Combined is directionally locality-like beyond corrected curvature only if it has:

- larger mean `path_over_logN` than corrected-curvature-only; and
- smaller mean spectral gap than corrected-curvature-only.

These are directional diagnostics only. They are not sufficient for a candidate phase.

## 8. Pathology veto

A run/cell is vetoed as structurally pathological if its apparent non-expander movement is dominated by fragile bottlenecks rather than distributed local structure.

Stage A must report, not hide, the following failure signatures:

- bridge count increases materially relative to null;
- articulation points appear systematically where null has few/none;
- edge/node connectivity collapses;
- one-edge or one-vertex removal splits the graph into large lobes;
- graphs become near-tree-like or barbell-like;
- the determinant action simply drives spanning-tree count downward through global fragility.

No exact numerical pathology threshold is invented in advance for the smoke run because the current source program does not provide a validated one. Stage A is therefore classified conservatively as one of:

- `NO DIRECTIONAL EFFECT`
- `DIRECTIONAL EFFECT WITH BOTTLENECK PATHOLOGY`
- `DIRECTIONAL EFFECT WITHOUT OBVIOUS BOTTLENECK PATHOLOGY`

The third category earns a separately preregistered scaling experiment. It is not an RQO-1 pass.

## 9. Historical gate retained only as reference

The surviving historical provisional gate

```text
avg_shortest_path > 1.3 * log(N)
```

must still be reported, but it remains a historical placeholder rather than a statistically derived law. Crossing it at `N=40` would not establish a phase and would not override the pathology veto.

## 10. Hard stop conditions

Do not proceed to larger `N`, tune coefficients, or add more terms if:

- the determinant implementation fails the matrix-tree validation;
- the new term only creates bottlenecked/crumpled structures;
- the effect is absent or inconsistent across seeds;
- a code change would require modifying the historical reconstruction;
- interpretation would require importing target geometry into the action.

If the term fails cleanly, record the negative result and move to a different independently motivated action family.

## 11. Explicitly forbidden during this experiment

- triangle/square/loop rewards;
- target spectral dimension;
- direct spectral-gap optimization;
- path-length or diameter terms in the action;
- community/modularity rewards;
- effective-resistance optimization;
- causal orientation or internal clock;
- M1/M2 tuning or canon consequences;
- Navigator/GIS/runtime imports or state changes.

## 12. Success ladder

Stage A can only earn permission for a Stage B scaling preregistration.

RQO-1 remains:

```text
relation-first ensemble
→ robust non-expander/local phase
→ finite emergent dimension
→ continuum geometry
```

with a stop sign between every arrow.

No result from this protocol validates LOOM physics.
