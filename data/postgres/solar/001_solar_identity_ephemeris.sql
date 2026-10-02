BEGIN;
CREATE SCHEMA IF NOT EXISTS loom_solar;

CREATE TABLE loom_solar.body (
    body_id text PRIMARY KEY,
    canonical_name text NOT NULL,
    body_class text NOT NULL,
    parent_body_id text NULL REFERENCES loom_solar.body(body_id),
    status text NOT NULL DEFAULT 'ACTIVE',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE loom_solar.body_identifier (
    body_id text NOT NULL REFERENCES loom_solar.body(body_id),
    authority text NOT NULL,
    identifier_type text NOT NULL,
    identifier_value text NOT NULL,
    status text NOT NULL DEFAULT 'ACTIVE',
    valid_from timestamptz NULL,
    valid_until timestamptz NULL,
    PRIMARY KEY (authority, identifier_type, identifier_value),
    UNIQUE (body_id, authority, identifier_type, identifier_value),
    CHECK (valid_until IS NULL OR valid_from IS NULL OR valid_until > valid_from)
);

CREATE TABLE loom_solar.ephemeris_source (
    source_id text PRIMARY KEY,
    provider text NOT NULL,
    product_name text NOT NULL,
    product_version text NULL,
    artifact_filename text NOT NULL,
    sha256 text NOT NULL UNIQUE CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    byte_count bigint NOT NULL CHECK (byte_count > 0),
    source_url text NOT NULL,
    acquired_at timestamptz NOT NULL,
    source_class text NOT NULL,
    status text NOT NULL DEFAULT 'ACQUIRED'
);

CREATE TABLE loom_solar.ephemeris_coverage (
    source_id text NOT NULL REFERENCES loom_solar.ephemeris_source(source_id),
    body_id text NOT NULL REFERENCES loom_solar.body(body_id),
    provider_target_id text NOT NULL,
    center_id text NULL,
    frame text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_until timestamptz NOT NULL,
    quality_class text NOT NULL,
    PRIMARY KEY (source_id, body_id, provider_target_id, frame),
    CHECK (valid_until > valid_from)
);
COMMIT;
