-- LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3
--
-- This is the executable additive DDL delta applied to a pristine frozen
-- v0.2 SQLite specimen by migration.py. The legacy v0.2 tables remain
-- authoritative for all pre-existing columns and rows. SQLite requires the
-- source table rebuild in migration.py because its source_type CHECK cannot
-- be altered in place.

ALTER TABLE observation ADD COLUMN spatial_resolution_value REAL;
ALTER TABLE observation ADD COLUMN spatial_resolution_unit TEXT;
ALTER TABLE observation ADD COLUMN spatial_resolution_semantics TEXT;
ALTER TABLE observation ADD COLUMN vertical_sensitivity_min REAL;
ALTER TABLE observation ADD COLUMN vertical_sensitivity_max REAL;
ALTER TABLE observation ADD COLUMN vertical_sensitivity_unit TEXT;

CREATE TABLE fact_input(
    fact_input_id INTEGER PRIMARY KEY,
    fact_id INTEGER NOT NULL REFERENCES fact(fact_id) ON DELETE CASCADE,
    input_fact_id INTEGER REFERENCES fact(fact_id),
    input_observation_id INTEGER REFERENCES observation(observation_id),
    input_model_product_id INTEGER REFERENCES body_model_product(model_product_id),
    input_role TEXT NOT NULL,
    notes TEXT,
    CHECK((input_fact_id IS NOT NULL) + (input_observation_id IS NOT NULL) +
          (input_model_product_id IS NOT NULL) = 1),
    CHECK(length(trim(input_role))>0),
    CHECK(input_fact_id IS NULL OR input_fact_id<>fact_id)
);
CREATE UNIQUE INDEX uq_fact_input_fact ON fact_input(fact_id,input_fact_id,input_role)
    WHERE input_fact_id IS NOT NULL;
CREATE UNIQUE INDEX uq_fact_input_observation ON fact_input(fact_id,input_observation_id,input_role)
    WHERE input_observation_id IS NOT NULL;
CREATE UNIQUE INDEX uq_fact_input_model ON fact_input(fact_id,input_model_product_id,input_role)
    WHERE input_model_product_id IS NOT NULL;

CREATE TABLE knowledge_event(
    knowledge_event_id INTEGER PRIMARY KEY,
    event_key TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL CHECK(event_type IN(
        'OBSERVED','PUBLISHED','RELEASED','REVISED','SUPERSEDED','RETRACTED','INGESTED')),
    event_time TEXT NOT NULL CHECK(length(trim(event_time))>0),
    target_fact_id INTEGER REFERENCES fact(fact_id),
    target_observation_id INTEGER REFERENCES observation(observation_id),
    target_model_product_id INTEGER REFERENCES body_model_product(model_product_id),
    target_source_id INTEGER REFERENCES source(source_id),
    source_id INTEGER REFERENCES source(source_id),
    notes TEXT,
    CHECK(length(trim(event_key))>0),
    CHECK((target_fact_id IS NOT NULL) + (target_observation_id IS NOT NULL) +
          (target_model_product_id IS NOT NULL) + (target_source_id IS NOT NULL) = 1)
);
CREATE INDEX idx_knowledge_event_time ON knowledge_event(event_time);
CREATE INDEX idx_knowledge_event_type ON knowledge_event(event_type);

-- Cross-body and observational-scale triggers are installed by migration.py
-- in the same transaction after legacy data, typed lineage, and unambiguous
-- observation events have been copied.
