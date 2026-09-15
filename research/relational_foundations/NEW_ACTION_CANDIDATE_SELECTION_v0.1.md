# LOOM 2226 — Relational Foundations
## New Action Candidate Selection v0.1

**Status:** EXPLORATORY RESEARCH DESIGN — NON-CANON — NON-RUNTIME  
**Purpose:** Select the first genuinely new relation-first action family after the recovered RQO-1 curvature/short-cycle program failed to produce a non-expander phase.

## 1. Starting point

The recovered RQO-1 program established the correct gate: a relation-first ensemble must generate a broad, stable, non-expander/local phase without embedded coordinates, a target lattice, or a hand-picked dimension. Generic finite-degree graphs remain expander-like. The recovered short-cycle term risks encoding the desired answer directly. The corrected Ollivier-Ricci sign produces a reproducible locality-like directional bias but still does not approach the historical non-expander gate.

Therefore the next action must add a new physical/mathematical mechanism rather than another tuned graph-shape reward.

## 2. Anti-answer-smuggling rules

A candidate action is rejected before coding if it directly contains any of the following:

- Euclidean coordinates or distances;
- a target lattice, manifold, dimension, diameter, path length, spectral dimension, Hausdorff dimension, or desired spectral gap;
- an explicit reward for triangles, squares, fixed cycle lengths, clustering, communities, modularity, or geometric neighborhoods;
- a penalty whose sole rationale is "expanders are bad";
- a fitted term chosen because a prior run moved a diagnostic in the desired direction;
- a causal/time variable before the spatial/locality gate is passed.

Diagnostics may measure these quantities after evolution, but the action may not optimize them directly.

## 3. Candidate families considered

### A. More curvature engineering

Examples: curvature variance, higher powers of Ollivier-Ricci curvature, mixed curvature moments.

**Decision:** defer. These are useful later as controlled higher-curvature tests, but immediately adding them would risk turning the project into parameter tuning around a term already shown to be insufficient.

### B. Additional short-cycle / motif actions

Examples: triangle, square, plaquette, motif-count rewards.

**Decision:** reject for the first new-action test. The source program already warns that ad hoc cycle terms can smuggle locality into the microscopic action.

### C. Direct spectral/locality objectives

Examples: optimize spectral gap, heat-kernel plateau, return probability, resistance distance, path scaling, or a target spectral dimension.

**Decision:** reject. These are excellent diagnostics but too close to the desired macroscopic answer to serve as the first microscopic mechanism.

### D. Matter-induced graph backreaction

Couple an ordinary Gaussian scalar degree of freedom to the graph through the combinatorial Laplacian, then integrate out the scalar field. The resulting graph effective action is a Laplacian determinant term.

**Decision:** select for preregistration.

## 4. Selected mechanism: Gaussian matter determinant

Let `L_G` be the combinatorial graph Laplacian of a connected graph `G`. For a real massless Gaussian scalar field with the constant zero mode removed,

```text
S_phi[phi | G] = 1/2 * phi^T L_G phi
```

and the Gaussian integral gives, up to graph-independent constants,

```text
Z_phi[G] ∝ (det' L_G)^(-1/2)
```

so the induced graph contribution to the effective action is

```text
Gamma_matter[G] = +1/2 * log det' L_G.
```

The prime denotes omission of the single zero eigenvalue for a connected graph.

This sign is not selected from the LOOM results. It is fixed by the Gaussian integral. No target dimension or locality observable appears in the term.

For a connected graph with `N` vertices, Kirchhoff's matrix-tree theorem implies

```text
det' L_G = N * tau(G)
```

where `tau(G)` is the number of spanning trees. Thus, at fixed `N`, this term is equivalently proportional to the logarithm of the spanning-tree count.

That equivalence makes the test especially falsifiable: the term may suppress highly redundant expander connectivity, but it may just as easily create bottlenecks, barbell-like structures, or other non-manifold pathologies. A decrease in expansion by itself will not count as success.

## 5. Why this is independently motivated

The mechanism is not introduced because it resembles a lattice. It follows from a standard relation-first construction:

1. define matter on vertices;
2. let adjacency determine the kinetic operator through the graph Laplacian;
3. integrate out the matter field;
4. allow the resulting matter free energy to backreact on graph configurations.

This is the discrete analogue of matter contributing an effective action to geometry. It does not assume the graph already approximates spacetime.

## 6. First ablation family

The first experiment must keep the new term isolated. The preregistered comparison set is:

1. **null:** no graph action;
2. **corrected-curvature only:** the previously qualified `-alpha * curvature_sum` term;
3. **matter only:** `+1/2 * log det' L`;
4. **combined:** corrected curvature plus the matter determinant.

No triangle term, no extra curvature moments, no target-dimension term, and no sign scan are allowed in this first test.

## 7. Interpretation guardrails

A matter-only or combined run is interesting only if it produces a robust reduction in expander behavior without collapsing into a trivial bottlenecked/crumpled state. A single long path, two dense lobes connected by a bridge, a near-tree, or another obvious graph pathology is a failure even if average shortest path rises sharply.

The RQO-1 pass remains stronger: a broad, stable, non-expander, manifold-like phase with finite measured dimensionality and robustness, without explicit target-lattice terms.

This candidate selection does not alter M1, M2, canon, Navigator/GIS, runtime, or the historical RQO-1 reconstruction.

## 8. Research ancestry

Project source basis:

- `LOOM_2226_Relational_Foundations_Research_Hypotheses_v0.2.pdf` — RQO-1 gate, anti-cycle-smuggling warning, relation-first research sequence.
- recovered `RQO-1_protocol.md` and `rqo1_experiment.py` — null, curvature, short-cycle mechanics and diagnostics.
- `RQO1_SOURCE_AUDIT_v0.1.md` — historical curvature-sign issue.
- `CORRECTED_SIGN_SCALING_PROTOCOL_v0.1.md` — corrected-sign directional effect and failure to cross the non-expander gate.

External mathematical ancestry:

- Gaussian/free-field partition functions on discrete Laplacians use Laplacian determinants.
- Kirchhoff's matrix-tree theorem relates a Laplacian cofactor, equivalently the product of nonzero Laplacian eigenvalues up to the factor `N`, to the spanning-tree count.

These facts motivate the term; they do not imply that matter-induced backreaction will generate spacetime or validate LOOM physics.
