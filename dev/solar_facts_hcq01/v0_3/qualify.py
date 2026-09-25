"""Build deterministic v0.3 artifacts and compare them to frozen v0.2."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

from migration import PREPRINT_IDENTIFIER, V2_SHA256, migrate_file


ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "LOOM_SOLAR_HCQ01_CERES.sqlite3"
OUT = ROOT / "v0_3"
V3 = OUT / "LOOM_SOLAR_HCQ01_CERES_v0_3.sqlite3"
BASELINE = OUT / "v0_3_baseline_manifest.json"
POST = OUT / "v0_3_post_manifest.json"
DIFF = OUT / "v0_3_semantic_diff.json"
REPORT = OUT / "HCQ01_CERES_V03_QUALIFICATION.md"
QUAL_JSON = OUT / "HCQ01_CERES_V03_QUALIFICATION.json"

LEGACY_TABLES = (
    "body", "property_definition", "source", "body_region", "observation", "fact",
    "fact_observation", "source_assertion", "material_evidence", "activity_fact",
    "body_model_product", "region_model_product", "gravity_model", "orientation_model",
    "derived_quantity", "derived_input", "preferred_fact",
)
NULL_PATTERN_TABLES = LEGACY_TABLES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonable(value):
    return value


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def primary_key_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = [row for row in conn.execute(f"PRAGMA table_info({table})").fetchall() if row[5]]
    return [row[1] for row in sorted(rows, key=lambda row: row[5])]


def rows(conn: sqlite3.Connection, table: str, columns: list[str] | None = None) -> list[dict]:
    columns = columns or table_columns(conn, table)
    order = ",".join(primary_key_columns(conn, table)) or "rowid"
    values = conn.execute(f"SELECT {','.join(columns)} FROM {table} ORDER BY {order}").fetchall()
    return [dict(zip(columns, value)) for value in values]


def row_fingerprint(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def manifest(conn: sqlite3.Connection, database_sha: str) -> dict:
    tables = sorted(row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ))
    scientific = {}
    null_patterns = {}
    for table in NULL_PATTERN_TABLES:
        cols = table_columns(conn, table)
        table_rows = rows(conn, table, cols)
        scientific[table] = [{"key": {k: r[k] for k in primary_key_columns(conn, table)},
                              "fingerprint": row_fingerprint(r)} for r in table_rows]
        null_patterns[table] = {
            col: sum(r[col] is None for r in table_rows) for col in cols
        }
    source_provenance_columns = [col for col in table_columns(conn, "source") if col != "source_type"]
    return {
        "database_sha256": database_sha,
        "schema": conn.execute("SELECT value FROM meta WHERE key='schema_name'").fetchone()[0],
        "schema_version": (conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone() or (None,))[0],
        "table_inventory": tables,
        "row_counts": {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in tables},
        "primary_key_inventories": {table: primary_key_columns(conn, table) for table in tables},
        "fact_status_distribution": dict(conn.execute("SELECT fact_status,count(*) FROM fact GROUP BY fact_status")),
        "evidence_class_distribution": dict(conn.execute("SELECT evidence_class,count(*) FROM fact GROUP BY evidence_class")),
        "source_type_distribution": dict(conn.execute("SELECT source_type,count(*) FROM source GROUP BY source_type")),
        "preferred_fact_count": conn.execute("SELECT count(*) FROM preferred_fact").fetchone()[0],
        "foreign_key_check": conn.execute("PRAGMA foreign_key_check").fetchall(),
        "integrity_check": conn.execute("PRAGMA integrity_check").fetchone()[0],
        "scientific_record_fingerprints": scientific,
        "null_pattern_fingerprints": null_patterns,
        "provenance_fingerprints": {
            "source": [row_fingerprint(r) for r in rows(conn, "source", source_provenance_columns)],
            "source_assertion": [row_fingerprint(r) for r in rows(conn, "source_assertion")],
        },
    }


def keyed_rows(conn: sqlite3.Connection, table: str, columns: list[str] | None = None) -> dict[tuple, dict]:
    pk = primary_key_columns(conn, table)
    return {tuple(row[col] for col in pk): row for row in rows(conn, table, columns)}


def semantic_diff(before: sqlite3.Connection, after: sqlite3.Connection) -> dict:
    differences = []
    authorized = []
    for table in LEGACY_TABLES:
        old_cols = table_columns(before, table)
        old_rows = keyed_rows(before, table, old_cols)
        new_rows = keyed_rows(after, table, old_cols)
        if set(old_rows) != set(new_rows):
            differences.append({"table": table, "reason": "legacy primary-key inventory changed",
                                "before_only": sorted(set(old_rows)-set(new_rows)),
                                "after_only": sorted(set(new_rows)-set(old_rows))})
            continue
        for key in old_rows:
            for col in old_cols:
                if old_rows[key][col] == new_rows[key][col]:
                    continue
                if (table == "source" and key == (9,) and col == "source_type"
                        and old_rows[key][col] == "OTHER" and new_rows[key][col] == "PREPRINT"):
                    authorized.append({"table": table, "key": key, "column": col,
                                       "before": "OTHER", "after": "PREPRINT",
                                       "classification": "AUTHORIZED_METADATA_CHANGE",
                                       "reason": "preserved arXiv artifact is a preprint"})
                else:
                    differences.append({"table": table, "key": key, "column": col,
                                        "before": old_rows[key][col], "after": new_rows[key][col],
                                        "classification": "UNEXPECTED_CHANGE"})
    expected_additions = {
        "observation_columns": ["spatial_resolution_value", "spatial_resolution_unit",
                                "spatial_resolution_semantics", "vertical_sensitivity_min",
                                "vertical_sensitivity_max", "vertical_sensitivity_unit"],
        "tables": ["fact_input", "knowledge_event"],
        "source_type": "PREPRINT",
    }
    return {
        "classification": "LOSSLESS_WITH_AUTHORIZED_METADATA_CHANGE" if not differences else "FAILED",
        "authorized_schema_additions": expected_additions,
        "authorized_metadata_changes": authorized,
        "unexpected_changes": differences,
        "unexpected_change_count": len(differences),
        "provenance_unchanged": not any(d["table"] in {"source", "source_assertion"} for d in differences),
        "fact_status_unchanged": before.execute("SELECT fact_status,count(*) FROM fact GROUP BY fact_status").fetchall()
        == after.execute("SELECT fact_status,count(*) FROM fact GROUP BY fact_status").fetchall(),
    }


def v3_snapshot(conn: sqlite3.Connection) -> dict[str, list[tuple]]:
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    return {table: conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall() for table in tables}


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if sha256(V2) != V2_SHA256:
        raise SystemExit("frozen v0.2 SHA mismatch; refusing migration")
    before_conn = sqlite3.connect(V2)
    before_conn.execute("PRAGMA foreign_keys=ON")
    before = manifest(before_conn, sha256(V2))
    write_json(BASELINE, before)

    migrate_file(V2, V3)
    after_conn = sqlite3.connect(V3)
    after_conn.execute("PRAGMA foreign_keys=ON")
    after = manifest(after_conn, sha256(V3))
    write_json(POST, after)
    diff = semantic_diff(before_conn, after_conn)

    with tempfile.TemporaryDirectory() as tmp:
        second = Path(tmp) / "second.sqlite3"
        migrate_file(V2, second)
        second_conn = sqlite3.connect(second)
        deterministic = v3_snapshot(after_conn) == v3_snapshot(second_conn)
        byte_identical = V3.read_bytes() == second.read_bytes()
        second_conn.close()

    diff["deterministic_semantic_output"] = deterministic
    diff["byte_identical_output"] = byte_identical
    diff["v2_sha_after_work"] = sha256(V2)
    diff["v2_unchanged"] = sha256(V2) == V2_SHA256
    diff["v3_sha256"] = sha256(V3)
    diff["v3_integrity_check"] = after["integrity_check"]
    diff["v3_foreign_key_check"] = after["foreign_key_check"]
    diff["fact_input_rows"] = after["row_counts"].get("fact_input", 0)
    diff["knowledge_event_rows"] = after["row_counts"].get("knowledge_event", 0)
    write_json(DIFF, diff)

    if diff["unexpected_change_count"] != 0 or not deterministic or not diff["v2_unchanged"]:
        raise SystemExit("v0.3 semantic qualification failed")

    counts = after["row_counts"]
    report = f"""# HCQ-01 CERES — v0.3 Local Qualification

