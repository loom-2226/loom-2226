-- PROPOSED DESIGN ONLY: Build 6E substrate pass 1, 2026-10-06.
-- NOT authorization to install; no database was provisioned to produce this file.
-- PostgreSQL 18, UTF8 database, trusted DBA, fresh dedicated database/namespaces.
-- Exactly-once installation; existing roles/schema/extension collisions abort.
-- No UUID defaults, sequences, causal wall clocks, schedulers or reducers.
BEGIN;
CREATE ROLE wa_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE wa_science_writer NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_science_governor NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_world_writer NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_runtime_writer NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_admission_writer NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_reference_reader NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_auditor NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_agent_reader NOLOGIN NOSUPERUSER NOBYPASSRLS;
CREATE ROLE wa_agent_view_owner NOLOGIN NOSUPERUSER NOINHERIT NOBYPASSRLS;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA wa_crypto AUTHORIZATION wa_owner;
CREATE EXTENSION pgcrypto WITH SCHEMA wa_crypto;
CREATE SCHEMA wa_meta AUTHORIZATION wa_owner;
CREATE SCHEMA wa_geo AUTHORIZATION wa_owner;
CREATE SCHEMA wa_nav AUTHORIZATION wa_owner;
CREATE SCHEMA wa_science AUTHORIZATION wa_owner;
CREATE SCHEMA wa_world AUTHORIZATION wa_owner;
CREATE SCHEMA wa_run AUTHORIZATION wa_owner;
CREATE SCHEMA wa_info AUTHORIZATION wa_owner;
CREATE SCHEMA wa_agent_api AUTHORIZATION wa_owner;
SET LOCAL ROLE wa_owner;
SET LOCAL search_path = pg_catalog;
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE DOMAIN wa_meta.ident AS text COLLATE "C" CHECK (VALUE <> '');
CREATE DOMAIN wa_meta.sha256 AS text COLLATE "C" CHECK (VALUE ~ '^[0-9a-f]{64}$');
CREATE DOMAIN wa_meta.finite AS numeric CHECK (VALUE::text NOT IN ('NaN','Infinity','-Infinity'));
CREATE DOMAIN wa_meta.context AS text CHECK (VALUE IN ('REAL','SCENARIO','REALIZED'));
CREATE DOMAIN wa_meta.fact_state AS text CHECK (VALUE IN ('KNOWN','UNKNOWN','BLOCKED'));
CREATE DOMAIN wa_meta.standing AS text CHECK (VALUE IN ('CANDIDATE','HOLD','REJECTED','QUARANTINED','ADMITTED'));
CREATE DOMAIN wa_meta.science_ontology AS text CHECK (VALUE IN ('REAL_EVIDENCE','MODEL_INFERENCE','DERIVED','REALIZED_OBSERVATION'));
CREATE DOMAIN wa_meta.scope_kind AS text CHECK (VALUE IN ('BODY','REGION','FOOTPRINT','LOCAL_SITE','SAMPLE','MODEL_DOMAIN'));
CREATE DOMAIN wa_meta.sim_period AS numrange CHECK (NOT isempty(VALUE) AND NOT lower_inf(VALUE) AND lower(VALUE)>=0 AND lower(VALUE)::text NOT IN ('NaN','Infinity','-Infinity') AND (upper_inf(VALUE) OR upper(VALUE)::text NOT IN ('NaN','Infinity','-Infinity')) AND lower_inc(VALUE) AND NOT upper_inc(VALUE));
CREATE DOMAIN wa_meta.time_basis AS text CHECK (VALUE IN ('SIM_TIME','CALENDAR_YEAR'));
CREATE FUNCTION wa_meta.reject_rewrite() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN RAISE EXCEPTION 'immutable authority/history: append a governed successor'; END $$;

CREATE TABLE wa_meta.design_version (
version_key wa_meta.ident PRIMARY KEY, ddl_sha256 wa_meta.sha256 NOT NULL,
 contract_sha256 wa_meta.sha256 NOT NULL, authority_main_sha text NOT NULL CHECK (authority_main_sha ~ '^[0-9a-f]{40}$'),
 qualified_6d_sha text NOT NULL CHECK (qualified_6d_sha ~ '^[0-9a-f]{40}$'), installed_by text NOT NULL,
 installed_at timestamptz NOT NULL
);

CREATE TABLE wa_meta.source_snapshot (
snapshot_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL,
 repository text NOT NULL, git_commit text NOT NULL CHECK (git_commit ~ '^[0-9a-f]{40}$'),
 source_path text NOT NULL, byte_sha256 wa_meta.sha256 NOT NULL, byte_count bigint NOT NULL CHECK(byte_count>=0),
 schema_ref text NOT NULL, authority_class text NOT NULL, original_manifest bytea NOT NULL
);

CREATE TABLE wa_meta.legacy_row (
snapshot_id uuid NOT NULL REFERENCES wa_meta.source_snapshot, table_name wa_meta.ident NOT NULL,
 source_key wa_meta.ident NOT NULL, original_columns jsonb NOT NULL CHECK(jsonb_typeof(original_columns)='object'),
 row_digest wa_meta.sha256 NOT NULL, PRIMARY KEY(snapshot_id,table_name,source_key)
);

CREATE TABLE wa_meta.unit (
unit_key wa_meta.ident PRIMARY KEY, source_lexeme text NOT NULL,
 dimension_ref text, canonical_unit_ref text, conversion_profile_ref text,
 interpretation_state text NOT NULL CHECK(interpretation_state IN ('CHARACTERIZED','UNCHARACTERIZED'))
);

CREATE TABLE wa_geo.time_support (
time_id uuid PRIMARY KEY, kind text NOT NULL CHECK(kind IN ('UNKNOWN','LEXICAL','INSTANT','INTERVAL')),
 time_lexeme text, start_lexeme text, end_lexeme text, calendar_ref text, timescale_ref text,
 instant_utc timestamptz, interval_utc tstzrange, parsing_warrant_ref text,
 CHECK ((kind IN ('UNKNOWN','LEXICAL') AND instant_utc IS NULL AND interval_utc IS NULL)
 OR (kind='INSTANT' AND instant_utc IS NOT NULL AND interval_utc IS NULL AND parsing_warrant_ref IS NOT NULL)
 OR (kind='INTERVAL' AND instant_utc IS NULL AND interval_utc IS NOT NULL AND NOT isempty(interval_utc) AND parsing_warrant_ref IS NOT NULL)),
 CHECK(kind<>'UNKNOWN' OR (time_lexeme IS NULL AND start_lexeme IS NULL AND end_lexeme IS NULL))
);

CREATE TABLE wa_geo.vertical_support (
vertical_id uuid PRIMARY KEY, coordinate_kind text NOT NULL CHECK(coordinate_kind IN ('NONE','UNKNOWN','ALTITUDE','DEPTH_BELOW_SURFACE','PRESSURE_LEVEL')),
 lower_value wa_meta.finite, upper_value wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 datum_ref text, original_coordinate_lexeme text,
 CHECK(lower_value IS NULL OR upper_value IS NULL OR lower_value<=upper_value),
 CHECK(coordinate_kind NOT IN ('NONE','UNKNOWN') OR (lower_value IS NULL AND upper_value IS NULL)),
 CHECK(coordinate_kind<>'DEPTH_BELOW_SURFACE' OR ((lower_value IS NULL OR lower_value>=0) AND (upper_value IS NULL OR upper_value>=0)))
);

CREATE TABLE wa_geo.body (
body_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL,
 canonical_name text NOT NULL, body_class wa_meta.ident NOT NULL,
 parent_body_id uuid REFERENCES wa_geo.body DEFERRABLE INITIALLY DEFERRED,
 status_lexeme text NOT NULL, original_ref text, CHECK(parent_body_id IS DISTINCT FROM body_id)
);

CREATE TABLE wa_geo.body_identifier (
body_id uuid NOT NULL REFERENCES wa_geo.body, authority wa_meta.ident NOT NULL,
 identifier_type wa_meta.ident NOT NULL, identifier_value wa_meta.ident NOT NULL, status_lexeme text NOT NULL,
 PRIMARY KEY(body_id,authority,identifier_type,identifier_value), UNIQUE(authority,identifier_type,identifier_value)
);

CREATE TABLE wa_geo.body_system (
system_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL, name text NOT NULL,
 authority_ref text NOT NULL, characterization_ref text NOT NULL
);

CREATE TABLE wa_geo.system_member (
system_id uuid NOT NULL REFERENCES wa_geo.body_system, body_id uuid NOT NULL REFERENCES wa_geo.body,
 role_lexeme text NOT NULL, PRIMARY KEY(system_id,body_id,role_lexeme)
);

CREATE TABLE wa_geo.frame (
frame_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL, body_id uuid REFERENCES wa_geo.body, system_id uuid REFERENCES wa_geo.body_system,
 frame_kind text NOT NULL CHECK(frame_kind IN ('BODY_FIXED','LOCAL','INERTIAL','AUTHORITY_REFERENCE','UNRESOLVED')),
 authority text NOT NULL, authority_frame_id text, definition_ref text NOT NULL, definition_sha256 wa_meta.sha256,
 length_unit_key wa_meta.ident REFERENCES wa_meta.unit, angular_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 epoch_id uuid REFERENCES wa_geo.time_support, UNIQUE(frame_id,body_id),
 CHECK(num_nonnulls(body_id,system_id)<=1),
 CHECK(frame_kind<>'BODY_FIXED' OR body_id IS NOT NULL), CHECK(frame_kind<>'LOCAL' OR num_nonnulls(body_id,system_id)=1)
);

CREATE TABLE wa_geo.geometry (
geometry_id uuid PRIMARY KEY, body_id uuid REFERENCES wa_geo.body, system_id uuid REFERENCES wa_geo.body_system,
 frame_id uuid NOT NULL, geometry_kind text NOT NULL CHECK(geometry_kind IN ('POINT','LINE','POLYGON','VOLUME','MESH','FOOTPRINT','ORBITAL_REFERENCE','UNCHARACTERIZED')),
 encoding_ref text NOT NULL, product_locator text, product_sha256 wa_meta.sha256,
 coordinate_1 wa_meta.finite, coordinate_2 wa_meta.finite, coordinate_3 wa_meta.finite,
 coordinate_semantics text NOT NULL, coordinate_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 angular_unit_key wa_meta.ident REFERENCES wa_meta.unit, vertical_id uuid REFERENCES wa_geo.vertical_support,
 epoch_id uuid REFERENCES wa_geo.time_support, characterization_ref text NOT NULL,
 FOREIGN KEY(frame_id) REFERENCES wa_geo.frame(frame_id), UNIQUE(geometry_id,body_id), UNIQUE(geometry_id,system_id), CHECK(num_nonnulls(body_id,system_id)=1),
 CHECK(geometry_kind='POINT' OR (coordinate_1 IS NULL AND coordinate_2 IS NULL AND coordinate_3 IS NULL)),
 CHECK(geometry_kind NOT IN ('LINE','POLYGON','VOLUME','MESH','FOOTPRINT') OR product_locator IS NOT NULL),
 CHECK(product_sha256 IS NULL OR product_locator IS NOT NULL)
);

CREATE TABLE wa_geo.location (
location_id uuid PRIMARY KEY, body_id uuid REFERENCES wa_geo.body, system_id uuid REFERENCES wa_geo.body_system,
 semantic_key wa_meta.ident NOT NULL, name text NOT NULL,
 location_kind text NOT NULL CHECK(location_kind IN ('REGION','SITE','FOOTPRINT','MODEL_DOMAIN','LOCAL_FEATURE','ORBITAL_DOMAIN','ATMOSPHERIC_DOMAIN','INTERIOR_DOMAIN','RING_DOMAIN')),
 original_region_type text, origin_kind text NOT NULL CHECK(origin_kind IN ('EMPIRICALLY_IDENTIFIED','SCIENTIFIC_MODEL_DOMAIN','AUTHORED_SPATIAL_ANCHOR')),
 geometry_id uuid, source_ref text NOT NULL, notes text,
 FOREIGN KEY(geometry_id,body_id) REFERENCES wa_geo.geometry(geometry_id,body_id),
 FOREIGN KEY(geometry_id,system_id) REFERENCES wa_geo.geometry(geometry_id,system_id),
 CHECK(num_nonnulls(body_id,system_id)=1), UNIQUE(body_id,semantic_key), UNIQUE(system_id,semantic_key),
 UNIQUE(location_id,body_id), UNIQUE(location_id,system_id)
);

CREATE TABLE wa_geo.location_relation (
 from_location_id uuid NOT NULL REFERENCES wa_geo.location, to_location_id uuid NOT NULL REFERENCES wa_geo.location,
 relation_kind text NOT NULL CHECK(relation_kind IN ('CONTAINS','OVERLAPS','ADJACENT','ASSOCIATED')),
 warrant_ref text NOT NULL, PRIMARY KEY(from_location_id,to_location_id,relation_kind),
 CHECK(from_location_id<>to_location_id), CHECK(relation_kind NOT IN ('OVERLAPS','ADJACENT') OR from_location_id<to_location_id)
);

CREATE TABLE wa_science.source (
source_id uuid PRIMARY KEY, semantic_key wa_meta.ident NOT NULL, revision wa_meta.ident NOT NULL,
 title text NOT NULL, authority text NOT NULL, source_type text NOT NULL, url text, doi text,
 publication_time_id uuid REFERENCES wa_geo.time_support, acquired_time_id uuid REFERENCES wa_geo.time_support,
 notes text, snapshot_id uuid REFERENCES wa_meta.source_snapshot, UNIQUE(semantic_key,revision)
);

CREATE TABLE wa_science.source_artifact (
artifact_id uuid PRIMARY KEY, source_id uuid NOT NULL REFERENCES wa_science.source,
 semantic_key wa_meta.ident NOT NULL, revision wa_meta.ident NOT NULL, local_path_lexeme text, retrieval_url text,
 byte_sha256 wa_meta.sha256, byte_count bigint CHECK(byte_count>=0), acquired_time_id uuid REFERENCES wa_geo.time_support,
 custody_kind text NOT NULL CHECK(custody_kind IN ('LOOM_FROZEN','REMOTE_REFERENCE_ONLY','GOVERNED_PINNED')),
 CHECK(custody_kind='REMOTE_REFERENCE_ONLY' OR (byte_sha256 IS NOT NULL AND byte_count IS NOT NULL)),
 UNIQUE(semantic_key,revision), UNIQUE(artifact_id,source_id)
);

