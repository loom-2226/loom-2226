"""Run 1 only: read-only ephemeris catalog and sparse body opportunities."""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD_DB = ROOT / "data" / "LOOM_2226.sqlite3"
PARAMETERS = HERE / "parameters.json"
RELEASE_MANIFEST = ROOT / "manifests" / "release_manifest.json"
UNKNOWN_FIELDS = (
    "radiation_environment", "thermal_environment", "solar_energy_potential",
    "water_potential", "volatile_potential", "bulk_material_potential", "metal_potential",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_world_db(path: Path) -> sqlite3.Connection:
    """Connect to a closed, versioned SQLite file without write capability."""
    path = Path(path).resolve(strict=True)
    conn = sqlite3.connect(f"{path.as_uri()}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def build_catalog(conn: sqlite3.Connection) -> list[dict]:
    """Include each distinct ephemeris_states.entity_id once, regardless of grade."""
    rows = conn.execute("""
        SELECT p.entity_id, p.epoch_utc, p.source, p.ephemeris_status,
               p.navigation_grade, e.name, e.entity_class, e.parent_entity_id,
               e.provenance
        FROM ephemeris_states AS p
        LEFT JOIN entities AS e ON e.entity_id = p.entity_id
        ORDER BY p.entity_id, p.epoch_utc, p.source, p.ephemeris_status
    """).fetchall()
    grouped: dict[str, list[sqlite3.Row]] = {}
    for row in rows:
        body_id = row["entity_id"]
        if not body_id or row["name"] is None:
            raise ValueError(f"Ephemeris ID lacks a registered entity: {body_id!r}")
        grouped.setdefault(body_id, []).append(row)
    catalog = []
    for body_id, states in sorted(grouped.items()):
        latest = states[-1]
        catalog.append({
            "body_id": body_id,
            "name": latest["name"],
            "body_class": latest["entity_class"],
            "parent_body_id": latest["parent_entity_id"],
            "entity_provenance": latest["provenance"],
            "ephemeris": {
                "registry_table": "ephemeris_states",
                "registry_key": body_id,
                "state_count": len(states),
                "latest_epoch_utc": latest["epoch_utc"],
                "source": latest["source"],
                "status": latest["ephemeris_status"],
                "navigation_grade": bool(latest["navigation_grade"]),
            },
        })
    return catalog


def build_opportunities(catalog: list[dict], db_path: Path, parameters: dict) -> list[dict]:
    """Attach class test priors and one qualified formula; leave all else unknown."""
    priors = parameters["body_class_test_priors"]
    with open_world_db(db_path) as conn:
        props = {row["entity_id"]: row for row in conn.execute(
            "SELECT entity_id, gm_km3_s2, mean_radius_km, source_id, status FROM celestial_properties")}
    result = []
    seen = set()
    for body in catalog:
        body_id = body["body_id"]
        if body_id in seen:
            raise ValueError(f"Duplicate body_id: {body_id}")
        seen.add(body_id)
        body_class = body["body_class"]
        prior = priors.get(body_class, {})
        flags = {field: prior.get(field) for field in ("surface_possible", "orbital_possible")}
        provenance = {
            field: {"kind": "EXPERIMENTAL_CLASS_PRIOR", "body_class": body_class,
                    "source": "parameters.json:body_class_test_priors"}
            for field, value in flags.items() if value is not None
        }
        gravity = None
        physical = props.get(body_id)
        if flags["surface_possible"] is True and physical is not None:
            gm = physical["gm_km3_s2"]
            radius = physical["mean_radius_km"]
            if (physical["status"] == parameters["gravity_source_status"]
                    and physical["source_id"] == parameters["gravity_source_id"]
                    and gm is not None and radius is not None
                    and math.isfinite(gm) and math.isfinite(radius)
                    and gm > 0 and radius > 0):
                gravity = 1000.0 * gm / (radius * radius)
                provenance["surface_gravity"] = {
                    "kind": "DERIVED_FROM_ENGINEERING_REFERENCE",
                    "source_table": "celestial_properties",
                    "source_id": physical["source_id"],
                    "source_status": physical["status"],
                    "gm_km3_s2": gm,
                    "mean_radius_km": radius,
                    "formula": "1000 * gm_km3_s2 / mean_radius_km**2",
                    "unit": "m/s^2",
                }
        result.append({
            "body_id": body_id,
            "body_class": body_class,
            **flags,
            "surface_gravity": gravity,
            **{field: None for field in UNKNOWN_FIELDS},
            "field_provenance": provenance,
        })
    return result


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def generate_bytes(db_path: Path, parameters: dict) -> tuple[bytes, bytes]:
    with open_world_db(db_path) as conn:
        catalog = build_catalog(conn)
    opportunities = build_opportunities(catalog, db_path, parameters)
    catalog_ids = [row["body_id"] for row in catalog]
    opportunity_ids = [row["body_id"] for row in opportunities]
    if catalog_ids != opportunity_ids:
        raise ValueError("Catalog and opportunity body IDs disagree")
    common = {
        "status": parameters["status"],
        "source_database": "data/LOOM_2226.sqlite3",
        "source_database_sha256": sha256(db_path),
        "baseline_main_sha": parameters["baseline_main_sha"],
        "body_count": len(catalog),
    }
    return (
        _json_bytes({"schema": "loom-solar-emergence-v0-body-catalog-v1", **common,
                     "inclusion_rule": "distinct ephemeris_states.entity_id joined to entities; all navigation grades",
                     "bodies": catalog}),
        _json_bytes({"schema": "loom-solar-emergence-v0-body-opportunities-v1", **common,
                     "opportunities": opportunities}),
    )


def main() -> int:
    parameters = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    actual = sha256(WORLD_DB)
    release = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
    registered = [item for item in release["artifacts"] if item["path"] == "data/LOOM_2226.sqlite3"]
    if len(registered) != 1 or actual != registered[0]["sha256"] or actual != parameters["world_db_sha256"]:
        raise ValueError("World DB hash does not match current release authority and Run 1 parameters")
    catalog, opportunities = generate_bytes(WORLD_DB, parameters)
    (HERE / "body_catalog.json").write_bytes(catalog)
    (HERE / "body_opportunities.json").write_bytes(opportunities)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