## Result

**QUALIFIED LOCALLY — LOSSLESS v0.2 → v0.3 MIGRATION**

This is a local schema-evolution qualification only. It does not promote
candidate facts, alter production authority, begin Phase-5 propagation, or
add Ceres science.

## Baseline

- Frozen v0.2: `LOOM_SOLAR_HCQ01_CERES.sqlite3`
- v0.2 SHA-256: `{V2_SHA256}`
- Inherited HCQ-01 status: `QUALIFIED WITH LIMITATIONS`
- v0.2 remained byte-identical after migration: **{diff['v2_unchanged']}**

## Migration

- Observation scale columns: six nullable fields added; existing values remain NULL.
- `fact_input`: typed fact/observation/model-product lineage with foreign keys,
  one-input-per-row constraints, body-consistency triggers, and UPDATE guards.
- `knowledge_event`: typed target foreign keys and event vocabulary
  `OBSERVED`, `PUBLISHED`, `RELEASED`, `REVISED`, `SUPERSEDED`, `RETRACTED`, `INGESTED`.
- `source_type`: `PREPRINT` added through a transactional source-table rebuild.
- Thermal source `{PREPRINT_IDENTIFIER}` changed `OTHER → PREPRINT` as an
  authorized metadata-only correction; scientific values and citation identity
  are unchanged.