CREATE TABLE wa_nav.product (
product_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL, provider text NOT NULL,
 product_name text NOT NULL, product_version text, asset_filename text, byte_sha256 wa_meta.sha256,
 byte_count bigint CHECK(byte_count>=0), source_url text, acquired_time_id uuid REFERENCES wa_geo.time_support,
 status_lexeme text NOT NULL
);

CREATE TABLE wa_nav.coverage (
product_id uuid NOT NULL REFERENCES wa_nav.product, body_id uuid NOT NULL REFERENCES wa_geo.body,
 coverage_key wa_meta.ident NOT NULL, valid_time_id uuid NOT NULL REFERENCES wa_geo.time_support,
 frame_id uuid REFERENCES wa_geo.frame, original_frame_lexeme text, units_lexeme text,
 coverage_class text NOT NULL, status_lexeme text NOT NULL, PRIMARY KEY(product_id,body_id,coverage_key)
);

CREATE TABLE wa_science.sample (
sample_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body, location_id uuid,
 semantic_key wa_meta.ident UNIQUE NOT NULL, sample_name text NOT NULL, collection_site_lexeme text,
 collection_method text, collection_time_id uuid REFERENCES wa_geo.time_support, mass_value wa_meta.finite,
 mass_unit_key wa_meta.ident REFERENCES wa_meta.unit, source_id uuid NOT NULL REFERENCES wa_science.source, notes text,
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id), UNIQUE(sample_id,body_id)
);

CREATE TABLE wa_science.support (
support_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body,
 scope_kind wa_meta.scope_kind NOT NULL, location_id uuid, sample_id uuid, geometry_id uuid,
 support_resolution text NOT NULL CHECK(support_resolution IN ('IDENTIFIED','UNRESOLVED')),
 vertical_id uuid REFERENCES wa_geo.vertical_support, valid_time_id uuid REFERENCES wa_geo.time_support,
 representativeness_lexeme text NOT NULL, scope_warrant_ref text NOT NULL,
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id),
 FOREIGN KEY(sample_id,body_id) REFERENCES wa_science.sample(sample_id,body_id),
 FOREIGN KEY(geometry_id,body_id) REFERENCES wa_geo.geometry(geometry_id,body_id), UNIQUE(support_id,body_id),
 CHECK((scope_kind='BODY' AND location_id IS NULL AND sample_id IS NULL AND support_resolution='IDENTIFIED')
 OR (scope_kind='SAMPLE' AND ((sample_id IS NOT NULL AND support_resolution='IDENTIFIED') OR (sample_id IS NULL AND support_resolution='UNRESOLVED')))
 OR (scope_kind IN ('REGION','FOOTPRINT','LOCAL_SITE','MODEL_DOMAIN') AND ((location_id IS NOT NULL AND support_resolution='IDENTIFIED') OR (location_id IS NULL AND support_resolution='UNRESOLVED')))),
 CHECK(scope_kind='SAMPLE' OR sample_id IS NULL)
);

CREATE TABLE wa_science.spatial_product (
product_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body,
 support_id uuid NOT NULL, semantic_key wa_meta.ident UNIQUE NOT NULL, product_type text NOT NULL, title text NOT NULL,
 source_id uuid NOT NULL REFERENCES wa_science.source, horizontal_resolution_value wa_meta.finite,
 horizontal_resolution_unit_key wa_meta.ident REFERENCES wa_meta.unit, vertical_sensitivity_min wa_meta.finite,
 vertical_sensitivity_max wa_meta.finite, vertical_sensitivity_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 geometry_ref_lexeme text, coordinate_frame_lexeme text, status_lexeme text NOT NULL,
 FOREIGN KEY(support_id,body_id) REFERENCES wa_science.support(support_id,body_id), UNIQUE(product_id,body_id),
 CHECK(vertical_sensitivity_min IS NULL OR vertical_sensitivity_max IS NULL OR vertical_sensitivity_min<=vertical_sensitivity_max)
);

