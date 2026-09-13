#!/usr/bin/env python3
"""Build the LOOM production database data dictionary.

Reads both production SQLite databases directly from data/ and emits exhaustive
Markdown + JSON dictionaries. Every current table and every current column is
included. Maintained field definitions are merged from
`docs/database_semantics/DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json`.

This tool does not infer a definition from a table/column name. Missing recovered
meaning is emitted explicitly as DEFINITION_NOT_RECOVERED.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DBS = [
    ROOT / "data" / "LOOM_2226.sqlite3",
    ROOT / "data" / "LOOM_2226_CIVSTATE.sqlite3",
]
DEFAULT_DEFS = ROOT / "docs" / "database_semantics" / "DATA_DICTIONARY_FIELD_DEFINITIONS_v0.1.json"
DEFAULT_MD = ROOT / "docs" / "database_semantics" / "LOOM_DATABASE_DATA_DICTIONARY_v0.1.md"
DEFAULT_JSON = ROOT / "docs" / "database_semantics" / "LOOM_DATABASE_DATA_DICTIONARY_v0.1.json"


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def load_definitions(path: Path) -> tuple[dict[tuple[str, str, str], dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    exact: dict[tuple[str, str, str], dict[str, Any]] = {}
    wildcard: dict[tuple[str, str], dict[str, Any]] = {}
    for row in payload.get("fields", []):
        key = (row["database"], row["table"], row["column"])
        if row["column"] == "*":
            wildcard[(row["database"], row["table"])] = row
        else:
            exact[key] = row
    return exact, wildcard


def table_names(con: sqlite3.Connection) -> list[str]:
    return [
        r[0]
        for r in con.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def table_schema(con: sqlite3.Connection, table: str) -> dict[str, Any]:
    cols = []
    for r in con.execute(f"PRAGMA table_info({qident(table)})"):
        cols.append(
            {
                "cid": r[0],
                "name": r[1],
                "declared_type": r[2] or None,
                "not_null": bool(r[3]),
                "default": r[4],
                "pk_position": int(r[5]),
            }
        )

    fks_by_col: dict[str, list[dict[str, Any]]] = {}
    for r in con.execute(f"PRAGMA foreign_key_list({qident(table)})"):
        item = {
            "target_table": r[2],
            "from_column": r[3],
            "target_column": r[4],
            "on_update": r[5],
            "on_delete": r[6],
        }
        fks_by_col.setdefault(r[3], []).append(item)

    indexes = []
    for r in con.execute(f"PRAGMA index_list({qident(table)})"):
        index_name = r[1]
        indexes.append(
            {
                "name": index_name,
                "unique": bool(r[2]),
                "origin": r[3],
                "columns": [x[2] for x in con.execute(f"PRAGMA index_info({qident(index_name)})")],
            }
        )

    for c in cols:
        c["foreign_keys"] = fks_by_col.get(c["name"], [])

    row_count = con.execute(f"SELECT COUNT(*) FROM {qident(table)}").fetchone()[0]
    pk = [c["name"] for c in sorted((c for c in cols if c["pk_position"]), key=lambda x: x["pk_position"])]
    return {"table": table, "row_count": row_count, "primary_key": pk, "indexes": indexes, "columns": cols}


def attach_definition(db_name: str, table: str, col: dict[str, Any], exact, wildcard) -> dict[str, Any]:
    row = exact.get((db_name, table, col["name"]))
    if row is None:
        row = wildcard.get((db_name, table))
    if row is None:
        definition = {
            "definition_status": "DEFINITION_NOT_RECOVERED",
            "definition": None,
            "unit": None,
            "data_role": None,
            "scope": None,
            "epistemic_status": None,
            "generation": None,
            "join_notes": None,
            "misuse_warning": None,
        }
    else:
        definition = {
            "definition_status": "DEFINED",
            "definition": row.get("definition"),
            "unit": row.get("unit"),
            "data_role": row.get("data_role"),
            "scope": row.get("scope"),
            "epistemic_status": row.get("epistemic_status"),
            "generation": row.get("generation"),
            "join_notes": row.get("join_notes"),
            "misuse_warning": row.get("misuse_warning"),
        }
    out = dict(col)
    out.update(definition)
    return out


def build(db_paths: list[Path], defs_path: Path) -> dict[str, Any]:
    exact, wildcard = load_definitions(defs_path)
    result: dict[str, Any] = {
        "version": "0.1",
        "definition_rule": "Never infer intended meaning from a field name. Unrecovered definitions are explicit.",
        "databases": [],
    }
    for path in db_paths:
        if not path.exists():
            raise FileNotFoundError(path)
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        db = {"database": path.name, "tables": []}
        for t in table_names(con):
            info = table_schema(con, t)
            info["columns"] = [attach_definition(path.name, t, c, exact, wildcard) for c in info["columns"]]
            db["tables"].append(info)
        con.close()
        result["databases"].append(db)
    return result


def render_markdown(doc: dict[str, Any]) -> str:
    lines = [
        "# LOOM Production Database Data Dictionary v0.1",
        "",
        "Generated directly from the production SQLite schemas and merged with the maintained field-definition registry.",
        "",
        "`DEFINITION_NOT_RECOVERED` means the column is structurally inventoried but its concrete data definition has not yet been recovered from builder/methodology/source evidence.",
        "",
    ]
    total_tables = 0
    total_cols = 0
    missing = 0
    for db in doc["databases"]:
        lines += [f"## `{db['database']}`", ""]
        for t in db["tables"]:
            total_tables += 1
            total_cols += len(t["columns"])
            grain = ", ".join(t["primary_key"]) if t["primary_key"] else "NO DECLARED PRIMARY KEY"
            lines += [
                f"### `{t['table']}`",
                "",
                f"- Rows: `{t['row_count']}`",
                f"- Primary key / row identity: `{grain}`",
                "",
                "| Column | SQLite type | Key/nullability | FK | Definition | Unit / scale | Role | Generation / source |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for c in t["columns"]:
                if c["definition_status"] != "DEFINED":
                    missing += 1
                keybits = []
                if c["pk_position"]:
                    keybits.append(f"PK#{c['pk_position']}")
                keybits.append("NOT NULL" if c["not_null"] else "NULLABLE")
                fks = "; ".join(f"{x['target_table']}.{x['target_column']}" for x in c["foreign_keys"]) or "—"
                definition = c["definition"] or "**DEFINITION_NOT_RECOVERED**"
                unit = c["unit"] or "—"
                role = c["data_role"] or "—"
                generation = c["generation"] or "—"
                def esc(v: Any) -> str:
                    return str(v).replace("|", "\\|").replace("\n", " ")
                lines.append(
                    f"| `{esc(c['name'])}` | `{esc(c['declared_type'] or 'UNTYPED')}` | {esc(', '.join(keybits))} | {esc(fks)} | {esc(definition)} | {esc(unit)} | {esc(role)} | {esc(generation)} |"
                )
            lines.append("")
    lines += [
        "## Coverage",
        "",
        f"- Databases: `{len(doc['databases'])}`",
        f"- Tables: `{total_tables}`",
        f"- Columns: `{total_cols}`",
        f"- Columns whose concrete definition is not yet recovered: `{missing}`",
        "",
        "Coverage is structural and exhaustive for the database bytes used to generate this file; definition completeness is reported separately and is never faked.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", type=Path, default=DEFAULT_DBS[0])
    ap.add_argument("--civstate", type=Path, default=DEFAULT_DBS[1])
    ap.add_argument("--definitions", type=Path, default=DEFAULT_DEFS)
    ap.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    ap.add_argument("--json", type=Path, default=DEFAULT_JSON)
    ap.add_argument("--check", action="store_true", help="Fail if generated outputs differ from committed outputs.")
    args = ap.parse_args()

    doc = build([args.world, args.civstate], args.definitions)
    md = render_markdown(doc)
    js = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        ok = True
        for path, expected in ((args.markdown, md), (args.json, js)):
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                print(f"STALE: {path}")
                ok = False
        return 0 if ok else 1

    args.markdown.write_text(md, encoding="utf-8")
    args.json.write_text(js, encoding="utf-8")
    print(f"wrote {args.markdown}")
    print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
