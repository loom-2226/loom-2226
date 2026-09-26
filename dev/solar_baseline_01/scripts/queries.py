"""Body-neutral read-only baseline queries."""
import sqlite3

def facts_by_body(connection,body_id):
    connection.row_factory=sqlite3.Row
    return list(connection.execute("SELECT * FROM candidate_assertion WHERE body_id=? ORDER BY property_code,source_lineage,assertion_id",(body_id,)))
def provenance_by_assertion(connection,assertion_id):
    connection.row_factory=sqlite3.Row
    return connection.execute("SELECT a.*,s.artifact_id AS source_artifact_artifact_id,s.authority,s.product,s.source_url,s.version,s.acquired_at_utc,s.sha256,s.byte_count FROM candidate_assertion a JOIN source_artifact s ON s.artifact_id=a.source_artifact_id WHERE assertion_id=?",(assertion_id,)).fetchone()
def same_property_by_body(connection,property_code):
    connection.row_factory=sqlite3.Row
    return list(connection.execute("SELECT body_id,property_code,reported_value,reported_unit,epistemic_class,source_value_kind,source_artifact_id,source_lineage FROM candidate_assertion WHERE property_code=? ORDER BY body_id,source_lineage",(property_code,)))
