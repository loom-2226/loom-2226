# LOOM 2226 — RQO-1 Source Audit v0.1

**Date:** 6 September 2026  
**Status:** NON-CANON / NON-RUNTIME RESEARCH AUDIT

## Purpose

Record source-level issues discovered after reproducing the historical AUIF null (R3) and isolating the recovered curvature/triangle action terms (R4). This document does **not** rewrite the historical implementation. Historical reconstruction remains frozen; corrected variants must live in separate experimental modules.

## Recovered source status

The surviving 28 August 2026 File Library artifacts are:

- `rqo1_experiment.py`
- `RQO-1_protocol.md`

They establish the mechanics recorded in `RQO1_HISTORICAL_SOURCE_NOTE_v0.1.md`. Git currently contains a labeled reconstruction/adaptation, not a claim of byte-for-byte archival identity with those File Library objects.

## Audit finding A — curvature-action sign

Recovered code minimizes

`S = alpha * curvature_sum - beta * triangle_count`

under Metropolis acceptance. Therefore, with `alpha > 0`, lower/more-negative `curvature_sum` lowers the action and is favored. This is opposite to any prose interpretation that positive `alpha` rewards more-positive Ollivier–Ricci curvature.

R4 is behaviorally consistent with this observation: positive historical `alpha` reduced mean path/log(N) and increased spectral gap relative to the null at the tested smoke scale, i.e. it pushed toward stronger expander-like behavior rather than away from it.

**Audit disposition:** preserve the historical sign exactly in `rqo1_reconstruction.py`. Any `-alpha * curvature_sum` test is a new experimental action convention, not historical reproduction.

## Audit finding B — `curvature_mean_sampled` naming/denominator

The reconstructed diagnostic computes:

`curvature_sum(G, max_edges=60) / min(60, E)`

but `curvature_sum` already rescales a sampled edge sum by `E / sample_count`. For `E > 60`, dividing that rescaled estimate by `60` does not produce the estimated mean curvature per graph edge. The quantity is therefore misnamed as a mean for graphs with more than 60 edges.

**Audit disposition:** do not silently change historical/reconstruction output. Future experimental diagnostics may add a correctly named/per-edge estimator alongside the historical field.

## Audit finding C — stochastic reproducibility

The recovered source uses module-global `random.sample` in curvature and dimension sampling. The reconstruction seeds some sampling paths for repeatability, so it is not byte-identical historical behavior.

**Audit disposition:** preserve this distinction in provenance notes. Exact-compatibility and deterministic-adapted implementations should never be conflated.

## Audit finding D — fixed-N path gate is not a scaling law

The surviving provisional gate

`mean shortest path > 1.3 * log(N)`

is useful as a historical classifier, but a single fixed-N threshold is not evidence of manifold-like scaling. R3 improved this by evaluating the null across increasing N, but any positive result must ultimately survive multiple sizes, seeds, longer chains, and independent dimensional/locality diagnostics.

**Audit disposition:** retain `1.3 * log(N)` only as the historical gate. Do not promote it into a physically derived criterion.

## Experimental fork authorized by this audit

The next bounded experiment may compare:

1. the frozen historical curvature convention `+alpha * curvature_sum`; and
2. a clearly labeled sign-corrected hypothesis `-alpha * curvature_sum`.

The comparison must use the same graph initialization, proposal machinery, seeds, step count, curvature sampling cap and diagnostics. It is a sign-sensitivity test only.

A favorable corrected-sign result is **not** an RQO-1 PASS and is not evidence that curvature generically produces emergent geometry. At most it identifies a candidate convention worth a later increasing-N robustness test.

## Hard boundary

This audit changes no canon, Navigator/GIS/runtime state, M1/M2 assumptions, ship engineering, campaign databases, or production dependencies.