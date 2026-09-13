# LOOM CIVSTATE Recovery Consolidation v1.0

**Date:** 13 September 2026  
**Class:** `class:data` documentation / evidence recovery  
**Scope:** CIVSTATE field definitions, generating lineage, social/place/texture recovery, and Phase-13 historical authority  
**Runtime mutation:** NONE

## 1. Purpose

This document consolidates the recovery work that closes or narrows definitions used by the production database data dictionary. It does not create new world state, canon, or model values.

The governing question remains:

> What exactly is this field, at what row grain, in what units/domain, how is it generated, and how does it join?

A recovered checkpoint or observed equality may establish state, lineage, structure, or an exact formula. It does not authorize inference beyond what the evidence supports.

---

# 2. Critical Phase-13 recovery

The exact historical checkpoint has been recovered:

`LOOM_2226_CIVSTATE_Phase13_v0.1.sqlite3`

SHA-256:

`5cb7c3c9faa89dba6ff42500f2b70756a6f9f58027c7f6035df5cb447f186753`

The recovered database passed:

- `PRAGMA integrity_check`: `ok`
- foreign-key violations: `0`
- CIVSTATE application tables: `24`
- subjects: `799`
- assumptions: `20` (`20 LOCKED_CANON`)
- infrastructure-state rows: `127`
- Place-DNA rows: `127`
- infrastructure social-state rows: `127`
- social-pressure rows: `1,016`
- influence edges: `1,237`
- jurisdiction-recognition rows: `635`
- actor-economic rows: `13`
- actor-lineage rows: `37`

The physical checkpoint contains the original Phase-13 sense-of-place/gameplay layer, including:

- `civ_place_dna`
- `civ_social_state`
- `civ_social_pressure`
- `civ_governance_profile`
- `civ_influence_edge`
- `civ_jurisdiction_recognition`
- `civ_infrastructure_state`
- `civ_actor_economic_state`
- `civ_actor_lineage`

The compact behavioral scaffold is physically present in `civ_place_dna.concise_behavioral_prompt`.

## 2.1 Authority consequence

For a question about what **Phase 13** actually contained, evidence order is:

1. recovered Phase-13 SQLite checkpoint;
2. contemporary Phase-13 contrast/validation report;
3. later/current CIVSTATE for descendant comparison;
4. archaeology/recovery notes;
5. inference.

For **current runtime values**, current production CIVSTATE remains authoritative.

## 2.2 Important correction to earlier archaeology

`LOOM_CIVSTATE_BUILDER_ARCHAEOLOGY_v0.7.md` correctly recorded that the original standalone Phase-13 source builder had not been found in production Git or the earlier recovered source corpus. Its stronger practical implication — that the physical Phase-13 gameplay state was unavailable — is now superseded.

The checkpoint is recovered.

What remains incompletely recovered is the complete original **source-code equation set** behind every `DERIV:GAMEPLAY2226` scalar.

Therefore:

> **checkpoint recovered ≠ every generator equation recovered**

---

# 3. Phase-13 sense-of-place design evidence

The contemporary Phase-13 contrast report states that the first pass underweighted facility morphology and that a narrow tuning pass strengthened:

- aerostat / family-commonwealth roles;
- protected-science / quarantine roles;
- industrial-authority roles;
- cooperative-frontier roles;
- deep-frontier roles;

without changing macro totals or governing assumptions.

This establishes that the Phase-13 Place-DNA layer was intentionally designed to create differentiated facility/institutional environments rather than simply encode distance.

For example, the original Ceres Belt Exchange anchor is recorded as:

