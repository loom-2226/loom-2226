#!/usr/bin/env python3
"""Deterministic Earth authority preservation contract.

The contract is deliberately database-driven: it fingerprints the live catalog,
complete Earth/control content, and every narrator view before and after Ceres
retirement.  It is usable against a live database or a pg_restore disposable
copy and exits non-zero on any mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

SNAPSHOT = "earth-v0-1-9934d0ac-20260925"
CONTROL_TABLES = (
    "snapshot", "snapshot_source", "source_artifact", "semantic_version",
    "import_batch", "variable_semantics", "model_context_record",
    "temporal_coverage",
)
EARTH_TABLES = (
    "earth_area", "earth_biological_cohort_year", "earth_demographic_year",
    "earth_derivation", "earth_economic_year", "earth_labor_composition_year",
    "earth_legacy_labor_year", "earth_sector_asset_year", "earth_sector_year",
)


def psql(db: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", db, "-c", sql],
        check=False, capture_output=True, text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def rows(db: str, sql: str) -> list[dict]:
    value = psql(db, "SELECT COALESCE(jsonb_agg(x), '[]'::jsonb) FROM (" + sql + ") x")
    return json.loads(value)


def ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def table_columns(db: str, schema: str, table: str) -> list[str]:
    return [r["column_name"] for r in rows(db, f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema={schema!r} AND table_name={table!r}
        ORDER BY ordinal_position""")]


