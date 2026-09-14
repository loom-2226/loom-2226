#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 probe for exact celestial-state coverage at qualified flight epochs.

This does not solve a route, interpolate ephemeris, choose metric-domain radii,
mutate campaign state, or alter the E1 flight implementation. It answers whether
the promoted SQLite provider already has exact navigation-grade center states for
the Ceres departure and Neptune arrival epochs earned by the Pixel qualification.
"""

import argparse
import json
from pathlib import Path

from src.loom_sqlite_celestial_provider import SQLiteCelestialCatalog

DEPARTURE = "2226-08-22T01:32:00Z"
ARRIVAL = "2226-08-22T09:45:17.864616Z"


def _row(catalog: SQLiteCelestialCatalog, entity_id: str, epoch: str) -> dict:
    state = catalog.direct_state(entity_id, epoch)
    if state is None:
        return {
            "entity_id": entity_id,
            "epoch_utc": epoch,
            "exact_direct_navigation_grade": False,
        }
    return {
        "entity_id": state.entity_id,
        "epoch_utc": state.epoch_utc,
        "reference_frame": state.reference_frame,
        "position_km": list(state.position_km),
        "velocity_km_s": list(state.velocity_km_s),
        "navigation_grade": state.navigation_grade,
        "provenance": dict(state.provenance),
        "exact_direct_navigation_grade": state.navigation_grade is True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/LOOM_2226.sqlite3"),
        help="Path to authoritative LOOM WORLD/CORE celestial SQLite database",
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    catalog = SQLiteCelestialCatalog(args.db)
    rows = [
        _row(catalog, "CERES", DEPARTURE),
        _row(catalog, "NEPTUNE", ARRIVAL),
    ]
    passed = all(row["exact_direct_navigation_grade"] for row in rows)
    result = {
        "schema": "LOOM_E1_CELESTIAL_EXACT_EPOCH_COVERAGE_PROBE_V1",
        "e1_route": "CERES>NEPTUNE_SYSTEM",
        "purpose": "DECIDE_IF_INTERPOLATION_PROMOTION_IS_REQUIRED",
        "database": str(args.db.resolve()),
        "rows": rows,
        "exact_epoch_coverage_pass": passed,
        "next_action": (
            "PROCEED_TO_E1_METRIC_DOMAIN_HYDRATION"
            if passed
            else "PROMOTE_EXISTING_QUALIFIED_INTERPOLATION_SEAM"
        ),
        "authority_note": "DIAGNOSTIC_ONLY_NO_CAMPAIGN_OR_ROUTE_MUTATION",
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