- governance style: `NETWORK_COMPACT`
- civil authority: Ceres Commonwealth
- administration: Belt Transit Authority
- security: Belt Security & Rescue Directorate
- commercial actors: Concord Mutual Infrastructure & Assurance / Ferrum Meridian
- resident population: ~94,466
- transient/day: ~82,363
- workforce: ~241,151
- security posture: ~0.67
- commercial openness: ~0.46
- corporate proxy: ~0.34
- local autonomy: ~0.37
- institutional trust: ~0.43
- synthetic acceptance: ~0.61
- migration openness: ~0.58
- frontier mentality: ~0.44
- scarcity pressure: ~0.41
- social tension: ~0.64
- enforcement reach: ~0.77
- data sharing: ~0.56
- outsider openness: ~0.47

These are Phase-13 anchor values and must not be generalized into a universal stereotype for all Ceres people or locations.

---

# 4. Social-pressure layer

Phase 13 physically preserves `1,016` `civ_social_pressure` rows. Direct recovery identified `32` Ceres-related rows in the recovered checkpoint.

This layer is important because it supplies an explicit intermediate object between macro/place state and daily-life consequences.

Preferred causal interpretation:

> world/institutional condition → named social pressure → affected group → routine/opportunity constraint → encounter/event → relationship history → situation

Do **not** collapse this into:

> scalar → personality/stereotype

Social-pressure rows are model/gameplay constructs unless a separate contract promotes a particular field to observed fact.

---

# 5. Exact current CIVSTATE carry-throughs

The following cross-layer relationships are exact for the verified current CIVSTATE population tested during recovery:

- `civ_place_dna.corporate_proxy_level = civ_governance_profile.corporate_proxy_governance`
- `civ_place_dna.local_autonomy = civ_governance_profile.local_autonomy`
- `civ_place_dna.law_enforcement_reach = civ_governance_profile.enforcement_capacity`
- `civ_place_dna.data_sharing_level = civ_governance_profile.data_sharing_level`
- `civ_place_dna.institutional_trust = civ_social_state.institutional_trust`
- `civ_social_state.political_autonomy = civ_governance_profile.local_autonomy`

These are data-definition facts for the current database.

**Misuse warning:** copied/carry-through fields are not independent confirmations. A downstream model must not count them as multiple votes for the same underlying condition.

---

# 6. Exact recovered node-texture definitions

The following definitions were exactly recovered/verified for the current runtime:

### `actor_fragmentation`

`1 - HHI(normalized influence-edge weights at node)`

### `control_concentration`

`HHI(normalized influence-edge weights at node)`

### `authority_complexity`

`clip(0.2*(actor_count - 6) + 0.15*(domain_count - 5), 0, 1)`

where `actor_count` is the distinct influencing actor count and `domain_count` is the distinct influence-domain count at the node.

### `gateway_character`

`0.25*logistics_intensity + 0.30*mobility_intensity + 0.25*strategic_intensity + 0.20*authority_complexity`

### Diagnostic ratios

- `transient_resident_ratio = transient_daily_population / resident_population`
- `workforce_resident_ratio = workforce / resident_population`
- `cargo_per_resident = cargo_throughput_tonnes_year / resident_population`
- `passengers_per_resident = passenger_movements_year / resident_population`
- `shipcalls_per_million_residents = ship_calls_year / resident_population * 1e6`

### `strategic_intensity`

The current runtime population was exactly reproduced by the recovered current-universe rule:

`0.2916666666666667 + 0.35*u_norm + 0.16*si_norm`

The normalization bounds are universe-sensitive. Do not promote the current min/max normalization bounds to timeless canon or a universal future builder contract.

## 6.1 Generators still unresolved

Exact source-code generators remain unrecovered for:

- `mobility_intensity`
- `logistics_intensity`
- `activity_pressure`
- `frontier_operational_pressure`

Their stored current values may be used as bounded world/place state. Approximate regression or a plausible-looking fitted equation is **not** a recovered definition.

---

# 7. Social-state interpretation boundary

The following current fields have useful recovered conceptual domains but not complete original `GAMEPLAY2226` equations:

- `biological_age_pressure`
- `synthetic_presence`
- `automation_exposure`
- `family_viability`
- `migration_dependence`
- `capital_concentration`
- `access_scarcity`
- `external_dependence`
- `strategic_leverage`
- `cultural_distance`
- `cognitive_sovereignty_pressure`
- `local_born_share`

Use them as settlement/place pressures and priors, not deterministic individual traits.

## 7.1 `cognitive_sovereignty_pressure`

The current defensible contract is deliberately narrow:

> bounded `GAMEPLAY2226` social-pressure value stored at infrastructure/place scope; exact field-specific semantic meaning and source-code generator remain unresolved.

Do not silently reinterpret it as mind control, surveillance, autonomy violation, coercive neurotechnology, or any other specific mechanism.

---

# 8. Social-demographic causal bridge

Recovered demographic/social design material states the governing rule:

> social change may alter fertility, migration, family formation, labor geography, medical access, and settlement attractiveness; it does not receive arbitrary population multipliers.

Recovered scenario mechanisms include:

1. capital lock / weak lifetime transfer can delay household formation and suppress realized fertility;
2. earlier lifetime capital transfer, broad social wealth, and housing access can improve realized fertility;
3. reproductive technology and family-formation institutions can offset long-life postponement pressure.

Safe CIVSTATE interpretation channels:

- `family_viability` → conditions that make durable family formation/retention easier or harder;
- `capital_concentration` → pressure on access, succession, housing/assets/opportunity;
- `access_scarcity` → pressure around scarce housing, services, permissions, priority, or premium resources;
- `migration_dependence` → reliance on continued newcomer inflow rather than local demographic replacement alone;
- `local_born_share` → origin structure of the resident population;
- `biological_age_pressure` → age-structure pressure on succession/caregiving/life-course timing;
- `automation_exposure` → resident labor demand and encounter ecology;
- `synthetic_presence` → recognized synthetic-person presence, not machine capacity.

These are causal-domain constraints, not hidden equations.

---

# 9. Economic/materialization builder recovery

Two historical economic/materialization builders were recovered:

- `LOOM_2226_CIVSTATE_Phase2B_2190_2226_Coverage_Aware_Materializer_v0.1.py`
- `LOOM_2226_CIVSTATE_Constrained_Full_Earth_Materializer_v0.1.py`

They recover exact historical lineage for population/employment/value-added/capital/investment materialization and constrained full-Earth allocation.

Key Phase2B structure:

`factor[m] = BLIND_2226[m] / aggregate_2190[m]`

for the relevant parent-conserved metrics.

The constrained full-Earth materializer:

- preserves the fixed Earth parent;
- uses 80 named economies plus an accounting `ROW` residual;
- does not treat `ROW` as a sovereign actor;
- preserves/reconciles source shares to parent totals;
- does not use later political scores as demographic/economic allocation weights.

## 9.1 Current supersession warning

Current `DERIV:ALPHA_INV_DISTRIBUTION` / `RUN:ALPHA_INV_ECONOMIC_CORRECTION_V1.0` later supersedes parts of the historical country distribution.

Therefore the historical builders are valid **definition and lineage evidence**, but do not prove that every current numeric row is byte-for-byte reproduced by those earlier builders.

---

# 10. Existing exact CIVSTATE variable contracts

The in-database `civ_variable_semantics` layer remains primary current-runtime evidence for the fields it covers. Important recovered definitions include:

- `civ_demographic_state.biological_population`: biological resident population; persons; do not add transients unless asking for present headcount.
- `civ_demographic_state.synthetic_population`: recognized synthetic persons; never equate with non-person automation/machine-task equivalents.
- `civ_demographic_state.transient_population`: nonresident transient presence; persons/day-equivalent; not resident census.
- `civ_workforce_state.synthetic_workers`: recognized synthetic persons participating in labor; person-FTE proxy.
- `civ_workforce_state.machine_task_equivalent`: non-person automated task capacity; FTE-equivalent; never add to synthetic-person population.
- `civ_country_numeric_state.value_added`: location production; model currency/year; per-capita/worker ratios are production intensity, not household income/wages/consumption.
- `civ_country_numeric_state.capital`: productive fixed capital stock; model currency; capital/person is not household wealth.
- `civ_country_numeric_state.investment`: gross productive investment; model currency/year; may include replacement.
- `civ_transport_flow.passengers_year`: annual OD corridor-demand proxy; not a timetable, service count, unique-traveler count, or guaranteed direct route.
- `civ_transport_flow.accessibility_index`: relative topology/ephemeris accessibility, not travel time.
- `civ_place_dna.synthetic_acceptance`: slow structural/cultural prior; duplicated/regional values are not local differentiators.
- `civ_node_texture_overlay.gateway_character`: operating texture derived from infrastructure/influence; not population geography.
- `civ_census_node_relation.relationship_type`: `LOCATED_IN` primary zone context / `GATEWAY_FOR` supported access relation; neither transfers population.
- `civ_census_node_relation.confidence`: relationship-basis confidence, not population or traffic share.
- `civ_infrastructure_state.habitable_capacity`: accommodation-equivalent proxy; not certified emergency/life-support capacity.
- `civ_infrastructure_state.industrial_capacity_index`: relative percentile composite; not an absolute production ceiling.
- `civ_infrastructure_state.berths_equivalent`: annual ship-call throughput equivalent; not literal physical berth count.
- `civ_country_operating_profile.*`: low-confidence political-breadth gameplay scores; never quantitative allocation weights.

---

# 11. Exact economic diagnostic relationships recovered

For their verified applicable current rows:

- `civ_economic_state.capital_output_ratio = productive_capital / value_added`
- `civ_economic_state.investment_output_ratio = investment / value_added`
- `civ_economic_state.income_per_capita = value_added / (biological_population + synthetic_population)`

The last field is a diagnostic production-intensity measure despite its historical column name. It is **not household income or welfare**.

---

# 12. Recalculation prohibitions

Unless a governed source explicitly changes these rules:

- no machine-task → person conversion;
- no silent economic rescaling;
- no political-score allocation of population/economics;
- no biological age bins for synthetic persons without explicit support;
- no invented transport times, fares, or schedules;
- no copying census-zone populations into infrastructure-node resident counts;
- no name-only census-node linking;
- confidence ≠ allocation weight;
- workforce ≠ occupancy;
- berth equivalent ≠ literal berth count;
- country operating-profile scores do not reallocate population/economics;
- bloc/institution membership does not make the bloc the parent sovereign.

---

# 13. Full production data-dictionary coverage

The source-controlled generator and tests cover the exact verified production inventory:

- core-world: `42` tables / `457` columns;
- CIVSTATE: `53` tables / `557` columns;
- total: **95 tables / 1,014 columns**.

Every column receives one of the four recovery statuses. `RECOVERED_STORAGE_ONLY` is a valid documentation outcome and means the field is represented but its intended semantics remain unresolved.

This is the key distinction that permits the dictionary to be **complete without pretending knowledge we do not have**.

---

# 14. Global interpretation rules

1. Current runtime database outranks historical checkpoint for current values.
2. Historical checkpoint outranks reconstruction for historical checkpoint state.
3. Exact source/formula outranks statistical fit.
4. Schema proves storage structure, not intended scientific/gameplay meaning.
5. Summary statistic does not imply preserved underlying distribution.
6. Organization-scope fact does not become individual-scope fact.
7. Co-presence does not establish a social relationship.
8. Influence/control/dependency does not imply ownership.
9. Gateway/access relation does not transfer population.
10. Unresolved meaning remains unresolved.

This document supersedes the earlier practical assumption that Phase-13 social/place state had to be reconstructed from later data. It does not supersede the warning that the complete original Phase-13 source builder remains incompletely recovered.
