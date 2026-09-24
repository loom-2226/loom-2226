-- Immutable Earth temporal projection. Existing snapshots and Ceres tables are untouched.
CREATE SCHEMA IF NOT EXISTS loom_narrator;

CREATE TABLE loom_control.import_batch (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    batch_id text NOT NULL,
    fact_family text NOT NULL,
    source_artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    source_model text NOT NULL,
    derivation_id text NOT NULL,
    record_count bigint NOT NULL CHECK (record_count >= 0),
    valid_from_year integer NOT NULL,
    valid_to_year integer NOT NULL,
    source_key_rule text NOT NULL,
    imported_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_id, batch_id),
    CHECK (valid_from_year <= valid_to_year)
);

CREATE TABLE loom_control.variable_semantics (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    variable_key text NOT NULL,
    human_label text NOT NULL,
    definition text NOT NULL,
    unit text NOT NULL,
    grain text NOT NULL,
    population_accounting_basis text NOT NULL,
    epistemic_status text NOT NULL,
    interpretation text NOT NULL,
    misuse_warning text NOT NULL,
    valid_from_year integer NOT NULL,
    valid_to_year integer NOT NULL,
    temporal_grain text NOT NULL,
    coverage_scope text NOT NULL,
    source_model_identity text NOT NULL,
    selected_scenario text,
    derivation_method text NOT NULL,
    source_artifact_hashes jsonb NOT NULL,
    predecessor text,
    future_limitation text,
    PRIMARY KEY (snapshot_id, variable_key)
);

CREATE TABLE loom_control.model_context_record (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    context_key text NOT NULL,
    context_value jsonb NOT NULL,
    description text NOT NULL,
    PRIMARY KEY (snapshot_id, context_key)
);

CREATE TABLE loom_control.temporal_coverage (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    fact_family text NOT NULL,
    variable_key text,
    coverage_scope text NOT NULL,
    valid_from_year integer NOT NULL,
    valid_to_year integer NOT NULL,
    temporal_grain text NOT NULL,
    geographic_coverage text NOT NULL,
    source_model text NOT NULL,
    epistemic_status text NOT NULL,
    handoff_predecessor text,
    unavailable_intervals jsonb NOT NULL DEFAULT '[]'::jsonb,
    PRIMARY KEY (snapshot_id, fact_family, coverage_scope, valid_from_year)
);

CREATE TABLE loom_civ.earth_derivation (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    derivation_id text NOT NULL,
    source_model text NOT NULL,
    method text NOT NULL,
    epistemic_status text NOT NULL,
    selected_scenario text,
    source_artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    notes text NOT NULL,
    PRIMARY KEY (snapshot_id, derivation_id)
);

CREATE TABLE loom_civ.earth_area (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    display_name text NOT NULL,
    wpp_location_id integer,
    wpp_location_type text NOT NULL,
    economic_qualified boolean NOT NULL,
    PRIMARY KEY (snapshot_id, iso3)
);

CREATE TABLE loom_civ.earth_demographic_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2226),
    biological_population double precision NOT NULL CHECK (biological_population >= 0),
    births double precision,
    deaths double precision,
    median_age double precision,
    age_under_20 double precision,
    age_20_64 double precision,
    age_65_plus double precision,
    age_80_plus double precision,
    age_100_plus double precision,
    age_120_plus double precision,
    age_150_plus double precision,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_biological_cohort_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2226),
    sex char(1) NOT NULL CHECK (sex IN ('F','M')),
    age_start integer NOT NULL CHECK (age_start >= 0),
    age_span integer,
    persons double precision NOT NULL CHECK (persons >= 0),
    open_ended boolean NOT NULL DEFAULT false,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, year, sex, age_start),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_economic_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2226),
    value_added double precision NOT NULL,
    gross_output double precision NOT NULL,
    investment double precision NOT NULL,
    capital double precision NOT NULL,
    population double precision,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_sector_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    sector text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2226),
    value_added double precision NOT NULL,
    gross_output double precision NOT NULL,
    investment double precision NOT NULL,
    capital double precision NOT NULL,
    employment double precision,
    effective_labor double precision,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, sector, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_sector_asset_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    sector text NOT NULL,
    asset_class text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2226),
    capital double precision NOT NULL,
    investment double precision,
    depreciation_rate double precision,
    replacement_need double precision,
    replacement_funded double precision,
    expansion_investment double precision,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, sector, asset_class, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_legacy_labor_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2026 AND 2100),
    legacy_employment double precision NOT NULL,
    legacy_labor_force double precision,
    labor_market_working_age_population double precision,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation
);

CREATE TABLE loom_civ.earth_labor_composition_year (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    iso3 text NOT NULL,
    year integer NOT NULL CHECK (year BETWEEN 2100 AND 2226),
    biological_population double precision NOT NULL,
    labor_capable_biological_population double precision NOT NULL,
    biological_effective_labor double precision NOT NULL,
    synthetic_population double precision NOT NULL,
    synthetic_effective_labor double precision NOT NULL,
    machine_task_capacity double precision NOT NULL,
    total_effective_labor double precision NOT NULL,
    recognized_person_population double precision NOT NULL,
    derivation_id text NOT NULL,
    PRIMARY KEY (snapshot_id, iso3, year),
    FOREIGN KEY (snapshot_id, iso3) REFERENCES loom_civ.earth_area,
    FOREIGN KEY (snapshot_id, derivation_id) REFERENCES loom_civ.earth_derivation,
    CHECK (biological_effective_labor <= labor_capable_biological_population + 1e-6),
    CHECK (labor_capable_biological_population <= biological_population + 1e-6)
);

CREATE INDEX earth_demographic_year_year_idx ON loom_civ.earth_demographic_year(snapshot_id,year);
CREATE INDEX earth_cohort_year_idx ON loom_civ.earth_biological_cohort_year(snapshot_id,year);
CREATE INDEX earth_economic_year_year_idx ON loom_civ.earth_economic_year(snapshot_id,year);
CREATE INDEX earth_sector_year_year_idx ON loom_civ.earth_sector_year(snapshot_id,year);
CREATE INDEX earth_asset_year_year_idx ON loom_civ.earth_sector_asset_year(snapshot_id,year);

COMMENT ON SCHEMA loom_narrator IS 'Read-only semantic retrieval surface over validated snapshot projections.';
COMMENT ON TABLE loom_civ.earth_legacy_labor_year IS 'Historical employment under v4 semantics; not biological effective labor.';
COMMENT ON TABLE loom_civ.earth_labor_composition_year IS 'Post-2100 selected biological, synthetic-person, and non-person machine labor categories.';
