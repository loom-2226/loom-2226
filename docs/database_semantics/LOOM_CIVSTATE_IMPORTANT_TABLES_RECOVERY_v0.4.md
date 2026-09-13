# LOOM CIVSTATE Important Tables Recovery v0.4

**Database authority used for runtime checks:** `LOOM_2226_CIVSTATE.sqlite3`, SHA-256 `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`.

This supplement deepens the seven high-value CIVSTATE tables identified after the v0.3 field inventory. It uses preserved self-documentation plus exact runtime algebra/equality checks. It does **not** infer intended meaning from identifiers alone.

## Recovery summary

The focused pass covers 130 fields across:

- `civ_country_operating_profile`
- `civ_governance_profile`
- `civ_place_dna`
- `civ_economic_state`
- `civ_node_texture_overlay`
- `civ_social_state`
- `civ_sector_state`

The local generated supplement classifies 56 fields as `RECOVERED_EXACT` and 74 as `RECOVERED_PARTIAL`. No field in these seven tables is left as `RECOVERED_STORAGE_ONLY` in the focused supplement: every field now has either a preserved/verified exact contract or a bounded partial definition that explicitly says what remains unresolved.

## `civ_country_operating_profile`

Purpose: country/polity operating scaffold for gameplay differentiation. The preserved `POL.BREADTH_SCORE` semantics define the score family as low-confidence 0..1 gameplay scaffolding summarizing continuity, institutional embedding and relative state-capacity context. Scores are not population/economic/infrastructure allocation weights. For non-federal polities, `federal_coherence` is interpreted generically as internal state/territorial coherence.

Preserved evidence: `civ_variable_semantics` (`POL.BREADTH_SCORE`), `METHOD:POLITICAL_BREADTH_V1`, `DERIV:POLITICAL_BREADTH_PROFILE_V1`.

Exact generated-breadth recoveries:

- `constitutional_continuity = 0.55*legal_continuity + 0.45*identity_continuity`; verified exactly on all 58 `POLITICAL_BREADTH_V1` rows.
- `regional_authority_delegation = 0.55*max(civil_integration) + 0.45*(1-min(autonomy_retention))`; verified exactly on all 58 generated breadth rows.
- `alliance_security_integration = max(security_integration)` across country institution memberships; verified exactly on all 58 generated breadth rows.
- `economic_capacity = 0.55*percentile_rank(log1p(value_added)) + 0.45*percentile_rank(log1p(capital))` over the 58-country generated breadth universe; verified exactly on all 58 rows.

Two important discrepancies are now explicit rather than hidden:

1. `METHOD:POLITICAL_BREADTH_V1` states `state_coherence = 0.45*identity + 0.35*legal + 0.20*border`, but current `federal_coherence` values in the 58 generated rows do not exactly reproduce that expression from current `civ_country_continuity` values (max absolute difference about 0.031).
2. The methodology states `internal_contestation = 0.55*(1-legal)+0.30*(1-border)+0.15*(1-identity)`, but current generated values do not exactly reproduce that expression from current continuity rows (max absolute difference about 0.0368).

Therefore those two fields are semantically recovered but their exact runtime generation path remains open pending builder/history recovery. Runtime values must not be silently rewritten to match the prose formula.

## `civ_governance_profile`

Purpose: governance-channel profile that deliberately keeps legal sovereignty, local civil authority, administration, security, ownership/operation, finance, certification and practical governance separate.

Preserved evidence: assumptions A11-A14 plus `DERIV:GAMEPLAY2226`.

Recovered channel definitions:

- `ultimate_sovereign`: named ultimate legal-sovereignty channel.
- `local_civil_authority`: named local civil-government channel.
- `administrative_authority`: named administrative/functional authority.
- `security_provider`: named security-provider channel.
- `primary_owner_operator`: primary owner/operator organization.
- `primary_financier`: financing channel; currently NULL in all runtime rows.
- `primary_certifier`: certification channel; currently NULL in all runtime rows.

The numeric fields (`state_control`, `local_autonomy`, `corporate_proxy_governance`, `corporate_state_alignment`, `institutional_fragmentation`, `enforcement_capacity`, `data_sharing_level`, `torch_corporate_legacy`, `metric_reassertion`, `loom_frontier_disruption`) are now defined as 0..1 `GAMEPLAY_ESTIMATE` governance-profile scores. Their conceptual roles are supported by A11-A14 and the gameplay derivation, but their exact field-level builder equations are not preserved in the current self-documentation. They remain `RECOVERED_PARTIAL`, not invented formulas.

## `civ_place_dna`

Purpose: slow place-character/cultural prior. It is not current operating texture; that is `civ_node_texture_overlay`.

Preserved evidence: `PLACE.DNA`, `DERIV:GAMEPLAY2226`, `METHOD:NODE_TEXTURE_V0_2`.

All score fields are now bounded as node-level gameplay priors rather than unexplained storage. `synthetic_acceptance` retains the explicit `PLACE.DNA` definition.

Exact runtime carry-through relationships verified for all 127 nodes:

- `corporate_proxy_level == civ_governance_profile.corporate_proxy_governance`
- `local_autonomy == civ_governance_profile.local_autonomy`
- `law_enforcement_reach == civ_governance_profile.enforcement_capacity`
- `data_sharing_level == civ_governance_profile.data_sharing_level`
- `institutional_trust == civ_social_state.institutional_trust`

