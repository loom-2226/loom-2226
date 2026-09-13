# Open Semantic Gaps v0.1

This is not a backlog of permission to guess. It is the list of semantic contracts that still need recovery before the corresponding fields can safely drive derivation.

## Highest priority

1. `civ_actor_exposure`: exact semantics and builder trace for `service_dependency_weight`, `control_weight`, and grouping/normalization behavior.
2. `civ_country_evolution_phase`: provenance and intended role of `forcing_function` and `political_effect`.
3. `civ_jurisdiction_recognition`: whether any field represents recognition only versus authorization/prerequisite effects.
4. `civ_social_pressure`, `civ_social_state`, `civ_place_dna`: exact score construction, grouping levels, and prohibited individual-level interpretations.
5. `civ_asset_state`, `civ_sector_state`, `civ_workforce_state`: units, allocation rules, and model/observed boundary per field.
6. Core-world database: recover generating schema/migrations/builders for all tables currently marked `NOT_UNDERSTOOD`, especially `entity_authorities`, demographic/economic/transport profiles, placement/location/spatial/orbit tables, and legacy empty/planned tables.
7. `graph_link_enrichment`: recover intended annotation workflow from builder/consumer history before populating it.

## Closure evidence standard

A gap closes only with one or more of:

- generating builder/migration whose logic and comments establish meaning;
- frozen specification/methodology;
- derivation/audit/variable-semantics record;
- authoritative consumer contract that unambiguously establishes field meaning;
- source manifest/documentation tied to the field.

Observed value behavior is useful for validating the recovered contract, not for creating it.
