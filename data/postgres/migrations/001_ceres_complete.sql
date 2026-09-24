-- Ceres complete development source projection v1. Source values remain exact; semantics live in loom_control.field_semantics.
-- Apply once with tools/ceres_pg.py migrate. No production consumer binding is changed.
CREATE SCHEMA IF NOT EXISTS loom_control;
CREATE SCHEMA IF NOT EXISTS loom_world;
CREATE SCHEMA IF NOT EXISTS loom_civ;
CREATE SCHEMA IF NOT EXISTS loom_media;
CREATE SCHEMA IF NOT EXISTS loom_ceres;
CREATE TABLE loom_control.schema_migration (
    revision text PRIMARY KEY, script_sha256 char(64) NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE loom_control.source_artifact (
    artifact_sha256 char(64) PRIMARY KEY, source_role text NOT NULL,
    source_path text NOT NULL, byte_count bigint NOT NULL,
    source_git_commit text, retained_location text NOT NULL);
CREATE TABLE loom_control.semantic_version (
    semantic_sha256 char(64) PRIMARY KEY, source_path text NOT NULL,
    source_git_commit text, recorded_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE loom_control.snapshot (
    snapshot_id text PRIMARY KEY, consumer_git_commit char(40) NOT NULL,
    consumer_query_sha256 char(64) NOT NULL,
    contract_sha256 char(64) NOT NULL,
    semantic_sha256 char(64) NOT NULL REFERENCES loom_control.semantic_version,
    state text NOT NULL CHECK (state IN ('CANDIDATE','VALIDATED','RETIRED')),
    created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE loom_control.snapshot_source (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    source_role text NOT NULL,
    PRIMARY KEY(snapshot_id, artifact_sha256, source_role));
CREATE TABLE loom_control.field_semantics (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    source_database text NOT NULL, source_table text NOT NULL, source_column text NOT NULL,
    semantic_status text NOT NULL CHECK (semantic_status IN ('STRUCTURAL','QUALIFIED','UNRESOLVED','NOT_ASSESSED','NOT_APPLICABLE')),
    presentation_label text NOT NULL,
    definition text NOT NULL, unit text NOT NULL, grain text NOT NULL,
    epoch_basis text NOT NULL, accounting_population_basis text NOT NULL,
    evidence_reference jsonb NOT NULL, missing_evidence text,
    PRIMARY KEY(snapshot_id, source_database, source_table, source_column));

CREATE TABLE loom_world.entities (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    entity_id text NOT NULL,
    name text,
    entity_class text,
    parent_entity_id text,
    source_command text,
    glyph_px double precision,
    provenance text,
    display_name_short text,
    visibility_class text,
    label_priority bigint,
    spatial_regime text,
    image_prompt text,
    image_prompt_status text,
    image_prompt_version text,
    PRIMARY KEY (snapshot_id, entity_id)
);
CREATE TABLE loom_world.celestial_properties (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    entity_id text NOT NULL,
    gm_km3_s2 double precision,
    mean_radius_km double precision,
    rotation_period_s double precision,
    source_id text,
    status text,
    PRIMARY KEY (snapshot_id, entity_id)
);
CREATE TABLE loom_world.celestial_dynamics (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    entity_id text NOT NULL,
    primary_gravity_parent_id text,
    horizons_command text,
    parent_center_command text,
    reference_orbit_radius_km double precision,
    orbital_period_days double precision,
    gm_km3_s2 double precision,
    mean_radius_km double precision,
    soi_radius_km double precision,
    hill_radius_km double precision,
    atmosphere_class text,
    metadata_status text,
    source text,
    PRIMARY KEY (snapshot_id, entity_id)
);
CREATE TABLE loom_world.infrastructure_nodes (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    node_id text NOT NULL,
    node_name text,
    system text,
    parent_body text,
    traffic text,
    facility_type text,
    commercial_1 text,
    commercial_2 text,
    commercial_regime text,
    civil_authority text,
    administrative_authority text,
    security_authority text,
    synthetic_constituency_1 text,
    institutional_morphology text,
    source text,
    entity_id text,
    region_entity_id text,
    parent_entity_id text,
    PRIMARY KEY (snapshot_id, node_id)
);
CREATE TABLE loom_world.knowledge_entities (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    noun_id text NOT NULL,
    canonical_name text,
    noun_class text,
    quick_description text,
    boundary_note text,
    spatial_entity_id text,
    canon_status text,
    source text,
    source_detail text,
    display_name_short text,
    image_prompt text,
    image_prompt_status text,
    image_prompt_version text,
    PRIMARY KEY (snapshot_id, noun_id)
);
CREATE TABLE loom_world.image_assets (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    asset_id text NOT NULL,
    entity_id text,
    asset_role text,
    prompt_version text,
    prompt_hash text,
    provider text,
    model_id text,
    generation_status text,
    review_status text,
    media_key text,
    mime_type text,
    width_px bigint,
    height_px bigint,
    content_hash text,
    byte_length bigint,
    thumbnail_hash text,
    thumbnail_byte_length bigint,
    created_at text,
    updated_at text,
    is_current bigint,
    PRIMARY KEY (snapshot_id, asset_id)
);
CREATE TABLE loom_world.provenance_sources (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    source_id text NOT NULL,
    source_class text,
    citation text,
    authority_status text,
    PRIMARY KEY (snapshot_id, source_id)
);
CREATE TABLE loom_civ.civ_subject (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    subject_class text,
    display_name text,
    navigator_entity_id text,
    navigator_node_id text,
    navigator_noun_id text,
    iso3 text,
    parent_subject_id text,
    spatial_subject_id text,
    aggregation_class text,
    active_2226 bigint,
    PRIMARY KEY (snapshot_id, subject_id)
);
CREATE TABLE loom_civ.civ_model_run (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    run_id text NOT NULL,
    model_name text,
    version text,
    status text,
    boundary_year bigint,
    source_detail text,
    assumptions_json text,
    created_at text,
    PRIMARY KEY (snapshot_id, run_id)
);
CREATE TABLE loom_civ.civ_derivation (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    derivation_id text NOT NULL,
    epistemic_class text,
    run_id text,
    method text,
    source_detail text,
    confidence double precision,
    uncertainty_low double precision,
    uncertainty_high double precision,
    notes text,
    PRIMARY KEY (snapshot_id, derivation_id)
);
CREATE TABLE loom_civ.civ_demographic_state (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    biological_population double precision,
    synthetic_population double precision,
    transient_population double precision,
    working_age_population double precision,
    age_0_14 double precision,
    age_15_64 double precision,
    age_65_plus double precision,
    age_80_plus double precision,
    median_age double precision,
    households double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year)
);
CREATE TABLE loom_civ.civ_economic_state (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    value_added double precision,
    gross_output double precision,
    consumption double precision,
    investment double precision,
    productive_capital double precision,
    infrastructure_capital double precision,
    residential_capital double precision,
    capital_output_ratio double precision,
    investment_output_ratio double precision,
    productivity_index double precision,
    income_per_capita double precision,
    consumption_per_capita double precision,
    price_level_index double precision,
    economic_complexity_index double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year)
);
CREATE TABLE loom_civ.civ_workforce_state (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    sector_id text NOT NULL,
    biological_workers double precision,
    synthetic_workers double precision,
    remote_workers double precision,
    transient_workers double precision,
    machine_task_equivalent double precision,
    total_fte_equivalent double precision,
    mean_paid_hours_week double precision,
    automation_task_share double precision,
    participation_rate double precision,
    employment_rate double precision,
    skill_index double precision,
    labor_productivity_index double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year, sector_id)
);
CREATE TABLE loom_civ.civ_place_dna (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    governance_style text,
    security_posture double precision,
    commercial_openness double precision,
    corporate_proxy_level double precision,
    local_autonomy double precision,
    institutional_trust double precision,
    synthetic_acceptance double precision,
    migration_openness double precision,
    frontier_mentality double precision,
    wealth_level double precision,
    scarcity_pressure double precision,
    social_tension double precision,
    law_enforcement_reach double precision,
    data_sharing_level double precision,
    outsider_attitude double precision,
    concise_behavioral_prompt text,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year)
);
CREATE TABLE loom_civ.civ_governance_profile (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    ultimate_sovereign text,
    local_civil_authority text,
    administrative_authority text,
    security_provider text,
    primary_owner_operator text,
    primary_financier text,
    primary_certifier text,
    state_control double precision,
    local_autonomy double precision,
    corporate_proxy_governance double precision,
    corporate_state_alignment double precision,
    institutional_fragmentation double precision,
    enforcement_capacity double precision,
    data_sharing_level double precision,
    torch_corporate_legacy double precision,
    metric_reassertion double precision,
    loom_frontier_disruption double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year)
);
CREATE TABLE loom_civ.civ_infrastructure_state (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    node_subject_id text NOT NULL,
    year bigint NOT NULL,
    resident_population double precision,
    transient_daily_population double precision,
    workforce double precision,
    capital_stock double precision,
    replacement_value double precision,
    annual_value_added double precision,
    annual_operating_cost double precision,
    power_average_mw double precision,
    power_peak_mw double precision,
    habitable_capacity double precision,
    industrial_capacity_index double precision,
    cargo_throughput_tonnes_year double precision,
    passenger_movements_year double precision,
    ship_calls_year double precision,
    berths_equivalent double precision,
    utilization double precision,
    strategic_importance double precision,
    economic_centrality double precision,
    transport_centrality double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, node_subject_id, year)
);
CREATE TABLE loom_civ.civ_social_state (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    biological_age_pressure double precision,
    synthetic_presence double precision,
    automation_exposure double precision,
    family_viability double precision,
    migration_dependence double precision,
    capital_concentration double precision,
    access_scarcity double precision,
    external_dependence double precision,
    strategic_leverage double precision,
    political_autonomy double precision,
    cultural_distance double precision,
    institutional_trust double precision,
    cognitive_sovereignty_pressure double precision,
    local_born_share double precision,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year)
);
CREATE TABLE loom_civ.civ_social_pressure (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    year bigint NOT NULL,
    pressure_type text NOT NULL,
    intensity double precision,
    direction text,
    affected_groups text,
    trigger_basis text,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, year, pressure_type)
);
CREATE TABLE loom_civ.civ_census_node_relation (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    node_subject_id text NOT NULL,
    zone_subject_id text NOT NULL,
    year bigint NOT NULL,
    relationship_type text NOT NULL,
    primary_relation bigint,
    confidence double precision,
    basis_code text,
    basis_text text,
    derivation_id text,
    PRIMARY KEY (snapshot_id, node_subject_id, zone_subject_id, year, relationship_type)
);
CREATE TABLE loom_civ.civ_influence_edge (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    subject_id text NOT NULL,
    actor_subject_id text NOT NULL,
    year bigint NOT NULL,
    influence_domain text NOT NULL,
    influence_weight double precision,
    control_class text,
    basis text,
    derivation_id text,
    PRIMARY KEY (snapshot_id, subject_id, actor_subject_id, year, influence_domain)
);
CREATE TABLE loom_media.media_assets (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    media_key text NOT NULL,
    asset_id text,
    mime_type text,
    width_px bigint,
    height_px bigint,
    original_blob bytea,
    original_byte_length bigint,
    original_sha256 text,
    thumbnail_mime_type text,
    thumbnail_blob bytea,
    thumbnail_byte_length bigint,
    thumbnail_sha256 text,
    created_at text,
    updated_at text,
    PRIMARY KEY (snapshot_id, media_key)
);
CREATE TABLE loom_media.ceres_manifest_asset (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    node_id text NOT NULL, name text NOT NULL, facility_type text NOT NULL,
    noun_id text NOT NULL, asset_id text NOT NULL, role text NOT NULL,
    is_current bigint NOT NULL CHECK (is_current IN (0,1)),
    review_status text NOT NULL, media_key text NOT NULL,
    civstate_zones jsonb NOT NULL, export_status text NOT NULL,
    filename text NOT NULL, sha256 char(64) NOT NULL, byte_length bigint NOT NULL,
    PRIMARY KEY (snapshot_id,node_id));
