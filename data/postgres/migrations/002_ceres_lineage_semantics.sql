-- Development provenance extension. Source keys only; no generic value payload.
ALTER TABLE loom_control.field_semantics
    ADD COLUMN embedded_claim_status text NOT NULL DEFAULT 'NOT_APPLICABLE',
    ADD COLUMN admission_scope text NOT NULL DEFAULT 'NONE';

CREATE TABLE loom_control.row_lineage (
    snapshot_id text NOT NULL REFERENCES loom_control.snapshot,
    target_schema text NOT NULL,
    target_table text NOT NULL,
    source_database text NOT NULL,
    source_table text NOT NULL,
    source_artifact_sha256 char(64) NOT NULL REFERENCES loom_control.source_artifact,
    source_key jsonb NOT NULL CHECK (jsonb_typeof(source_key) = 'object'),
    PRIMARY KEY(snapshot_id,target_schema,target_table,source_key)
);

COMMENT ON TABLE loom_control.row_lineage IS
    'Exact source PK components for typed imported rows; no unresolved descriptive values.';
