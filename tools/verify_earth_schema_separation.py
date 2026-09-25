#!/usr/bin/env python3
"""Qualify the Earth/CIVSTATE PostgreSQL namespace boundary."""
from __future__ import annotations

import argparse
import json
import subprocess

EARTH = "earth-v0-1-9934d0ac-20260925"
CERES = "ceres-v1-0231e5f7da744728ab5021268b6f239b"
EARTH_TABLES = [
    "earth_area", "earth_biological_cohort_year", "earth_demographic_year",
    "earth_derivation", "earth_economic_year", "earth_labor_composition_year",
    "earth_legacy_labor_year", "earth_sector_asset_year", "earth_sector_year",
]
CIV_TABLES = [
    "civ_census_node_relation", "civ_demographic_state", "civ_derivation",
    "civ_economic_state", "civ_governance_profile", "civ_influence_edge",
    "civ_infrastructure_state", "civ_model_run", "civ_place_dna",
    "civ_social_pressure", "civ_social_state", "civ_subject", "civ_workforce_state",
]
EXPECTED = {
    "earth_area": 237, "earth_biological_cohort_year": 2657718,
    "earth_demographic_year": 47637, "earth_derivation": 7,
    "earth_economic_year": 16080, "earth_labor_composition_year": 10160,
    "earth_legacy_labor_year": 6000, "earth_sector_asset_year": 643200,
    "earth_sector_year": 160800,
}


def q(database: str, sql: str) -> list[str]:
    result = subprocess.run(
        ["psql", "-X", "-d", database, "-At", "-v", "ON_ERROR_STOP=1", "-c", sql],
        check=True, text=True, capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="loom_dev")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    objects = q(args.database, """
        SELECT n.nspname || '.' || c.relname
        FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relkind='r' AND (n.nspname IN ('loom_earth','loom_civ'))
          AND (c.relname LIKE 'earth_%' OR c.relname LIKE 'civ_%')
        ORDER BY 1
    """)
    legacy_civ_schema = 'loom_civ' in q(args.database, "SELECT nspname FROM pg_namespace WHERE nspname='loom_civ'")
    expected_objects = [*(f"loom_earth.{t}" for t in EARTH_TABLES)]
    if legacy_civ_schema:
        expected_objects.extend(f"loom_civ.{t}" for t in CIV_TABLES)
    if objects != sorted(expected_objects):
        raise SystemExit(f"namespace object guard failed: {objects}")
    counts = {}
    snapshots = {}
    for table in EARTH_TABLES:
        rows = q(args.database, f"SELECT count(*) FROM loom_earth.{table}")
        counts[table] = int(rows[0])
        if counts[table] != EXPECTED[table]:
            raise SystemExit(f"{table}: expected {EXPECTED[table]}, got {counts[table]}")
        snapshots[table] = q(args.database, f"SELECT snapshot_id || ':' || count(*) FROM loom_earth.{table} GROUP BY snapshot_id ORDER BY 1")
        if snapshots[table] != [f"{EARTH}:{EXPECTED[table]}"]:
            raise SystemExit(f"{table}: unexpected snapshot membership {snapshots[table]}")
    if legacy_civ_schema:
        for table in CIV_TABLES:
            bad = q(args.database, f"SELECT count(*) FROM loom_civ.{table} WHERE snapshot_id <> '{CERES}'")
            if bad and int(bad[0]) != 0:
                raise SystemExit(f"{table}: non-CIVSTATE snapshot rows: {bad[0]}")
    views = q(args.database, """
        SELECT viewname FROM pg_views WHERE schemaname='loom_narrator'
        AND viewname IN ('current_earth_year','current_country_year','current_country_fact','current_earth_fact')
        ORDER BY 1
    """)
    if views != ['current_country_fact', 'current_country_year', 'current_earth_fact', 'current_earth_year']:
        raise SystemExit(f"narrator view guard failed: {views}")
    result = {"status": "PASS", "database": args.database, "earth_snapshot": EARTH,
              "civ_snapshot": CERES if legacy_civ_schema else "RETIRED_FORENSIC_BASELINE",
              "legacy_civ_schema": "PRESENT_CERES_ONLY" if legacy_civ_schema else "RETIRED_EMPTY",
              "counts": counts, "earth_objects": expected_objects,
              "narrator_views": views}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
