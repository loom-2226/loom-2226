from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

HEL_NODE_LIKE = ("NODE:HEL-%", "ENTITY:HEL-%")
IDENTITY_NAMES = {
    "subject_id",
    "node_subject_id",
    "spatial_subject_id",
    "navigator_entity_id",
    "navigator_node_id",
    "navigator_noun_id",
    "display_name",
    "name",
    "label",
}


def _stable(v):
    if isinstance(v, float):
        return round(v, 12)
    return v


def summarize_field_variation(table: str, rows: list[dict], identity_fields: set[str]) -> dict:
    all_fields = sorted(set().union(*(set(r) for r in rows)) if rows else set())
    excluded = sorted(f for f in all_fields if f in identity_fields)
    comparable = [f for f in all_fields if f not in identity_fields]
    varying, constant = [], []
    cardinality = {}
    for field in comparable:
        vals = {_stable(r.get(field)) for r in rows}
        cardinality[field] = len(vals)
        (varying if len(vals) > 1 else constant).append(field)
    return {
        "table": table,
        "row_count": len(rows),
        "identity_fields_excluded": excluded,
        "varying_fields": varying,
        "constant_fields": constant,
        "field_cardinality": cardinality,
        "mutation_authority": "ZERO",
        "allocator_design_authority": "ZERO",
    }


def _tables(conn: sqlite3.Connection) -> list[str]:
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'civ_%' ORDER BY name"
    )]


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def _candidate_keys(cols: list[str]) -> list[str]:
    return [c for c in ("node_subject_id", "subject_id", "spatial_subject_id") if c in cols]


def _load_rows_for_table(conn: sqlite3.Connection, table: str) -> tuple[list[dict], list[str]]:
    cols = _columns(conn, table)
    keys = _candidate_keys(cols)
    if not keys:
        return [], []
    where = []
    params = []
    for key in keys:
        where.append(f"({key} LIKE ? OR {key} LIKE ?)")
        params.extend(HEL_NODE_LIKE)
    year_clause = ""
    if "year" in cols:
        year_clause = " AND (year=2226 OR year IS NULL)"
    sql = f"SELECT * FROM {table} WHERE ({' OR '.join(where)}){year_clause}"
    return [dict(r) for r in conn.execute(sql, params)], keys


def _load_derivation_metadata(conn: sqlite3.Connection, derivation_ids: set[str]) -> dict:
    out = {}
    if not derivation_ids:
        return out
    tables = set(_tables(conn))
    if "civ_derivation" not in tables:
        return out
    cols = _columns(conn, "civ_derivation")
    if "derivation_id" not in cols:
        return out
    for did in sorted(derivation_ids):
        row = conn.execute("SELECT * FROM civ_derivation WHERE derivation_id=?", (did,)).fetchone()
        if row is not None:
            out[did] = dict(row)
    return out


def _load_assumptions(conn: sqlite3.Connection) -> list[dict]:
    for table in ("civ_assumption", "civ_assumptions"):
        if table in set(_tables(conn)):
            return [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY 1")]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only HEL differentiator input inventory")
    parser.add_argument("--db", default="data/LOOM_2226_CIVSTATE.sqlite3")
    args = parser.parse_args()

    conn = sqlite3.connect(f"file:{Path(args.db)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        table_results = []
        derivation_ids: set[str] = set()
        for table in _tables(conn):
            rows, keys = _load_rows_for_table(conn, table)
            if not rows:
                continue
            identity = set(keys) | IDENTITY_NAMES
            summary = summarize_field_variation(table, rows, identity)
            if "derivation_id" in _columns(conn, table):
                derivation_ids.update(r.get("derivation_id") for r in rows if r.get("derivation_id"))
            summary["subject_keys"] = keys
            table_results.append(summary)

        varying_tables = [r for r in table_results if r["varying_fields"]]
        constant_tables = [r for r in table_results if not r["varying_fields"]]
        report = {
            "schema": "LOOM_CIVSTATE_HEL_DIFFERENTIATOR_INPUT_INVENTORY_V1",
            "status": "PASS",
            "scope": "ALL_STORED_HEL_ROWS_2226_OR_NULL",
            "table_count": len(table_results),
            "varying_table_count": len(varying_tables),
            "constant_table_count": len(constant_tables),
            "tables": table_results,
            "derivation_metadata": _load_derivation_metadata(conn, derivation_ids),
            "assumptions": _load_assumptions(conn),
            "candidate_input_rule": "VARIATION_IS_EVIDENCE_ONLY_NOT_AUTOMATIC_ALLOCATOR_AUTHORITY",
            "conservation_rule": "PRESERVE_DOCUMENTED_PARENT_TOTALS_AND_RESIDUALS_BEFORE_ANY_REALLOCATION",
            "name_inference_authority": "ZERO",
            "coefficient_invention_authority": "ZERO",
            "mutation_authority": "ZERO",
            "allocator_design_authority": "ZERO",
            "next_action": "REVIEW_VARYING_FIELDS_BY_DERIVATION_AND_CONSERVATION_ROLE_BEFORE_PROPOSING_ALLOCATOR_V2",
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
