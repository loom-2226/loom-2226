#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 probe for interpolated Ceres/Neptune state at earned flight epochs."""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.loom_sqlite_interpolated_celestial_provider import SQLiteInterpolatedCelestialResolver

DEPARTURE = "2226-08-22T01:32:00Z"
ARRIVAL = "2226-08-22T09:45:17.864616Z"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=REPO_ROOT / "data" / "LOOM_2226.sqlite3")
    args = parser.parse_args()

    resolver = SQLiteInterpolatedCelestialResolver(args.db)
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
            rows.append({"entity_id": entity_id, "epoch_utc": epoch, "pass": False, "error": f"{type(exc).__name__}: {exc}"})
    ok = ok and all(row.get("pass") is True for row in rows)
    result = {
        "schema": "LOOM_E1_INTERPOLATED_CELESTIAL_PROBE_V1",
        "route": "CERES>NEPTUNE_SYSTEM",
        "rows": rows,
        "interpolated_coverage_pass": ok,
        "next_action": "RUN_REAL_E1_DOMAIN_HYDRATION" if ok else "INSPECT_EPHEMERIS_ANCHOR_COVERAGE",
        "authority_note": "READ_ONLY_DIAGNOSTIC_NO_ROUTE_OR_CAMPAIGN_MUTATION",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