def table_fingerprint(db: str, schema: str, table: str) -> dict:
    columns = table_columns(db, schema, table)
    order = ", ".join(ident(c) for c in columns)
    select_cols = ", ".join(ident(c) for c in columns)
    sql = f"COPY (SELECT row_to_json(x)::text FROM (SELECT {select_cols} FROM {ident(schema)}.{ident(table)} ORDER BY {order}) x) TO STDOUT"
    proc = subprocess.Popen(
        ["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", db, "-c", sql],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    digest = hashlib.sha256()
    count = 0
    assert proc.stdout is not None
    for line in proc.stdout:
        digest.update(line)
        count += 1
    stderr = proc.stderr.read().decode()
    code = proc.wait()
    if code:
        raise RuntimeError(stderr.strip())
    return {"schema": schema, "table": table, "columns": columns,
            "row_count": count, "content_sha256": digest.hexdigest()}


def schema_fingerprint(db: str, schema: str, tables: list[str]) -> dict:
    table_set = ", ".join("%s" % repr(t) for t in tables)
    column_rows = rows(db, f"""
      SELECT table_schema, table_name, ordinal_position, column_name, data_type,
             udt_schema, udt_name, is_nullable, column_default
      FROM information_schema.columns
      WHERE table_schema={schema!r} AND table_name IN ({table_set})
      ORDER BY table_name, ordinal_position""")
    constraints = rows(db, f"""
      SELECT n.nspname AS schema_name, c.relname AS table_name,
             con.conname, con.contype, pg_get_constraintdef(con.oid, true) AS definition
      FROM pg_constraint con JOIN pg_class c ON c.oid=con.conrelid
      JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname={schema!r} AND c.relname IN ({table_set})
      ORDER BY c.relname, con.conname""")
    indexes = rows(db, f"""
      SELECT schemaname, tablename, indexname, indexdef FROM pg_indexes
      WHERE schemaname={schema!r} AND tablename IN ({table_set})
      ORDER BY tablename, indexname""")
    comments = rows(db, f"""
      SELECT n.nspname AS schema_name, c.relname AS object_name,
             d.description FROM pg_description d JOIN pg_class c ON c.oid=d.objoid
      JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname={schema!r} AND c.relname IN ({table_set})
      ORDER BY c.relname, d.objsubid""")
    payload = {"schema": schema, "tables": tables, "columns": column_rows,
               "constraints": constraints, "indexes": indexes, "comments": comments}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {"content_sha256": hashlib.sha256(encoded).hexdigest(), "catalog": payload}


def view_fingerprint(db: str) -> dict:
    views = rows(db, """
      SELECT c.oid, n.nspname AS schema_name, c.relname AS view_name,
             pg_get_viewdef(c.oid, true) AS definition
      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='loom_narrator' AND c.relkind IN ('v','m')
      ORDER BY c.relname""")
    result = []
    for view in views:
        deps = rows(db, f"""
          SELECT n.nspname AS schema_name, c.relname AS object_name, c.relkind
          FROM pg_depend d JOIN pg_class c ON c.oid=d.refobjid
          JOIN pg_namespace n ON n.oid=c.relnamespace
          WHERE d.objid={view['oid']} AND d.classid='pg_rewrite'::regclass
          ORDER BY n.nspname, c.relname""")
        columns = table_columns(db, "loom_narrator", view["view_name"])
        order = ", ".join(ident(c) for c in columns)
        sql = f"COPY (SELECT row_to_json(x)::text FROM (SELECT * FROM loom_narrator.{ident(view['view_name'])} ORDER BY {order}) x) TO STDOUT"
        proc = subprocess.Popen(["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-d", db, "-c", sql], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        digest, count = hashlib.sha256(), 0
        assert proc.stdout is not None
        for line in proc.stdout:
            digest.update(line); count += 1
        stderr = proc.stderr.read().decode(); code = proc.wait()
        if code: raise RuntimeError(stderr.strip())
        result.append({"view": view["view_name"], "definition": view["definition"],
                       "columns": columns, "dependencies": deps,
                       "row_count": count, "result_sha256": digest.hexdigest()})
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {"views": result, "content_sha256": hashlib.sha256(encoded).hexdigest()}


def build(db: str) -> dict:
    snapshot = rows(db, f"SELECT * FROM loom_control.snapshot WHERE snapshot_id={SNAPSHOT!r}")[0]
    associated = {"snapshot_source": rows(db, f"SELECT * FROM loom_control.snapshot_source WHERE snapshot_id={SNAPSHOT!r} ORDER BY artifact_sha256, source_role"),
                  "source_artifact": rows(db, f"""SELECT a.* FROM loom_control.source_artifact a
                    JOIN loom_control.snapshot_source s USING (artifact_sha256)
                    WHERE s.snapshot_id={SNAPSHOT!r} ORDER BY a.artifact_sha256"""),
                  "semantic_version": rows(db, "SELECT * FROM loom_control.semantic_version ORDER BY semantic_sha256"),
                  "import_batch": rows(db, f"SELECT * FROM loom_control.import_batch WHERE snapshot_id={SNAPSHOT!r} ORDER BY batch_id"),
                  "variable_semantics": rows(db, f"SELECT * FROM loom_control.variable_semantics WHERE snapshot_id={SNAPSHOT!r} ORDER BY variable_key"),
                  "model_context_record": rows(db, f"SELECT * FROM loom_control.model_context_record WHERE snapshot_id={SNAPSHOT!r} ORDER BY context_key"),
                  "temporal_coverage": rows(db, f"SELECT * FROM loom_control.temporal_coverage WHERE snapshot_id={SNAPSHOT!r} ORDER BY fact_family, variable_key"),
                  "earth_derivation": rows(db, f"SELECT * FROM loom_earth.earth_derivation WHERE snapshot_id={SNAPSHOT!r} ORDER BY derivation_id")}
    earth_data = [table_fingerprint(db, "loom_earth", t) for t in EARTH_TABLES]
    earth_schema = schema_fingerprint(db, "loom_earth", list(EARTH_TABLES))
    metadata_encoded = json.dumps(associated, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    metadata = {"content_sha256": hashlib.sha256(metadata_encoded).hexdigest(), "rows": associated}
    payload = {"snapshot": snapshot, "earth_schema": earth_schema, "earth_data": earth_data,
               "earth_metadata": metadata, "narrator": view_fingerprint(db)}
    payload["overall_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return {"contract_version": "1", "database": db, "snapshot_id": SNAPSHOT, **payload}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="loom_dev")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    artifact = build(args.database)
    if args.compare:
        prior = json.loads(args.compare.read_text())
        if prior["snapshot_id"] != artifact["snapshot_id"]:
            raise SystemExit("snapshot identity mismatch")
        if prior["overall_sha256"] != artifact["overall_sha256"]:
            raise SystemExit(json.dumps({"status": "FAIL", "pre": prior["overall_sha256"], "post": artifact["overall_sha256"]}))
        artifact["comparison"] = "EXACT_PASS"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "PASS", "overall_sha256": artifact["overall_sha256"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
