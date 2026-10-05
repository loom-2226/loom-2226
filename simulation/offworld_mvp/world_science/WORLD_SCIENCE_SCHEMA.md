# World Science Schema Guide

The executable schema is `lab_v0_1/SCHEMA.sql`. This document explains its architecture rather than replacing the DDL.

## Empirical identity and evidence
Core empirical tables include `body`, `body_identifier`, `region`, `source`, `source_artifact`, `scientific_assertion`, `assertion_input`, `material_evidence`, `spatial_product`, `sample`, `coverage`, `ephemeris_source`, `ephemeris_coverage`, `supersession` and `reconciliation`.

The intended spatial ladder is:

`BODY -> REGION -> FOOTPRINT / LOCAL_SITE -> SAMPLE`

A future project layer extends conceptually as:

`BODY -> REGION -> PROJECT_SITE -> DEPOSIT`

but empirical science does not create fictional project sites or deposits.

## Future-generation namespace
The schema deliberately contains empty structures for `generation_model`, `generation_policy`, `world_realization`, `world_constraint_binding`, `hidden_world_state`, `project_site` and `deposit`. Their existence tests semantic separation; the preserved empirical baseline contains no populated hidden worlds, sites or deposits.

## Observation and knowledge
`observation` and `knowledge_event` support the distinction between WORLD truth, measured/realized observations and later knowledge state. Runtime admission remains outside this database.

## Design principles
One semantic container does not mean one facts table. Physical evidence, model inference, spatial products, samples, navigation references, fictional WORLD state and project/deposit state remain typed and separately queryable.

Do not add body-specific columns when a general scope, region, temporal support, vertical support, source relation or model relation can represent the science. Do not create fake precision to satisfy NOT NULL symmetry.

## Production migration
A production relational implementation may normalize or physically partition these tables differently, but migration must preserve semantic identity, keys, lineage, uncertainty, scope and ontology. PostgreSQL migration is therefore a mapping exercise, not permission to reinterpret evidence.
