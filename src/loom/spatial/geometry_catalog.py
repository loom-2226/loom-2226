"""Deterministic Earth-Luna spatial/geometry runtime database builder.

WORLD remains authoritative for facility identity and world facts.  This module
materializes a separate runtime SQLite that can be consumed by HUD/Navigator and
progressively enriched with procedural or GLB geometry without mutating WORLD.

The generated database is a runtime/cache product.  The committed seed SQL and
this builder are the reviewable source artifacts.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3


EARTH_LUNA_BODY_IDS = ("EA", "LU")


def _readonly_connection(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def build_earth_luna_geometry_db(world_path: str | Path, seed_path: str | Path, output_path: str | Path) -> Path:
    """Build a fresh Earth-Luna HUD geometry/runtime SQLite database.

    The function intentionally does not copy orbital physics out of WORLD into
    Python constants. Existing facility identity and descriptive facts are read
    from WORLD; non-facility standard orbit targets come from the committed seed.
    """
    world = Path(world_path)
    seed = Path(seed_path)
    out = Path(output_path)
    if not world.exists():
        raise FileNotFoundError(world)
    if not seed.exists():
        raise FileNotFoundError(seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    runtime = sqlite3.connect(out)
    runtime.row_factory = sqlite3.Row
    try:
        runtime.executescript(seed.read_text(encoding="utf-8"))
        source = _readonly_connection(world)
        try:
            rows = source.execute(
                """
                SELECT e.entity_id, e.name, e.parent_entity_id,
                       n.facility_type, n.system, n.traffic,
                       n.civil_authority, n.administrative_authority, n.security_authority
                FROM entities e
                JOIN infrastructure_nodes n ON n.entity_id=e.entity_id
                WHERE e.parent_entity_id IN (?, ?)
                ORDER BY e.entity_id
                """,
                EARTH_LUNA_BODY_IDS,
            ).fetchall()
        finally:
            source.close()

        for row in rows:
            object_id = str(row["entity_id"])
            parent = str(row["parent_entity_id"])
            name = str(row["name"])
            facility_type = row["facility_type"]
            runtime.execute(
                """
                INSERT OR REPLACE INTO spatial_objects
                (object_id, object_kind, world_entity_id, display_name, parent_body_id,
                 operational_role, status, source_class, source_ref, notes)
                VALUES (?, 'FACILITY', ?, ?, ?, ?, 'WORLD_BACKED',
                        'WORLD_SQL', 'data/LOOM_2226.sqlite3',
                        'Identity and facility facts imported from authoritative WORLD runtime baseline')
                """,
                (object_id, object_id, name, parent, str(facility_type or "INFRASTRUCTURE")),
            )
            runtime.execute(
                """
                INSERT OR REPLACE INTO facility_world_bindings
                (object_id, world_entity_id, imported_name, imported_parent_body_id,
                 facility_type, system, traffic, civil_authority,
                 administrative_authority, security_authority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    object_id, object_id, name, parent, facility_type,
                    row["system"], row["traffic"], row["civil_authority"],
                    row["administrative_authority"], row["security_authority"],
                ),
            )
            runtime.execute(
                """
                INSERT OR REPLACE INTO geometry_assets
                (asset_id, object_id, geometry_role, status, provenance, navigation_authority)
                VALUES (?, ?, 'HUD_SYMBOLIC', 'WORLD_BACKED_PLACEHOLDER',
                        'Symbolic facility geometry until procedural/GLB asset is registered', 0)
                """,
                (f"HUDSYM:{object_id}", object_id),
            )
            runtime.execute(
                """
                INSERT OR REPLACE INTO visual_profiles
                (object_id, hero_media_entity_id, default_symbol, label_priority, status, notes)
                VALUES (?, ?, 'FACILITY', 50, 'WORLD_BACKED',
                        'hero_media_entity_id is the WORLD spatial entity key used by the MEDIA linkage')
                """,
                (object_id, object_id),
            )
        runtime.commit()
    finally:
        runtime.close()
    return out


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build LOOM Earth-Luna spatial geometry runtime SQLite")
    parser.add_argument("--world", default="data/LOOM_2226.sqlite3")
    parser.add_argument("--seed", default="geometry/earth_luna_spatial_geometry_seed.sql")
    parser.add_argument("--output", default="data/LOOM_2226_SPATIAL_GEOMETRY.sqlite3")
    args = parser.parse_args()
    out = build_earth_luna_geometry_db(args.world, args.seed, args.output)
    print(f"BUILT {out}")


if __name__ == "__main__":
    main()
