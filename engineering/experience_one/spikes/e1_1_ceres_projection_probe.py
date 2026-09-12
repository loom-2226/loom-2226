#!/usr/bin/env python3
from __future__ import annotations

"""Experience One E1.1 — read-only Ceres projection probe.

Purpose:
- inspect the actual local WORLD/CIVSTATE schemas without assuming table names;
- find governed rows that already mention the requested entity;
- emit a small evidence artifact for DATA-vs-PROJECTION diagnosis;
- never mutate WORLD, CIVSTATE, campaign state, or UI behavior.

This is a diagnostic/projection probe, not production Mara architecture.
"""

import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = "LOOM_E1_1_CANON_CONTEXT_PROBE_V1"
DEFAULT_ANDROID_ROOT = Path("/storage/emulated/0/Download/LOOM_TEST")
DEFAULT_ANDROID_OUT = Path("/storage/emulated/0/Download/E1_1_CERES_PROJECTION_PROBE.json")
MAX_RELATIONS = 500
MAX_ROWS_PER_RELATION = 8
MAX_CELL_CHARS = 500


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def runtime_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("LOOM_HOME", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    if DEFAULT_ANDROID_ROOT.exists():
        return DEFAULT_ANDROID_ROOT
    return Path.cwd().resolve()


def db_paths(root: Path) -> dict[str, Path]:
    data_dir = Path(os.environ.get("LOOM_DATA_DIR", str(root / "data"))).expanduser().resolve()
    world = Path(os.environ.get("LOOM_WORLD_DB", str(data_dir / "LOOM_2226.sqlite3"))).expanduser().resolve()
    civ = Path(os.environ.get("LOOM_CIVSTATE_DB", str(data_dir / "LOOM_2226_CIVSTATE.sqlite3"))).expanduser().resolve()
    return {"WORLD": world, "CIVSTATE": civ}


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def scalar(v: Any) -> Any:
    if v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, bytes):
        return f"<BLOB {len(v)} bytes>"
    s = str(v)
    if len(s) > MAX_CELL_CHARS:
        return s[:MAX_CELL_CHARS] + "…"
    return s


def relation_columns(conn: sqlite3.Connection, relation: str) -> list[dict[str, Any]]:
    rows = conn.execute(f"PRAGMA table_info({qident(relation)})").fetchall()
    return [
        {
            "name": r[1],
            "declared_type": r[2] or "",
            "notnull": bool(r[3]),
            "pk": bool(r[5]),
        }
        for r in rows
    ]


def searchable_columns(cols: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for c in cols:
        t = c["declared_type"].upper()
        # SQLite typing is permissive. Empty declarations are included because many
        # legacy/generated schemas store text without a declared TEXT affinity.
        if not t or any(x in t for x in ("CHAR", "CLOB", "TEXT", "JSON")):
            out.append(c["name"])
    return out


def inspect_database(label: str, path: Path, needle: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "database": label,
        "path": str(path),
        "exists": path.is_file(),
        "sha256": sha256_file(path),
        "mode": "READ_ONLY",
        "relations_scanned": 0,
        "matching_relations": [],
    }
    if not path.is_file():
        return result

    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        relations = conn.execute(
            "SELECT name, type FROM sqlite_master "
            "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name LIMIT ?",
            (MAX_RELATIONS,),
        ).fetchall()
        for rel in relations:
            name = str(rel["name"])
            cols = relation_columns(conn, name)
            text_cols = searchable_columns(cols)
            result["relations_scanned"] += 1
            if not text_cols:
                continue

            where = " OR ".join(
                f"instr(lower(CAST({qident(c)} AS TEXT)), lower(?)) > 0" for c in text_cols
            )
            sql = f"SELECT * FROM {qident(name)} WHERE {where} LIMIT ?"
            params = [needle] * len(text_cols) + [MAX_ROWS_PER_RELATION]
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.DatabaseError as exc:
                result["matching_relations"].append(
                    {
                        "relation": name,
                        "relation_type": rel["type"],
                        "search_error": str(exc),
                        "columns": cols,
                        "rows": [],
                    }
                )
                continue
            if not rows:
                continue

            samples = []
            for row in rows:
                samples.append({k: scalar(row[k]) for k in row.keys()})
            result["matching_relations"].append(
                {
                    "relation": name,
                    "relation_type": rel["type"],
                    "columns": cols,
                    "matched_row_sample_count": len(samples),
                    "sample_limit": MAX_ROWS_PER_RELATION,
                    "rows": samples,
                }
            )
    finally:
        conn.close()
    result["matching_relation_count"] = len(result["matching_relations"])
    result["sampled_matching_rows"] = sum(
        int(x.get("matched_row_sample_count", 0)) for x in result["matching_relations"]
    )
    return result


def atlas_probe(repo_root: Path, needle: str) -> dict[str, Any]:
    atlas = repo_root / "canon" / "current" / "LOOM_2226_Earth_Solar_System_Canon_Atlas_v3.2.md"
    result: dict[str, Any] = {
        "path": str(atlas),
        "exists": atlas.is_file(),
        "sha256": sha256_file(atlas),
        "matching_blocks": [],
    }
    if not atlas.is_file():
        return result
    text = atlas.read_text(encoding="utf-8", errors="replace")
    blocks = [b.strip() for b in text.split("\n\n") if needle.lower() in b.lower()]
    result["matching_blocks"] = [b[:2500] for b in blocks[:20]]
    result["matching_block_count"] = len(blocks)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", help="LOOM runtime root; defaults to LOOM_HOME / Android LOOM_TEST / cwd")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Git checkout root for canon source probe")
    ap.add_argument("--entity", default="Ceres")
    ap.add_argument("--out", type=Path, default=DEFAULT_ANDROID_OUT)
    args = ap.parse_args()

    root = runtime_root(args.root)
    paths = db_paths(root)
    entity = args.entity.strip()
    if not entity:
        raise RuntimeError("--entity may not be empty")

    db_results = [inspect_database(label, path, entity) for label, path in paths.items()]
    atlas = atlas_probe(args.repo_root.expanduser().resolve(), entity)

    matching_relations = sum(int(x.get("matching_relation_count", 0)) for x in db_results)
    sampled_rows = sum(int(x.get("sampled_matching_rows", 0)) for x in db_results)
    data_presence = bool(matching_relations or atlas.get("matching_block_count", 0))

    result = {
        "schema": SCHEMA,
        "entity": entity,
        "runtime_root": str(root),
        "authority_policy": {
            "database_access": "READ_ONLY_URI_MODE",
            "mutation": False,
            "model_used": False,
            "ui_replacement": False,
            "classification": "E1_1_PROJECTION_DIAGNOSTIC_ONLY",
        },
        "databases": db_results,
        "atlas": atlas,
        "summary": {
            "matching_database_relations": matching_relations,
            "sampled_matching_rows": sampled_rows,
            "atlas_matching_blocks": int(atlas.get("matching_block_count", 0)),
            "governed_data_presence_observed": data_presence,
            "diagnostic_interpretation": (
                "DATA_PRESENT_PROJECTION_TEST_NEXT" if data_presence else "DATA_NOT_OBSERVED_IN_CURRENT_PROBE"
            ),
        },
        "limits": [
            "Substring probe is evidence discovery, not a canonical entity-resolution contract.",
            "Rows are sampled and cell text is truncated; absence from samples does not prove global absence.",
            "No production projection schema is selected by this probe.",
            "No new canon may be inferred from relation names or coincidental text matches.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print("OUTPUT:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
