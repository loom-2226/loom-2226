from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

PAIRS = (
    ("HEL-03", "HEL-10"),
    ("HEL-04", "HEL-06"),
    ("HEL-07", "HEL-08"),
)

CANDIDATE_ID_COLUMNS = (
    "subject_id",
    "node_subject_id",
    "spatial_subject_id",
    "location_subject_id",
    "parent_subject_id",
    "origin_subject_id",
    "destination_subject_id",
)


def _ids(code: str) -> set[str]:
    return {f"NODE:{code}", f"ENTITY:{code}"}


def _normalize_value(value, self_ids: set[str]):
    if isinstance(value, str) and value in self_ids:
        return "<SELF>"
    return value


def _normalize_rows(rows: list[dict], self_ids: set[str]) -> list[dict]:
    normalized = [
        {key: _normalize_value(value, self_ids) for key, value in row.items()}
        for row in rows
    ]
    return sorted(normalized, key=lambda row: json.dumps(row, sort_keys=True, default=str))


def compare_pair_records(
    left_rows: list[dict],
    right_rows: list[dict],
    left_ids: set[str],
    right_ids: set[str],
) -> dict:
    if not left_rows or not right_rows:
        return {
            "classification": "MISSING_SIDE",
            "different_fields": [],
            "left_row_count": len(left_rows),
            "right_row_count": len(right_rows),
        }

    left = _normalize_rows(left_rows, left_ids)
    right = _normalize_rows(right_rows, right_ids)
    if left == right:
        return {
            "classification": "SAME_AFTER_ID_NORMALIZATION",
            "different_fields": [],
            "left_row_count": len(left_rows),
            "right_row_count": len(right_rows),
        }

    fields = sorted(set().union(*(set(row) for row in left + right)))
    different = []
    for field in fields:
        left_values = sorted(
            [row.get(field) for row in left], key=lambda value: json.dumps(value, sort_keys=True, default=str)
        )
        right_values = sorted(
            [row.get(field) for row in right], key=lambda value: json.dumps(value, sort_keys=True, default=str)
        )
        if left_values != right_values:
            different.append(field)

    return {
        "classification": "DISTINCT_STATE",
        "different_fields": different,
        "left_row_count": len(left_rows),
        "right_row_count": len(right_rows),
    }


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({_quote(table)})")]


def _load_rows_for_ids(
    conn: sqlite3.Connection,
    table: str,
    columns: list[str],
    ids: set[str],
) -> list[dict]:
    id_columns = [column for column in CANDIDATE_ID_COLUMNS if column in columns]
    if not id_columns:
        return []

    clauses = []
    params = []
    for column in id_columns:
        for value in sorted(ids):
            clauses.append(f"{_quote(column)} = ?")
            params.append(value)

    sql = f"SELECT * FROM {_quote(table)} WHERE (" + " OR ".join(clauses) + ")"
    if "year" in columns:
        sql += " AND (year = 2226 OR year IS NULL)"
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def audit_database(db_path: str | Path) -> dict:
    conn = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]

        node_rows: dict[str, dict[str, list[dict]]] = defaultdict(dict)
        table_columns: dict[str, list[str]] = {}
        eligible_tables = []
        for table in tables:
            columns = _table_columns(conn, table)
            table_columns[table] = columns
            if not any(column in columns for column in CANDIDATE_ID_COLUMNS):
                continue
            eligible_tables.append(table)
            for code in sorted({code for pair in PAIRS for code in pair}):
                rows = _load_rows_for_ids(conn, table, columns, _ids(code))
                if rows:
                    node_rows[code][table] = rows

        pair_results = []
        table_summary = defaultdict(lambda: {"same": 0, "distinct": 0, "missing": 0})
        for left_code, right_code in PAIRS:
            tables_for_pair = sorted(set(node_rows[left_code]) | set(node_rows[right_code]))
            comparisons = []
            for table in tables_for_pair:
                result = compare_pair_records(
                    node_rows[left_code].get(table, []),
                    node_rows[right_code].get(table, []),
                    _ids(left_code),
                    _ids(right_code),
                )
                classification = result["classification"]
                if classification == "SAME_AFTER_ID_NORMALIZATION":
                    table_summary[table]["same"] += 1
                elif classification == "DISTINCT_STATE":
                    table_summary[table]["distinct"] += 1
                else:
                    table_summary[table]["missing"] += 1
                comparisons.append({"table": table, **result})

            pair_results.append({
                "pair": [f"NODE:{left_code}", f"NODE:{right_code}"],
                "tables_compared": len(comparisons),
                "same_table_count": sum(c["classification"] == "SAME_AFTER_ID_NORMALIZATION" for c in comparisons),
                "distinct_table_count": sum(c["classification"] == "DISTINCT_STATE" for c in comparisons),
                "missing_side_count": sum(c["classification"] == "MISSING_SIDE" for c in comparisons),
                "comparisons": comparisons,
            })

        return {
            "schema": "LOOM_CIVSTATE_HEL_CROSS_DOMAIN_DIFFERENTIATION_V1",
            "status": "PASS",
            "scope": "QUALIFIED_DUPLICATE_HEL_PAIRS_ACROSS_CIVSTATE",
            "eligible_table_count": len(eligible_tables),
            "tables_with_target_rows": sorted({table for per_node in node_rows.values() for table in per_node}),
            "pair_results": pair_results,
            "table_summary": dict(sorted(table_summary.items())),
            "interpretation_authority": "DIAGNOSTIC_ONLY_NO_ROLE_INFERENCE_FROM_NAMES",
            "mutation_authority": "ZERO",
            "canon_change_authority": "ZERO",
            "allocation_change_authority": "ZERO",
            "next_action": "USE_ACTUAL_DISTINCT_STATE_TABLES_AS_ROLE_EVIDENCE_BEFORE_DESIGNING_ANY_DETERMINISTIC_DIFFERENTIATOR",
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only HEL cross-domain differentiation audit")
    parser.add_argument("--db", default="data/LOOM_2226_CIVSTATE.sqlite3")
    args = parser.parse_args()
    print(json.dumps(audit_database(args.db), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
