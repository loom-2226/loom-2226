from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DUPLICATE_PAIRS = (
    ("NODE:HEL-03", "NODE:HEL-10"),
    ("NODE:HEL-04", "NODE:HEL-06"),
    ("NODE:HEL-07", "NODE:HEL-08"),
)

PREFERRED_INFRA_FIELDS = (
    "resident_population", "transient_daily_population", "workforce_assigned",
    "cargo_throughput_tonnes_year", "passenger_movements_year", "ship_calls_year",
    "utilization", "strategic_importance", "economic_centrality", "transport_centrality",
)


def _same(a, b) -> bool:
    if a is None or b is None:
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= 1e-12
    return a == b


def summarize_upstream_rows(rows: list[dict], pairs=DUPLICATE_PAIRS) -> dict:
    by_id = {row["node_subject_id"]: row for row in rows}
    compared_fields = sorted(set().union(*(set(row) for row in rows)) - {"node_subject_id"}) if rows else []
    pair_results = []
    for left, right in pairs:
        if left not in by_id or right not in by_id:
            pair_results.append({"pair": [left, right], "status": "MISSING_NODE"})
            continue
        identical = [f for f in compared_fields if _same(by_id[left].get(f), by_id[right].get(f))]
        different = [f for f in compared_fields if f not in identical]
        pair_results.append({"pair": [left, right], "status": "COMPARED", "identical_upstream_fields": identical, "different_upstream_fields": different})
    return {
        "schema": "LOOM_CIVSTATE_HEL_TEXTURE_UPSTREAM_PROVENANCE_V1",
        "status": "PASS", "scope": "DUPLICATE_HEL_TEXTURE_PAIRS",
        "compared_fields": compared_fields, "pair_results": pair_results,
        "interpretation_authority": "DIAGNOSTIC_ONLY_NO_DEFECT_DECLARATION",
        "mutation_authority": "ZERO", "canon_change_authority": "ZERO",
        "equation_invention_authority": "ZERO",
        "next_action": "TRACE_IDENTICAL_SOURCE_FAMILIES_OR_NORMALIZATION_COLLAPSE_ONLY_WHERE_RUNTIME_EVIDENCE_SUPPORTS_IT",
    }


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def _node_key(columns: list[str]) -> str:
    for candidate in ("node_subject_id", "subject_id", "node_id"):
        if candidate in columns:
            return candidate
    raise RuntimeError("No supported node key found")


def load_upstream_rows(db_path: str | Path) -> tuple[list[dict], dict]:
    conn = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        infra_cols = _columns(conn, "civ_infrastructure_state")
        influence_cols = _columns(conn, "civ_influence_edge")
        infra_key, influence_key = _node_key(infra_cols), _node_key(influence_cols)
        infra_fields = [f for f in PREFERRED_INFRA_FIELDS if f in infra_cols]
        node_ids = sorted({node for pair in DUPLICATE_PAIRS for node in pair})
        rows = []
        for node_id in node_ids:
            selected = [infra_key] + infra_fields
            where = f"{infra_key}=?" + (" AND year=2226" if "year" in infra_cols else "")
            infra = conn.execute(f"SELECT {', '.join(selected)} FROM civ_infrastructure_state WHERE {where}", (node_id,)).fetchone()
            row = {"node_subject_id": node_id, **{f: (infra[f] if infra is not None else None) for f in infra_fields}}
            if {"actor_subject_id", "influence_domain", "influence_weight"}.issubset(influence_cols):
                agg = conn.execute(
                    f"SELECT COUNT(DISTINCT actor_subject_id) actor_count, COUNT(DISTINCT influence_domain) domain_count, SUM(influence_weight) weight_sum, MAX(influence_weight) weight_max FROM civ_influence_edge WHERE {influence_key}=?",
                    (node_id,),
                ).fetchone()
                row.update({"influence_actor_count": agg["actor_count"], "influence_domain_count": agg["domain_count"], "influence_weight_sum": agg["weight_sum"], "influence_weight_max": agg["weight_max"]})
            rows.append(row)
        return rows, {"infrastructure_node_key": infra_key, "influence_node_key": influence_key, "infrastructure_fields_found": infra_fields, "infrastructure_columns": infra_cols, "influence_columns": influence_cols}
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only HEL texture upstream provenance audit")
    parser.add_argument("--db", default="data/LOOM_2226_CIVSTATE.sqlite3")
    args = parser.parse_args()
    rows, metadata = load_upstream_rows(args.db)
    report = summarize_upstream_rows(rows)
    report["source_schema"], report["upstream_rows"] = metadata, rows
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
