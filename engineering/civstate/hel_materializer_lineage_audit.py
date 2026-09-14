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

SUBJECT_FIELDS = (
    "subject_class",
    "display_name",
    "parent_subject_id",
    "spatial_subject_id",
    "aggregation_class",
    "active_2226",
)

INFLUENCE_SIGNATURE_FIELDS = (
    "actor_subject_id",
    "influence_domain",
    "influence_weight",
    "control_class",
    "basis",
    "derivation_id",
)


def summarize_lineage(nodes: dict[str, dict], pairs=DUPLICATE_PAIRS) -> dict:
    pair_results = []
    for left, right in pairs:
        if left not in nodes or right not in nodes:
            pair_results.append({"pair": [left, right], "status": "MISSING_NODE"})
            continue
        a = nodes[left]
        b = nodes[right]
        same_subject = a.get("subject") == b.get("subject")
        same_infra_derivation = a.get("infrastructure_derivation_id") == b.get("infrastructure_derivation_id")
        same_influence = a.get("influence_signature") == b.get("influence_signature")

        if same_subject and same_infra_derivation and same_influence:
            classification = "EXACT_INSPECTED_LINEAGE_CLONE"
        elif same_infra_derivation:
            classification = "SHARED_DERIVATION_DISTINCT_INSPECTED_LINEAGE"
        else:
            classification = "DISTINCT_INSPECTED_LINEAGE"

        pair_results.append({
            "pair": [left, right],
            "status": "COMPARED",
            "same_subject_metadata": same_subject,
            "same_infrastructure_derivation": same_infra_derivation,
            "same_influence_signature": same_influence,
            "classification": classification,
        })

    return {
        "schema": "LOOM_CIVSTATE_HEL_MATERIALIZER_LINEAGE_AUDIT_V1",
        "status": "PASS",
        "scope": "QUALIFIED_DUPLICATE_HEL_TEXTURE_PAIRS",
        "pair_results": pair_results,
        "interpretation_authority": "DIAGNOSTIC_ONLY_NO_INTENT_INFERENCE",
        "mutation_authority": "ZERO",
        "canon_change_authority": "ZERO",
        "generator_reconstruction_authority": "ZERO",
        "next_action": "IF_EXACT_LINEAGE_CLONES_EXIST_RECOVER_CLASS_OR_ALLOCATION_RATIONALE_BEFORE_PROPOSING_DIVERSIFICATION",
    }


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone() is not None


def _fetch_subject(conn: sqlite3.Connection, node_id: str) -> dict:
    if not _table_exists(conn, "civ_subject"):
        return {}
    cols = _columns(conn, "civ_subject")
    fields = [field for field in SUBJECT_FIELDS if field in cols]
    if "subject_id" not in cols:
        return {}
    selected = ["subject_id"] + fields
    row = conn.execute(
        f"SELECT {', '.join(selected)} FROM civ_subject WHERE subject_id=?",
        (node_id,),
    ).fetchone()
    if row is None:
        return {}
    return {field: row[field] for field in fields}


def _fetch_infrastructure_derivation(conn: sqlite3.Connection, node_id: str) -> str | None:
    if not _table_exists(conn, "civ_infrastructure_state"):
        return None
    cols = _columns(conn, "civ_infrastructure_state")
    if "node_subject_id" not in cols or "derivation_id" not in cols:
        return None
    where = "node_subject_id=?"
    args: list[object] = [node_id]
    if "year" in cols:
        where += " AND year=?"
        args.append(2226)
    row = conn.execute(
        f"SELECT derivation_id FROM civ_infrastructure_state WHERE {where}",
        args,
    ).fetchone()
    return None if row is None else row["derivation_id"]


def _fetch_influence_signature(conn: sqlite3.Connection, node_id: str) -> tuple:
    if not _table_exists(conn, "civ_influence_edge"):
        return tuple()
    cols = _columns(conn, "civ_influence_edge")
    key = "subject_id" if "subject_id" in cols else ("node_subject_id" if "node_subject_id" in cols else None)
    if key is None:
        return tuple()
    fields = [field for field in INFLUENCE_SIGNATURE_FIELDS if field in cols]
    if not fields:
        return tuple()
    where = f"{key}=?"
    args: list[object] = [node_id]
    if "year" in cols:
        where += " AND year=?"
        args.append(2226)
    rows = conn.execute(
        f"SELECT {', '.join(fields)} FROM civ_influence_edge WHERE {where}",
        args,
    ).fetchall()
    normalized = []
    for row in rows:
        values = []
        for field in INFLUENCE_SIGNATURE_FIELDS:
            if field not in fields:
                values.append(None)
            else:
                value = row[field]
                if isinstance(value, float):
                    value = round(value, 12)
                values.append(value)
        normalized.append(tuple(values))
    return tuple(sorted(normalized, key=repr))


def _derivation_rows(conn: sqlite3.Connection, derivation_ids: set[str]) -> dict:
    candidates = [name for name in ("civ_derivation", "civ_derivation_registry", "civ_derivation_method") if _table_exists(conn, name)]
    result = {}
    for table in candidates:
        cols = _columns(conn, table)
        key = next((k for k in ("derivation_id", "id") if k in cols), None)
        if key is None:
            continue
        for derivation_id in sorted(derivation_ids):
            row = conn.execute(f"SELECT * FROM {table} WHERE {key}=?", (derivation_id,)).fetchone()
            if row is not None:
                result.setdefault(derivation_id, []).append({"table": table, "row": dict(row)})
    return result


def load_lineage(db_path: str | Path) -> tuple[dict[str, dict], dict]:
    conn = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        node_ids = sorted({node for pair in DUPLICATE_PAIRS for node in pair})
        nodes = {}
        derivation_ids: set[str] = set()
        for node_id in node_ids:
            infra_derivation = _fetch_infrastructure_derivation(conn, node_id)
            influence_signature = _fetch_influence_signature(conn, node_id)
            nodes[node_id] = {
                "subject": _fetch_subject(conn, node_id),
                "infrastructure_derivation_id": infra_derivation,
                "influence_signature": influence_signature,
            }
            if infra_derivation:
                derivation_ids.add(infra_derivation)
            for signature_row in influence_signature:
                derivation_id = signature_row[5]
                if derivation_id:
                    derivation_ids.add(derivation_id)

        metadata = {
            "derivation_rows": _derivation_rows(conn, derivation_ids),
            "tables_with_derivation_id": sorted(
                table
                for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                if "derivation_id" in _columns(conn, table)
            ),
        }
        return nodes, metadata
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only HEL materializer lineage audit")
    parser.add_argument("--db", default="data/LOOM_2226_CIVSTATE.sqlite3")
    args = parser.parse_args()
    nodes, metadata = load_lineage(args.db)
    report = summarize_lineage(nodes)
    report["nodes"] = {
        node_id: {
            "subject": data["subject"],
            "infrastructure_derivation_id": data["infrastructure_derivation_id"],
            "influence_signature": [list(row) for row in data["influence_signature"]],
        }
        for node_id, data in nodes.items()
    }
    report["metadata"] = metadata
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