CREATE TABLE wa_science.observation (
observation_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body, support_id uuid NOT NULL,
 product_id uuid, semantic_key wa_meta.ident UNIQUE NOT NULL, measurement_method text NOT NULL,
 observation_time_id uuid REFERENCES wa_geo.time_support, source_id uuid NOT NULL REFERENCES wa_science.source,
 horizontal_resolution_value wa_meta.finite, horizontal_resolution_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 vertical_sensitivity_min wa_meta.finite, vertical_sensitivity_max wa_meta.finite,
 vertical_sensitivity_unit_key wa_meta.ident REFERENCES wa_meta.unit, notes text,
 FOREIGN KEY(support_id,body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(product_id,body_id) REFERENCES wa_science.spatial_product(product_id,body_id), UNIQUE(observation_id,body_id)
);

CREATE TABLE wa_science.assertion (
assertion_id uuid PRIMARY KEY, semantic_key wa_meta.ident NOT NULL, revision wa_meta.ident NOT NULL,
 body_id uuid NOT NULL REFERENCES wa_geo.body, support_id uuid NOT NULL, property_code wa_meta.ident NOT NULL,
 ontology wa_meta.science_ontology NOT NULL, world_context wa_meta.context NOT NULL CHECK(world_context='REAL'),
 observation_id uuid, sample_id uuid, product_id uuid,
 value_kind text NOT NULL CHECK(value_kind IN ('NUMERIC','TEXT','RANGE','BOUND','DETECTION','MODEL','VECTOR','SPATIAL_PRODUCT','CATEGORY','UNKNOWN')),
 value_numeric wa_meta.finite, value_text text, value_min wa_meta.finite, value_max wa_meta.finite, bound_operator text,
 unit_key wa_meta.ident REFERENCES wa_meta.unit, uncertainty_numeric wa_meta.finite, uncertainty_text text,
 unit_state text NOT NULL CHECK(unit_state IN ('SUPPLIED','NOT_SUPPLIED','NOT_APPLICABLE')),
 epistemic_class_lexeme text NOT NULL, measurement_method text, confidence_lexeme text,
 knowledge_time_id uuid REFERENCES wa_geo.time_support, source_id uuid NOT NULL REFERENCES wa_science.source,
 source_artifact_id uuid, source_locator text, lineage_lexeme text,
 initial_standing wa_meta.standing NOT NULL CHECK(initial_standing<>'ADMITTED'), preferred_lexeme boolean NOT NULL,
 origin_lexeme text NOT NULL, notes text, metadata_bytes bytea NOT NULL, metadata_sha256 wa_meta.sha256 NOT NULL,
 CHECK(metadata_sha256=encode(wa_crypto.digest(metadata_bytes,'sha256'),'hex')),
 FOREIGN KEY(support_id,body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(observation_id,body_id) REFERENCES wa_science.observation(observation_id,body_id),
 FOREIGN KEY(sample_id,body_id) REFERENCES wa_science.sample(sample_id,body_id),
 FOREIGN KEY(product_id,body_id) REFERENCES wa_science.spatial_product(product_id,body_id),
 FOREIGN KEY(source_artifact_id,source_id) REFERENCES wa_science.source_artifact(artifact_id,source_id),
 UNIQUE(semantic_key,revision), UNIQUE(assertion_id,body_id), UNIQUE(assertion_id,support_id),
 CHECK((unit_state='SUPPLIED' AND unit_key IS NOT NULL) OR (unit_state<>'SUPPLIED' AND unit_key IS NULL)),
 CHECK(value_min IS NULL OR value_max IS NULL OR value_min<=value_max),
 CHECK(value_kind<>'UNKNOWN' OR (value_numeric IS NULL AND value_text IS NULL AND value_min IS NULL AND value_max IS NULL)),
 CHECK(uncertainty_numeric IS NULL OR uncertainty_numeric>=0)
);

CREATE TABLE wa_science.assertion_input (
body_id uuid NOT NULL REFERENCES wa_geo.body, assertion_id uuid NOT NULL, input_key wa_meta.ident NOT NULL,
 input_assertion_id uuid, input_observation_id uuid, input_product_id uuid, input_material_id uuid, role_lexeme text NOT NULL,
 PRIMARY KEY(assertion_id,input_key), FOREIGN KEY(assertion_id,body_id) REFERENCES wa_science.assertion(assertion_id,body_id),
 FOREIGN KEY(input_assertion_id) REFERENCES wa_science.assertion(assertion_id),
 FOREIGN KEY(input_observation_id) REFERENCES wa_science.observation(observation_id),
 FOREIGN KEY(input_product_id) REFERENCES wa_science.spatial_product(product_id),
 CHECK(num_nonnulls(input_assertion_id,input_observation_id,input_product_id,input_material_id)=1), CHECK(assertion_id IS DISTINCT FROM input_assertion_id)
);

CREATE TABLE wa_science.material_evidence (
evidence_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body, support_id uuid NOT NULL,
 observation_id uuid, sample_id uuid, material_family text NOT NULL, material_species text, phase_lexeme text,
 physical_form_lexeme text, evidence_class_lexeme text NOT NULL, abundance_semantics_lexeme text NOT NULL,
 value wa_meta.finite, value_min wa_meta.finite, value_max wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 legacy_depth_min wa_meta.finite, legacy_depth_max wa_meta.finite, legacy_depth_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 source_id uuid NOT NULL REFERENCES wa_science.source, initial_standing wa_meta.standing NOT NULL CHECK(initial_standing<>'ADMITTED'),
 origin_lexeme text NOT NULL, notes text,
 FOREIGN KEY(support_id,body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(observation_id,body_id) REFERENCES wa_science.observation(observation_id,body_id),
 FOREIGN KEY(sample_id,body_id) REFERENCES wa_science.sample(sample_id,body_id), UNIQUE(evidence_id,body_id),
 CHECK(value_min IS NULL OR value_max IS NULL OR value_min<=value_max)
);

ALTER TABLE wa_science.assertion_input ADD CONSTRAINT assertion_input_material_fk
 FOREIGN KEY(input_material_id) REFERENCES wa_science.material_evidence(evidence_id);
CREATE INDEX assertion_input_material_reverse ON wa_science.assertion_input(input_material_id,assertion_id);

CREATE TABLE wa_science.coverage (
coverage_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body,
 domain_lexeme text NOT NULL, property_or_class_lexeme text NOT NULL, state_lexeme text NOT NULL,
 origin_lexeme text NOT NULL, reason text NOT NULL
);

CREATE TABLE wa_science.reconciliation (
reconciliation_id uuid PRIMARY KEY, body_id uuid NOT NULL REFERENCES wa_geo.body,
 property_code wa_meta.ident NOT NULL, assertion_a uuid NOT NULL, assertion_b uuid NOT NULL,
 classification_lexeme text NOT NULL, reason text NOT NULL, status_lexeme text NOT NULL,
 FOREIGN KEY(assertion_a,body_id) REFERENCES wa_science.assertion(assertion_id,body_id),
 FOREIGN KEY(assertion_b,body_id) REFERENCES wa_science.assertion(assertion_id,body_id), CHECK(assertion_a<>assertion_b)
);

CREATE TABLE wa_science.supersession (
old_assertion_id uuid NOT NULL REFERENCES wa_science.assertion,
 new_assertion_id uuid NOT NULL REFERENCES wa_science.assertion, source_id uuid NOT NULL REFERENCES wa_science.source,
 reason text NOT NULL, PRIMARY KEY(old_assertion_id,new_assertion_id), CHECK(old_assertion_id<>new_assertion_id)
);

CREATE TABLE wa_science.knowledge_event (
event_id uuid PRIMARY KEY, semantic_key wa_meta.ident UNIQUE NOT NULL,
 event_type text NOT NULL, event_time_id uuid REFERENCES wa_geo.time_support,
 target_assertion_id uuid REFERENCES wa_science.assertion, target_observation_id uuid REFERENCES wa_science.observation,
 target_product_id uuid REFERENCES wa_science.spatial_product, target_source_id uuid REFERENCES wa_science.source,
 CHECK(num_nonnulls(target_assertion_id,target_observation_id,target_product_id,target_source_id)=1)
);

CREATE TABLE wa_science.admission (
admission_id uuid PRIMARY KEY, target_assertion_id uuid REFERENCES wa_science.assertion,
 target_material_id uuid REFERENCES wa_science.material_evidence, target_warrant_id uuid, decision_ordinal bigint UNIQUE NOT NULL CHECK(decision_ordinal>=0),
 standing wa_meta.standing NOT NULL, use_contract_ref text NOT NULL, authorization_ref text NOT NULL,
 decision_time_id uuid REFERENCES wa_geo.time_support, decision_sha256 wa_meta.sha256 NOT NULL,
 CHECK(num_nonnulls(target_assertion_id,target_material_id,target_warrant_id)=1), UNIQUE(target_assertion_id,decision_ordinal),
 UNIQUE(target_material_id,decision_ordinal), UNIQUE(target_warrant_id,decision_ordinal), UNIQUE(admission_id,target_assertion_id)
);

CREATE TABLE wa_science.extrapolation (
warrant_id uuid PRIMARY KEY, assertion_id uuid NOT NULL, from_body_id uuid NOT NULL, to_body_id uuid NOT NULL,
 from_support_id uuid NOT NULL, to_support_id uuid NOT NULL, property_code wa_meta.ident NOT NULL,
 model_family_ref text NOT NULL, method_ref text NOT NULL, uncertainty_ref text NOT NULL,
 knowledge_ordinal bigint NOT NULL CHECK(knowledge_ordinal>=0), initial_standing wa_meta.standing NOT NULL CHECK(initial_standing='CANDIDATE'),
 admission_id uuid NOT NULL, authorization_ref text NOT NULL, scientific_warrant_artifact_id uuid NOT NULL REFERENCES wa_science.source_artifact,
 FOREIGN KEY(assertion_id,from_support_id) REFERENCES wa_science.assertion(assertion_id,support_id),
 FOREIGN KEY(from_support_id,from_body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(to_support_id,to_body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(admission_id,assertion_id) REFERENCES wa_science.admission(admission_id,target_assertion_id),
 CHECK(from_support_id<>to_support_id), UNIQUE(warrant_id,assertion_id,to_support_id)
);

ALTER TABLE wa_science.admission ADD CONSTRAINT admission_warrant_fk
 FOREIGN KEY(target_warrant_id) REFERENCES wa_science.extrapolation(warrant_id);
CREATE INDEX scientific_warrant_standing ON wa_science.admission(target_warrant_id,decision_ordinal DESC) WHERE target_warrant_id IS NOT NULL;

CREATE TABLE wa_world.scenario (
scenario_id uuid PRIMARY KEY, semantic_key wa_meta.ident NOT NULL, version wa_meta.ident NOT NULL,
 definition_sha256 wa_meta.sha256 NOT NULL, authorization_ref text NOT NULL, definition_locator text NOT NULL,
 world_context wa_meta.context NOT NULL CHECK(world_context='SCENARIO'), UNIQUE(semantic_key,version)
);

CREATE TABLE wa_world.generation_model (
model_id uuid PRIMARY KEY, semantic_key wa_meta.ident NOT NULL, version wa_meta.ident NOT NULL,
 name text NOT NULL, status_lexeme text NOT NULL, implementation_sha256 wa_meta.sha256 NOT NULL,
 implementation_locator text NOT NULL, model_family_ref text NOT NULL, uncertainty_contract_ref text NOT NULL,
 parameter_schema_ref text NOT NULL, UNIQUE(semantic_key,version)
);

CREATE TABLE wa_world.generation_policy (
policy_id uuid PRIMARY KEY, model_id uuid NOT NULL REFERENCES wa_world.generation_model,
 semantic_key wa_meta.ident NOT NULL, version wa_meta.ident NOT NULL, body_id uuid NOT NULL REFERENCES wa_geo.body,
 property_code wa_meta.ident NOT NULL, policy_type_lexeme text NOT NULL, parameters jsonb NOT NULL CHECK(jsonb_typeof(parameters)='object'),
 parameter_schema_ref text NOT NULL, original_parameter_lexeme text, policy_bytes bytea NOT NULL, policy_sha256 wa_meta.sha256 NOT NULL,
 CHECK(policy_sha256=encode(wa_crypto.digest(policy_bytes,'sha256'),'hex')),
 authorization_ref text NOT NULL, notes text, UNIQUE(semantic_key,version), UNIQUE(policy_id,model_id,body_id)
);

CREATE TABLE wa_world.realization (
world_id uuid PRIMARY KEY, scenario_id uuid NOT NULL REFERENCES wa_world.scenario,
 model_id uuid NOT NULL REFERENCES wa_world.generation_model, policy_id uuid NOT NULL,
 body_id uuid NOT NULL REFERENCES wa_geo.body, semantic_key wa_meta.ident NOT NULL,
 world_seed_lexeme text NOT NULL, seed_lineage_ref text NOT NULL, scientific_cutoff_ordinal bigint NOT NULL CHECK(scientific_cutoff_ordinal>=0), random_algorithm_ref text NOT NULL,
 key_schema_ref text NOT NULL, constraints_digest wa_meta.sha256 NOT NULL, generator_output_sha256 wa_meta.sha256 NOT NULL,
 status_lexeme text NOT NULL, created_time_lexeme text, initial_epoch_id uuid REFERENCES wa_geo.time_support, world_context wa_meta.context NOT NULL CHECK(world_context='SCENARIO'),
 FOREIGN KEY(policy_id,model_id,body_id) REFERENCES wa_world.generation_policy(policy_id,model_id,body_id),
 UNIQUE(scenario_id,semantic_key), UNIQUE(world_id,body_id), UNIQUE(world_id,scenario_id)
);

CREATE TABLE wa_world.constraint_binding (
world_id uuid NOT NULL, body_id uuid NOT NULL, binding_key wa_meta.ident NOT NULL,
 assertion_id uuid NOT NULL, admission_id uuid NOT NULL, target_support_id uuid NOT NULL,
 extrapolation_warrant_id uuid, assertion_metadata_sha256 wa_meta.sha256 NOT NULL,
 binding_role text NOT NULL, use_contract_ref text NOT NULL, PRIMARY KEY(world_id,binding_key),
 FOREIGN KEY(world_id,body_id) REFERENCES wa_world.realization(world_id,body_id),
 FOREIGN KEY(assertion_id) REFERENCES wa_science.assertion(assertion_id),
 FOREIGN KEY(admission_id,assertion_id) REFERENCES wa_science.admission(admission_id,target_assertion_id),
 FOREIGN KEY(target_support_id,body_id) REFERENCES wa_science.support(support_id,body_id),
 FOREIGN KEY(extrapolation_warrant_id,assertion_id,target_support_id) REFERENCES wa_science.extrapolation(warrant_id,assertion_id,to_support_id)
);

CREATE TABLE wa_world.physical_property (
property_code wa_meta.ident PRIMARY KEY, value_domain text NOT NULL CHECK(value_domain IN ('NUMBER','TEXT','CATEGORY','MODEL_REFERENCE')),
 physical_semantics_ref text NOT NULL, schema_ref text NOT NULL,
 CHECK(property_code NOT LIKE 'financial.%' AND property_code NOT LIKE 'belief.%' AND property_code NOT LIKE 'decision.%')
);

CREATE TABLE wa_world.hidden_state (
state_id uuid PRIMARY KEY, world_id uuid NOT NULL, body_id uuid NOT NULL,
 location_id uuid, property_code wa_meta.ident NOT NULL REFERENCES wa_world.physical_property,
 value_state wa_meta.fact_state NOT NULL CHECK(value_state IN ('KNOWN','UNKNOWN')),
 numeric_value wa_meta.finite, text_value text, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 model_family_ref text NOT NULL, uncertainty_ref text NOT NULL, derivation_ref text NOT NULL,
 value_sha256 wa_meta.sha256 NOT NULL, original_provenance_lexeme text,
 FOREIGN KEY(world_id,body_id) REFERENCES wa_world.realization(world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id),
 UNIQUE(world_id,state_id), UNIQUE(state_id,world_id,body_id),
 UNIQUE NULLS NOT DISTINCT(world_id,location_id,property_code),
 CHECK((value_state='KNOWN' AND num_nonnulls(numeric_value,text_value)=1) OR
 (value_state='UNKNOWN' AND numeric_value IS NULL AND text_value IS NULL))
);

CREATE TABLE wa_world.site (
site_id uuid PRIMARY KEY, world_id uuid NOT NULL, body_id uuid NOT NULL, location_id uuid NOT NULL,
 semantic_key wa_meta.ident NOT NULL, name text NOT NULL, status_lexeme text NOT NULL,
 refinement_model_ref text NOT NULL, refinement_seed_lineage_ref text NOT NULL, realization_sha256 wa_meta.sha256 NOT NULL,
 FOREIGN KEY(world_id,body_id) REFERENCES wa_world.realization(world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id),
 UNIQUE(world_id,semantic_key), UNIQUE(world_id,location_id), UNIQUE(site_id,world_id,body_id), UNIQUE(site_id,world_id,body_id,location_id)
);

CREATE TABLE wa_world.deposit (
deposit_id uuid PRIMARY KEY, world_id uuid NOT NULL, body_id uuid NOT NULL, site_id uuid NOT NULL,
 location_id uuid NOT NULL, resource_class wa_meta.ident NOT NULL, geometry_class_lexeme text NOT NULL,
 initial_in_situ_state wa_meta.fact_state NOT NULL CHECK(initial_in_situ_state IN ('KNOWN','UNKNOWN')),
 initial_in_situ_quantity wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 concentration_state wa_meta.fact_state NOT NULL CHECK(concentration_state IN ('KNOWN','UNKNOWN')),
 concentration_value wa_meta.finite, concentration_unit_key wa_meta.ident REFERENCES wa_meta.unit,
 vertical_id uuid REFERENCES wa_geo.vertical_support, phase_ref text NOT NULL, physical_form_ref text NOT NULL,
 original_accessibility_lexeme text, provenance_ref text NOT NULL,
 FOREIGN KEY(site_id,world_id,body_id) REFERENCES wa_world.site(site_id,world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id), UNIQUE(deposit_id,world_id,body_id), UNIQUE(world_id,location_id,resource_class,phase_ref),
 CHECK((initial_in_situ_state='KNOWN' AND initial_in_situ_quantity IS NOT NULL AND initial_in_situ_quantity>=0 AND unit_key IS NOT NULL)
 OR (initial_in_situ_state='UNKNOWN' AND initial_in_situ_quantity IS NULL)),
 CHECK((concentration_state='KNOWN' AND concentration_value IS NOT NULL AND concentration_value>=0 AND concentration_unit_key IS NOT NULL)
 OR (concentration_state='UNKNOWN' AND concentration_value IS NULL))
);

CREATE TABLE wa_run.execution (
run_id wa_meta.ident PRIMARY KEY, scenario_id uuid NOT NULL REFERENCES wa_world.scenario,
 original_run_identity bytea NOT NULL, identity_sha256 wa_meta.sha256 NOT NULL,
 code_contract wa_meta.ident NOT NULL, code_tree_sha256 wa_meta.sha256 NOT NULL, input_snapshot_ref text NOT NULL,
 boundary_manifest_bytes bytea NOT NULL, boundary_manifest_sha256 wa_meta.sha256 NOT NULL,
 policy_seed_lexeme text NOT NULL, world_seed_manifest_ref text NOT NULL, world_seed_lexeme text NOT NULL, comparison_group_ref text NOT NULL,
 comparison_key_schema_ref text NOT NULL, random_algorithm_ref text NOT NULL,
 decimal_precision integer NOT NULL CHECK(decimal_precision>0), decimal_rounding_ref text NOT NULL,
 clock_mapping_ref text NOT NULL, qualification_protocol_ref text NOT NULL,
 CHECK(identity_sha256=encode(wa_crypto.digest(original_run_identity,'sha256'),'hex')),
 CHECK(boundary_manifest_sha256=encode(wa_crypto.digest(boundary_manifest_bytes,'sha256'),'hex')),
 CHECK(world_seed_lexeme<>policy_seed_lexeme), UNIQUE(run_id,scenario_id)
);

CREATE TABLE wa_run.world_binding (
run_id wa_meta.ident NOT NULL, scenario_id uuid NOT NULL, world_id uuid NOT NULL,
 body_id uuid NOT NULL, binding_key wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,world_id), UNIQUE(run_id,world_id,body_id),
 FOREIGN KEY(run_id,scenario_id) REFERENCES wa_run.execution(run_id,scenario_id),
 FOREIGN KEY(world_id,scenario_id) REFERENCES wa_world.realization(world_id,scenario_id),
 FOREIGN KEY(world_id,body_id) REFERENCES wa_world.realization(world_id,body_id), UNIQUE(run_id,binding_key)
);

CREATE TABLE wa_run.artifact (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, artifact_ref wa_meta.ident NOT NULL,
 record_kind wa_meta.ident NOT NULL, serializer_ref text NOT NULL, payload_bytes bytea NOT NULL,
 payload_sha256 wa_meta.sha256 NOT NULL, PRIMARY KEY(run_id,artifact_ref),
 CHECK(payload_sha256=encode(wa_crypto.digest(payload_bytes,'sha256'),'hex')),
 CHECK(artifact_ref=record_kind||':'||payload_sha256)
);

CREATE TABLE wa_run.causal_envelope (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, envelope_id wa_meta.ident NOT NULL,
 event_ordinal bigint NOT NULL CHECK(event_ordinal>=0), record_version wa_meta.ident NOT NULL,
 scheduled_event_id wa_meta.ident NOT NULL, epoch_id text NOT NULL, actor_ref text NOT NULL,
 process_ref text NOT NULL, action_ref text NOT NULL, world_context wa_meta.context NOT NULL CHECK(world_context='REALIZED'),
 context_id wa_meta.ident NOT NULL, perspective wa_meta.ident NOT NULL,
 time_basis wa_meta.time_basis NOT NULL CHECK(time_basis='SIM_TIME'),
 effective_time wa_meta.finite NOT NULL CHECK(effective_time>=0), decision_time wa_meta.finite,
 authorization_time wa_meta.finite, realized_time wa_meta.finite NOT NULL CHECK(realized_time>=0),
 effective_time_lexeme text NOT NULL, decision_time_lexeme text, authorization_time_lexeme text, realized_time_lexeme text NOT NULL,
 reason_code text NOT NULL, original_envelope_bytes bytea NOT NULL, original_envelope_sha256 wa_meta.sha256 NOT NULL,
 original_hash_material bytea NOT NULL, envelope_hash wa_meta.sha256 NOT NULL,
 previous_trace_hash text NOT NULL CHECK(previous_trace_hash='' OR previous_trace_hash ~ '^[0-9a-f]{64}$'),
 pre_domain_hash wa_meta.sha256 NOT NULL, post_domain_hash wa_meta.sha256 NOT NULL,
 PRIMARY KEY(run_id,envelope_id), UNIQUE(run_id,event_ordinal), UNIQUE(run_id,envelope_hash),
 CHECK(decision_time IS NULL OR (decision_time>=0 AND decision_time<=realized_time)),
 CHECK(authorization_time IS NULL OR (authorization_time>=0 AND authorization_time<=realized_time)),
 CHECK(effective_time_lexeme::wa_meta.finite=effective_time AND realized_time_lexeme::wa_meta.finite=realized_time),
 CHECK(decision_time_lexeme IS NULL OR decision_time_lexeme::wa_meta.finite=decision_time),
 CHECK(authorization_time_lexeme IS NULL OR authorization_time_lexeme::wa_meta.finite=authorization_time),
 CHECK((decision_time IS NULL)=(decision_time_lexeme IS NULL)), CHECK((authorization_time IS NULL)=(authorization_time_lexeme IS NULL)),
 CHECK(original_envelope_sha256=encode(wa_crypto.digest(original_envelope_bytes,'sha256'),'hex')),
 CHECK(envelope_hash=encode(wa_crypto.digest(original_hash_material,'sha256'),'hex'))
);

CREATE TABLE wa_run.trace_artifact_edge (
run_id wa_meta.ident NOT NULL, envelope_id wa_meta.ident NOT NULL,
 edge_role wa_meta.ident NOT NULL, edge_ordinal integer NOT NULL CHECK(edge_ordinal>=0), artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,envelope_id,edge_role,edge_ordinal),
 FOREIGN KEY(run_id,envelope_id) REFERENCES wa_run.causal_envelope,
 FOREIGN KEY(run_id,artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.trace_parent (
run_id wa_meta.ident NOT NULL, child_envelope_id wa_meta.ident NOT NULL,
 parent_envelope_id wa_meta.ident NOT NULL, PRIMARY KEY(run_id,child_envelope_id,parent_envelope_id),
 FOREIGN KEY(run_id,child_envelope_id) REFERENCES wa_run.causal_envelope,
 FOREIGN KEY(run_id,parent_envelope_id) REFERENCES wa_run.causal_envelope,
 CHECK(child_envelope_id<>parent_envelope_id)
);

CREATE TABLE wa_run.actor_reference (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, actor_id wa_meta.ident NOT NULL,
 original_runtime_class text NOT NULL CHECK(original_runtime_class IN ('AGENT','AGGREGATE','SYSTEM')),
 original_artifact_ref wa_meta.ident NOT NULL, PRIMARY KEY(run_id,actor_id),
 FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.organization_reference (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, organization_id wa_meta.ident NOT NULL,
 original_ref text NOT NULL, name text NOT NULL, PRIMARY KEY(run_id,organization_id)
);

CREATE TABLE wa_run.project (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, project_id wa_meta.ident NOT NULL,
 name text NOT NULL, original_project_artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,project_id), FOREIGN KEY(run_id,original_project_artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.project_location (
run_id wa_meta.ident NOT NULL, project_id wa_meta.ident NOT NULL, binding_key wa_meta.ident NOT NULL,
 world_id uuid, body_id uuid, site_id uuid, location_id uuid NOT NULL REFERENCES wa_geo.location,
 effective_period wa_meta.sim_period NOT NULL CHECK(NOT isempty(effective_period) AND NOT lower_inf(effective_period) AND lower(effective_period)>=0),
 purpose_ref text NOT NULL, origin_artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,project_id,binding_key), CHECK(num_nonnulls(world_id,body_id,site_id) IN (0,3)), FOREIGN KEY(run_id,project_id) REFERENCES wa_run.project,
 FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(site_id,world_id,body_id,location_id) REFERENCES wa_world.site(site_id,world_id,body_id,location_id),
 FOREIGN KEY(run_id,origin_artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.project_party (
run_id wa_meta.ident NOT NULL, project_id wa_meta.ident NOT NULL, organization_id wa_meta.ident NOT NULL,
 relationship_ref wa_meta.ident NOT NULL, effective_period wa_meta.sim_period NOT NULL CHECK(NOT isempty(effective_period)),
 original_artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,project_id,organization_id,relationship_ref,effective_period),
 FOREIGN KEY(run_id,project_id) REFERENCES wa_run.project, FOREIGN KEY(run_id,organization_id) REFERENCES wa_run.organization_reference,
 FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.asset (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, asset_id wa_meta.ident NOT NULL,
 asset_class_ref wa_meta.ident NOT NULL, runtime_class text NOT NULL CHECK(runtime_class='ENTITY_ASSET'),
 original_asset_ref wa_meta.ident NOT NULL, installed_event_id wa_meta.ident,
 PRIMARY KEY(run_id,asset_id), FOREIGN KEY(run_id,original_asset_ref) REFERENCES wa_run.artifact,
 FOREIGN KEY(run_id,installed_event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_run.asset_location (
run_id wa_meta.ident NOT NULL, asset_id wa_meta.ident NOT NULL, placement_key wa_meta.ident NOT NULL,
 world_id uuid, body_id uuid, location_id uuid NOT NULL REFERENCES wa_geo.location,
 effective_period wa_meta.sim_period NOT NULL CHECK(NOT isempty(effective_period)), placement_mode text NOT NULL CHECK(placement_mode IN ('STATIONARY','MOBILE','IN_TRANSIT','ORBITAL')),
 trajectory_product_ref text, event_id wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,asset_id,placement_key), FOREIGN KEY(run_id,asset_id) REFERENCES wa_run.asset,
 FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id), CHECK(num_nonnulls(world_id,body_id) IN (0,2)),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_run.settlement (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, settlement_id wa_meta.ident NOT NULL,
 name text NOT NULL, runtime_class text NOT NULL CHECK(runtime_class='AGGREGATE'),
 original_state_ref wa_meta.ident NOT NULL, PRIMARY KEY(run_id,settlement_id),
 FOREIGN KEY(run_id,original_state_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.settlement_location (
run_id wa_meta.ident NOT NULL, settlement_id wa_meta.ident NOT NULL, occupation_key wa_meta.ident NOT NULL,
 world_id uuid, body_id uuid, location_id uuid NOT NULL REFERENCES wa_geo.location,
 effective_period wa_meta.sim_period NOT NULL CHECK(NOT isempty(effective_period)), event_id wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,settlement_id,occupation_key), FOREIGN KEY(run_id,settlement_id) REFERENCES wa_run.settlement,
 FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id), CHECK(num_nonnulls(world_id,body_id) IN (0,2)), FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_run.settlement_asset (
run_id wa_meta.ident NOT NULL, settlement_id wa_meta.ident NOT NULL, asset_id wa_meta.ident NOT NULL,
 relationship_ref wa_meta.ident NOT NULL, organization_id wa_meta.ident, effective_period wa_meta.sim_period NOT NULL CHECK(NOT isempty(effective_period)),
 event_id wa_meta.ident NOT NULL, PRIMARY KEY(run_id,settlement_id,asset_id,relationship_ref,effective_period),
 FOREIGN KEY(run_id,settlement_id) REFERENCES wa_run.settlement, FOREIGN KEY(run_id,asset_id) REFERENCES wa_run.asset,
 FOREIGN KEY(run_id,organization_id) REFERENCES wa_run.organization_reference, FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_run.settlement_state (
run_id wa_meta.ident NOT NULL, settlement_id wa_meta.ident NOT NULL, event_id wa_meta.ident NOT NULL,
 stage_ref text NOT NULL, habitation_state wa_meta.fact_state NOT NULL,
 habitation_capacity wa_meta.finite, original_state_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,settlement_id,event_id), FOREIGN KEY(run_id,settlement_id) REFERENCES wa_run.settlement,
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_state_ref) REFERENCES wa_run.artifact,
 CHECK((habitation_state='KNOWN' AND habitation_capacity IS NOT NULL AND habitation_capacity>=0)
 OR (habitation_state IN ('UNKNOWN','BLOCKED') AND habitation_capacity IS NULL))
);

CREATE TABLE wa_run.population_origin (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, cohort_id wa_meta.ident NOT NULL,
 origin_location_id uuid REFERENCES wa_geo.location, external_origin_ref text, initial_person_count bigint NOT NULL CHECK(initial_person_count>=0),
 source_admission_artifact_ref wa_meta.ident NOT NULL, genesis_event_id wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,cohort_id), CHECK(num_nonnulls(origin_location_id,external_origin_ref)=1),
 FOREIGN KEY(run_id,source_admission_artifact_ref) REFERENCES wa_run.artifact,
 FOREIGN KEY(run_id,genesis_event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_run.population_state (
run_id wa_meta.ident NOT NULL, cohort_id wa_meta.ident NOT NULL, event_id wa_meta.ident NOT NULL,
 position_key wa_meta.ident NOT NULL, location_id uuid REFERENCES wa_geo.location, settlement_id wa_meta.ident,
 position_class text NOT NULL CHECK(position_class IN ('EARTH','RESIDENT','ROTATIONAL','VISITOR','IN_TRANSIT','DECEASED')),
 person_count bigint NOT NULL CHECK(person_count>=0), original_state_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,cohort_id,event_id,position_key), FOREIGN KEY(run_id,cohort_id) REFERENCES wa_run.population_origin,
 FOREIGN KEY(run_id,settlement_id) REFERENCES wa_run.settlement, FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope,
 FOREIGN KEY(run_id,original_state_ref) REFERENCES wa_run.artifact,
 CHECK(position_class IN ('EARTH','IN_TRANSIT','DECEASED') OR location_id IS NOT NULL)
);

CREATE TABLE wa_run.stock_state (
run_id wa_meta.ident NOT NULL, world_id uuid NOT NULL, body_id uuid NOT NULL, deposit_id uuid NOT NULL,
 event_id wa_meta.ident NOT NULL, remaining_state wa_meta.fact_state NOT NULL,
 remaining_in_situ wa_meta.finite, cumulative_extracted wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 original_physical_state_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,deposit_id,event_id), FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(deposit_id,world_id,body_id) REFERENCES wa_world.deposit(deposit_id,world_id,body_id),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_physical_state_ref) REFERENCES wa_run.artifact,
 CHECK((remaining_state='KNOWN' AND remaining_in_situ IS NOT NULL AND remaining_in_situ>=0 AND cumulative_extracted IS NOT NULL AND cumulative_extracted>=0 AND unit_key IS NOT NULL)
 OR (remaining_state IN ('UNKNOWN','BLOCKED') AND remaining_in_situ IS NULL AND cumulative_extracted IS NULL))
);

CREATE TABLE wa_run.accessibility_assessment (
run_id wa_meta.ident NOT NULL, deposit_id uuid NOT NULL, world_id uuid NOT NULL, body_id uuid NOT NULL,
 assessment_key wa_meta.ident NOT NULL, event_id wa_meta.ident NOT NULL, value_state wa_meta.fact_state NOT NULL,
 accessible_quantity wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 capability_ref text NOT NULL, environment_ref text NOT NULL, method_ref text NOT NULL, original_assessment_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,deposit_id,assessment_key), FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(deposit_id,world_id,body_id) REFERENCES wa_world.deposit(deposit_id,world_id,body_id),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_assessment_ref) REFERENCES wa_run.artifact,
 CHECK((value_state='KNOWN' AND accessible_quantity IS NOT NULL AND accessible_quantity>=0 AND unit_key IS NOT NULL)
 OR (value_state IN ('UNKNOWN','BLOCKED') AND accessible_quantity IS NULL))
);

CREATE TABLE wa_run.recoverability_assessment (
run_id wa_meta.ident NOT NULL, deposit_id uuid NOT NULL, project_id wa_meta.ident NOT NULL,
 assessment_key wa_meta.ident NOT NULL, accessibility_key wa_meta.ident NOT NULL, event_id wa_meta.ident NOT NULL,
 value_state wa_meta.fact_state NOT NULL, recoverable_quantity wa_meta.finite, unit_key wa_meta.ident REFERENCES wa_meta.unit,
 realized_capability_ref text NOT NULL, method_ref text NOT NULL, original_assessment_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,deposit_id,project_id,assessment_key), FOREIGN KEY(run_id,project_id) REFERENCES wa_run.project,
 FOREIGN KEY(run_id,deposit_id,accessibility_key) REFERENCES wa_run.accessibility_assessment(run_id,deposit_id,assessment_key),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_assessment_ref) REFERENCES wa_run.artifact,
 CHECK((value_state='KNOWN' AND recoverable_quantity IS NOT NULL AND recoverable_quantity>=0 AND unit_key IS NOT NULL)
 OR (value_state IN ('UNKNOWN','BLOCKED') AND recoverable_quantity IS NULL))
);

CREATE TABLE wa_run.reserve_interpretation (
run_id wa_meta.ident NOT NULL, deposit_id uuid NOT NULL, project_id wa_meta.ident NOT NULL,
 interpretation_key wa_meta.ident NOT NULL, recovery_key wa_meta.ident NOT NULL, event_id wa_meta.ident NOT NULL,
 value_state wa_meta.fact_state NOT NULL CHECK(value_state IN ('UNKNOWN','BLOCKED')),
 reason_code text NOT NULL, economic_contract_ref text, institutional_contract_ref text,
 original_interpretation_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,deposit_id,project_id,interpretation_key),
 FOREIGN KEY(run_id,deposit_id,project_id,recovery_key) REFERENCES wa_run.recoverability_assessment(run_id,deposit_id,project_id,assessment_key),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_interpretation_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_run.mission (
run_id wa_meta.ident NOT NULL, mission_id wa_meta.ident NOT NULL, project_id wa_meta.ident,
 world_id uuid NOT NULL, body_id uuid NOT NULL, target_location_id uuid NOT NULL,
 planned_activity_artifact_ref wa_meta.ident NOT NULL, interaction_contract_ref text NOT NULL,
 PRIMARY KEY(run_id,mission_id), FOREIGN KEY(run_id,project_id) REFERENCES wa_run.project,
 FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(target_location_id,body_id) REFERENCES wa_geo.location(location_id,body_id),
 FOREIGN KEY(run_id,planned_activity_artifact_ref) REFERENCES wa_run.artifact, UNIQUE(run_id,mission_id,world_id,body_id)
);

CREATE TABLE wa_run.observation (
run_id wa_meta.ident NOT NULL, observation_id wa_meta.ident NOT NULL,
 mission_id wa_meta.ident, world_id uuid NOT NULL, body_id uuid NOT NULL, location_id uuid NOT NULL,
 event_id wa_meta.ident NOT NULL, effective_time wa_meta.finite NOT NULL CHECK(effective_time>=0),
 source_time_lexeme text NOT NULL, source_time_basis wa_meta.time_basis NOT NULL,
 geometry_id uuid, vertical_id uuid REFERENCES wa_geo.vertical_support,
 method_ref text NOT NULL, measurement_schema_ref text NOT NULL, original_observation_ref wa_meta.ident NOT NULL,
 world_context wa_meta.context NOT NULL CHECK(world_context='REALIZED'),
 PRIMARY KEY(run_id,observation_id), FOREIGN KEY(run_id,world_id,body_id) REFERENCES wa_run.world_binding(run_id,world_id,body_id),
 FOREIGN KEY(run_id,mission_id,world_id,body_id) REFERENCES wa_run.mission(run_id,mission_id,world_id,body_id),
 FOREIGN KEY(location_id,body_id) REFERENCES wa_geo.location(location_id,body_id),
 FOREIGN KEY(geometry_id,body_id) REFERENCES wa_geo.geometry(geometry_id,body_id),
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,original_observation_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_info.context_value (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, value_ref wa_meta.ident NOT NULL,
 assertion_ref wa_meta.ident NOT NULL, subject_ref wa_meta.ident NOT NULL, concept wa_meta.ident NOT NULL, scope_ref wa_meta.ident NOT NULL,
 world_context wa_meta.context NOT NULL, context_id text NOT NULL, perspective text NOT NULL CHECK(perspective IN ('AGENT','WORLD_SIM','GOVERNANCE')),
 perspective_actor_id text NOT NULL, value_state wa_meta.fact_state NOT NULL, value_lexeme text,
 unit_lexeme wa_meta.ident NOT NULL, reason_code text NOT NULL, proposition_kind wa_meta.ident NOT NULL,
 proposition_role wa_meta.ident NOT NULL, epistemic_mode wa_meta.ident NOT NULL, admission_state wa_meta.standing NOT NULL,
 uncertainty_state wa_meta.ident NOT NULL, uncertainty_ref text NOT NULL, time_basis wa_meta.time_basis NOT NULL,
 valid_from wa_meta.finite NOT NULL, valid_to wa_meta.finite NOT NULL, available_from wa_meta.finite NOT NULL, source_time wa_meta.finite NOT NULL,
 source_refs text[] NOT NULL, source_hashes text[] NOT NULL, warrant_refs text[] NOT NULL, support_conflict_refs text[] NOT NULL,
 dependency_refs text[] NOT NULL, transformation_ref text NOT NULL, transformation_version text NOT NULL,
 authorization_ref wa_meta.ident NOT NULL, reference_role text NOT NULL, record_version wa_meta.ident NOT NULL,
 original_artifact_ref wa_meta.ident NOT NULL, fingerprint wa_meta.sha256 NOT NULL,
 PRIMARY KEY(run_id,value_ref), UNIQUE(run_id,value_ref,fingerprint), FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact,
 CHECK((value_state='KNOWN' AND value_lexeme IS NOT NULL) OR (value_state IN ('UNKNOWN','BLOCKED') AND value_lexeme IS NULL)),
 CHECK((world_context='REAL' AND context_id='') OR (world_context<>'REAL' AND context_id<>'')),
 CHECK(valid_from<=valid_to AND available_from>=0 AND source_time>=0),
 CHECK(cardinality(source_refs)>0 AND cardinality(source_refs)=cardinality(source_hashes)),
 CHECK(array_position(source_refs,NULL) IS NULL AND array_position(source_hashes,NULL) IS NULL)
);

CREATE TABLE wa_info.consumption_request (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, request_id wa_meta.ident NOT NULL,
 consumer_id wa_meta.ident NOT NULL, use_ref wa_meta.ident NOT NULL, subject_ref wa_meta.ident NOT NULL,
 concept wa_meta.ident NOT NULL, scope_ref wa_meta.ident NOT NULL, time_basis wa_meta.time_basis NOT NULL,
 effective_time wa_meta.finite NOT NULL, knowledge_cutoff wa_meta.finite NOT NULL,
 world_context wa_meta.context NOT NULL, context_id text NOT NULL, perspective text NOT NULL CHECK(perspective IN ('AGENT','WORLD_SIM','GOVERNANCE')),
 perspective_actor_id text NOT NULL, assertion_set text NOT NULL CHECK(assertion_set IN ('ADMITTED','ALL_RECORDED')),
 required_unit wa_meta.ident NOT NULL, required_role wa_meta.ident NOT NULL, original_artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,request_id), FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact,
 CHECK(knowledge_cutoff>=0 AND effective_time>=knowledge_cutoff),
 CHECK((world_context='REAL' AND context_id='') OR (world_context<>'REAL' AND context_id<>'')),
 CHECK(perspective<>'AGENT' OR perspective_actor_id=consumer_id)
);

CREATE TABLE wa_info.receipt (
run_id wa_meta.ident NOT NULL, receipt_id wa_meta.ident NOT NULL, request_id wa_meta.ident NOT NULL,
 value_ref wa_meta.ident NOT NULL, resolved_value_hash wa_meta.sha256 NOT NULL, state wa_meta.fact_state NOT NULL,
 reason_code text NOT NULL, consumer_contract_ref wa_meta.ident NOT NULL, consumer_contract_version wa_meta.ident NOT NULL,
 receipt_version wa_meta.ident NOT NULL, original_artifact_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,receipt_id), FOREIGN KEY(run_id,request_id) REFERENCES wa_info.consumption_request,
 FOREIGN KEY(run_id,value_ref,resolved_value_hash) REFERENCES wa_info.context_value(run_id,value_ref,fingerprint),
 FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_info.information_artifact (
run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, information_id wa_meta.ident NOT NULL,
 source_observation_id wa_meta.ident, source_context_value_ref wa_meta.ident,
 created_time wa_meta.finite NOT NULL CHECK(created_time>=0), source_time_lexeme text NOT NULL,
 source_time_basis wa_meta.time_basis NOT NULL, payload_schema_ref wa_meta.ident NOT NULL,
 original_artifact_ref wa_meta.ident NOT NULL, publication_contract_ref text NOT NULL,
 PRIMARY KEY(run_id,information_id), FOREIGN KEY(run_id,source_observation_id) REFERENCES wa_run.observation,
 FOREIGN KEY(run_id,source_context_value_ref) REFERENCES wa_info.context_value,
 FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact,
 CHECK(num_nonnulls(source_observation_id,source_context_value_ref)=1)
);

CREATE TABLE wa_info.possession (
run_id wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL, information_id wa_meta.ident NOT NULL,
 possession_key wa_meta.ident NOT NULL, available_from wa_meta.finite NOT NULL CHECK(available_from>=0),
 event_id wa_meta.ident NOT NULL, access_contract_ref text NOT NULL,
 PRIMARY KEY(run_id,actor_id,information_id,possession_key), FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,information_id) REFERENCES wa_info.information_artifact, FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope
);

CREATE TABLE wa_info.belief (
run_id wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL, belief_key wa_meta.ident NOT NULL,
 event_id wa_meta.ident NOT NULL, source_information_id wa_meta.ident,
 value_state wa_meta.fact_state NOT NULL, original_belief_ref wa_meta.ident NOT NULL, update_rule_ref text NOT NULL,
 PRIMARY KEY(run_id,actor_id,belief_key,event_id), FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,event_id) REFERENCES wa_run.causal_envelope, FOREIGN KEY(run_id,source_information_id) REFERENCES wa_info.information_artifact,
 FOREIGN KEY(run_id,original_belief_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_info.agent_snapshot (
 run_id wa_meta.ident NOT NULL REFERENCES wa_run.execution, snapshot_ref wa_meta.ident NOT NULL,
 actor_id wa_meta.ident NOT NULL, period_key wa_meta.ident NOT NULL,
 effective_time wa_meta.finite NOT NULL CHECK(effective_time>=0), effective_time_lexeme text NOT NULL,
 original_snapshot_bytes bytea NOT NULL, original_snapshot_sha256 wa_meta.sha256 NOT NULL,
 original_artifact_ref wa_meta.ident NOT NULL, worker_fingerprint wa_meta.sha256 NOT NULL,
 producer_contract_ref wa_meta.ident NOT NULL, sanitizer_attestation_sha256 wa_meta.sha256 NOT NULL,
 PRIMARY KEY(run_id,snapshot_ref), UNIQUE(run_id,actor_id,snapshot_ref,effective_time),
 FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,original_artifact_ref) REFERENCES wa_run.artifact,
 CHECK(snapshot_ref='decision-snapshot:'||period_key||':'||worker_fingerprint),
 CHECK(effective_time_lexeme::wa_meta.finite=effective_time),
 CHECK(original_snapshot_sha256=encode(wa_crypto.digest(original_snapshot_bytes,'sha256'),'hex'))
);

CREATE TABLE wa_info.decision (
run_id wa_meta.ident NOT NULL, decision_id wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL,
 decision_time wa_meta.finite NOT NULL CHECK(decision_time>=0), original_snapshot_ref wa_meta.ident NOT NULL, worker_snapshot_ref wa_meta.ident NOT NULL,
 original_decision_ref wa_meta.ident NOT NULL, policy_version_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,decision_id), FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,original_snapshot_ref) REFERENCES wa_run.artifact,
 FOREIGN KEY(run_id,worker_snapshot_ref) REFERENCES wa_info.agent_snapshot(run_id,snapshot_ref),
 FOREIGN KEY(run_id,original_decision_ref) REFERENCES wa_run.artifact
);

