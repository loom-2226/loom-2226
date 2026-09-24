-- Additive Solar Phase-1 identity and ephemeris metadata. Existing domains are untouched.
CREATE SCHEMA IF NOT EXISTS loom_solar;

CREATE TABLE loom_solar.body (
    body_id text PRIMARY KEY,
    canonical_name text NOT NULL UNIQUE,
    body_class text NOT NULL,
    parent_body_id text REFERENCES loom_solar.body(body_id),
    status text NOT NULL CHECK (status IN ('ACTIVE', 'RETIRED', 'CANDIDATE')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE loom_solar.body_identifier (
    body_id text NOT NULL REFERENCES loom_solar.body(body_id),
    authority text NOT NULL,
    identifier_type text NOT NULL,
    identifier_value text NOT NULL,
    status text NOT NULL CHECK (status IN ('ACTIVE', 'RETIRED', 'ALIAS')),
    PRIMARY KEY (body_id, authority, identifier_type, identifier_value),
    UNIQUE (authority, identifier_type, identifier_value)
);

CREATE TABLE loom_solar.ephemeris_source (
    ephemeris_source_id text PRIMARY KEY,
    provider text NOT NULL,
    product_name text NOT NULL,
    product_version text NOT NULL,
    asset_filename text NOT NULL,
    sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    byte_count bigint NOT NULL CHECK (byte_count > 0),
    source_url text NOT NULL,
    acquired_at timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('CANDIDATE', 'QUALIFIED', 'RETIRED')),
    UNIQUE (provider, product_name, product_version, sha256)
);

CREATE TABLE loom_solar.ephemeris_coverage (
    ephemeris_source_id text NOT NULL REFERENCES loom_solar.ephemeris_source(ephemeris_source_id),
    body_id text NULL REFERENCES loom_solar.body(body_id),
    valid_from timestamptz NOT NULL,
    valid_until timestamptz NOT NULL,
    reference_frame text NOT NULL CHECK (reference_frame = 'ECLIPJ2000'),
    units text NOT NULL CHECK (units = 'km,km/s'),
    coverage_class text NOT NULL CHECK (coverage_class IN ('PRODUCT', 'BODY', 'DERIVED')),
    status text NOT NULL CHECK (status IN ('CANDIDATE', 'QUALIFIED', 'RETIRED')),
    UNIQUE NULLS NOT DISTINCT (ephemeris_source_id, body_id, valid_from),
    CHECK (valid_from < valid_until),
    CHECK ((coverage_class = 'PRODUCT' AND body_id IS NULL)
        OR (coverage_class IN ('BODY', 'DERIVED') AND body_id IS NOT NULL))
);

CREATE INDEX ephemeris_coverage_body_time_idx
    ON loom_solar.ephemeris_coverage(body_id, valid_from, valid_until);
