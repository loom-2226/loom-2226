#!/usr/bin/env python3
"""Audit Earth-Luna infrastructure completeness from authoritative WORLD SQLite.

Produces JSON and Markdown inventories. Read-only: never mutates WORLD.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

BODY_IDS = ("EA", "LU")
SUPPORT_TABLES = {
    "physical": "infrastructure_physical_properties",
    "engineering": "infrastructure_engineering_profiles",
    "energy": "infrastructure_energy_profiles",
    "capacity": "infrastructure_capacity_profiles",
    "transport": "entity_transport_profiles",
}


def has_row(conn: sqlite3.Connection, table: str, entity_id: str) -> bool:
    return conn.execute(f"SELECT 1 FROM {table} WHERE entity_id=? LIMIT 1", (entity_id,)).fetchone() is not None


def get_optional_row(conn: sqlite3.Connection, sql: str, params=()):
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None


def classify_runtime(location: dict | None, orbit: dict | None) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if not location:
        return "NO", ["missing entity_location_models"]
    frame = location.get("frame_family")
    if frame == "PARENT_BODY_FIXED":
        blockers.append("body-fixed->inertial runtime transform not yet qualified")
    if frame and frame.endswith("ROTATING"):
        blockers.append("rotating-frame runtime propagation/transform required")
    if orbit and orbit.get("navigation_grade") in (0, "0", False):
        blockers.append("orbit geometry is engineering-reference, not navigation-grade")
    if location.get("precision_class") in ("POINT_OR_REGION", "REGION", "ROLE_CONSTRAINED"):
        blockers.append(f"placement precision is {location.get('precision_class')}")
    return ("YES" if not blockers else "PARTIAL", blockers)


def audit(world: Path) -> list[dict]:
    conn = sqlite3.connect(world)
    conn.row_factory = sqlite3.Row
    try:
        entities = conn.execute(
            """
            SELECT e.entity_id, e.name, e.parent_entity_id,
                   n.facility_type, n.system, n.traffic,
                   n.civil_authority, n.administrative_authority, n.security_authority
            FROM entities e
            JOIN infrastructure_nodes n ON n.entity_id=e.entity_id
            WHERE e.parent_entity_id IN (?, ?)
            ORDER BY e.entity_id
            """,
            BODY_IDS,
        ).fetchall()
        out = []
        for e in entities:
            entity_id = e["entity_id"]
            loc = get_optional_row(conn, "SELECT * FROM entity_location_models WHERE entity_id=?", (entity_id,))
            orbit = get_optional_row(conn, "SELECT * FROM orbit_geometry_models WHERE entity_id=?", (entity_id,))
            media = get_optional_row(
                conn,
                """
                SELECT ia.media_key, ia.asset_role, ia.review_status, ia.is_current
                FROM knowledge_entities ke
                JOIN image_assets ia ON ia.knowledge_entity_id=ke.knowledge_entity_id
                WHERE ke.spatial_entity_id=? AND ia.asset_role='HERO' AND ia.is_current=1
                ORDER BY ia.media_key LIMIT 1
                """,
                (entity_id,),
            )
            runtime, blockers = classify_runtime(loc, orbit)
            row = {
                "entity_id": entity_id,
                "name": e["name"],
                "parent_body_id": e["parent_entity_id"],
                "facility_type": e["facility_type"],
                "system": e["system"],
                "traffic": e["traffic"],
                "civil_authority": e["civil_authority"],
                "administrative_authority": e["administrative_authority"],
                "security_authority": e["security_authority"],
                "location_model": loc,
                "orbit_geometry": orbit,
                "profiles": {key: has_row(conn, table, entity_id) for key, table in SUPPORT_TABLES.items()},
                "hero_media": media,
                "hud_runtime_resolvable": runtime,
                "runtime_blockers": blockers,
            }
            out.append(row)
        return out
    finally:
        conn.close()


def markdown(rows: list[dict]) -> str:
    lines = [
        "# Earth-Luna Infrastructure Completeness Matrix v0.1",
        "",
        "Generated read-only from `data/LOOM_2226.sqlite3`. WORLD remains authority. Classification describes present runtime readiness only; it does not promote engineering-reference geometry to canon or navigation-grade status.",
        "",
        "| ID | Name | Type | Frame | Placement precision | Orbit family | Phys | Eng | Energy | Cap | Transport | HERO | Runtime | Blockers |",
        "|---|---|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|---|",
    ]
    for r in rows:
        loc = r["location_model"] or {}
        orb = r["orbit_geometry"] or {}
        p = r["profiles"]
        blockers = "; ".join(r["runtime_blockers"]) or "—"
        lines.append(
            "| {entity_id} | {name} | {facility_type} | {frame} | {precision} | {orbit} | {physical} | {engineering} | {energy} | {capacity} | {transport} | {hero} | {runtime} | {blockers} |".format(
                entity_id=r["entity_id"],
                name=str(r["name"]).replace("|", "/"),
                facility_type=r["facility_type"] or "—",
                frame=loc.get("frame_family") or "—",
                precision=loc.get("precision_class") or "—",
                orbit=orb.get("orbit_family") or "—",
                physical="Y" if p["physical"] else "—",
                engineering="Y" if p["engineering"] else "—",
                energy="Y" if p["energy"] else "—",
                capacity="Y" if p["capacity"] else "—",
                transport="Y" if p["transport"] else "—",
                hero="Y" if r["hero_media"] else "—",
                runtime=r["hud_runtime_resolvable"],
                blockers=blockers.replace("|", "/"),
            )
        )
    lines += ["", "## Summary", ""]
    lines.append(f"- Facilities audited: **{len(rows)}**")
    for status in ("YES", "PARTIAL", "NO"):
        lines.append(f"- Runtime {status}: **{sum(1 for r in rows if r['hud_runtime_resolvable']==status)}**")
    lines.append(f"- Current HERO media: **{sum(1 for r in rows if r['hero_media'])}/{len(rows)}**")
    for key in SUPPORT_TABLES:
        lines.append(f"- {key.title()} profile present: **{sum(1 for r in rows if r['profiles'][key])}/{len(rows)}**")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="data/LOOM_2226.sqlite3")
    ap.add_argument("--json", default="earth_luna_completeness.json")
    ap.add_argument("--markdown", default="earth_luna_completeness.md")
    args = ap.parse_args()
    rows = audit(Path(args.world))
    Path(args.json).write_text(json.dumps(rows, indent=2, sort_keys=True, default=str), encoding="utf-8")
    Path(args.markdown).write_text(markdown(rows), encoding="utf-8")
    print(markdown(rows))


if __name__ == "__main__":
    main()
