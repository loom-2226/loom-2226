#!/usr/bin/env python3
from __future__ import annotations

"""Read-only qualification of already-versioned Geometric Admissibility inputs.

This module deliberately uses an exact allowlist of physically defensible fields
for Neptune rather than keyword-matching the entire database schema. It reports
what LOOM already has, plus canon-relevant families that remain missing. It does
not define a metric threshold, admissibility score, or runtime policy.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "data" / "LOOM_2226.sqlite3"
ENTITY_CANDIDATES = ("NE", "NEPTUNE", "NEPTUNE_SYSTEM")


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    escaped = table.replace("'", "''")
    try:
        return {str(row[1]) for row in conn.execute(f"PRAGMA table_info('{escaped}')")}
    except sqlite3.DatabaseError:
        return set()


def _first_entity_row(conn: sqlite3.Connection, table: str, columns: list[str]) -> sqlite3.Row | None:
    available = _table_columns(conn, table)
    if "entity_id" not in available:
        return None
    selected = [column for column in columns if column in available]
    if not selected:
        return None
    select_sql = ",".join(["entity_id", *selected])
    for entity_id in ENTITY_CANDIDATES:
        row = conn.execute(f"SELECT {select_sql} FROM {table} WHERE entity_id=? LIMIT 1", (entity_id,)).fetchone()
        if row is not None:
            return row
    return None


def _latest_state(conn: sqlite3.Connection) -> sqlite3.Row | None:
    available = _table_columns(conn, "states")
    required = {"entity_id", "epoch_utc"}
    if not required.issubset(available):
        return None
    selected = [c for c in ("entity_id", "epoch_utc", "source", "navigation_grade", "reference_frame", "reference_plane") if c in available]
    select_sql = ",".join(selected)
    for entity_id in ENTITY_CANDIDATES:
        row = conn.execute(
            f"SELECT {select_sql} FROM states WHERE entity_id=? ORDER BY epoch_utc DESC LIMIT 1",
            (entity_id,),
        ).fetchone()
        if row is not None:
            return row
    return None


def qualify_neptune_inputs(db_path: Path) -> dict[str, Any]:
    path = Path(db_path).resolve()
    if not path.is_file():
        raise RuntimeError(f"LOOM database not found: {path}")

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA query_only=ON")
        props = _first_entity_row(
            conn,
            "celestial_properties",
            ["gm_km3_s2", "mean_radius_km", "source_id", "status"],
        )
        dyn = _first_entity_row(
            conn,
            "celestial_dynamics",
            [
                "gm_km3_s2",
                "mean_radius_km",
                "reference_orbit_radius_km",
                "hill_radius_km",
                "soi_radius_km",
                "atmosphere_class",
                "source",
                "metadata_status",
            ],
        )
        state = _latest_state(conn)
    finally:
        conn.close()

    if props is None and dyn is None:
        raise RuntimeError(f"no Neptune physical row found for candidates {ENTITY_CANDIDATES}")

    body = str((props or dyn)["entity_id"])

    gravity: dict[str, Any] = {}
    geometry: dict[str, Any] = {}
    matter: dict[str, Any] = {}
    provenance: dict[str, Any] = {}

    if props is not None:
        if "gm_km3_s2" in props.keys() and props["gm_km3_s2"] is not None:
            gravity["gm_km3_s2"] = float(props["gm_km3_s2"])
            provenance["gm_source"] = f"celestial_properties:{props['source_id'] or ''}:{props['status']}"
        if "mean_radius_km" in props.keys() and props["mean_radius_km"] is not None:
            geometry["mean_radius_km"] = float(props["mean_radius_km"])
        if "source_id" in props.keys():
            provenance["celestial_properties_source_id"] = props["source_id"]
        if "status" in props.keys():
            provenance["celestial_properties_status"] = props["status"]

    if dyn is not None:
        if not gravity and "gm_km3_s2" in dyn.keys() and dyn["gm_km3_s2"] is not None:
            gravity["gm_km3_s2"] = float(dyn["gm_km3_s2"])
            provenance["gm_source"] = f"celestial_dynamics:{dyn['source'] or ''}:{dyn['metadata_status']}"
        if "mean_radius_km" in dyn.keys() and dyn["mean_radius_km"] is not None and "mean_radius_km" not in geometry:
            geometry["mean_radius_km"] = float(dyn["mean_radius_km"])
        for field in ("reference_orbit_radius_km", "hill_radius_km", "soi_radius_km"):
            if field in dyn.keys() and dyn[field] is not None:
                geometry[field] = float(dyn[field])
        if "atmosphere_class" in dyn.keys() and dyn["atmosphere_class"] not in (None, ""):
            matter["atmosphere_class"] = dyn["atmosphere_class"]
        if "source" in dyn.keys():
            provenance["celestial_dynamics_source"] = dyn["source"]
        if "metadata_status" in dyn.keys():
            provenance["celestial_dynamics_metadata_status"] = dyn["metadata_status"]

    if state is not None:
        if "epoch_utc" in state.keys():
            provenance["state_epoch_utc"] = state["epoch_utc"]
        if "source" in state.keys():
            provenance["state_source"] = state["source"]
        if "navigation_grade" in state.keys():
            provenance["navigation_grade"] = state["navigation_grade"]
        if "reference_frame" in state.keys():
            provenance["reference_frame"] = state["reference_frame"]
        if "reference_plane" in state.keys():
            provenance["reference_plane"] = state["reference_plane"]

    available = {
        "gravity": gravity,
        "geometry": geometry,
        "matter_environment": matter,
        "electromagnetic_environment": {},
        "physical_uncertainty": {},
        "loom_coherence": {},
        "provenance_quality": provenance,
    }

    missing: list[str] = []
    if "atmosphere_class" not in matter:
        missing.append("atmospheric_classification")
    missing.extend(
        [
            "local_matter_density",
            "electromagnetic_environment",
            "physical_uncertainty",
            "loom_coherence",
        ]
    )

    return {
        "schema": "LOOM_E1_GEOMETRIC_ADMISSIBILITY_INPUT_QUALIFICATION_V1",
        "status": "PASS",
        "body": body,
        "database": str(path),
        "available": available,
        "missing_required_families": missing,
        "rejected_false_positive_classes": [
            "infrastructure_mass_fields_are_not_local_gravity",
            "transport_feeder_density_is_not_local_matter_density",
            "generic_schema_keyword_match_is_not_physical_qualification",
        ],
        "authority_note": "READ_ONLY_EXACT_FIELD_QUALIFICATION_NO_THRESHOLD_NO_SCORE_NO_METRIC_POLICY_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        "interpretation": "AVAILABLE_MEANS_VERSIONED_FIELD_PRESENT_FOR_NEPTUNE_ONLY_NOT_PHYSICALLY_SUFFICIENT_FOR_ADMISSIBILITY",
        "next_action": "PURSUE_MISSING_ENVIRONMENT_AND_UNCERTAINTY_FAMILIES_BEFORE_COMPOUND_ADMISSIBILITY_MODEL",
    }


def main() -> int:
    print(json.dumps(qualify_neptune_inputs(DB_PATH), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