These are recorded as exact runtime relationships; they are not used to claim a stronger causal interpretation than the evidence supports.

## `civ_economic_state`

Purpose: location-level economic state for modeled subjects. Preserved economic methodology explicitly separates economic numerators from demographic corrections; per-capita/per-worker measures are diagnostic location-intensity measures, not household welfare.

Recovered units/roles:

- `value_added`: model currency/year, annual production flow.
- `investment`: model currency/year, gross productive investment.
- `productive_capital`: model currency, productive fixed-capital stock.
- `infrastructure_capital`: model currency, infrastructure-capital stock.
- `gross_output`, `consumption`, `residential_capital`, `consumption_per_capita`, `price_level_index`, `economic_complexity_index`: schema-supported but currently NULL across this runtime table.

Exact runtime formulas verified:

- `capital_output_ratio = productive_capital / value_added` for all 142 populated rows.
- `investment_output_ratio = investment / value_added` for all 57 populated rows.
- `income_per_capita = value_added / (biological_population + synthetic_population)` for all 139 rows with matching demographic state.

`income_per_capita` is therefore a production-intensity diagnostic and must not be presented as household income or welfare.

`productivity_index` remains semantically bounded as a productivity diagnostic, but its normalization formula is not recovered and remains partial.

## `civ_node_texture_overlay`

Purpose: deterministic current operating texture. `METHOD:NODE_TEXTURE_V0_2` states it is derived from infrastructure activity, strategic/economic/transport centrality, actor influence count/domain count and influence concentration. No random jitter and no name-based scoring are permitted.

The following operational ratios are now explicitly defined and runtime-checked against `civ_infrastructure_state`:

- `transient_resident_ratio = transient_daily_population / resident_population`
- `workforce_resident_ratio = workforce_assigned / resident_population`
- `cargo_per_resident = cargo_throughput_tonnes_year / resident_population`
- `passengers_per_resident = passenger_movements_year / resident_population`
- `shipcalls_per_million_residents = ship_calls_year / resident_population * 1,000,000`

The 0..1 texture fields (`mobility_intensity`, `logistics_intensity`, `strategic_intensity`, `activity_pressure`, `actor_fragmentation`, `authority_complexity`, `control_concentration`, `gateway_character`, `frontier_operational_pressure`) are deterministic model-derived texture signals. The methodology preserves their source families and percentile logic, but not every field-level equation; those remain `RECOVERED_PARTIAL` except `gateway_character`, which already has an explicit `NODE.TEXTURE` contract.

`dominant_texture` is the relatively most prominent texture dimension based on percentile prominence among nodes. `derivation_basis` records that the overlay is derived from infrastructure/influence evidence only, without random jitter.

## `civ_social_state`

Purpose: gameplay-facing social-pressure profile constrained by demography, governance, migration, scarcity, automation and frontier assumptions.

Preserved evidence: `DERIV:GAMEPLAY2226` plus A15-A18.

All score fields are now defined as 0..1 node/year gameplay-social scores rather than unexplained storage. Exact field-level builder equations are not preserved, so most remain `RECOVERED_PARTIAL`. A18 remains a hard interpretation guardrail: high social pressure does **not** imply violence; it may manifest as politics, activism, bargaining, discrimination or institutional change.

Two exact carry-through relationships are verified across all 127 node rows:

- `political_autonomy == civ_governance_profile.local_autonomy`
- `institutional_trust == civ_place_dna.institutional_trust`

`cognitive_sovereignty_pressure` is deliberately kept partial. Current evidence proves only that it is a 0..1 `GAMEPLAY_ESTIMATE` social-pressure field under `DERIV:GAMEPLAY2226`; a stronger field-specific semantic definition or formula has not been recovered. Do not invent one.

## `civ_sector_state`

Purpose: runtime country-sector economic state.

`DERIV:RUNTIME_SECTOR_STATE` is explicit: supported runtime fields are copied directly from `civ_country_sector_numeric_state`; unsupported fields remain NULL.

Exact supported fields:

- `value_added`: sector value added, model currency/year.
- `gross_output`: sector gross output, model currency/year.
- `employment`: sector employment/person-FTE proxy.
- `capital_stock`: sector capital stock, model currency.
- `investment`: sector investment, model currency/year.

Exact intentionally unsupported/NULL fields in the current runtime materialization:

- `energy_use`
- `labor_share`
- `capital_share`
- `productivity_index`
- `automation_share`
- `export_share`
- `import_dependency`

These NULLs are a data contract, not missing values to be casually synthesized.

## Remaining work after this pass

These seven tables are no longer acceptable candidates for the generic `RECOVERED_STORAGE_ONLY` bucket. Their meanings are now bounded. The remaining open work is narrower:

- recover original field-level builder equations for governance/place/social score families;
- recover the exact normalization formulas for the unresolved node-texture component scores and `civ_economic_state.productivity_index`;
- trace the two political-breadth methodology/runtime mismatches through Git history/builders;
- preserve NULL-as-unsupported contracts for sector/economic fields unless a separately qualified model supersedes them.
