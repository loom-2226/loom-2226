#!/usr/bin/env python3
from __future__ import annotations

"""Read-only inventory of already-versioned Geometric Admissibility inputs.

This module audits SQLite schema only. It identifies concrete columns that may
support canon-named Geometric Admissibility observable families. Presence of a
column does not establish physical relevance, a threshold, an admissibility
rule, or runtime policy.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "data" / "LOOM_2226.sqlite3"

FAMILY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "gravity": ("gm_", "mass_", "gravity", "gravitational"),
    "geometry": ("radius", "diameter", "flattening", "ellipsoid"),
    "matter_environment": ("density", "atmospher", "pressure", "composition", "plasma_density"),
    "electromagnetic_environment": ("magnetic", "magnet", "electric_field", "flux_density", "radiation", "solar_wind"),
    "uncertainty": ("uncertainty", "sigma", "error_bound", "stddev", "confidence_interval"),
    "provenance_quality": ("source", "status", "quality", "grade", "provenance", "epoch", "updated", "timestamp"),
}


def _matches(column_name: str, keywords: tuple[str, ...]) -> bool:
    name = column_name.lower()
    return any(keyword in name for keyword in keywords)


def inventory_schema(db_path: Path) -> dict[str, Any]:
    path = Path(db_path).resolve()
    if not path.is_file():
        raise RuntimeError(f"LOOM database not found: {path}")

    families: dict[str, list[str]] = {name: [] for name in FAMILY_KEYWORDS}
    scanned_tables: list[str] = []

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        for table in tables:
            scanned_tables.append(table)
            escaped = table.replace("'", "''")
            for row in conn.execute(f"PRAGMA table_info('{escaped}')"):
                column = str(row[1])
                qualified = f"{table}.{column}"
                for family, keywords in FAMILY_KEYWORDS.items():
                    if _matches(column, keywords):
                        families[family].append(qualified)
    finally:
        conn.close()

    for values in families.values():
        values.sort()

    return {
        "schema": "LOOM_E1_GEOMETRIC_ADMISSIBILITY_DATA_INVENTORY_V1",
        "status": "PASS",
        "classification": "DATA_AVAILABILITY_AUDIT_ONLY_NOT_ADMISSIBILITY_POLICY",
        "database": str(path),
        "tables_scanned": scanned_tables,
        "families": families,
        "authority_note": "READ_ONLY_SCHEMA_AUDIT_NO_THRESHOLD_NO_METRIC_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "interpretation": "COLUMN_PRESENCE_ONLY_DO_NOT_INFER_PHYSICAL_RELEVANCE_OR_ADMISSIBILITY",
    }


def main() -> int:
    print(json.dumps(inventory_schema(DB_PATH), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