CREATE TABLE wa_info.action_authorization (
run_id wa_meta.ident NOT NULL, authorization_id wa_meta.ident NOT NULL, decision_id wa_meta.ident,
 actor_id wa_meta.ident NOT NULL, authorization_time wa_meta.finite NOT NULL CHECK(authorization_time>=0),
 rule_origin_kind text NOT NULL CHECK(rule_origin_kind IN ('DECISION','SYSTEM','GENESIS')),
 rule_ref wa_meta.ident NOT NULL, planned_action_ref wa_meta.ident NOT NULL,
 PRIMARY KEY(run_id,authorization_id), FOREIGN KEY(run_id,decision_id) REFERENCES wa_info.decision,
 FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference, FOREIGN KEY(run_id,planned_action_ref) REFERENCES wa_run.artifact,
 CHECK((rule_origin_kind='DECISION')=(decision_id IS NOT NULL))
);

CREATE TABLE wa_info.epistemic_loop (
run_id wa_meta.ident NOT NULL, loop_key wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL,
 receipt_id wa_meta.ident NOT NULL, belief_event_id wa_meta.ident, belief_key wa_meta.ident,
 decision_id wa_meta.ident NOT NULL, authorization_id wa_meta.ident NOT NULL,
 consequence_envelope_id wa_meta.ident NOT NULL, subsequent_information_id wa_meta.ident,
 subsequent_possession_key wa_meta.ident,
 PRIMARY KEY(run_id,loop_key), FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,receipt_id) REFERENCES wa_info.receipt, FOREIGN KEY(run_id,actor_id,belief_key,belief_event_id) REFERENCES wa_info.belief,
 FOREIGN KEY(run_id,decision_id) REFERENCES wa_info.decision, FOREIGN KEY(run_id,authorization_id) REFERENCES wa_info.action_authorization,
 FOREIGN KEY(run_id,consequence_envelope_id) REFERENCES wa_run.causal_envelope,
 FOREIGN KEY(run_id,actor_id,subsequent_information_id,subsequent_possession_key) REFERENCES wa_info.possession,
 CHECK((belief_event_id IS NULL)=(belief_key IS NULL)),
 CHECK((subsequent_information_id IS NULL)=(subsequent_possession_key IS NULL))
);

