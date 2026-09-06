# LOOM 2226 — R3 AUIF Null Scaling Protocol v0.1

**Status:** NON-CANON / NON-RUNTIME RESEARCH  
**Purpose:** Reproduce the earlier AUIF null failure at increasing graph sizes before testing locality-generating terms.

## Question

Does the coordinate-free finite-degree null ensemble remain expander-like as graph size increases?

This is deliberately narrower than RQO-1. A positive R3 result means only that the historical null failure has been reproduced. It cannot establish an emergent geometric phase.

## Frozen null model

- Graph family: random regular, degree 4.
- Supplied spatial coordinates: none.
- Action coefficients: `alpha = 0`, `beta = 0`.
- Dynamics: recovered degree-preserving connected double-edge-swap Metropolis machinery.
- With zero action every valid proposal is accepted, so the dynamics samples the degree-preserving null rather than introducing a locality preference.

## Qualification matrix

- `N = 40, 80, 160`
- seeds `2226, 2227, 2228`
- `5 * N` proposal steps per run
- nine total runs

The first pass is intentionally small enough for Pixel/Termux qualification. It is not the final finite-size study.

## Recorded diagnostics

For every run record:

- degree mean and variance;
- mean shortest path;
- `log(N)`;
- mean-shortest-path / `log(N)` ratio;
- diameter;
- normalized-Laplacian spectral gap;
- mean clustering;
- triangle count;
- seed and proposal-step count;
- action coefficients and final action.

## Historical gate

The surviving RQO-1 material used a provisional non-expander threshold of mean shortest path greater than `1.3 * log(N)`.

R3 classifies the AUIF null failure as reproduced when every tested run at every tested size remains at or below that threshold. Spectral gap is recorded as a second diagnostic but is not given a newly invented pass threshold in R3.

If any run crosses the historical path-length gate, R3 reports that the old null failure was **not cleanly reproduced** and stops for inspection rather than adjusting the gate.

## Interpretation discipline

Allowed conclusion after a clean R3 result:

> The recovered coordinate-free degree-4 null remains expander-like over the tested sizes and seeds under the historical path-length gate. The earlier AUIF null failure is reproduced for this qualification matrix.

Not allowed:

- RQO-1 PASS or FAIL;
- evidence for M1 or M2;
- evidence that spacetime emerges from relations;
- tuning or adding curvature/triangle/locality terms;
- movement to RQO-2.

The next protocol step after R3 is R4 term isolation: curvature-only, triangle-only, combined, and ablation comparisons against this frozen null baseline.
