"""Read-only Stage F-PA physical-authority inventory for governed LOOM SQLite data."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import sqlite3

AUDIT_CONTRACT = "LOOM_F_PA_PHYSICAL_AUTHORITY_AUDIT_V1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(r[1]) for r in conn.execute(f"PRAGMA table_info({json.dumps(table)})")]


def _count(conn: sqlite3.Connection, table: str) -> int:
    quoted = '"' + table.replace('"', '""') + '"'
    return int(conn.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])


def audit_sqlite(path: Path | str) -> dict[str, Any]:
    db = Path(path).expanduser().resolve()
    with _connect(db) as conn:
        objects = conn.execute(
            "SELECT name,type,sql FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type,name"
        ).fetchall()
        tables: dict[str, Any] = {}
        views: dict[str, Any] = {}
        for row in objects:
            name = str(row["name"])
            item = {"columns": _columns(conn, name), "sql": row["sql"]}
            if row["type"] == "table":
                item["row_count"] = _count(conn, name)
                tables[name] = item
            else:
                views[name] = item

        feature_tokens = {
            "surface_coordinates": ("latitude", "longitude", "elevation", "lat_deg", "lon_deg"),
            "body_orientation": ("pole", "prime_meridian", "rotation", "body_fixed"),
            "orbit_authority": ("semi_major", "eccentricity", "inclination", "raan", "mean_anomaly", "orbit"),
            "traffic_authority": ("traffic", "corridor", "clearance", "roadstead"),
            "docking": ("dock", "rendezvous", "approach", "keep_out", "transition"),
            "navigation_quality": ("navigation_grade", "provenance", "validity", "uncertainty", "source"),
        }
        feature_hits: dict[str, list[str]] = {k: [] for k in feature_tokens}
        for table, meta in tables.items():
            lowered = {c.lower() for c in meta["columns"]}
            for feature, tokens in feature_tokens.items():
                if any(any(token in col for token in tokens) for col in lowered):
                    feature_hits[feature].append(table)

    return {
        "contract": AUDIT_CONTRACT,
        "database": str(db),
        "size_bytes": db.stat().st_size,
        "sha256": _sha256(db),
        "table_count": len(tables),
        "view_count": len(views),
        "tables": tables,
        "views": views,
        "feature_hits": feature_hits,
    }


def audit_pair(world: Path | str, civstate: Path | str) -> dict[str, Any]:
    return {
        "contract": AUDIT_CONTRACT,
        "world": audit_sqlite(world),
        "civstate": audit_sqlite(civstate),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", default="data/LOOM_2226.sqlite3")
    parser.add_argument("--civstate", default="data/LOOM_2226_CIVSTATE.sqlite3")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit_pair(args.world, args.civstate)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