CREATE TABLE wa_info.principal_binding (
 login_name name PRIMARY KEY, run_id wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL,
 authorized_snapshot_ref wa_meta.ident NOT NULL, effective_time wa_meta.finite NOT NULL CHECK(effective_time>=0),
 authorization_ref wa_meta.ident NOT NULL,
 FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,actor_id,authorized_snapshot_ref,effective_time) REFERENCES wa_info.agent_snapshot(run_id,actor_id,snapshot_ref,effective_time)
);

CREATE TABLE wa_info.agent_fact (
run_id wa_meta.ident NOT NULL, actor_id wa_meta.ident NOT NULL, snapshot_ref wa_meta.ident NOT NULL,
 fact_key wa_meta.ident NOT NULL, receipt_id wa_meta.ident NOT NULL,
 effective_time wa_meta.finite NOT NULL CHECK(effective_time>=0), value_state wa_meta.fact_state NOT NULL,
 value_lexeme text, worker_source_ref text NOT NULL CHECK(worker_source_ref='admitted:'||fact_key),
 producer_contract_ref wa_meta.ident NOT NULL, sanitizer_attestation_sha256 wa_meta.sha256 NOT NULL,
 PRIMARY KEY(run_id,actor_id,snapshot_ref,fact_key), FOREIGN KEY(run_id,actor_id) REFERENCES wa_run.actor_reference,
 FOREIGN KEY(run_id,receipt_id) REFERENCES wa_info.receipt, FOREIGN KEY(run_id,actor_id,snapshot_ref,effective_time) REFERENCES wa_info.agent_snapshot(run_id,actor_id,snapshot_ref,effective_time),
 CHECK((value_state='KNOWN' AND value_lexeme IS NOT NULL) OR (value_state IN ('UNKNOWN','BLOCKED') AND value_lexeme IS NULL))
);

CREATE FUNCTION wa_geo.guard_location_relation() RETURNS trigger
LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NEW.relation_kind='CONTAINS' AND EXISTS (
  WITH RECURSIVE descendants(id) AS (
   SELECT NEW.to_location_id UNION
   SELECT r.to_location_id FROM wa_geo.location_relation r JOIN descendants d ON r.from_location_id=d.id
   WHERE r.relation_kind='CONTAINS')
  SELECT 1 FROM descendants WHERE id=NEW.from_location_id)
 THEN RAISE EXCEPTION 'cyclic spatial containment'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER location_relation_cycle AFTER INSERT ON wa_geo.location_relation
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION wa_geo.guard_location_relation();
CREATE FUNCTION wa_geo.guard_body_parent() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NEW.parent_body_id IS NOT NULL AND EXISTS (
 WITH RECURSIVE ancestry(id) AS (SELECT NEW.parent_body_id UNION
 SELECT b.parent_body_id FROM wa_geo.body b JOIN ancestry a ON b.body_id=a.id WHERE b.parent_body_id IS NOT NULL)
 SELECT 1 FROM ancestry WHERE id=NEW.body_id) THEN RAISE EXCEPTION 'cyclic body association'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER body_parent_cycle AFTER INSERT ON wa_geo.body DEFERRABLE INITIALLY DEFERRED
 FOR EACH ROW EXECUTE FUNCTION wa_geo.guard_body_parent();
