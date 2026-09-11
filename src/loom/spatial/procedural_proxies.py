"""Deterministic visualization-only geometry for Earth-Luna facilities.

The proxies in this module are normalized presentation silhouettes. They are not
claims about physical dimensions, berth counts, internal topology, collision
volumes, approach corridors, or navigation geometry.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any, Mapping


_PROXY_COMPONENTS: dict[str, list[dict[str, Any]]] = {
    "HABITAT_PORT": [
        {"primitive": "torus", "position": [0, 0, 0], "rotation_deg": [90, 0, 0], "size": [1.00, 0.10]},
        {"primitive": "cylinder", "position": [0, 0, 0], "rotation_deg": [0, 0, 90], "size": [0.18, 1.35]},
        {"primitive": "box", "position": [0.00, 0.82, 0], "size": [0.12, 0.72, 0.03]},
        {"primitive": "box", "position": [0.00, -0.82, 0], "size": [0.12, 0.72, 0.03]},
    ],
    "INDUSTRIAL_PORT": [
        {"primitive": "box", "position": [0, 0, 0], "size": [1.55, 0.12, 0.12]},
        {"primitive": "box", "position": [-0.45, 0.38, 0], "size": [0.48, 0.42, 0.34]},
        {"primitive": "box", "position": [0.35, -0.40, 0], "size": [0.60, 0.38, 0.30]},
        {"primitive": "box", "position": [0.00, 0, 0.52], "size": [1.20, 0.04, 0.28]},
    ],
    "SERVICE_PORT": [
        {"primitive": "cylinder", "position": [0, 0, 0], "rotation_deg": [0, 0, 90], "size": [0.22, 1.15]},
        {"primitive": "box", "position": [0.00, 0.45, 0], "size": [0.75, 0.08, 0.08]},
        {"primitive": "box", "position": [0.00, -0.45, 0], "size": [0.75, 0.08, 0.08]},
        {"primitive": "cylinder", "position": [0.58, 0.45, 0], "size": [0.13, 0.34]},
        {"primitive": "cylinder", "position": [-0.58, -0.45, 0], "size": [0.13, 0.34]},
    ],
    "SHIPYARD": [
        {"primitive": "box", "position": [0, 0, 0], "size": [1.75, 0.10, 0.10]},
        {"primitive": "box", "position": [0.00, 0.52, 0], "size": [1.35, 0.08, 0.08]},
        {"primitive": "box", "position": [0.00, -0.52, 0], "size": [1.35, 0.08, 0.08]},
        {"primitive": "box", "position": [0.65, 0, 0], "size": [0.08, 1.25, 0.72]},
        {"primitive": "box", "position": [-0.65, 0, 0], "size": [0.08, 1.25, 0.72]},
    ],
    "ROTATING_HABITAT": [
        {"primitive": "torus", "position": [-0.34, 0, 0], "rotation_deg": [90, 0, 0], "size": [0.72, 0.08]},
        {"primitive": "torus", "position": [0.34, 0, 0], "rotation_deg": [90, 0, 0], "size": [0.72, 0.08]},
        {"primitive": "cylinder", "position": [0, 0, 0], "rotation_deg": [0, 0, 90], "size": [0.13, 1.45]},
        {"primitive": "box", "position": [0, 0.88, 0], "size": [0.08, 0.65, 0.03]},
        {"primitive": "box", "position": [0, -0.88, 0], "size": [0.08, 0.65, 0.03]},
    ],
    "STRATEGIC_PORT": [
        {"primitive": "sphere", "position": [0, 0, 0], "size": [0.36]},
        {"primitive": "cylinder", "position": [0.48, 0, 0], "rotation_deg": [0, 0, 90], "size": [0.10, 0.80]},
        {"primitive": "dish", "position": [-0.50, 0.08, 0.18], "rotation_deg": [0, -35, 0], "size": [0.42, 0.12]},
        {"primitive": "box", "position": [0, 0.62, 0], "size": [0.08, 0.58, 0.03]},
        {"primitive": "box", "position": [0, -0.62, 0], "size": [0.08, 0.58, 0.03]},
    ],
    "SURFACE_PORT": [
        {"primitive": "cylinder", "position": [0, 0, 0], "size": [0.60, 0.05]},
        {"primitive": "box", "position": [-0.55, 0.15, 0.10], "size": [0.55, 0.36, 0.18]},
        {"primitive": "box", "position": [0.45, -0.20, 0.08], "size": [0.42, 0.28, 0.14]},
        {"primitive": "cylinder", "position": [0.15, 0.48, 0.32], "size": [0.08, 0.62]},
    ],
    "GENERIC_FACILITY": [
        {"primitive": "sphere", "position": [0, 0, 0], "size": [0.30]},
        {"primitive": "cylinder", "position": [0, 0, 0], "rotation_deg": [0, 0, 90], "size": [0.09, 1.00]},
        {"primitive": "box", "position": [0, 0.52, 0], "size": [0.52, 0.05, 0.03]},
        {"primitive": "box", "position": [0, -0.52, 0], "size": [0.52, 0.05, 0.03]},
    ],
}


def proxy_archetype_for(facility_type: str | None) -> str:
    value = str(facility_type or "").upper()
    if "SHIPYARD" in value:
        return "SHIPYARD"
    if "ROTATING_HABITAT" in value:
        return "ROTATING_HABITAT"
    if "INDUSTRIAL" in value or "CARGO" in value:
        return "INDUSTRIAL_PORT"
    if "SERVICE" in value:
        return "SERVICE_PORT"
    if "HABITAT" in value:
        return "HABITAT_PORT"
    if "STRATEGIC" in value or "SCIENCE" in value or "RELAY" in value:
        return "STRATEGIC_PORT"
    if "SURFACE" in value or "LANDING" in value:
        return "SURFACE_PORT"
    if "TRANSFER_HUB" in value:
        return "HABITAT_PORT"
    return "GENERIC_FACILITY"


def ensure_proxy_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS procedural_visual_proxies (
            proxy_id TEXT PRIMARY KEY,
            object_id TEXT NOT NULL UNIQUE REFERENCES spatial_objects(object_id) ON DELETE CASCADE,
            proxy_archetype TEXT NOT NULL,
            geometry_authority TEXT NOT NULL DEFAULT 'VISUALIZATION_ONLY',
            navigation_authority INTEGER NOT NULL DEFAULT 0,
            canon_geometry INTEGER NOT NULL DEFAULT 0,
            scale_basis TEXT NOT NULL DEFAULT 'NORMALIZED_PRESENTATION_UNITS',
            physical_scale_m REAL,
            component_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ENGINEERING_VISUAL_PROXY',
            provenance TEXT NOT NULL,
            notes TEXT,
            CHECK (geometry_authority='VISUALIZATION_ONLY'),
            CHECK (navigation_authority=0),
            CHECK (canon_geometry=0),
            CHECK (physical_scale_m IS NULL)
        );
        """
    )


