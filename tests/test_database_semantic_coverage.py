#!/usr/bin/env python3
"""Fail if either production SQLite schema outruns the semantic index.

This checker validates coverage only. It does not certify that a semantic
entry is correct or sufficiently understood.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "database_semantics" / "LOOM_DATABASE_SEMANTIC_INDEX_v0.1.json"
DBS = {
    "LOOM_2226_CIVSTATE.sqlite3": ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3",
    "LOOM_2226.sqlite3": ROOT / "data" / "LOOM_2226.sqlite3",
}


def schema(path: Path) -> dict[str, list[str]]:
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        return {t: [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')] for t in tables}
    finally:
        con.close()


def main() -> int:
    obj = json.loads(INDEX.read_text(encoding="utf-8"))
    indexed = {(r["database"], r["table"]): set(r.get("schema_columns", [])) for r in obj["tables"]}
    errors: list[str] = []
    for db_name, path in DBS.items():
        live = schema(path)
        for table, cols in live.items():
            key = (db_name, table)
            if key not in indexed:
                errors.append(f"MISSING TABLE {db_name}:{table}")
                continue
            missing = sorted(set(cols) - indexed[key])
            extra = sorted(indexed[key] - set(cols))
            if missing:
                errors.append(f"MISSING COLUMNS {db_name}:{table}: {missing}")
            if extra:
                errors.append(f"STALE COLUMNS {db_name}:{table}: {extra}")
        extra_tables = sorted(t for (d,t) in indexed if d == db_name and t not in live)
        for t in extra_tables:
            errors.append(f"STALE TABLE {db_name}:{t}")
    if errors:
        print("SEMANTIC COVERAGE FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("SEMANTIC COVERAGE PASS: every production table and column is represented in the semantic index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
