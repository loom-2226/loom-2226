#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 probe for interpolated Ceres/Neptune state at earned flight epochs.

When interpolation cannot resolve an endpoint, report the actual SQLite anchor
coverage needed to decide the next E1 step. This remains diagnostic-only: no
route solve, no ephemeris generation, no database mutation, no campaign change.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.loom_sqlite_interpolated_celestial_provider import SQLiteInterpolatedCelestialResolver

DEPARTURE = "2226-08-22T01:32:00Z"
ARRIVAL = "2226-08-22T09:45:17.864616Z"


def _coverage(db: Path, entity_id: str, requested_epoch: str) -> dict:
    """Describe real `states` coverage around one requested E1 epoch."""
    conn = sqlite3.connect(f"file:{db.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    try:
        totals = conn.execute(
            """
            SELECT
              COUNT(*) AS total_rows,
              SUM(CASE WHEN reference_frame='J2000' AND reference_plane='ECLIPTIC' THEN 1 ELSE 0 END) AS canonical_rows,
              SUM(CASE WHEN reference_frame='J2000' AND reference_plane='ECLIPTIC' AND navigation_grade=1 THEN 1 ELSE 0 END) AS navigation_grade_rows,
              MIN(epoch_utc) AS min_epoch,
              MAX(epoch_utc) AS max_epoch
            FROM states WHERE entity_id=?
            """,
            (entity_id,),
        ).fetchone()

        def one(sql: str):
            row = conn.execute(sql, (entity_id, requested_epoch)).fetchone()
            return None if row is None else dict(row)

        before = one(
            """
            SELECT epoch_utc,reference_frame,reference_plane,navigation_grade,source
            FROM states
            WHERE entity_id=? AND epoch_utc<=?
              AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
              AND navigation_grade=1
            ORDER BY epoch_utc DESC LIMIT 1
            """
        )
        after = one(
            """
            SELECT epoch_utc,reference_frame,reference_plane,navigation_grade,source
            FROM states
            WHERE entity_id=? AND epoch_utc>=?
              AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
              AND navigation_grade=1
            ORDER BY epoch_utc ASC LIMIT 1
            """
        )
        nearest_any = conn.execute(
            """
            SELECT epoch_utc,reference_frame,reference_plane,navigation_grade,source
            FROM states
            WHERE entity_id=?
            ORDER BY ABS(julianday(epoch_utc)-julianday(?)) ASC
            LIMIT 5
            """,
            (entity_id, requested_epoch),
        ).fetchall()
        return {
            "total_rows": int(totals["total_rows"] or 0),
            "canonical_rows": int(totals["canonical_rows"] or 0),
            "navigation_grade_rows": int(totals["navigation_grade_rows"] or 0),
            "min_epoch": totals["min_epoch"],
            "max_epoch": totals["max_epoch"],
            "navigation_grade_before": before,
            "navigation_grade_after": after,
            "nearest_rows_any_grade": [dict(row) for row in nearest_any],
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=REPO_ROOT / "data" / "LOOM_2226.sqlite3")
    args = parser.parse_args()
    db = args.db.expanduser().resolve()

    resolver = SQLiteInterpolatedCelestialResolver(db)
    rows = []
    ok = True
    for entity_id, epoch in (("CERES", DEPARTURE), ("NEPTUNE", ARRIVAL)):
        try:
            state = resolver.resolve(entity_id, epoch)
            rows.append({
                "entity_id": entity_id,
                "epoch_utc": state.epoch_utc,
                "position_km": list(state.position_km),
                "velocity_km_s": list(state.velocity_km_s),
                "reference_frame": state.reference_frame,
                "navigation_grade": state.navigation_grade,
                "provenance": dict(state.provenance),
                "pass": state.navigation_grade is True,
            })
        except Exception as exc:
            ok = False
            rows.append({
                "entity_id": entity_id,
                "epoch_utc": epoch,
                "pass": False,
                "error": f"{type(exc).__name__}: {exc}",
                "anchor_coverage": _coverage(db, entity_id, epoch),
            })
    ok = ok and all(row.get("pass") is True for row in rows)
    result = {
        "schema": "LOOM_E1_INTERPOLATED_CELESTIAL_PROBE_V2",
        "route": "CERES>NEPTUNE_SYSTEM",
        "database": str(db),
        "rows": rows,
        "interpolated_coverage_pass": ok,
        "next_action": "RUN_REAL_E1_DOMAIN_HYDRATION" if ok else "DECIDE_FROM_REPORTED_ANCHOR_COVERAGE",
        "authority_note": "READ_ONLY_DIAGNOSTIC_NO_ROUTE_OR_CAMPAIGN_MUTATION",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
