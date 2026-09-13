# LOOM CIVSTATE Important Tables Recovery v0.6

**Database authority:** `LOOM_2226_CIVSTATE.sqlite3`  
**SHA-256:** `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`

This pass continues the high-value table recovery. It promotes only equations that reproduce every applicable runtime row to floating-point precision and are consistent with the preserved CIVSTATE methodology.

## Newly locked exact node-texture equations

### `actor_fragmentation`

For a node's `civ_influence_edge` rows:

`HHI = Σ (influence_weight / Σ influence_weight)^2`

`actor_fragmentation = 1 - HHI`

Maximum absolute runtime error across all 127 nodes: `1.110e-16`.

### `control_concentration`

`control_concentration = HHI`

using the same normalized influence-weight Herfindahl index.

Maximum absolute runtime error: `1.388e-16`.

### `authority_complexity`

Let:

- `actor_count` = distinct `actor_subject_id` values for the node;
- `domain_count` = distinct `influence_domain` values for the node.

Then:

`authority_complexity = clip(0.2*(actor_count - 6) + 0.15*(domain_count - 5), 0, 1)`

Maximum absolute runtime error: `1.110e-16`.

This explains why two nodes with the same actor count can differ in authority complexity: influence-domain diversity contributes independently.

### `strategic_intensity`

For the current declared 127-node universe:

`u_norm = (utilization - 0.608) / (0.888 - 0.608)`

`si_norm = (strategic_importance - 0.348) / (0.988 - 0.348)`

`strategic_intensity = 0.2916666666666667 + 0.35*u_norm + 0.16*si_norm`

Maximum absolute runtime error: `1.110e-16`.

This score is universe-sensitive because the normalization extrema come from the current node population.

### `gateway_character`

`gateway_character = 0.25*logistics_intensity + 0.30*mobility_intensity + 0.25*strategic_intensity + 0.20*authority_complexity`

Maximum absolute runtime error: `0.000e+00`.

## Important non-recoveries

I tested the remaining node-texture fields against the obvious current source families, including:

- raw infrastructure values;
- per-resident ratios;
- min-max normalizations;
- empirical percentile ranks;
- log-transformed normalizations;
- low-order linear combinations;
- clipped low-order linear combinations.

The following did **not** yield an exact reproducible equation and therefore remain `RECOVERED_PARTIAL`:

- `mobility_intensity`
- `logistics_intensity`
- `activity_pressure`
- `frontier_operational_pressure`

Approximate regressions were deliberately rejected. They are not definitions.

The same rule remains in force for:

- `civ_economic_state.productivity_index`;
- the unrecovered field-level generators for `civ_governance_profile`;
- the unrecovered field-level generators for several `civ_place_dna` priors;
- the unrecovered field-level generators for several `civ_social_state` scores;
- the documented/runtime discrepancy for generated `federal_coherence`;
- the documented/runtime discrepancy for generated `internal_contestation`.

## Historical-source check

The preserved pre-governance runtime branch contains the CIVSTATE consumer/runtime but does not expose the original builder equations for these remaining score fields in the recovered GIS source. Therefore the current production repository still does not justify promoting those fields to exact.

## Current interpretation boundary

At this point the high-value tables are no longer semantically opaque. The unresolved items are specifically **generator recovery** problems, not table-purpose problems.

Do not replace the remaining partial definitions with correlations, fitted equations, or plausible formulas.