CREATE FUNCTION wa_science.guard_assertion_lineage() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NEW.input_assertion_id IS NOT NULL AND EXISTS (
 WITH RECURSIVE inputs(id) AS (SELECT NEW.input_assertion_id UNION
 SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN inputs p ON i.assertion_id=p.id WHERE i.input_assertion_id IS NOT NULL)
 SELECT 1 FROM inputs WHERE id=NEW.assertion_id) THEN RAISE EXCEPTION 'cyclic scientific lineage'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER assertion_lineage_cycle AFTER INSERT ON wa_science.assertion_input
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION wa_science.guard_assertion_lineage();
CREATE FUNCTION wa_world.guard_constraint() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE a wa_science.assertion%ROWTYPE; d wa_science.admission%ROWTYPE; w wa_science.extrapolation%ROWTYPE;
BEGIN
 SELECT * INTO STRICT a FROM wa_science.assertion WHERE assertion_id=NEW.assertion_id;
 SELECT * INTO STRICT d FROM wa_science.admission WHERE admission_id=NEW.admission_id;
 IF EXISTS(SELECT 1 FROM wa_science.support WHERE support_id IN (a.support_id,NEW.target_support_id) AND support_resolution='UNRESOLVED')
 THEN RAISE EXCEPTION 'unresolved scientific support cannot constrain a location'; END IF;
 IF d.decision_ordinal>(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id) OR EXISTS
 (SELECT 1 FROM wa_science.admission later WHERE later.target_assertion_id=a.assertion_id AND later.decision_ordinal>d.decision_ordinal
 AND later.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id))
 THEN RAISE EXCEPTION 'constraint standing does not match pinned knowledge cutoff'; END IF;
 IF d.standing<>'ADMITTED' OR d.target_assertion_id<>a.assertion_id OR d.use_contract_ref<>NEW.use_contract_ref
 OR NEW.assertion_metadata_sha256<>a.metadata_sha256 THEN RAISE EXCEPTION 'unadmitted or stale constraint'; END IF;
 -- Explicit typed derivation cannot launder an unadmitted assertion/material parent.
 IF EXISTS (
 WITH RECURSIVE ancestors(id) AS (SELECT a.assertion_id UNION
 SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN ancestors p ON i.assertion_id=p.id WHERE i.input_assertion_id IS NOT NULL)
 SELECT 1 FROM ancestors p LEFT JOIN LATERAL
 (SELECT standing,use_contract_ref FROM wa_science.admission d2 WHERE d2.target_assertion_id=p.id
 AND d2.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id)
 ORDER BY decision_ordinal DESC LIMIT 1) ds ON true
 WHERE ds.standing IS DISTINCT FROM 'ADMITTED' OR ds.use_contract_ref IS DISTINCT FROM NEW.use_contract_ref)
 THEN RAISE EXCEPTION 'derived constraint contains an unadmitted assertion parent'; END IF;
 IF EXISTS (
 WITH RECURSIVE ancestors(id) AS (SELECT a.assertion_id UNION
 SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN ancestors p ON i.assertion_id=p.id WHERE i.input_assertion_id IS NOT NULL)
 SELECT 1 FROM ancestors p JOIN wa_science.assertion_input i ON i.assertion_id=p.id LEFT JOIN LATERAL
 (SELECT standing,use_contract_ref FROM wa_science.admission dm WHERE dm.target_material_id=i.input_material_id
 AND dm.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id)
 ORDER BY decision_ordinal DESC LIMIT 1) ms ON true
 WHERE i.input_material_id IS NOT NULL AND (ms.standing IS DISTINCT FROM 'ADMITTED' OR ms.use_contract_ref IS DISTINCT FROM NEW.use_contract_ref))
 THEN RAISE EXCEPTION 'derived constraint contains unadmitted material evidence'; END IF;
 IF EXISTS (
 WITH RECURSIVE ancestors(id) AS (SELECT a.assertion_id UNION
 SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN ancestors p ON i.assertion_id=p.id WHERE i.input_assertion_id IS NOT NULL)
 SELECT 1 FROM ancestors p JOIN wa_science.assertion_input i ON i.assertion_id=p.id
 JOIN wa_science.assertion child ON child.assertion_id=i.assertion_id
 JOIN wa_science.assertion parent ON parent.assertion_id=i.input_assertion_id
 JOIN wa_science.support ps ON ps.support_id=parent.support_id
 WHERE ps.support_resolution='UNRESOLVED' OR (parent.support_id<>child.support_id AND NOT EXISTS
 (SELECT 1 FROM wa_science.extrapolation x WHERE x.assertion_id=parent.assertion_id AND x.to_support_id=child.support_id
 AND x.knowledge_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id)
 AND (SELECT dx.standing FROM wa_science.admission dx WHERE dx.target_warrant_id=x.warrant_id AND dx.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id) ORDER BY dx.decision_ordinal DESC LIMIT 1)='ADMITTED'
 AND (SELECT dx.use_contract_ref FROM wa_science.admission dx WHERE dx.target_warrant_id=x.warrant_id AND dx.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id) ORDER BY dx.decision_ordinal DESC LIMIT 1)=NEW.use_contract_ref)))
 THEN RAISE EXCEPTION 'derived assertion crosses unsupported source scope'; END IF;
 IF EXISTS (
 WITH RECURSIVE ancestors(id) AS (SELECT a.assertion_id UNION
 SELECT i.input_assertion_id FROM wa_science.assertion_input i JOIN ancestors p ON i.assertion_id=p.id WHERE i.input_assertion_id IS NOT NULL)
 SELECT 1 FROM ancestors p JOIN wa_science.assertion_input i ON i.assertion_id=p.id
 JOIN wa_science.assertion child ON child.assertion_id=i.assertion_id
 JOIN wa_science.material_evidence m ON m.evidence_id=i.input_material_id
 JOIN wa_science.support ms ON ms.support_id=m.support_id
 WHERE ms.support_resolution='UNRESOLVED' OR m.support_id<>child.support_id)
 THEN RAISE EXCEPTION 'material evidence must become assertion at its own supported scope before any warranted extrapolation'; END IF;
 IF a.support_id<>NEW.target_support_id THEN
  IF NEW.extrapolation_warrant_id IS NULL THEN RAISE EXCEPTION 'scientific scope crossing without warrant'; END IF;
  SELECT * INTO STRICT w FROM wa_science.extrapolation WHERE warrant_id=NEW.extrapolation_warrant_id;
  IF w.knowledge_ordinal>(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id)
 OR (SELECT dx.standing FROM wa_science.admission dx WHERE dx.target_warrant_id=w.warrant_id AND dx.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id) ORDER BY dx.decision_ordinal DESC LIMIT 1) IS DISTINCT FROM 'ADMITTED'
 OR (SELECT dx.use_contract_ref FROM wa_science.admission dx WHERE dx.target_warrant_id=w.warrant_id AND dx.decision_ordinal<=(SELECT scientific_cutoff_ordinal FROM wa_world.realization WHERE world_id=NEW.world_id) ORDER BY dx.decision_ordinal DESC LIMIT 1) IS DISTINCT FROM NEW.use_contract_ref
 OR w.assertion_id<>a.assertion_id OR w.to_support_id<>NEW.target_support_id OR w.property_code<>a.property_code
  THEN RAISE EXCEPTION 'wrong extrapolation scope/property'; END IF;
 ELSIF NEW.extrapolation_warrant_id IS NOT NULL THEN RAISE EXCEPTION 'redundant extrapolation cannot launder lineage'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER constraint_admission_scope BEFORE INSERT ON wa_world.constraint_binding FOR EACH ROW EXECUTE FUNCTION wa_world.guard_constraint();
CREATE FUNCTION wa_run.guard_envelope() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE p wa_run.causal_envelope%ROWTYPE;
BEGIN
 -- Serialize import/export order for one run; no simulation order is generated here.
 PERFORM pg_advisory_xact_lock(hashtextextended('wa_run:'||NEW.run_id,0));
 IF NEW.context_id<>NEW.run_id THEN RAISE EXCEPTION 'REALIZED context must identify exact run'; END IF;
 IF NEW.event_ordinal=0 THEN
  IF NEW.previous_trace_hash<>'' THEN RAISE EXCEPTION 'genesis previous hash'; END IF;
 ELSE
  SELECT * INTO STRICT p FROM wa_run.causal_envelope WHERE run_id=NEW.run_id AND event_ordinal=NEW.event_ordinal-1;
  IF NEW.previous_trace_hash<>p.envelope_hash OR NEW.pre_domain_hash<>p.post_domain_hash OR NEW.realized_time<p.realized_time
  THEN RAISE EXCEPTION 'discontinuous causal chain'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER envelope_chain BEFORE INSERT ON wa_run.causal_envelope FOR EACH ROW EXECUTE FUNCTION wa_run.guard_envelope();
CREATE FUNCTION wa_run.guard_parent() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE c bigint; p bigint;
BEGIN
 SELECT event_ordinal INTO STRICT c FROM wa_run.causal_envelope WHERE run_id=NEW.run_id AND envelope_id=NEW.child_envelope_id;
 SELECT event_ordinal INTO STRICT p FROM wa_run.causal_envelope WHERE run_id=NEW.run_id AND envelope_id=NEW.parent_envelope_id;
 IF p>=c THEN RAISE EXCEPTION 'forward or cyclic causal parent'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER ordered_trace_parent BEFORE INSERT ON wa_run.trace_parent FOR EACH ROW EXECUTE FUNCTION wa_run.guard_parent();
CREATE FUNCTION wa_info.guard_request_context() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE s text;
BEGIN
 SELECT c.semantic_key INTO STRICT s FROM wa_run.execution r JOIN wa_world.scenario c ON r.scenario_id=c.scenario_id WHERE r.run_id=NEW.run_id;
 IF (NEW.world_context='REALIZED' AND NEW.context_id<>NEW.run_id) OR (NEW.world_context='SCENARIO' AND NEW.context_id<>s)
 THEN RAISE EXCEPTION 'implicit run/scenario context crossing'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER request_context BEFORE INSERT ON wa_info.consumption_request FOR EACH ROW EXECUTE FUNCTION wa_info.guard_request_context();
CREATE TRIGGER value_context BEFORE INSERT ON wa_info.context_value FOR EACH ROW EXECUTE FUNCTION wa_info.guard_request_context();
CREATE FUNCTION wa_info.guard_receipt() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE q wa_info.consumption_request%ROWTYPE; v wa_info.context_value%ROWTYPE;
BEGIN
 SELECT * INTO STRICT q FROM wa_info.consumption_request WHERE run_id=NEW.run_id AND request_id=NEW.request_id;
 SELECT * INTO STRICT v FROM wa_info.context_value WHERE run_id=NEW.run_id AND value_ref=NEW.value_ref;
 IF NEW.state<>v.value_state THEN RAISE EXCEPTION 'receipt state mismatch'; END IF;
 IF NEW.state='KNOWN' AND ((q.subject_ref,q.concept,q.scope_ref,q.world_context,q.context_id,q.time_basis,q.required_unit,q.required_role)
 IS DISTINCT FROM (v.subject_ref,v.concept,v.scope_ref,v.world_context,v.context_id,v.time_basis,v.unit_lexeme,v.proposition_role)
 OR v.admission_state<>'ADMITTED' OR q.effective_time<v.valid_from OR q.effective_time>v.valid_to OR v.available_from>q.knowledge_cutoff
 OR (q.perspective='AGENT' AND (v.perspective<>'AGENT' OR v.perspective_actor_id<>q.consumer_id)))
 THEN RAISE EXCEPTION 'receipt cannot assert known outside admitted scope/time/perspective'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER receipt_integrity BEFORE INSERT ON wa_info.receipt FOR EACH ROW EXECUTE FUNCTION wa_info.guard_receipt();
CREATE FUNCTION wa_info.guard_agent_fact() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE q wa_info.consumption_request%ROWTYPE; r wa_info.receipt%ROWTYPE; v wa_info.context_value%ROWTYPE;
BEGIN
 SELECT * INTO STRICT r FROM wa_info.receipt WHERE run_id=NEW.run_id AND receipt_id=NEW.receipt_id;
 SELECT * INTO STRICT q FROM wa_info.consumption_request WHERE run_id=r.run_id AND request_id=r.request_id;
 SELECT * INTO STRICT v FROM wa_info.context_value WHERE run_id=r.run_id AND value_ref=r.value_ref;
 IF q.perspective<>'AGENT' OR q.consumer_id<>NEW.actor_id OR q.use_ref<>'POLICY' OR q.concept<>NEW.fact_key
 OR q.effective_time<>NEW.effective_time OR NEW.value_state<>r.state OR NEW.value_lexeme IS DISTINCT FROM v.value_lexeme
 OR NEW.value_state='BLOCKED' THEN RAISE EXCEPTION 'invalid Agent snapshot fact'; END IF;
 IF q.concept IN ('R_IN_SITU','R_ACCESSIBLE','R_RECOVERABLE','R_RESERVE','resource.R_IN_SITU','resource.R_ACCESSIBLE','resource.R_RECOVERABLE','resource.R_RESERVE')
 THEN RAISE EXCEPTION 'hidden resource state is not Agent information'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER agent_fact_integrity BEFORE INSERT ON wa_info.agent_fact FOR EACH ROW EXECUTE FUNCTION wa_info.guard_agent_fact();

-- Cross-record guards validate projections; they never calculate a simulation outcome.
CREATE FUNCTION wa_geo.guard_geometry_frame() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE f wa_geo.frame%ROWTYPE;
BEGIN
 SELECT * INTO STRICT f FROM wa_geo.frame WHERE frame_id=NEW.frame_id;
 IF (f.body_id IS NOT NULL AND f.body_id IS DISTINCT FROM NEW.body_id) OR (f.system_id IS NOT NULL AND f.system_id IS DISTINCT FROM NEW.system_id) THEN RAISE EXCEPTION 'geometry frame belongs to another body'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER geometry_frame_body BEFORE INSERT ON wa_geo.geometry FOR EACH ROW EXECUTE FUNCTION wa_geo.guard_geometry_frame();
CREATE FUNCTION wa_science.guard_extrapolation() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE a wa_science.assertion%ROWTYPE; d wa_science.admission%ROWTYPE; x wa_science.source_artifact%ROWTYPE;
BEGIN
 SELECT * INTO STRICT a FROM wa_science.assertion WHERE assertion_id=NEW.assertion_id;
 SELECT * INTO STRICT d FROM wa_science.admission WHERE admission_id=NEW.admission_id;
 SELECT * INTO STRICT x FROM wa_science.source_artifact WHERE artifact_id=NEW.scientific_warrant_artifact_id;
 IF a.body_id<>NEW.from_body_id OR a.property_code<>NEW.property_code OR d.standing<>'ADMITTED'
 OR d.decision_ordinal>NEW.knowledge_ordinal OR x.byte_sha256 IS NULL OR x.custody_kind='REMOTE_REFERENCE_ONLY'
 THEN RAISE EXCEPTION 'unqualified extrapolation warrant'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER scientific_extrapolation_guard BEFORE INSERT ON wa_science.extrapolation FOR EACH ROW EXECUTE FUNCTION wa_science.guard_extrapolation();
CREATE FUNCTION wa_science.guard_warrant_decision() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE k bigint;
BEGIN
 IF NEW.target_warrant_id IS NOT NULL THEN
 SELECT knowledge_ordinal INTO STRICT k FROM wa_science.extrapolation WHERE warrant_id=NEW.target_warrant_id;
 IF NEW.decision_ordinal<k THEN RAISE EXCEPTION 'warrant decision predates recorded scientific availability'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER warrant_decision_time BEFORE INSERT ON wa_science.admission FOR EACH ROW EXECUTE FUNCTION wa_science.guard_warrant_decision();

CREATE FUNCTION wa_science.guard_supersession() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF EXISTS (WITH RECURSIVE successors(id) AS (SELECT NEW.new_assertion_id UNION
 SELECT s.new_assertion_id FROM wa_science.supersession s JOIN successors p ON s.old_assertion_id=p.id)
 SELECT 1 FROM successors WHERE id=NEW.old_assertion_id) THEN RAISE EXCEPTION 'cyclic supersession'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER supersession_cycle AFTER INSERT ON wa_science.supersession DEFERRABLE INITIALLY DEFERRED
 FOR EACH ROW EXECUTE FUNCTION wa_science.guard_supersession();
CREATE FUNCTION wa_world.guard_hidden_value() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE k text;
BEGIN
 SELECT value_domain INTO STRICT k FROM wa_world.physical_property WHERE property_code=NEW.property_code;
 IF NEW.value_state='KNOWN' AND ((k='NUMBER' AND NEW.numeric_value IS NULL) OR (k<>'NUMBER' AND NEW.text_value IS NULL))
 THEN RAISE EXCEPTION 'physical property type mismatch'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER physical_property_type BEFORE INSERT ON wa_world.hidden_state FOR EACH ROW EXECUTE FUNCTION wa_world.guard_hidden_value();
