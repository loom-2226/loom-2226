# LOOM CIVSTATE Important Tables Recovery v0.5

**Database authority:** `LOOM_2226_CIVSTATE.sqlite3`  
**SHA-256:** `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`

This pass continues v0.4 and narrows the remaining high-value uncertainties without inventing semantics from field names. It adds exact runtime equations where the current bytes reproduce them to floating-point precision.

## New exact recoveries

### `civ_node_texture_overlay.actor_fragmentation`

For each node, over its `civ_influence_edge` rows:

`HHI = sum((influence_weight / sum(influence_weight))^2)`

Then:

`actor_fragmentation = 1 - HHI`

Verified over all 127 node rows to floating-point precision.

### `civ_node_texture_overlay.control_concentration`

`control_concentration = HHI`

using the same normalized influence-weight Herfindahl index above.

Verified over all 127 node rows to floating-point precision.

### `civ_node_texture_overlay.authority_complexity`

Let:

- `actor_count` = distinct `actor_subject_id` count for the node;
- `domain_count` = distinct `influence_domain` count for the node.

Then:

`authority_complexity = clip(0.2*(actor_count - 6) + 0.15*(domain_count - 5), 0, 1)`

Verified over all 127 node rows to floating-point precision.

This explains the previously odd-looking case where a six-actor node can score either `0.00` or `0.15`: the sixth influence domain contributes the `0.15`.

### `civ_node_texture_overlay.strategic_intensity`

On the current 127-node runtime universe:

`u_norm = (utilization - min(utilization)) / (max(utilization)-min(utilization))`

`si_norm = (strategic_importance - min(strategic_importance)) / (max(strategic_importance)-min(strategic_importance))`

with current extrema:

- utilization: `0.52` to `0.76`
- strategic importance: `0.30` to `0.78`

Then:

`strategic_intensity = 0.2916666666666667 + 0.35*u_norm + 0.16*si_norm`

Verified over all 127 node rows to floating-point precision.

Because this formula depends on current-universe min/max values, it is universe-sensitive and should be regenerated rather than treated as an invariant physical quantity.

### `civ_node_texture_overlay.gateway_character`

`gateway_character = 0.25*logistics_intensity + 0.30*mobility_intensity + 0.25*strategic_intensity + 0.20*authority_complexity`

Verified over all 127 node rows exactly within floating-point representation.

This upgrades `gateway_character` from merely semantically bounded to an exact runtime composite.

## Reverified cross-table carry-throughs

The following remain exact across the 127-node runtime set:

- `civ_place_dna.corporate_proxy_level == civ_governance_profile.corporate_proxy_governance`
- `civ_place_dna.local_autonomy == civ_governance_profile.local_autonomy`
- `civ_place_dna.law_enforcement_reach == civ_governance_profile.enforcement_capacity`
- `civ_place_dna.data_sharing_level == civ_governance_profile.data_sharing_level`
- `civ_social_state.political_autonomy == civ_governance_profile.local_autonomy`
- `civ_social_state.institutional_trust == civ_place_dna.institutional_trust`

## What remains genuinely unresolved in these important tables

The unresolved work is now narrower than v0.4:

- `civ_node_texture_overlay.mobility_intensity`
- `civ_node_texture_overlay.logistics_intensity`
- `civ_node_texture_overlay.activity_pressure`
- `civ_node_texture_overlay.frontier_operational_pressure`
- `civ_economic_state.productivity_index`
- original field-level equations for many `civ_governance_profile` scores
- original field-level equations for several `civ_place_dna` priors
- original field-level equations for several `civ_social_state` pressure scores
- the exact runtime path behind the documented-vs-runtime mismatch for generated `federal_coherence`
- the exact runtime path behind the documented-vs-runtime mismatch for generated `internal_contestation`

For these remaining items, current repository/self-documentation supports meaning and scope but does not yet justify a stronger equation. They remain partial until the original builder/history or an exact reproducible algebraic relation is recovered.

## Epistemic rule

An exact numerical fit is promoted only when it reproduces every applicable runtime row to floating-point precision and is consistent with the preserved methodology/source family. Approximate regression is **not** a recovered definition.