def register_facility_proxy(conn: sqlite3.Connection, row: Mapping[str, Any]) -> None:
    object_id = str(row["entity_id"])
    facility_type = row["facility_type"]
    archetype = proxy_archetype_for(facility_type)
    components = json.dumps(_PROXY_COMPONENTS[archetype], sort_keys=True, separators=(",", ":"))
    proxy_id = f"PROXY:{object_id}"
    conn.execute(
        """
        INSERT OR REPLACE INTO procedural_visual_proxies
        (proxy_id,object_id,proxy_archetype,component_json,provenance,notes)
        VALUES (?,?,?,?,?,?)
        """,
        (
            proxy_id,
            object_id,
            archetype,
            components,
            "Deterministic normalized proxy derived only from WORLD facility_type; no physical dimensions inferred",
            "HUD/GIS visualization silhouette only; replaceable by later approved render asset",
        ),
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO geometry_assets
        (asset_id,object_id,geometry_role,mime_type,asset_uri,lod_level,scale_m_per_unit,
         navigation_authority,status,provenance)
        VALUES (?,?,'RENDER_LOW','application/vnd.loom.procedural+json',?,0,NULL,0,
                'ENGINEERING_VISUAL_PROXY',
                'Normalized deterministic procedural proxy; visualization only; non-canon geometry')
        """,
        (f"RENDERLOW:{object_id}", object_id, f"procedural://{proxy_id}"),
    )


def decode_proxy_row(row: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(row)
    result["navigation_authority"] = bool(result.get("navigation_authority"))
    result["canon_geometry"] = bool(result.get("canon_geometry"))
    result["components"] = json.loads(result.pop("component_json"))
    return result