CREATE FUNCTION wa_run.guard_stock() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE d wa_world.deposit%ROWTYPE;
BEGIN
 SELECT * INTO STRICT d FROM wa_world.deposit WHERE deposit_id=NEW.deposit_id;
 IF NEW.remaining_state='KNOWN' AND (d.initial_in_situ_state<>'KNOWN' OR NEW.unit_key IS DISTINCT FROM d.unit_key
 OR NEW.remaining_in_situ+NEW.cumulative_extracted<>d.initial_in_situ_quantity)
 THEN RAISE EXCEPTION 'finite in-situ projection does not reconcile'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER finite_stock_guard BEFORE INSERT ON wa_run.stock_state FOR EACH ROW EXECUTE FUNCTION wa_run.guard_stock();
CREATE FUNCTION wa_run.guard_accessibility() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE r wa_run.stock_state%ROWTYPE;
BEGIN
 IF NEW.value_state='KNOWN' THEN
 SELECT * INTO STRICT r FROM wa_run.stock_state WHERE run_id=NEW.run_id AND deposit_id=NEW.deposit_id AND event_id=NEW.event_id;
 IF r.remaining_state<>'KNOWN' OR NEW.unit_key IS DISTINCT FROM r.unit_key OR NEW.accessible_quantity>r.remaining_in_situ
 THEN RAISE EXCEPTION 'accessibility exceeds qualified local stock'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER accessibility_bound AFTER INSERT ON wa_run.accessibility_assessment
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION wa_run.guard_accessibility();
CREATE FUNCTION wa_run.guard_recovery() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE a wa_run.accessibility_assessment%ROWTYPE;
BEGIN
 SELECT * INTO STRICT a FROM wa_run.accessibility_assessment WHERE run_id=NEW.run_id AND deposit_id=NEW.deposit_id AND assessment_key=NEW.accessibility_key;
 IF NEW.value_state='KNOWN' AND (a.value_state<>'KNOWN' OR a.event_id<>NEW.event_id OR NEW.unit_key IS DISTINCT FROM a.unit_key
 OR NEW.recoverable_quantity>a.accessible_quantity) THEN RAISE EXCEPTION 'recovery lacks matching physical capability bound'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER recoverability_bound BEFORE INSERT ON wa_run.recoverability_assessment FOR EACH ROW EXECUTE FUNCTION wa_run.guard_recovery();
CREATE FUNCTION wa_info.guard_loop() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE d wa_info.decision%ROWTYPE; a wa_info.action_authorization%ROWTYPE; e wa_run.causal_envelope%ROWTYPE;
 q wa_info.consumption_request%ROWTYPE; p wa_info.possession%ROWTYPE;
BEGIN
 SELECT * INTO STRICT d FROM wa_info.decision WHERE run_id=NEW.run_id AND decision_id=NEW.decision_id;
 SELECT * INTO STRICT a FROM wa_info.action_authorization WHERE run_id=NEW.run_id AND authorization_id=NEW.authorization_id;
 SELECT * INTO STRICT e FROM wa_run.causal_envelope WHERE run_id=NEW.run_id AND envelope_id=NEW.consequence_envelope_id;
 SELECT cr.* INTO STRICT q FROM wa_info.receipt r JOIN wa_info.consumption_request cr ON (r.run_id,r.request_id)=(cr.run_id,cr.request_id)
 WHERE r.run_id=NEW.run_id AND r.receipt_id=NEW.receipt_id;
 IF d.actor_id<>NEW.actor_id OR a.actor_id<>NEW.actor_id OR a.decision_id IS DISTINCT FROM d.decision_id
 OR q.consumer_id<>NEW.actor_id OR q.perspective<>'AGENT' OR q.effective_time<>d.decision_time OR q.knowledge_cutoff>d.decision_time
 OR a.authorization_time<d.decision_time OR a.authorization_time>e.realized_time
 OR e.actor_ref<>NEW.actor_id THEN RAISE EXCEPTION 'open or mismatched epistemic-causal loop'; END IF;
 IF NEW.subsequent_information_id IS NOT NULL THEN
 SELECT * INTO STRICT p FROM wa_info.possession WHERE run_id=NEW.run_id AND actor_id=NEW.actor_id
 AND information_id=NEW.subsequent_information_id AND possession_key=NEW.subsequent_possession_key;
 IF p.available_from<e.realized_time THEN RAISE EXCEPTION 'subsequent information predates consequence'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER loop_integrity BEFORE INSERT ON wa_info.epistemic_loop FOR EACH ROW EXECUTE FUNCTION wa_info.guard_loop();
CREATE FUNCTION wa_info.guard_actor_class() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM wa_run.actor_reference a WHERE a.run_id=NEW.run_id AND a.actor_id=NEW.actor_id AND a.original_runtime_class='AGENT')
 THEN RAISE EXCEPTION 'Agent access requires existing AGENT identity'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER principal_actor_class BEFORE INSERT OR UPDATE ON wa_info.principal_binding FOR EACH ROW EXECUTE FUNCTION wa_info.guard_actor_class();
CREATE TRIGGER snapshot_actor_class BEFORE INSERT ON wa_info.agent_fact FOR EACH ROW EXECUTE FUNCTION wa_info.guard_actor_class();
CREATE FUNCTION wa_info.guard_possession() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE i wa_info.information_artifact%ROWTYPE; e wa_run.causal_envelope%ROWTYPE;
BEGIN
 SELECT * INTO STRICT i FROM wa_info.information_artifact WHERE run_id=NEW.run_id AND information_id=NEW.information_id;
 SELECT * INTO STRICT e FROM wa_run.causal_envelope WHERE run_id=NEW.run_id AND envelope_id=NEW.event_id;
 IF NEW.available_from<i.created_time OR NEW.available_from<e.realized_time
 THEN RAISE EXCEPTION 'possession predates publication/admission event'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER possession_time BEFORE INSERT ON wa_info.possession FOR EACH ROW EXECUTE FUNCTION wa_info.guard_possession();
CREATE FUNCTION wa_meta.require_serializable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
BEGIN
 IF current_setting('transaction_isolation')<>'serializable' THEN RAISE EXCEPTION 'authority writes require SERIALIZABLE transaction'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_meta.design_version FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_meta.design_version FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_meta.source_snapshot FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_meta.source_snapshot FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_meta.legacy_row FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_meta.legacy_row FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_meta.unit FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_meta.unit FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.time_support FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.time_support FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.vertical_support FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.vertical_support FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.body FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.body FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.body_identifier FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.body_identifier FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.body_system FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.body_system FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.system_member FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.system_member FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.frame FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.frame FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.geometry FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.geometry FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.location FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.location FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_geo.location_relation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_geo.location_relation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.source FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.source FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.source_artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.source_artifact FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_nav.product FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_nav.product FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_nav.coverage FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_nav.coverage FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.sample FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.sample FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.support FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.support FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.spatial_product FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.spatial_product FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.observation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.observation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.assertion FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.assertion FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.assertion_input FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.assertion_input FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.material_evidence FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.material_evidence FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.coverage FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.coverage FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.reconciliation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.reconciliation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.supersession FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.supersession FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.knowledge_event FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.knowledge_event FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.admission FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.admission FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_science.extrapolation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_science.extrapolation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.scenario FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.scenario FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.generation_model FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.generation_model FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.generation_policy FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.generation_policy FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.realization FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.realization FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.constraint_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.constraint_binding FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.physical_property FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.physical_property FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.hidden_state FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.hidden_state FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.site FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.site FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_world.deposit FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_world.deposit FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.execution FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.execution FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.world_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.world_binding FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.artifact FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.causal_envelope FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.causal_envelope FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.trace_artifact_edge FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.trace_artifact_edge FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.trace_parent FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.trace_parent FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.actor_reference FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.actor_reference FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.organization_reference FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.organization_reference FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.project FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.project FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.project_location FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.project_location FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.project_party FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.project_party FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.asset FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.asset FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.asset_location FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.asset_location FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.settlement FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.settlement FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.settlement_location FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.settlement_location FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.settlement_asset FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.settlement_asset FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.settlement_state FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.settlement_state FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.population_origin FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.population_origin FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.population_state FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.population_state FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.stock_state FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.stock_state FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.accessibility_assessment FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.accessibility_assessment FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.recoverability_assessment FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.recoverability_assessment FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.reserve_interpretation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.reserve_interpretation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.mission FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.mission FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_run.observation FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_run.observation FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.context_value FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.context_value FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.consumption_request FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.consumption_request FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.receipt FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.receipt FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.information_artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.information_artifact FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.possession FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.possession FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.belief FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.belief FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.decision FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.decision FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.action_authorization FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.action_authorization FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.epistemic_loop FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.epistemic_loop FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.agent_fact FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.agent_fact FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();

CREATE TRIGGER serializable_write BEFORE INSERT ON wa_meta.design_version FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_meta.source_snapshot FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_meta.legacy_row FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_meta.unit FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.time_support FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.vertical_support FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.body FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.body_identifier FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.body_system FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.system_member FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.frame FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.geometry FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.location FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_geo.location_relation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.source FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.source_artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_nav.product FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_nav.coverage FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.sample FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.support FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.spatial_product FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.observation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.assertion FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.assertion_input FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.material_evidence FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.coverage FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.reconciliation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.supersession FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.knowledge_event FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.admission FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_science.extrapolation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.scenario FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.generation_model FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.generation_policy FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.realization FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.constraint_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.physical_property FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.hidden_state FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.site FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_world.deposit FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.execution FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.world_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.causal_envelope FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.trace_artifact_edge FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.trace_parent FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.actor_reference FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.organization_reference FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.project FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.project_location FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.project_party FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.asset FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.asset_location FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.settlement FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.settlement_location FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.settlement_asset FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.settlement_state FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.population_origin FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.population_state FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.stock_state FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.accessibility_assessment FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.recoverability_assessment FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.reserve_interpretation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.mission FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_run.observation FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.context_value FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.consumption_request FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.receipt FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.information_artifact FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.possession FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.belief FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.decision FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.action_authorization FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.epistemic_loop FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.principal_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.agent_fact FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
CREATE FUNCTION wa_info.guard_safe_snapshot() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE a wa_run.artifact%ROWTYPE;
BEGIN
 SELECT * INTO STRICT a FROM wa_run.artifact WHERE run_id=NEW.run_id AND artifact_ref=NEW.original_artifact_ref;
 IF a.record_kind<>'DECISION_STATE' OR a.payload_bytes<>NEW.original_snapshot_bytes OR a.payload_sha256<>NEW.original_snapshot_sha256
 THEN RAISE EXCEPTION 'snapshot is not the exact original safe DecisionSnapshot artifact'; END IF;
 IF NOT EXISTS(SELECT 1 FROM wa_run.actor_reference WHERE run_id=NEW.run_id AND actor_id=NEW.actor_id AND original_runtime_class='AGENT')
 THEN RAISE EXCEPTION 'safe snapshot requires existing AGENT'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER safe_snapshot_original BEFORE INSERT ON wa_info.agent_snapshot FOR EACH ROW EXECUTE FUNCTION wa_info.guard_safe_snapshot();
CREATE FUNCTION wa_info.guard_decision_snapshot() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog AS $$
DECLARE a wa_info.agent_snapshot%ROWTYPE;
BEGIN
 SELECT * INTO STRICT a FROM wa_info.agent_snapshot WHERE run_id=NEW.run_id AND snapshot_ref=NEW.worker_snapshot_ref;
 IF a.actor_id<>NEW.actor_id OR a.effective_time<>NEW.decision_time OR a.original_artifact_ref<>NEW.original_snapshot_ref
 THEN RAISE EXCEPTION 'decision snapshot actor/time/artifact mismatch'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER decision_snapshot_original BEFORE INSERT ON wa_info.decision FOR EACH ROW EXECUTE FUNCTION wa_info.guard_decision_snapshot();
CREATE TRIGGER immutable_row BEFORE UPDATE OR DELETE ON wa_info.agent_snapshot FOR EACH ROW EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER immutable_table BEFORE TRUNCATE ON wa_info.agent_snapshot FOR EACH STATEMENT EXECUTE FUNCTION wa_meta.reject_rewrite();
CREATE TRIGGER serializable_write BEFORE INSERT ON wa_info.agent_snapshot FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();

