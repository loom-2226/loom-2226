# LOOM Database Semantic Dossier — Full Table Coverage v0.1

**Work item:** #115  
**Class:** `class:data` documentation only  
**Rule:** an unresolved semantic is recorded as unresolved; it is never filled from the identifier.

This file enumerates **every table in the verified production runtime inventory: 53 CIVSTATE + 42 core-world = 95 tables**. The initiating work order stated 43 core tables, but the preserved 2026-09-06 runtime inventory lists 42. No fictitious 43rd table is added.

## How to use this file

For a table marked `NOT_UNDERSTOOD`, stop before making a semantic inference and recover its builder/migration or authoritative consumer. For CIVSTATE, first consult the database's own `civ_variable_semantics`, `civ_derivation`, `civ_methodology_note`, `civ_assumption`, and `civ_readiness_audit` rows. Exact schema/value behavior can verify structure but cannot manufacture meaning.

## CIVSTATE tables — complete set

| Table | Status | Mandatory semantic caution |
|---|---|---|
| `civ_actor_economic_state` | NOT_UNDERSTOOD | Trace actor-economic builder/derivation before interpreting fields. |
| `civ_actor_exposure` | PARTIALLY_UNDERSTOOD | Exposure is influence/control/dependency, **not ownership**. Organization scope does not locate an individual. `service_dependency_weight` and `control_weight` require traced semantics before causal use. |
| `civ_actor_lineage` | NOT_UNDERSTOOD | Do not infer corporate genealogy semantics from column names alone. |
| `civ_alpha_inv_distribution_audit` | NOT_UNDERSTOOD | Audit purpose likely numeric, but exact alpha/invariant meaning must be traced. |
| `civ_asset_class` | NOT_UNDERSTOOD | Asset taxonomy semantics require source/builder trace. |
| `civ_asset_state` | NOT_UNDERSTOOD | Do not treat numeric state fields as literal physical inventories without derivation. |
| `civ_assumption` | UNDERSTOOD | Self-documenting assumption registry; quote `statement`, `rationale`, `model_basis`, `canon_basis`, sensitivity/status/downstream effects rather than paraphrasing when material. |
| `civ_assumption_dependency` | PARTIALLY_UNDERSTOOD | Dependency registry between assumptions/outputs; exact edge semantics must be read from builder/schema evidence. |
| `civ_census_node_relation` | PARTIALLY_UNDERSTOOD | Relates census zones and infrastructure nodes. A gateway relation is not resident assignment. |
| `civ_country_continuity` | NOT_UNDERSTOOD | Trace continuity model before using as political/historical fact. |
| `civ_country_demographic_v2_1_audit` | PARTIALLY_UNDERSTOOD | Demographic v2.1 audit artifact; audit results are model-validation evidence, not observed demographics. |
| `civ_country_evolution_phase` | NOT_UNDERSTOOD | Contains authored/modelled historical evolution material; `forcing_function`/`political_effect` must be traced before narrative use. |
| `civ_country_institution_membership` | NOT_UNDERSTOOD | Membership semantics, direction, status and time basis require builder trace. |
| `civ_country_narrative_lens` | NOT_UNDERSTOOD | Narrative lens is not objective world truth unless source contract says so. |
| `civ_country_numeric_state` | NOT_UNDERSTOOD | Numeric country state requires derivation and units per field. |
| `civ_country_operating_profile` | NOT_UNDERSTOOD | Profile semantics require source/builder trace. |
| `civ_country_sector_asset_numeric_state` | NOT_UNDERSTOOD | Cross-dimensional allocated/modelled state; do not assume observed microdata. |
| `civ_country_sector_numeric_state` | NOT_UNDERSTOOD | Sector allocation semantics and units require derivation. |
| `civ_declared_model_constant` | UNDERSTOOD | Registry of declared model constants. A constant cannot distinguish members of the grouping over which it is constant. |
| `civ_demographic_model_freeze` | UNDERSTOOD | Frozen demographic model record; limitations remain binding. It does not imply dense micro-demographic distributions exist. |
| `civ_demographic_state` | PARTIALLY_UNDERSTOOD | Aggregate demographic state. A populated median/summary does **not** imply the underlying distribution exists. CENSUS_ZONE age bands may be absent even when median age is populated. |
| `civ_derivation` | UNDERSTOOD | Derivation registry: epistemic class, run, method, source detail, confidence/uncertainty and notes. Follow `derivation_id`; do not upgrade model output to observation. |
| `civ_economic_state` | NOT_UNDERSTOOD | Economic aggregates require units/derivation per field. |
| `civ_field_derivation_binding` | UNDERSTOOD | Field-to-derivation binding surface. Absence of a binding means field-specific derivation is not preserved here; it does not authorize reverse engineering. |
| `civ_governance_profile` | PARTIALLY_UNDERSTOOD | Governance profile mixes named authorities and modelled scores. Organization-level authority is not individual authority. Check grouping-level variation before using scores as selectors. |
| `civ_influence_edge` | PARTIALLY_UNDERSTOOD | Influence/relationship graph edges; do not reinterpret as interpersonal relationships. Edge domain/type and derivation govern meaning. |
| `civ_infrastructure_state` | PARTIALLY_UNDERSTOOD | Infrastructure operating aggregates. `berths_equivalent` is a throughput/capacity proxy unless traced otherwise; **not a literal berth count by default**. |
| `civ_institution_morphology` | NOT_UNDERSTOOD | Institutional morphology semantics require builder/source trace. |
| `civ_jurisdiction_recognition` | PARTIALLY_UNDERSTOOD | Recognition is not automatically authorization, permission, or prerequisite dependency. Trace relationship semantics. |
| `civ_meta` | UNDERSTOOD | CIVSTATE metadata key/value surface; interpret individual keys according to recorded values/contracts. |
| `civ_methodology_note` | UNDERSTOOD | Self-documenting methodology registry. Preserve equations, assumptions, workarounds, invariants, recalculation steps and limitations verbatim when material. |
| `civ_model_run` | UNDERSTOOD | Model-run registry; status/version/source identify generated state and must not be mistaken for canon promotion. |
| `civ_node_texture_overlay` | NOT_UNDERSTOOD | Texture overlay semantics require builder trace; presentation texture is not automatically objective state. |
| `civ_numeric_reconciliation` | UNDERSTOOD | Reconciliation/audit records; a reconciliation demonstrates consistency under its test, not independent empirical truth. |
| `civ_place_dna` | NOT_UNDERSTOOD | Composite place descriptors require field semantics and derivation; do not narrativize score names directly. |
| `civ_readiness_audit` | UNDERSTOOD | Database self-audit. Read `finding` and `recommended_action` before using affected domains. Existing warnings outrank convenient interpretation. |
| `civ_recalculation_contract` | UNDERSTOOD | Recalculation contract surface; use to determine how derived state is expected to be rebuilt. |
| `civ_runtime_gate` | UNDERSTOOD | Runtime readiness/gate records. Gate status concerns runtime/model readiness, not canon truth. |
| `civ_runtime_source` | UNDERSTOOD | Runtime source/hash/provenance registry. Use to trace source artifacts; hash identity does not itself establish semantic meaning. |
| `civ_sector` | PARTIALLY_UNDERSTOOD | Sector taxonomy; exact sector definitions require source text. |
| `civ_sector_state` | NOT_UNDERSTOOD | Sector state values/units/derivation require field trace. |
| `civ_social_pressure` | NOT_UNDERSTOOD | Social-pressure fields are model constructs unless traced; do not treat scores as observed psychology. |
| `civ_social_state` | PARTIALLY_UNDERSTOOD | Aggregate/modelled social indicators. Scores such as cognitive-sovereignty pressure require explicit semantic contract before causal or individual interpretation. |
| `civ_subject` | PARTIALLY_UNDERSTOOD | CIVSTATE subject registry. `subject_id` identifies model subjects across bodies/zones/nodes/actors; subject class/scope must be respected in joins. |
| `civ_synthetic_demographic_profile` | NOT_UNDERSTOOD | Synthetic-demographic profile semantics require builder trace; do not map biological age concepts onto synthetics without explicit support. |
| `civ_transport_flow` | PARTIALLY_UNDERSTOOD | **Annual corridor demand, not scheduled direct service.** Reverse-paired/symmetric rows do not prove reciprocal or sequential operational dependency. Transport mode/access patterns may be topology-generated. |
| `civ_variable_semantics` | UNDERSTOOD | Authoritative in-database variable semantics surface. Quote `interpretation` and `misuse_warning`; coverage is incomplete, so absence of a row means unresolved, not obvious. |
| `civ_workforce_state` | PARTIALLY_UNDERSTOOD | Aggregate workforce state. Worker/task/FTE concepts must remain distinct; machine task equivalent is not automatically a count of synthetic persons. |
| `graph_link_enrichment` | PARTIALLY_UNDERSTOOD | Empty `link_key`-based annotation/enrichment surface. Empty table means no enrichment rows, not that graph links have no semantics. Do not invent future workflow. |
| `nav_graph_display_edges_cache` | PARTIALLY_UNDERSTOOD | Display-oriented graph cache; `support_count` and `is_derived` are display/derivation metadata and must not be discarded when interpreting a rendered edge. |
| `nav_graph_edges_cache` | PARTIALLY_UNDERSTOOD | Cached graph edges. Cache is a representation/consumer surface, not independent source authority. |
| `nav_graph_nodes_cache` | PARTIALLY_UNDERSTOOD | Cached graph nodes. Node domain/scope must be respected; cache presence does not promote semantics. |
| `nav_graph_refresh_meta` | PARTIALLY_UNDERSTOOD | Graph-cache refresh metadata; use for cache provenance/freshness, not world truth. |