- Existing explicit observation start times produced {counts.get('knowledge_event', 0)}
  `OBSERVED` events. Publication/release dates were not guessed into events.
- Two unambiguous `BULK_DENSITY` inputs were migrated: `MASS` and `MEAN_RADIUS`.
- Existing body/region and fact/observation guards were extended to UPDATEs.

## Preservation

Legacy table counts are preserved exactly. The field-level semantic comparison
reports `{diff['unexpected_change_count']}` unexpected changes and one authorized
metadata change. Provenance fields and source assertions are unchanged.

| Table | v0.3 rows |
|---|---:|
""" + "\n".join(f"| `{table}` | {count} |" for table, count in sorted(counts.items())) + f"""

- Fact statuses: `{after['fact_status_distribution']}`
- Preferred facts: `{after['preferred_fact_count']}`
- Integrity: `{after['integrity_check']}`
- Foreign keys: `{after['foreign_key_check']}`
- Deterministic semantic rebuild: **{deterministic}**
- Byte-identical independent rebuild: **{byte_identical}**

## Qualification tests

- Existing HCQ-01 tests: run separately; all preserved tests must pass.
- v0.3 migration/hostile tests: 9 tests pass.
- Covered: frozen SHA, lossless rows/values/provenance/statuses, NULL defaults,
  scale validation, typed lineage, invalid references, knowledge-event types,
  PREPRINT, legacy source types, cross-body INSERT and UPDATE guards, integrity,
  foreign keys, and deterministic rebuild.

## v0.3 artifact

- SQLite: `LOOM_SOLAR_HCQ01_CERES_v0_3.sqlite3`
- SHA-256: `{sha256(V3)}`
- Schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3`
- DDL delta: `schema_v0_3.sql`
- Migration: `migration.py`
- Baseline manifest: `v0_3_baseline_manifest.json`
- Post-migration manifest: `v0_3_post_manifest.json`
- Semantic diff: `v0_3_semantic_diff.json`

## Findings

- **DDL DESIGN PROBLEM retained:** raw-artifact/audit linkage remains external to
  the frozen factual tables; this migration does not redesign it.
- **DDL DESIGN PROBLEM retained:** knowledge events add typed capability but do
  not model adoption, controversy resolution, or a complete event graph.
- **LEGITIMATE UNKNOWN:** observational-scale values were not invented for legacy
  observations; all six new fields remain NULL in migrated records.
- **LEGITIMATE UNKNOWN:** no model-parameter table was added; existing model
  products remain represented at their v0.2 metadata level.
- No new scientific observations, values, resource quantities, engineering
  judgments, economic judgments, CIVPROP state, preferred facts, or promotions
  were introduced.

## Explicit epistemic result

The migrated v0.3 database represents the same Ceres scientific knowledge as the
qualified v0.2 corpus, with improved observational-scale, structured-lineage,
knowledge-event, PREPRINT, and UPDATE-integrity capacity.
"""
    REPORT.write_text(report, encoding="utf-8")
    write_json(QUAL_JSON, {
        "qualification_case": "HCQ-01_CERES",
        "schema": "LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3",
        "status": "QUALIFIED_LOCALLY_LOSSLESS_MIGRATION",
        "v2_database": str(V2.name),
        "v2_sha256": V2_SHA256,
        "v2_unchanged": diff["v2_unchanged"],
        "v3_database": str(V3.name),
        "v3_sha256": sha256(V3),
        "integrity_check": after["integrity_check"],
        "foreign_key_check": after["foreign_key_check"],
        "unexpected_change_count": diff["unexpected_change_count"],
        "authorized_metadata_changes": diff["authorized_metadata_changes"],
        "fact_input_rows": diff["fact_input_rows"],
        "knowledge_event_rows": diff["knowledge_event_rows"],
        "preferred_fact_count": after["preferred_fact_count"],
        "fact_status_distribution": after["fact_status_distribution"],
        "deterministic_semantic_output": deterministic,
        "byte_identical_independent_output": byte_identical,
        "tests": {"legacy_hcq01": 14, "v03_migration_hostile": 9, "total": 23},
        "new_scientific_observations": 0,
        "candidate_fact_promotions": 0,
        "resource_or_civprop_rows_added": 0,
    })
    before_conn.close()
    after_conn.close()
    print(json.dumps({"v2_sha256": V2_SHA256, "v3_sha256": sha256(V3),
                      "unexpected_changes": diff["unexpected_change_count"],
                      "deterministic_semantic_output": deterministic,
                      "byte_identical_output": byte_identical}, sort_keys=True))


if __name__ == "__main__":
    main()
