# LOOM CIVSTATE Semantic Recovery Supplement v0.1

**Status:** WIP evidence recovery for database semantic dossier  
**Bound production CIVSTATE SHA-256:** `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`  
**Rule:** no semantics are inferred from identifiers. This supplement records only semantics explicitly preserved in CIVSTATE self-documentation and repository-backed runtime contracts.

## Hard recovered semantics

### Actor exposure

`civ_actor_exposure` is a gameplay exposure layer generated from existing organization-level influence edges. Its own derivation states:

- `control_weight = max(existing OPERATIONS influence edge for actor,node)`;
- `service_dependency_weight = max(existing SUPPLY influence edge for actor,node)`;
- `sector_id = ALL`;
- `employment_share`, `asset_share`, and `revenue_share` are intentionally `NULL`.

`civ_readiness_audit` says: **“Interpret as influence/control/dependency, not ownership.”**

Therefore:

- organization-level exposure is not individual location;
- service dependency is not equity ownership;
- the three geographic share fields are unsupported, not zero;
- this table must not be used as a person-person relationship source.

Evidence: `DERIV:ACTOR_EXPOSURE_V1`, `METHOD:ACTOR_EXPOSURE_V1`, `AUDIT:ACTOR_EXPOSURE_ROWS`, `AUDIT:ACTOR_SHARES_NULL`.

### Transport

`civ_transport_flow` is a sparse annual OD **corridor-demand proxy**, not a timetable, service schedule, unique-traveler table, or guaranteed direct-route table.

`METHOD:TRANSPORT_FLOW_V2` preserves the exact construction contract:

- each node's annual passenger/freight/ship incidence is split symmetrically into outbound and inbound marginals;
- LOCAL_FEEDER, SYSTEM_TRANSFER, and INTERSYSTEM_TORCH are topology classes;
- intersystem accessibility is based on parent-ephemeris distance;
- the OD matrix is solved by doubly constrained IPF;
- sparse support retains 99.5% cumulative passenger/freight mass plus strongest per-node connections;
- `median_transit_hours` and `freight_value` remain intentionally NULL.

The method explicitly says: **“Transport flow is an annual OD demand proxy, not a schedule.”** It also states that directional imbalance is not modeled and annual incidence is symmetrically split inbound/outbound.

Therefore reverse-paired rows are generated structure and cannot evidence reciprocal or sequential operational dependency.

Evidence: `DERIV:TRANSPORT_FLOW_V2`, `METHOD:TRANSPORT_FLOW_V2`, `AUDIT:TRANSPORT_ROWS`, `AUDIT:TRANSPORT_TIME_NULL`, `AUDIT:TRANSPORT_FREIGHT_VALUE_NULL`, `CONTRACT:TRANSPORT_RECALC`.

### Infrastructure capacities

Three fields in `civ_infrastructure_state` have explicit v1 proxy contracts:

- `habitable_capacity = (resident_population + transient_daily_population) / utilization`; this is an accommodation-equivalent proxy, **not** certified life-support, refuge, or pressure-vessel capacity;
- `industrial_capacity_index` is an equal-weight average of empirical percentile ranks over log-transformed capital, value added, average power, cargo throughput, and ship calls across the 127-node network; it is relative 0..1 scale, **not** a physical production ceiling;
- `berths_equivalent = ship_calls_year / (365 * utilization)`; one berth-equivalent means throughput capacity for one ship call/day at 100% utilization. It is **not a literal berth or dock count**.

The method deliberately excludes workforce from physical-capacity calculations because some workforce is supported/assigned rather than physically present.

Evidence: `DERIV:INFRASTRUCTURE_CAPACITY_V1`, `METHOD:INFRASTRUCTURE_CAPACITY_V1`, `AUDIT:INFRA_NULL:habitable_capacity`, `AUDIT:INFRA_NULL:industrial_capacity_index`, `AUDIT:INFRA_NULL:berths_equivalent`, `CONTRACT:INFRASTRUCTURE_CAPACITY`.

### Census zones versus infrastructure nodes

`civ_census_node_relation` exists specifically to keep the two geographies separate:

- census zones are the resident-demography geography;
- infrastructure nodes are operational facilities;
- every active node has exactly one primary `LOCATED_IN` relation;
- gateway-capable facilities may also have `GATEWAY_FOR` relations to sibling zones;
- these links do **not** transfer census population to nodes and do not imply all residents use the facility;
- relation `confidence` is confidence in the relationship basis, not a population or traffic share and must never be normalized into an allocation weight.

Seven zones are intentionally unlinked where no defensible operational relation exists; this is a known valid gap, not missing data to be filled by guesswork.

Evidence: `DERIV:CENSUS_NODE_LINK_V1`, `METHOD:CENSUS_NODE_LINK_V1`, `AUDIT:CENSUS_NODE_PRIMARY_COVERAGE`, `AUDIT:CENSUS_NODE_REL_ROWS`, `AUDIT:CENSUS_NODE_UNLINKED_ZONES`, `CONTRACT:CENSUS_NODE_LINK`.

### Demography

`civ_demographic_state` is aggregate demographic state. The preserved variable semantics establish:

- `biological_population`: biological resident population at the row geography/year;
- `synthetic_population`: legally/socially recognized synthetic persons, distinct from machine-task capacity;
- `transient_population`: nonresident transient presence in persons/day-equivalent and not part of resident census totals.

`METHOD:DEMOGRAPHIC_V2_1_FREEZE` says the current biological age structure is aggregate/coarse and that migration, fertility, mortality, and household models are not yet endogenous at all future periods.

A populated median or summary field therefore does not imply that a local microdistribution exists.

Evidence: `METHOD:DEMOGRAPHIC_V2_1_FREEZE`, `FREEZE:DEMOGRAPHIC_V2_1`, `CONTRACT:DEMOGRAPHY_GENERAL`, `DEM.BIO_POP`, `DEM.SYNTH_POP`, `DEM.TRANSIENT`.

### Synthetic demography and machine/person firewall

`civ_synthetic_demographic_profile` is a diagnostic layer generated from conserved census-zone synthetic population and workforce state. It does not alter headcounts.

The preserved equations explicitly define synthetic shares and worker-participation proxies. Unsupported dimensions — activation cohort, continuity age, substrate mix, household integration, legal-status mix, mobility, local activation share, fork/merge rate — remain NULL rather than being fabricated.

`civ_workforce_state.synthetic_workers` means recognized synthetic persons participating in labor. `machine_task_equivalent` means non-person automated task capacity in FTE-equivalent units. They must never be added together as persons.

The current synthetic worker/person ratio is a coarse role-allocation prior, not mature life-cycle participation.

Evidence: `DERIV:SYNTHETIC_DEMOGRAPHIC_PROFILE_V1`, `METHOD:SYNTHETIC_DEMOGRAPHY_V1`, `AUDIT:SYNTH_PARTICIPATION_TIERS`, `AUDIT:SYNTH_UNSUPPORTED`, `CONTRACT:SYNTHETIC_LIFE_HISTORY`, `WORK.SYNTH_WORKERS`, `WORK.MACHINE_TASK`.

### Country economics

The frozen economic distribution method uses bounded alpha and persistent investment/output sensitivity and then reconciles country shares to frozen full-Earth value-added, capital, and investment parents.

Explicit variable semantics state:

- `value_added` is modeled location production, not wages/household income/consumption;
- `capital` is productive fixed capital stock, not household wealth;
- `investment` is gross productive investment including replacement and expansion, so high investment/value-added can be mostly replacement.

`civ_sector_state` is direct runtime materialization from corrected `civ_country_sector_numeric_state` for supported fields. `civ_asset_state` is direct runtime materialization from `civ_country_sector_asset_numeric_state`; capital/investment/depreciation are copied directly and utilization is unsupported/NULL.

Evidence: `METHOD:COUNTRY_ECONOMIC_DISTRIBUTION_ALPHA_INV`, `DERIV:ALPHA_INV_DISTRIBUTION`, `DERIV:RUNTIME_SECTOR_STATE`, `DERIV:RUNTIME_ASSET_STATE`, `CONTRACT:ECONOMIC_REDISTRIBUTION`, `ECON.VA`, `ECON.CAPITAL`, `ECON.INVESTMENT`.

### Political breadth

`civ_country_operating_profile`, `civ_country_narrative_lens`, and `civ_country_evolution_phase` contain a mixture of authored anchor profiles and deterministic low-confidence breadth scaffolds.

For the 58 breadth additions:

- operating fields are bounded composites of continuity, institution membership/integration, and economic-capacity context;
- economic scale is used only to characterize relative state-capacity context and does not alter economic state;
- generated operating scores are gameplay scaffolds, not empirical political forecasts;
- qualitative political scores are forbidden as population/GDP/capital/migration/synthetic/infrastructure allocation weights;
- country-specific future constitutional details remain open where unsupported;
- each generated country has six narrative lenses and five evolution phases;
- intermediate events remain revision-open.

Evidence: `METHOD:POLITICAL_BREADTH_V1`, `DERIV:POLITICAL_BREADTH_PROFILE_V1`, `DERIV:POLITICAL_BREADTH_LENS_V1`, `DERIV:POLITICAL_BREADTH_EVOLUTION_V1`, `AUDIT:POLITICAL_BREADTH_CONFIDENCE`, `CONTRACT:POLITICAL_BREADTH`, `POL.BREADTH_SCORE`.

### Place DNA and node texture

`civ_place_dna` is a slow structural/cultural prior. `civ_node_texture_overlay` is a deterministic current-operating overlay derived from infrastructure and influence state. The overlay was created to differentiate node families without random jitter or name-based scoring.

The overlay must not replace resident population geography, and infrastructure nodes remain facilities rather than full settlements.

Evidence: `METHOD:NODE_TEXTURE_V0_2`, `PLACE.DNA`, `NODE.TEXTURE`, `GATE:NODE_TEXTURE_OVERLAY`.

## Self-documenting/control tables

The following tables are themselves semantic/provenance/control surfaces and are considered understood at table purpose/grain level:

- `civ_assumption` — explicit assumptions, rationale, basis, sensitivity, status, downstream effects;
- `civ_assumption_dependency` — derivation-to-assumption dependency join;
- `civ_declared_model_constant` — model constants with units, classification, fit status, sensitivity role, notes;
- `civ_demographic_model_freeze` — frozen demographic allocator identity, parents, hashes, limitations, decision basis;
- `civ_derivation` — epistemic class/method/source/confidence/notes per derivation ID;
- `civ_field_derivation_binding` — field-level derivation binding where row-level provenance is insufficient;
- `civ_methodology_note` — equations, assumptions, workarounds, invariants, recalculation steps, limitations;
- `civ_model_run` — run identity/version/status/boundary/source/assumptions;
- `civ_numeric_reconciliation` — parent-versus-allocated closure and residuals;
- `civ_readiness_audit` — measured finding plus recommended interpretive action;
- `civ_recalculation_contract` — triggers/frozen inputs/mutable outputs/prohibitions/checks/procedures;
- `civ_runtime_gate` — runtime/model readiness gates, not canon promotion;
- `civ_runtime_source` — source artifact role and hash registry;
- `civ_variable_semantics` — explicit selected variable semantics/misuse warnings/future upgrades.

## Still unresolved after this pass

The full dossier remains authoritative for exhaustive table/column enumeration. The following tables still require builder/history recovery before all non-self-evident columns can be interpreted without relying on names:

`civ_actor_economic_state`, `civ_actor_lineage`, `civ_alpha_inv_distribution_audit`, `civ_asset_class`, `civ_country_continuity`, `civ_country_demographic_v2_1_audit`, `civ_country_institution_membership`, `civ_country_numeric_state` (beyond explicitly documented economics fields), `civ_country_sector_asset_numeric_state`, `civ_country_sector_numeric_state`, `civ_economic_state`, `civ_governance_profile`, `civ_influence_edge`, `civ_institution_morphology`, `civ_jurisdiction_recognition`, `civ_meta`, `civ_place_dna` (beyond documented fields), `civ_sector`, `civ_social_pressure`, `civ_social_state`, `civ_subject`, plus the four graph-cache/enrichment tables.

`NOT_UNDERSTOOD` here means **semantic recovery not yet completed**, not permission to infer from identifiers.

## Recovery rule for remaining gaps

For each unresolved column, search in this order:

1. generating builder/migration or frozen deployment script;
2. exact `civ_derivation` / `civ_methodology_note` / `civ_variable_semantics` / `civ_readiness_audit` record;
3. authoritative consumer code;
4. source manifest or checkpoint handoff;
5. commit/PR history.

Schema/value behavior may then verify grain and variation, but it never supplies missing intended meaning.