## Core world database tables — complete verified 42-table set

The core DB has no `civ_variable_semantics` equivalent. Until its generating migrations/builders are recovered table-by-table, this section is deliberately conservative.

| Table | Status | Current justified interpretation / warning |
|---|---|---|
| `atlas_mobility` | NOT_UNDERSTOOD | Trace GIS/Atlas builder. |
| `atlas_profiles` | NOT_UNDERSTOOD | Trace Atlas profile builder; do not assume objective truth from presentation profile. |
| `atlas_subfeatures` | NOT_UNDERSTOOD | Trace Atlas builder and subfeature taxonomy. |
| `body_zone_census` | NOT_UNDERSTOOD | Trace census materialization; do not infer cross-dimensional distributions not stored. |
| `canon_source_sections` | PARTIALLY_UNDERSTOOD | Source-section linkage to canon material; linkage does not make derived values canon by itself. |
| `celestial_dynamics` | NOT_UNDERSTOOD | Trace dynamics source/model and units before numerical use. |
| `celestial_properties` | NOT_UNDERSTOOD | Trace property source/units before numerical use. |
| `census_records` | NOT_UNDERSTOOD | Trace census source/grain. |
| `derivation_models` | PARTIALLY_UNDERSTOOD | Derivation-model registry; exact model contracts require row/source trace. |
| `entities` | PARTIALLY_UNDERSTOOD | Spatial/world entity catalog; `entity_id` is the spatial/world key. |
| `entity_authorities` | NOT_UNDERSTOOD | Organization/entity authority edges require scope/type semantics; do not project to individuals. |
| `entity_demographic_profiles` | NOT_UNDERSTOOD | Aggregate entity demographic profiles; exact fields/derivations require builder trace. |
| `entity_economic_profiles` | NOT_UNDERSTOOD | Aggregate entity economic profiles; exact fields/units require builder trace. |
| `entity_location_models` | NOT_UNDERSTOOD | Location-model semantics require builder trace. |
| `entity_scopes` | NOT_UNDERSTOOD | Scope relationships require explicit type semantics. |
| `entity_transport_profiles` | NOT_UNDERSTOOD | Transport profile is not a timetable or direct service claim unless contract says so. |
| `ephemeris_states` | NOT_UNDERSTOOD | Trace epoch/frame/source and units before navigation use. |
| `image_assets` | PARTIALLY_UNDERSTOOD | Image metadata linked through knowledge noun identity. Approved current hero selection uses `asset_role='HERO'`, `is_current=1`, `review_status='APPROVED_REFERENCE'`. |
| `image_generation_jobs` | NOT_UNDERSTOOD | Trace media-generation workflow; empty table does not imply no image assets. |
| `image_review_candidates` | NOT_UNDERSTOOD | Trace review workflow. |
| `image_review_state` | NOT_UNDERSTOOD | Trace review-state workflow. |
| `infrastructure_capacity_profiles` | NOT_UNDERSTOOD | Empty in verified inventory; schema purpose must be traced, not guessed. |
| `infrastructure_energy_profiles` | NOT_UNDERSTOOD | Empty in verified inventory; schema purpose must be traced, not guessed. |
| `infrastructure_engineering_profiles` | NOT_UNDERSTOOD | Trace engineering-profile builder and units. |
| `infrastructure_nodes` | PARTIALLY_UNDERSTOOD | Infrastructure-node catalog consumed by GIS/graph; institutional fields are node-level, not person-level. |
| `infrastructure_physical_properties` | NOT_UNDERSTOOD | Empty in verified inventory; do not assume missing physical values are zero. |
| `knowledge_entities` | PARTIALLY_UNDERSTOOD | **Knowledge noun/entity catalog, not propositions/claims.** `noun_id` is the knowledge noun key; `spatial_entity_id` bridges to spatial/world entity. |
| `knowledge_relationships` | PARTIALLY_UNDERSTOOD | Subject–predicate–object noun relationships with context/source/provenance. Not automatically interpersonal social relationships. |
| `meta` | PARTIALLY_UNDERSTOOD | Metadata key/value table; verified runtime inventory includes schema/version/media architecture keys. |
| `nodes` | PARTIALLY_UNDERSTOOD | Legacy table is recorded as deprecated/empty in schema v12 metadata; do not treat as current infrastructure source. |
| `orbit_geometry_models` | NOT_UNDERSTOOD | Trace geometry model, frame, units and derivation. |
| `orbit_snapshots` | NOT_UNDERSTOOD | Trace snapshot epoch/frame and intended consumer. |
| `organizations` | PARTIALLY_UNDERSTOOD | Organization catalog; organization existence/standing does not imply individual agents. |
| `placement_models` | NOT_UNDERSTOOD | Trace placement model semantics and epistemic class. |
| `provenance_sources` | PARTIALLY_UNDERSTOOD | Provenance/source registry; source reference does not automatically promote derived output. |
| `region_mobility` | NOT_UNDERSTOOD | Trace mobility model and units. |
| `regional_morphology` | PARTIALLY_UNDERSTOOD | Regional institutional/morphological descriptors; organization-level relationships remain organization-level. |
| `spatial_states` | NOT_UNDERSTOOD | Trace spatial frame/epoch/state semantics. |
| `states` | NOT_UNDERSTOOD | Generic name is insufficient; trace builder/consumer before interpretation. |
| `transport_hubs` | NOT_UNDERSTOOD | Trace hub model; hub presence does not establish service frequency. |
| `transport_links` | NOT_UNDERSTOOD | Empty in verified inventory; do not infer absence of transport from empty legacy/planned table. |
| `world_model_migrations` | PARTIALLY_UNDERSTOOD | Migration history for world-model schema/materialization. Use to recover builder intent and version transitions. |

## Required closure work for `NOT_UNDERSTOOD`

For each unresolved table, recover at least one of: generating migration/builder with comments or equations; frozen specification; methodology/derivation record; authoritative consumer contract; source manifest; or commit/PR history that unambiguously states the field's meaning. Schema/value inspection alone may validate grain/variation after meaning is recovered, but cannot supply the missing meaning.

## Acceptance interpretation

This file satisfies **table coverage** for the verified 95-table runtime inventory. It does **not** falsely claim complete semantic understanding. Any downstream use of an unresolved field must stop or explicitly carry the unresolved status. That distinction is the purpose of this dossier.