CREATE TABLE loom_media.ceres_manifest_zone_relation (
    snapshot_id text NOT NULL, node_id text NOT NULL,
    zone_subject_id text NOT NULL, relationship_type text NOT NULL,
    primary_relation boolean NOT NULL, confidence double precision NOT NULL,
    basis_code text NOT NULL,
    PRIMARY KEY(snapshot_id,node_id,zone_subject_id,relationship_type),
    FOREIGN KEY(snapshot_id,node_id) REFERENCES loom_media.ceres_manifest_asset(snapshot_id,node_id));

ALTER TABLE loom_world.entities ADD FOREIGN KEY (snapshot_id,parent_entity_id) REFERENCES loom_world.entities(snapshot_id,entity_id);
ALTER TABLE loom_world.celestial_properties ADD FOREIGN KEY (snapshot_id,entity_id) REFERENCES loom_world.entities(snapshot_id,entity_id);
ALTER TABLE loom_world.celestial_dynamics ADD FOREIGN KEY (snapshot_id,entity_id) REFERENCES loom_world.entities(snapshot_id,entity_id);
ALTER TABLE loom_world.infrastructure_nodes ADD FOREIGN KEY (snapshot_id,entity_id) REFERENCES loom_world.entities(snapshot_id,entity_id);
ALTER TABLE loom_world.infrastructure_nodes ADD FOREIGN KEY (snapshot_id,parent_entity_id) REFERENCES loom_world.entities(snapshot_id,entity_id);
ALTER TABLE loom_world.image_assets ADD FOREIGN KEY (snapshot_id,entity_id) REFERENCES loom_world.knowledge_entities(snapshot_id,noun_id);
ALTER TABLE loom_civ.civ_subject ADD FOREIGN KEY (snapshot_id,parent_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_derivation ADD FOREIGN KEY (snapshot_id,run_id) REFERENCES loom_civ.civ_model_run(snapshot_id,run_id);
ALTER TABLE loom_civ.civ_demographic_state ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_economic_state ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_workforce_state ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_place_dna ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_governance_profile ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_infrastructure_state ADD FOREIGN KEY (snapshot_id,node_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_social_state ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_social_pressure ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_demographic_state ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_economic_state ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_workforce_state ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_place_dna ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_governance_profile ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_infrastructure_state ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_social_state ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_social_pressure ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_census_node_relation ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_influence_edge ADD FOREIGN KEY (snapshot_id,derivation_id) REFERENCES loom_civ.civ_derivation(snapshot_id,derivation_id);
ALTER TABLE loom_civ.civ_census_node_relation ADD FOREIGN KEY (snapshot_id,node_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_census_node_relation ADD FOREIGN KEY (snapshot_id,zone_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_influence_edge ADD FOREIGN KEY (snapshot_id,subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_civ.civ_influence_edge ADD FOREIGN KEY (snapshot_id,actor_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
ALTER TABLE loom_media.media_assets ADD FOREIGN KEY (snapshot_id,asset_id) REFERENCES loom_world.image_assets(snapshot_id,asset_id);
ALTER TABLE loom_media.ceres_manifest_asset ADD FOREIGN KEY (snapshot_id,node_id) REFERENCES loom_world.infrastructure_nodes(snapshot_id,node_id);
ALTER TABLE loom_media.ceres_manifest_asset ADD FOREIGN KEY (snapshot_id,noun_id) REFERENCES loom_world.knowledge_entities(snapshot_id,noun_id);
ALTER TABLE loom_media.ceres_manifest_asset ADD FOREIGN KEY (snapshot_id,asset_id) REFERENCES loom_world.image_assets(snapshot_id,asset_id);
ALTER TABLE loom_media.ceres_manifest_asset ADD FOREIGN KEY (snapshot_id,media_key) REFERENCES loom_media.media_assets(snapshot_id,media_key);
ALTER TABLE loom_media.ceres_manifest_zone_relation ADD FOREIGN KEY (snapshot_id,zone_subject_id) REFERENCES loom_civ.civ_subject(snapshot_id,subject_id);
CREATE VIEW loom_civ.civ_runtime_place_context AS
SELECT s.snapshot_id,s.subject_id,s.display_name,s.navigator_entity_id,s.navigator_node_id,
 p.governance_style,p.security_posture,p.commercial_openness,p.corporate_proxy_level,
 p.local_autonomy,p.institutional_trust,p.synthetic_acceptance,p.migration_openness,
 p.frontier_mentality,p.scarcity_pressure,p.social_tension,p.law_enforcement_reach,
 p.data_sharing_level,p.outsider_attitude,p.concise_behavioral_prompt,
 g.ultimate_sovereign,g.local_civil_authority,g.administrative_authority,g.security_provider,
 g.primary_owner_operator,g.primary_financier,g.primary_certifier,
 g.torch_corporate_legacy,g.metric_reassertion,g.loom_frontier_disruption,
 i.resident_population,i.transient_daily_population,i.workforce,i.annual_value_added,
 i.power_average_mw,i.cargo_throughput_tonnes_year,i.strategic_importance,
 i.economic_centrality,i.transport_centrality
FROM loom_civ.civ_subject s
JOIN loom_civ.civ_place_dna p ON p.snapshot_id=s.snapshot_id AND p.subject_id=s.subject_id AND p.year=2226
LEFT JOIN loom_civ.civ_governance_profile g ON g.snapshot_id=s.snapshot_id AND g.subject_id=s.subject_id AND g.year=2226
LEFT JOIN loom_civ.civ_infrastructure_state i ON i.snapshot_id=s.snapshot_id AND i.node_subject_id=s.subject_id AND i.year=2226;
CREATE VIEW loom_civ.v_graph_civstate_influence_edges AS
SELECT i.snapshot_id,i.subject_id,s.display_name AS subject_name,
 CASE WHEN s.navigator_entity_id IS NOT NULL THEN 'ENTITY:' || s.navigator_entity_id
      WHEN s.navigator_noun_id IS NOT NULL THEN 'NOUN:' || s.navigator_noun_id ELSE NULL END AS subject_node_key,
 i.actor_subject_id,a.display_name AS actor_name,
 CASE WHEN a.navigator_entity_id IS NOT NULL THEN 'ENTITY:' || a.navigator_entity_id
      WHEN a.navigator_noun_id IS NOT NULL THEN 'NOUN:' || a.navigator_noun_id ELSE NULL END AS actor_node_key,
 i.year,i.influence_domain,i.influence_weight,i.control_class,i.basis,i.derivation_id
FROM loom_civ.civ_influence_edge i
JOIN loom_civ.civ_subject s ON s.snapshot_id=i.snapshot_id AND s.subject_id=i.subject_id
JOIN loom_civ.civ_subject a ON a.snapshot_id=i.snapshot_id AND a.subject_id=i.actor_subject_id;

CREATE VIEW loom_ceres.entities AS SELECT entity_id, name, entity_class, parent_entity_id, source_command, glyph_px, provenance, display_name_short, visibility_class, label_priority, spatial_regime, image_prompt, image_prompt_status, image_prompt_version FROM loom_world.entities WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.celestial_properties AS SELECT entity_id, gm_km3_s2, mean_radius_km, rotation_period_s, source_id, status FROM loom_world.celestial_properties WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.celestial_dynamics AS SELECT entity_id, primary_gravity_parent_id, horizons_command, parent_center_command, reference_orbit_radius_km, orbital_period_days, gm_km3_s2, mean_radius_km, soi_radius_km, hill_radius_km, atmosphere_class, metadata_status, source FROM loom_world.celestial_dynamics WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.infrastructure_nodes AS SELECT node_id, node_name, system, parent_body, traffic, facility_type, commercial_1, commercial_2, commercial_regime, civil_authority, administrative_authority, security_authority, synthetic_constituency_1, institutional_morphology, source, entity_id, region_entity_id, parent_entity_id FROM loom_world.infrastructure_nodes WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.knowledge_entities AS SELECT noun_id, canonical_name, noun_class, quick_description, boundary_note, spatial_entity_id, canon_status, source, source_detail, display_name_short, image_prompt, image_prompt_status, image_prompt_version FROM loom_world.knowledge_entities WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.image_assets AS SELECT asset_id, entity_id, asset_role, prompt_version, prompt_hash, provider, model_id, generation_status, review_status, media_key, mime_type, width_px, height_px, content_hash, byte_length, thumbnail_hash, thumbnail_byte_length, created_at, updated_at, is_current FROM loom_world.image_assets WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.provenance_sources AS SELECT source_id, source_class, citation, authority_status FROM loom_world.provenance_sources WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_subject AS SELECT subject_id, subject_class, display_name, navigator_entity_id, navigator_node_id, navigator_noun_id, iso3, parent_subject_id, spatial_subject_id, aggregation_class, active_2226 FROM loom_civ.civ_subject WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_model_run AS SELECT run_id, model_name, version, status, boundary_year, source_detail, assumptions_json, created_at FROM loom_civ.civ_model_run WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_derivation AS SELECT derivation_id, epistemic_class, run_id, method, source_detail, confidence, uncertainty_low, uncertainty_high, notes FROM loom_civ.civ_derivation WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_demographic_state AS SELECT subject_id, year, biological_population, synthetic_population, transient_population, working_age_population, age_0_14, age_15_64, age_65_plus, age_80_plus, median_age, households, derivation_id FROM loom_civ.civ_demographic_state WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_economic_state AS SELECT subject_id, year, value_added, gross_output, consumption, investment, productive_capital, infrastructure_capital, residential_capital, capital_output_ratio, investment_output_ratio, productivity_index, income_per_capita, consumption_per_capita, price_level_index, economic_complexity_index, derivation_id FROM loom_civ.civ_economic_state WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_workforce_state AS SELECT subject_id, year, sector_id, biological_workers, synthetic_workers, remote_workers, transient_workers, machine_task_equivalent, total_fte_equivalent, mean_paid_hours_week, automation_task_share, participation_rate, employment_rate, skill_index, labor_productivity_index, derivation_id FROM loom_civ.civ_workforce_state WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_place_dna AS SELECT subject_id, year, governance_style, security_posture, commercial_openness, corporate_proxy_level, local_autonomy, institutional_trust, synthetic_acceptance, migration_openness, frontier_mentality, wealth_level, scarcity_pressure, social_tension, law_enforcement_reach, data_sharing_level, outsider_attitude, concise_behavioral_prompt, derivation_id FROM loom_civ.civ_place_dna WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_governance_profile AS SELECT subject_id, year, ultimate_sovereign, local_civil_authority, administrative_authority, security_provider, primary_owner_operator, primary_financier, primary_certifier, state_control, local_autonomy, corporate_proxy_governance, corporate_state_alignment, institutional_fragmentation, enforcement_capacity, data_sharing_level, torch_corporate_legacy, metric_reassertion, loom_frontier_disruption, derivation_id FROM loom_civ.civ_governance_profile WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_infrastructure_state AS SELECT node_subject_id, year, resident_population, transient_daily_population, workforce, capital_stock, replacement_value, annual_value_added, annual_operating_cost, power_average_mw, power_peak_mw, habitable_capacity, industrial_capacity_index, cargo_throughput_tonnes_year, passenger_movements_year, ship_calls_year, berths_equivalent, utilization, strategic_importance, economic_centrality, transport_centrality, derivation_id FROM loom_civ.civ_infrastructure_state WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_social_state AS SELECT subject_id, year, biological_age_pressure, synthetic_presence, automation_exposure, family_viability, migration_dependence, capital_concentration, access_scarcity, external_dependence, strategic_leverage, political_autonomy, cultural_distance, institutional_trust, cognitive_sovereignty_pressure, local_born_share, derivation_id FROM loom_civ.civ_social_state WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_social_pressure AS SELECT subject_id, year, pressure_type, intensity, direction, affected_groups, trigger_basis, derivation_id FROM loom_civ.civ_social_pressure WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_census_node_relation AS SELECT node_subject_id, zone_subject_id, year, relationship_type, primary_relation, confidence, basis_code, basis_text, derivation_id FROM loom_civ.civ_census_node_relation WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_influence_edge AS SELECT subject_id, actor_subject_id, year, influence_domain, influence_weight, control_class, basis, derivation_id FROM loom_civ.civ_influence_edge WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.media_assets AS SELECT media_key, asset_id, mime_type, width_px, height_px, original_blob, original_byte_length, original_sha256, thumbnail_mime_type, thumbnail_blob, thumbnail_byte_length, thumbnail_sha256, created_at, updated_at FROM loom_media.media_assets WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.civ_runtime_place_context AS SELECT subject_id, display_name, navigator_entity_id, navigator_node_id, governance_style, security_posture, commercial_openness, corporate_proxy_level, local_autonomy, institutional_trust, synthetic_acceptance, migration_openness, frontier_mentality, scarcity_pressure, social_tension, law_enforcement_reach, data_sharing_level, outsider_attitude, concise_behavioral_prompt, ultimate_sovereign, local_civil_authority, administrative_authority, security_provider, primary_owner_operator, primary_financier, primary_certifier, torch_corporate_legacy, metric_reassertion, loom_frontier_disruption, resident_population, transient_daily_population, workforce, annual_value_added, power_average_mw, cargo_throughput_tonnes_year, strategic_importance, economic_centrality, transport_centrality FROM loom_civ.civ_runtime_place_context WHERE snapshot_id = current_setting('loom.snapshot_id', true);
CREATE VIEW loom_ceres.v_graph_civstate_influence_edges AS SELECT subject_id, subject_name, subject_node_key, actor_subject_id, actor_name, actor_node_key, year, influence_domain, influence_weight, control_class, basis, derivation_id FROM loom_civ.v_graph_civstate_influence_edges WHERE snapshot_id = current_setting('loom.snapshot_id', true);
COMMENT ON SCHEMA loom_ceres IS 'Read-only compatibility projections; session must set loom.snapshot_id. Unresolved legacy values require field_semantics labels before presentation.';