CREATE INDEX science_property_support ON wa_science.assertion(body_id,property_code,support_id,semantic_key,revision);
CREATE INDEX science_assertion_admission ON wa_science.admission(target_assertion_id,decision_ordinal DESC) WHERE target_assertion_id IS NOT NULL;
CREATE INDEX science_material_admission ON wa_science.admission(target_material_id,decision_ordinal DESC) WHERE target_material_id IS NOT NULL;
CREATE INDEX world_property_lookup ON wa_world.hidden_state(world_id,location_id,property_code);
CREATE INDEX realization_scenario_lookup ON wa_world.realization(scenario_id,body_id);
CREATE INDEX trace_realization_lookup ON wa_run.causal_envelope(run_id,realized_time,event_ordinal);
CREATE INDEX trace_artifact_reverse ON wa_run.trace_artifact_edge(run_id,artifact_ref,envelope_id);
CREATE INDEX observation_location_epoch ON wa_run.observation(run_id,location_id,effective_time,observation_id);
CREATE INDEX agent_snapshot_lookup ON wa_info.agent_fact(run_id,actor_id,effective_time,snapshot_ref,fact_key);
CREATE INDEX project_location_period ON wa_run.project_location USING gist(effective_period);
CREATE INDEX asset_location_period ON wa_run.asset_location USING gist(effective_period);
CREATE INDEX settlement_location_period ON wa_run.settlement_location USING gist(effective_period);
CREATE INDEX knowledge_epoch_lookup ON wa_science.knowledge_event(event_time_id,event_id);
CREATE INDEX location_relation_reverse ON wa_geo.location_relation(to_location_id,from_location_id);
CREATE INDEX fk_source_artifact_d9fb5c0ef2 ON wa_science.source_artifact(source_id);
CREATE INDEX fk_assertion_d9fb5c0ef2 ON wa_science.assertion(source_id);
CREATE INDEX fk_assertion_b1b7b17b27 ON wa_science.assertion(support_id,body_id);
CREATE INDEX fk_assertion_06418411f1 ON wa_science.assertion(observation_id,body_id);
CREATE INDEX fk_assertion_8a9995336f ON wa_science.assertion(sample_id,body_id);
CREATE INDEX fk_assertion_2ca43c5910 ON wa_science.assertion(product_id,body_id);
CREATE INDEX fk_assertion_input_c90eb37b6c ON wa_science.assertion_input(input_assertion_id);
CREATE INDEX fk_assertion_input_1798b2139d ON wa_science.assertion_input(input_observation_id);
CREATE INDEX fk_assertion_input_c5629f5b90 ON wa_science.assertion_input(input_product_id);
CREATE INDEX fk_supersession_d7c78fb65c ON wa_science.supersession(new_assertion_id);
CREATE INDEX fk_constraint_binding_3771fa59d7 ON wa_world.constraint_binding(assertion_id);
CREATE INDEX fk_constraint_binding_e331d0efb5 ON wa_world.constraint_binding(target_support_id,body_id);
CREATE INDEX fk_site_290759fe17 ON wa_world.site(location_id,body_id);
CREATE INDEX fk_deposit_4b46c15b93 ON wa_world.deposit(site_id,world_id,body_id);
CREATE INDEX fk_trace_parent_d8de8bcb5d ON wa_run.trace_parent(run_id,parent_envelope_id);
CREATE INDEX fk_project_location_78d43dea1c ON wa_run.project_location(run_id,world_id,body_id);
CREATE INDEX fk_project_location_4b46c15b93 ON wa_run.project_location(site_id,world_id,body_id);
CREATE INDEX fk_asset_location_290759fe17 ON wa_run.asset_location(location_id,body_id);
CREATE INDEX fk_asset_location_d8d2b9f586 ON wa_run.asset_location(run_id,event_id);
CREATE INDEX fk_settlement_location_290759fe17 ON wa_run.settlement_location(location_id,body_id);
CREATE INDEX fk_settlement_location_d8d2b9f586 ON wa_run.settlement_location(run_id,event_id);
CREATE INDEX fk_settlement_asset_29ed94cf38 ON wa_run.settlement_asset(run_id,asset_id);
CREATE INDEX fk_settlement_state_d8d2b9f586 ON wa_run.settlement_state(run_id,event_id);
CREATE INDEX fk_population_state_8e9a52df13 ON wa_run.population_state(run_id,settlement_id);
CREATE INDEX fk_population_state_d8d2b9f586 ON wa_run.population_state(run_id,event_id);
CREATE INDEX fk_stock_state_d8d2b9f586 ON wa_run.stock_state(run_id,event_id);
CREATE INDEX fk_accessibility_assessment_d8d2b9f586 ON wa_run.accessibility_assessment(run_id,event_id);
CREATE INDEX fk_recoverability_assessmen_d8d2b9f586 ON wa_run.recoverability_assessment(run_id,event_id);
CREATE INDEX fk_reserve_interpretation_d8d2b9f586 ON wa_run.reserve_interpretation(run_id,event_id);
CREATE INDEX fk_mission_82f0098807 ON wa_run.mission(run_id,project_id);
CREATE INDEX fk_observation_a3955ea04e ON wa_run.observation(run_id,mission_id,world_id,body_id);
CREATE INDEX fk_observation_d8d2b9f586 ON wa_run.observation(run_id,event_id);
CREATE INDEX fk_context_value_e937dc45b2 ON wa_info.context_value(run_id,original_artifact_ref);
CREATE INDEX fk_receipt_aa0b90e356 ON wa_info.receipt(run_id,request_id);
CREATE INDEX fk_receipt_1876e6a6fc ON wa_info.receipt(run_id,value_ref,resolved_value_hash);
CREATE INDEX fk_information_artifact_ec3ee08f92 ON wa_info.information_artifact(run_id,source_observation_id);
CREATE INDEX fk_information_artifact_9f6c143fce ON wa_info.information_artifact(run_id,source_context_value_ref);
CREATE INDEX fk_possession_614cd369c3 ON wa_info.possession(run_id,information_id);
CREATE INDEX fk_belief_d8d2b9f586 ON wa_info.belief(run_id,event_id);
CREATE INDEX fk_belief_3d3c5f3ef8 ON wa_info.belief(run_id,source_information_id);
CREATE INDEX fk_decision_d1b267933a ON wa_info.decision(run_id,original_snapshot_ref);
CREATE INDEX fk_action_authorization_928d448236 ON wa_info.action_authorization(run_id,decision_id);
CREATE INDEX fk_epistemic_loop_708412062d ON wa_info.epistemic_loop(run_id,consequence_envelope_id);
CREATE INDEX fk_agent_fact_dd12e757df ON wa_info.agent_fact(run_id,receipt_id);
CREATE VIEW wa_science.assertion_standing WITH (security_barrier=true) AS
 SELECT a.*, COALESCE(d.standing,a.initial_standing) AS current_standing
 FROM wa_science.assertion a LEFT JOIN LATERAL
 (SELECT standing FROM wa_science.admission d WHERE d.target_assertion_id=a.assertion_id ORDER BY decision_ordinal DESC LIMIT 1) d ON true;
-- COALESCE above resolves an explicitly recorded initial governance status only; never a scientific/numeric value.
CREATE VIEW wa_science.real_assertions WITH (security_barrier=true) AS SELECT * FROM wa_science.assertion_standing WHERE world_context='REAL';
CREATE VIEW wa_world.scenario_states WITH (security_barrier=true) AS
 SELECT r.scenario_id,s.* FROM wa_world.hidden_state s JOIN wa_world.realization r ON r.world_id=s.world_id;
CREATE VIEW wa_run.realized_events WITH (security_barrier=true) AS SELECT * FROM wa_run.causal_envelope WHERE world_context='REALIZED';

REVOKE ALL ON ALL TABLES IN SCHEMA wa_meta,wa_geo,wa_nav,wa_science,wa_world,wa_run,wa_info FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA wa_meta,wa_geo,wa_world,wa_run,wa_info FROM PUBLIC;
GRANT USAGE ON SCHEMA wa_meta,wa_geo,wa_nav,wa_science TO wa_science_writer,wa_science_governor,wa_reference_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA wa_meta,wa_geo,wa_nav,wa_science TO wa_science_writer,wa_science_governor,wa_reference_reader;
GRANT INSERT ON ALL TABLES IN SCHEMA wa_geo,wa_nav,wa_science TO wa_science_writer;
REVOKE INSERT ON wa_science.admission,wa_science.extrapolation FROM wa_science_writer;
GRANT INSERT ON wa_meta.source_snapshot,wa_meta.legacy_row,wa_meta.unit TO wa_science_writer;
GRANT INSERT ON wa_science.admission,wa_science.extrapolation TO wa_science_governor;
GRANT USAGE ON SCHEMA wa_meta,wa_geo,wa_nav,wa_science,wa_world TO wa_world_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA wa_meta,wa_geo,wa_nav,wa_science TO wa_world_writer;
GRANT SELECT,INSERT ON ALL TABLES IN SCHEMA wa_world TO wa_world_writer;
GRANT USAGE ON SCHEMA wa_meta,wa_geo,wa_world,wa_run,wa_info TO wa_runtime_writer,wa_admission_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA wa_geo,wa_world,wa_run,wa_info TO wa_runtime_writer,wa_admission_writer;
GRANT INSERT ON ALL TABLES IN SCHEMA wa_run TO wa_runtime_writer;
GRANT INSERT ON wa_info.context_value,wa_info.consumption_request,wa_info.receipt,wa_info.information_artifact,
 wa_info.possession,wa_info.belief,wa_info.decision,wa_info.action_authorization,wa_info.epistemic_loop,wa_info.agent_fact,wa_info.agent_snapshot TO wa_admission_writer;
GRANT SELECT,INSERT,UPDATE,DELETE ON wa_info.principal_binding TO wa_admission_writer;
CREATE TRIGGER serializable_acl BEFORE UPDATE OR DELETE ON wa_info.principal_binding FOR EACH ROW EXECUTE FUNCTION wa_meta.require_serializable();
GRANT USAGE ON SCHEMA wa_meta,wa_geo,wa_nav,wa_science,wa_world,wa_run,wa_info TO wa_auditor;
GRANT SELECT ON ALL TABLES IN SCHEMA wa_meta,wa_geo,wa_nav,wa_science,wa_world,wa_run,wa_info TO wa_auditor;
-- FORCE RLS even for owners. No Agent membership in writer/audit roles is permissible.

ALTER TABLE wa_world.scenario ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.scenario FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.scenario TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.generation_model ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.generation_model FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.generation_model TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.generation_policy ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.generation_policy FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.generation_policy TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.realization ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.realization FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.realization TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.constraint_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.constraint_binding FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.constraint_binding TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.physical_property ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.physical_property FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.physical_property TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.hidden_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.hidden_state FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.hidden_state TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.site ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.site FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.site TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_world.deposit ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_world.deposit FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_world.deposit TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer,wa_world_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.execution ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.execution FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.execution TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.world_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.world_binding FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.world_binding TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.artifact FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.artifact TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.causal_envelope ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.causal_envelope FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.causal_envelope TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.trace_artifact_edge ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.trace_artifact_edge FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.trace_artifact_edge TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.trace_parent ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.trace_parent FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.trace_parent TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.actor_reference ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.actor_reference FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.actor_reference TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.organization_reference ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.organization_reference FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.organization_reference TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.project ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.project FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.project TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.project_location ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.project_location FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.project_location TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.project_party ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.project_party FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.project_party TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.asset ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.asset FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.asset TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.asset_location ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.asset_location FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.asset_location TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.settlement ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.settlement FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.settlement TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.settlement_location ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.settlement_location FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.settlement_location TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.settlement_asset ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.settlement_asset FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.settlement_asset TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.settlement_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.settlement_state FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.settlement_state TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.population_origin ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.population_origin FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.population_origin TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.population_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.population_state FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.population_state TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.stock_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.stock_state FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.stock_state TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.accessibility_assessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.accessibility_assessment FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.accessibility_assessment TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.recoverability_assessment ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.recoverability_assessment FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.recoverability_assessment TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.reserve_interpretation ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.reserve_interpretation FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.reserve_interpretation TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.mission ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.mission FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.mission TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_run.observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_run.observation FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_run.observation TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.context_value ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.context_value FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.context_value TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.consumption_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.consumption_request FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.consumption_request TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.receipt FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.receipt TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.information_artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.information_artifact FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.information_artifact TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.possession ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.possession FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.possession TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.belief ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.belief FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.belief TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.decision ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.decision FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.decision TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.action_authorization ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.action_authorization FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.action_authorization TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.epistemic_loop ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.epistemic_loop FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.epistemic_loop TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.principal_binding ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.principal_binding FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.principal_binding TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.agent_fact ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.agent_fact FORCE ROW LEVEL SECURITY;

CREATE POLICY trusted_services ON wa_info.agent_fact TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);

ALTER TABLE wa_info.agent_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE wa_info.agent_snapshot FORCE ROW LEVEL SECURITY;
CREATE POLICY trusted_services ON wa_info.agent_snapshot TO wa_owner,wa_auditor,wa_runtime_writer,wa_admission_writer USING(true) WITH CHECK(true);
GRANT USAGE ON SCHEMA wa_meta,wa_info TO wa_agent_view_owner;
GRANT SELECT ON wa_info.principal_binding,wa_info.agent_fact,wa_info.agent_snapshot TO wa_agent_view_owner;
CREATE POLICY principal_self ON wa_info.principal_binding FOR SELECT TO wa_agent_view_owner USING(login_name=session_user);
CREATE POLICY agent_fact_self ON wa_info.agent_fact FOR SELECT TO wa_agent_view_owner USING
 (EXISTS (SELECT 1 FROM wa_info.principal_binding b WHERE b.login_name=session_user AND b.run_id=agent_fact.run_id AND b.actor_id=agent_fact.actor_id AND b.authorized_snapshot_ref=agent_fact.snapshot_ref AND b.effective_time=agent_fact.effective_time));
CREATE POLICY agent_snapshot_self ON wa_info.agent_snapshot FOR SELECT TO wa_agent_view_owner USING
 (EXISTS(SELECT 1 FROM wa_info.principal_binding b WHERE b.login_name=session_user AND b.run_id=agent_snapshot.run_id AND b.actor_id=agent_snapshot.actor_id AND b.authorized_snapshot_ref=agent_snapshot.snapshot_ref AND b.effective_time=agent_snapshot.effective_time));
-- Owner temporarily needs schema CREATE solely to become owner of the bounded view, then it is revoked.
GRANT CREATE,USAGE ON SCHEMA wa_agent_api TO wa_agent_view_owner;
SET LOCAL ROLE wa_agent_view_owner;
CREATE VIEW wa_agent_api.snapshot_facts WITH (security_barrier=true,security_invoker=false) AS
 SELECT f.actor_id,f.snapshot_ref,f.fact_key,f.effective_time,f.value_state,f.value_lexeme,f.worker_source_ref
 FROM wa_info.agent_fact f WHERE EXISTS
 (SELECT 1 FROM wa_info.principal_binding b WHERE b.login_name=session_user AND b.run_id=f.run_id AND b.actor_id=f.actor_id AND b.authorized_snapshot_ref=f.snapshot_ref AND b.effective_time=f.effective_time);
CREATE VIEW wa_agent_api.current_snapshot WITH (security_barrier=true,security_invoker=false) AS
 SELECT a.actor_id,a.snapshot_ref,a.period_key,a.effective_time,a.original_snapshot_bytes
 FROM wa_info.agent_snapshot a WHERE EXISTS(SELECT 1 FROM wa_info.principal_binding b WHERE b.login_name=session_user
 AND b.run_id=a.run_id AND b.actor_id=a.actor_id AND b.authorized_snapshot_ref=a.snapshot_ref AND b.effective_time=a.effective_time);
GRANT SELECT ON wa_agent_api.snapshot_facts,wa_agent_api.current_snapshot TO wa_agent_reader;
SET LOCAL ROLE wa_owner;
REVOKE CREATE ON SCHEMA wa_agent_api FROM wa_agent_view_owner;
GRANT USAGE ON SCHEMA wa_agent_api,wa_meta TO wa_agent_reader;
-- Extension functions are installer-owned; return to the installer context.
RESET ROLE;
-- pgcrypto digest overloads default to PUBLIC EXECUTE. Revoke those exact
-- callable surfaces, then grant only bytea digest to trusted writer services.
REVOKE EXECUTE ON FUNCTION wa_crypto.digest(bytea,text),wa_crypto.digest(text,text) FROM PUBLIC;

GRANT USAGE ON SCHEMA wa_crypto TO wa_owner,wa_science_writer,wa_world_writer,wa_runtime_writer,wa_admission_writer;
GRANT EXECUTE ON FUNCTION wa_crypto.digest(bytea,text) TO wa_owner,wa_science_writer,wa_world_writer,wa_runtime_writer,wa_admission_writer;
COMMIT;
-- End design DDL. Login provisioning, source admission, import, seeding and runtime activation are excluded.
