# LOOM 2226 — Relational Foundations
## Stage-A Instrumentation Addendum v0.1

**Status:** PREREGISTRATION AMENDMENT — NON-CANON — NON-RUNTIME  
**Applies to:** `MATTER_INDUCED_LOCALITY_PROTOCOL_v0.1.md` before any Stage-A result exists.  
**Reason:** Independent hostile review identified two instrumentation gaps: multi-edge bottlenecks can evade bridge/articulation tests, and the corrected-curvature comparator has not yet been qualified as stable under longer chains.

## 1. No action-family change

This addendum does **not** change the four frozen Stage-A action cells, coefficients, seeds, graph size, proposal count, temperature, or anti-answer-smuggling rules.

No Stage-A matter-action result has been generated before this amendment.

## 2. Multi-edge bottleneck instrumentation

Bridge count and articulation-point count are insufficient to veto a graph composed of dense lobes joined by a small multi-edge cut. Therefore Stage A must additionally report diagnostics that can detect sparse cuts and concentrated transport load even when no single bridge or articulation point exists.

Required additions:

- a conductance / Cheeger-style bottleneck estimate, with the exact computational approximation documented;
- edge-betweenness concentration and node-betweenness concentration, including at least max and a normalized concentration summary;
- low-mode eigenvector localization / inverse participation ratio (IPR) when available at negligible additional eigensolver cost.

Community-size summaries may be recorded descriptively but are not a success criterion.

These quantities are diagnostics only. None may enter the microscopic action.

## 3. Pathology-veto interpretation

A matter-only or combined cell is vetoed if its apparent locality-like movement is primarily explained by sparse-cut or load-concentration pathology, including a multi-edge barbell structure with:

- few or no bridges;
- few or no articulation points;
- anomalously low conductance;
- strongly concentrated betweenness;
- localized low-lying Laplacian modes.

A decrease in spectral gap is not independent evidence of locality when the action itself is a Laplacian spectral functional. Structural diagnostics outside the single spectral-gap statistic therefore carry special weight in Stage-A interpretation.

## 4. Corrected-curvature baseline qualification hold

Before Stage A is implemented or executed, the corrected-curvature comparator must undergo the separately preregistered longer-chain work package in `CURVATURE_CONVERGENCE_PROTOCOL_v0.1.md`.

That work package tests trajectory stability at `2N`, `5N`, and `10N` using the same recovered sampled-curvature implementation.

Important limitation: the current sampled curvature action is stochastic because `curvature_sum(..., max_edges=20)` samples edges through `random.sample`. Therefore the convergence work package may establish persistence/stability of the previously observed directional effect, but it may not claim rigorous equilibrium of a deterministic Metropolis target.

Stage A remains on hold until that result is reviewed and the status of the curvature comparator is explicitly recorded.

## 5. Historical and runtime firewalls

- Do not modify `rqo1_reconstruction.py` to satisfy this addendum.
- Do not silently reinterpret previous PR #14 results as equilibrium results.
- No Navigator/GIS/runtime, SQLite, deploy, canon, M1, or M2 changes.

## 6. Review provenance

This amendment is made **before** any matter-determinant Stage-A output exists, in response to an independent hostile review of the source-audited Relational Topography packet. It is therefore an instrumentation correction, not a post-result change of success criteria.
