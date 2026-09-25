-- Typed operational projection of LOOM chronology and technology scenario anchors.
-- Storage preserves source authority; PostgreSQL does not promote provisional material to canon.
CREATE SCHEMA IF NOT EXISTS loom_timeline;

CREATE TABLE loom_timeline.milestone (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    milestone_id text NOT NULL,
    id_origin text NOT NULL CHECK (id_origin IN ('SOURCE','PROJECTION_GENERATED')),
    family text,
    timeline_kind text NOT NULL CHECK (timeline_kind IN (
        'CANON_HISTORY','MODERATE_SCENARIO_ANCHOR',
        'FICTIONAL_PHYSICS_SCENARIO_ANCHOR','SOCIAL_SCENARIO_ANCHOR')),
    authority_class text NOT NULL CHECK (authority_class IN (
        'GOVERNING_CANON','PROVISIONAL_SIMULATION_SCAFFOLD')),
    epistemic_status text NOT NULL,
    reference_period text NOT NULL,
    start_year integer,
    end_year integer,
    temporal_precision text NOT NULL,
    capability_change_md text NOT NULL,
    threshold_gate_md text,
    basis_uncertainty_md text,
    source_section text NOT NULL,
    sort_order integer NOT NULL CHECK (sort_order > 0),
    notes_md text,
    PRIMARY KEY (snapshot_id, milestone_id),
    CHECK (start_year IS NULL OR start_year BETWEEN 1900 AND 3000),
    CHECK (end_year IS NULL OR end_year BETWEEN 1900 AND 3000),
    CHECK (start_year IS NULL OR end_year IS NULL OR start_year <= end_year)
);

CREATE TABLE loom_timeline.milestone_alias (
    snapshot_id text NOT NULL,
    milestone_id text NOT NULL,
    alias_id text NOT NULL,
    PRIMARY KEY (snapshot_id, alias_id),
    FOREIGN KEY (snapshot_id, milestone_id)
        REFERENCES loom_timeline.milestone(snapshot_id, milestone_id)
);

CREATE TABLE loom_timeline.milestone_source (
    snapshot_id text NOT NULL,
    milestone_id text NOT NULL,
    source_artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    source_role text NOT NULL CHECK (source_role IN (
        'GOVERNING_CONTENT','STABLE_ID_MAPPING','SCENARIO_DEFINITION')),
    source_git_commit char(40) NOT NULL,
    PRIMARY KEY (snapshot_id, milestone_id, source_artifact_sha256, source_role),
    FOREIGN KEY (snapshot_id, milestone_id)
        REFERENCES loom_timeline.milestone(snapshot_id, milestone_id)
);

CREATE TABLE loom_timeline.interpretation_rule (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    rule_key text NOT NULL,
    rule_text_md text NOT NULL,
    source_artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    source_section text NOT NULL,
    PRIMARY KEY (snapshot_id, rule_key)
);

CREATE INDEX timeline_milestone_year_idx
    ON loom_timeline.milestone(snapshot_id, start_year, end_year);
CREATE INDEX timeline_milestone_kind_idx
    ON loom_timeline.milestone(snapshot_id, timeline_kind, authority_class);

COMMENT ON SCHEMA loom_timeline IS
    'Typed operational projection of governing LOOM history and provisional simulation timeline scaffolds; authority remains source-derived.';
COMMENT ON TABLE loom_timeline.milestone IS
    'Timeline milestones with explicit authority and epistemic class. Persistence never upgrades provisional scenario material to canon.';
COMMENT ON TABLE loom_timeline.interpretation_rule IS
    'Source-backed rules constraining timeline interpretation by executable consumers such as future CIVPROP.';
