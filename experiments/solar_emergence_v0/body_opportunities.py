"""Corrective Run 1: read-only celestial registry audit and sparse opportunities."""

from __future__ import annotations

import ast
import base64
import hashlib
import importlib
import json
import math
import sqlite3
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD_DB = ROOT / "data" / "LOOM_2226.sqlite3"
PARAMETERS = HERE / "parameters.json"
RELEASE_MANIFEST = ROOT / "manifests" / "release_manifest.json"

# These classes come from SolarSceneStore.seed_reference_data and its entity
# taxonomy. They identify registered celestial objects, not facility hosts.
CELESTIAL_CLASSES = frozenset({
    "STAR", "PLANET", "SYSTEM_BARYCENTER", "DWARF_PLANET", "ASTEROID", "MOON",
})
UNKNOWN_FIELDS = (
    "radiation_environment", "thermal_environment", "solar_energy_potential",
    "water_potential", "volatile_potential", "bulk_material_potential", "metal_potential",
)
REGISTRY_RULE = (
    "entities.entity_class in the Solar scene celestial taxonomy AND "
    "(source_command is present OR STAR has HELIOCENTRIC_ORIGIN provenance); "
    "cross-check against Solar scene source registry; state rows are evidence, not membership"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_world_db(path: Path) -> sqlite3.Connection:
    path = Path(path).resolve(strict=True)
    conn = sqlite3.connect(f"{path.as_uri()}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _assignments(source: str) -> dict[str, ast.AST]:
    tree = ast.parse(source)
    return {
        target.id: node.value
        for node in tree.body if isinstance(node, ast.Assign)
        for target in node.targets if isinstance(target, ast.Name)
    }


def load_source_sets(root: Path) -> dict:
    """Read explicit checked-in registries as AST data; execute neither source."""
    root = Path(root)
    solar = _assignments((root / "src" / "loom_solar_gis.py").read_text(encoding="utf-8"))
    major = ast.literal_eval(solar["MAJOR_OBJECTS"])
    belt = ast.literal_eval(solar["BELT_OBJECTS"])
    moon_systems = ast.literal_eval(solar["MOON_SYSTEMS"])
    origin_literals = [n.value for n in ast.walk(solar["EXPECTED_IDS"])
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    if origin_literals != ["SOL"]:
        raise ValueError("Solar scene origin registration changed; review the registry rule")
    scene_records = {origin_literals[0]: {"name": "Sun", "body_class": "STAR", "parent_body_id": None}}
    for body_id, name, _, body_class in (*major, *belt):
        scene_records[body_id] = {"name": name, "body_class": body_class, "parent_body_id": "SOL"}
    for parent, system in moon_systems.items():
        for body_id, moon in system["moons"].items():
            scene_records[body_id] = {"name": moon["name"], "body_class": "MOON", "parent_body_id": parent}

    wrapper = _assignments((root / "src" / "loom_navigator_core.py").read_text(encoding="utf-8"))
    compressed = ast.literal_eval(wrapper["CORE_B64"])
    core = _assignments(zlib.decompress(base64.b64decode(compressed)).decode("utf-8"))
    routes = ast.literal_eval(core["ROUTE_OBJECTS"])
    base = ast.literal_eval(core["BASE_MAP_OBJECTS"])
    locals_ = ast.literal_eval(core["LOCAL_SYSTEMS"])
    token_to_entity = ast.literal_eval(wrapper["CIVSTATE_TOKEN_ENTITY"])
    base_to_entity = {}
    for token, route in routes.items():
        if route["kind"] == "base":
            body_id = token_to_entity[token]
            old = base_to_entity.setdefault(route["base_id"], body_id)
            if old != body_id:
                raise ValueError(f"Conflicting Navigator base identity: {route['base_id']}")
    acquisition = {base_to_entity.get(body_id, body_id) for body_id in base if body_id != "SOL"}
    acquisition.update(moon_id for system in locals_.values() for moon_id in system["moons"])
    return {
        "solar_scene_ids": set(scene_records),
        "solar_scene_records": scene_records,
        "solar_scene_acquisition_ids": set(scene_records) - {origin_literals[0]},
        "solar_scene_display_fallback_ids": {
            moon_id for system in moon_systems.values() for moon_id in system["moons"]
        },
        "navigator_target_ids": set(token_to_entity.values()),
        "navigator_acquisition_ids": acquisition,
        "navigator_base_ids": {base_to_entity.get(body_id, body_id) for body_id in base},
        "navigator_local_ids": {moon_id for system in locals_.values() for moon_id in system["moons"]},
    }


def _table_ids(conn: sqlite3.Connection, table: str) -> set[str]:
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone() is None:
        return set()
    return {row[0] for row in conn.execute(f"SELECT DISTINCT entity_id FROM {table}")}


def _candidate_role(body_class: str) -> str:
    if body_class == "STAR":
        return "REFERENCE_BODY"
    if body_class == "SYSTEM_BARYCENTER":
        return "SYSTEM_BARYCENTER"
    return "PHYSICAL_BODY"


def build_catalog(conn: sqlite3.Connection) -> list[dict]:
    """Use explicit entity registration; materialized states do not gate entry."""
    entities = conn.execute("""
        SELECT entity_id,name,entity_class,parent_entity_id,source_command,provenance
        FROM entities ORDER BY entity_id
    """).fetchall()
    ephemeris: dict[str, list[sqlite3.Row]] = {}
    for row in conn.execute("""
        SELECT entity_id,epoch_utc,source,ephemeris_status,navigation_grade
        FROM ephemeris_states ORDER BY entity_id,epoch_utc,source,ephemeris_status
    """):
        ephemeris.setdefault(row["entity_id"], []).append(row)
    direct_counts: dict[str, int] = {}
    for row in conn.execute("""
        SELECT entity_id,COUNT(*) AS n FROM states
        WHERE navigation_grade=1 AND reference_frame='J2000' AND reference_plane='ECLIPTIC'
        GROUP BY entity_id
    """):
        direct_counts[row["entity_id"]] = row["n"]
    catalog = []
    for row in entities:
        body_class = row["entity_class"]
        if body_class not in CELESTIAL_CLASSES:
            continue
        explicit = (row["source_command"] is not None or
                    (body_class == "STAR" and row["provenance"] == "HELIOCENTRIC_ORIGIN"))
        if not explicit:
            continue
        if body_class != "STAR" and not row["parent_entity_id"]:
            raise ValueError(f"Celestial registration lacks parent: {row['entity_id']}")
        body_id = row["entity_id"]
        states = ephemeris.get(body_id, [])
        latest = states[-1] if states else None
        catalog.append({
            "body_id": body_id,
            "name": row["name"],
            "body_class": body_class,
            "parent_body_id": row["parent_entity_id"],
            "candidate_role": _candidate_role(body_class),
            "registry_provenance": {
                "table": "entities", "entity_provenance": row["provenance"],
                "source_command": row["source_command"], "rule": REGISTRY_RULE,
            },
            "source_evidence": {
                "sqlite_entity": "data/LOOM_2226.sqlite3:entities.entity_id",
                "solar_scene": None,
            "direct_state": None,
            "propagation_model": None,
            "display_fallback": None,
            "solar_scene_acquisition": None,
            "navigator_acquisition": None,
            },
            "ephemeris_state_materialized": bool(states),
            "ephemeris": ({
                "state_count": len(states), "latest_epoch_utc": latest["epoch_utc"],
                "source": latest["source"], "status": latest["ephemeris_status"],
                "navigation_grade": bool(latest["navigation_grade"]),
            } if latest else None),
            "direct_state_capability": bool(direct_counts.get(body_id)),
            "direct_state_epoch_count": direct_counts.get(body_id, 0),
            "propagation_capability": None,
            "propagation_method": None,
            "display_fallback_capability": None,
            "acquisition_capability": None,
        })
    if len(catalog) != len({row["body_id"] for row in catalog}):
        raise ValueError("Duplicate registered body ID")
    return catalog


def _probe_propagation(catalog: list[dict], db_path: Path) -> None:
    """Ask the existing provider whether a genuine anchor yields an orbit model."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    provider = importlib.import_module("src.loom_sqlite_celestial_provider")
    current = provider.SQLiteCelestialCatalog(db_path)
    for row in catalog:
        epoch = row["ephemeris"]["latest_epoch_utc"] if row["ephemeris"] else "2226-08-29T05:00:00Z"
        try:
            current.orbit_model_from_direct_anchor(row["body_id"], epoch)
        except provider.SQLiteCelestialCatalogError:
            row["propagation_capability"] = False
        else:
            row["propagation_capability"] = True


def build_registry_audit(conn: sqlite3.Connection, source_sets: dict, catalog: list[dict] | None = None) -> dict:
    catalog = build_catalog(conn) if catalog is None else catalog
    by_id = {row["body_id"]: row for row in catalog}
    tables = {name: _table_ids(conn, name) for name in (
        "entities", "ephemeris_states", "states", "celestial_dynamics", "celestial_properties",
        "orbit_geometry_models", "orbit_snapshots", "spatial_states", "entity_location_models",
    )}
    scene = source_sets["solar_scene_ids"]
    ids = sorted(set(by_id) | scene | source_sets["navigator_target_ids"] |
                 source_sets["navigator_acquisition_ids"] | tables["ephemeris_states"] |
                 tables["celestial_dynamics"] | tables["celestial_properties"])
    conflicts = []
    scene_records = source_sets.get("solar_scene_records", {})
    for body_id in sorted(scene & set(by_id)):
        source = scene_records.get(body_id)
        if source:
            for field in ("name", "body_class", "parent_body_id"):
                if by_id[body_id][field] != source[field]:
                    conflicts.append({"body_id": body_id, "field": field,
                                      "sqlite": by_id[body_id][field], "solar_scene_source": source[field]})
    for row in conn.execute("SELECT entity_id,primary_gravity_parent_id FROM celestial_dynamics ORDER BY entity_id"):
        body_id = row["entity_id"]
        if body_id in by_id and row["primary_gravity_parent_id"] != by_id[body_id]["parent_body_id"]:
            conflicts.append({"body_id": body_id, "field": "parent_body_id",
                              "sqlite": by_id[body_id]["parent_body_id"],
                              "celestial_dynamics": row["primary_gravity_parent_id"]})
    ephemeris_columns = {row[1] for row in conn.execute("PRAGMA table_info(ephemeris_states)")}
    if "center_entity_id" in ephemeris_columns:
        for row in conn.execute("SELECT DISTINCT entity_id,center_entity_id FROM ephemeris_states ORDER BY entity_id,center_entity_id"):
            body_id = row["entity_id"]
            if body_id in by_id and row["center_entity_id"] != by_id[body_id]["parent_body_id"]:
                conflicts.append({"body_id": body_id, "field": "parent_body_id",
                                  "sqlite": by_id[body_id]["parent_body_id"],
                                  "ephemeris_center": row["center_entity_id"]})
    bodies = []
    for body_id in ids:
        body = by_id.get(body_id)
        flags = {f"present_in_{name}": body_id in values for name, values in tables.items()}
        bodies.append({
            "body_id": body_id,
            "name": body["name"] if body else None,
            "body_class": body["body_class"] if body else None,
            "parent_body_id": body["parent_body_id"] if body else None,
            **flags,
            "present_in_navigator_target_vocabulary": body_id in source_sets["navigator_target_ids"],
            "present_in_other_explicit_registry_sources": {
                "solar_scene_expected_ids": body_id in scene,
                "solar_scene_acquisition_commands": body_id in source_sets.get("solar_scene_acquisition_ids", set()),
                "solar_scene_display_fallback": body_id in source_sets.get("solar_scene_display_fallback_ids", set()),
                "navigator_acquisition_plan": body_id in source_sets["navigator_acquisition_ids"],
            },
            "ephemeris_state_materialized": body["ephemeris_state_materialized"] if body else body_id in tables["ephemeris_states"],
            "direct_state_capability": body["direct_state_capability"] if body else None,
            "propagation_capability": body["propagation_capability"] if body else None,
            "propagation_method": body["propagation_method"] if body else None,
            "display_fallback_capability": body["display_fallback_capability"] if body else None,
            "acquisition_capability": body["acquisition_capability"] if body else None,
            "registry_confidence": ("SQLITE_AND_SOLAR_SCENE" if body and body_id in scene else
                                    "SQLITE_EXPLICIT" if body else "UNRESOLVED_SOURCE_ONLY"),
            "proposed_registry_disposition": "INCLUDE" if body else "REVIEW_UNRESOLVED_NOT_INCLUDED",
            "evidence": {
                "identity": body["registry_provenance"] if body else None,
                "table_membership": {
                    name: f"data/LOOM_2226.sqlite3:{name}.entity_id"
                    for name, values in sorted(tables.items()) if body_id in values
                },
                "solar_scene": "src/loom_solar_gis.py:EXPECTED_IDS/seed_reference_data" if body_id in scene else None,
                "materialized_ephemeris": "data/LOOM_2226.sqlite3:ephemeris_states.entity_id" if body_id in tables["ephemeris_states"] else None,
                "direct_state": "src/loom_sqlite_celestial_provider.py:direct_state + qualified states row" if body and body["direct_state_capability"] else None,
                "propagation": (body["source_evidence"]["propagation_model"] or body["source_evidence"]["display_fallback"]) if body else None,
                "acquisition": {
                    "solar_scene": "src/loom_solar_gis.py:OBJECTS/MOON_OBJECTS provider requests" if body_id in source_sets.get("solar_scene_acquisition_ids", set()) else None,
                    "navigator": "src/loom_navigator_core.py:BASE_MAP_OBJECTS/LOCAL_SYSTEMS acquisition plan" if body_id in source_sets["navigator_acquisition_ids"] else None,
                },
            },
        })
    census_unlinked = []
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='body_zone_census'").fetchone():
        names = {r[0] for r in conn.execute("SELECT DISTINCT body_or_network FROM body_zone_census")}
        registered_names = {r["name"] for r in catalog}
        census_unlinked = sorted(names - registered_names)
    return {
        "schema": "loom-solar-emergence-v0-body-registry-audit-v1",
        "registry_rule": REGISTRY_RULE,
        "registry_boundary": "BOUNDED_EXPLICIT_SOLAR_SCENE_AND_SQLITE_ENTITY_REGISTRATION",
        "source_inventory": {
            "entities": "stable spatial/world identity registry; celestial classes and source commands establish candidate membership",
            "ephemeris_states": "materialized center-relative state cache; not registry",
            "states": "mixed celestial/infrastructure state cache; qualified direct states only at stored epochs",
            "celestial_dynamics": "orbit/gravity metadata for 48 registered non-origin bodies; not complete registry",
            "celestial_properties": "partial physical-reference data; not registry",
            "orbit_snapshots": "materialized heliocentric orbit geometry for 20 bodies; not registry",
            "orbit_geometry_models": "infrastructure geometry; not body registry",
            "spatial_states": "infrastructure state cache; not body registry",
            "entity_location_models": "infrastructure placement; not body registry",
            "solar_scene_expected_ids": "explicit 49-ID scene registration in src/loom_solar_gis.py",
            "solar_scene_acquisition_commands": "explicit Horizons request commands for 48 non-origin scene bodies",
            "solar_scene_display_fallback": "28 moon orbital radius/period records used only for approximate display fallback",
            "navigator_target_vocabulary": "11 mission destination identities; not complete body registry",
            "navigator_acquisition_plan": "10 base and 24 local acquisition requests; not complete body registry",
            "body_zone_census": "name-based 2226 worldbuilding/census rows without ephemeris IDs; not body registry",
            "sqlite_celestial_provider": "read-only direct-state and anchor-propagation capability, not registry",
        },
        "source_counts": {name: len(values) for name, values in sorted(tables.items())} | {
            "solar_scene_expected_ids": len(scene),
            "solar_scene_acquisition_commands": len(source_sets.get("solar_scene_acquisition_ids", set())),
            "solar_scene_display_fallback": len(source_sets.get("solar_scene_display_fallback_ids", set())),
            "navigator_target_vocabulary": len(source_sets["navigator_target_ids"]),
            "navigator_acquisition_plan": len(source_sets["navigator_acquisition_ids"]),
        },
        "unlinked_body_zone_names": census_unlinked,
        "unlinked_body_zone_note": "Name-only census/worldbuilding labels are not promoted to celestial IDs or ephemeris membership",
        "conflicts": conflicts,
        "bodies": bodies,
    }


def build_opportunities(catalog: list[dict], db_path: Path, parameters: dict) -> list[dict]:
    priors = parameters["body_class_test_priors"]
    with open_world_db(db_path) as conn:
        props = {row["entity_id"]: row for row in conn.execute(
            "SELECT entity_id,gm_km3_s2,mean_radius_km,source_id,status FROM celestial_properties")}
    result = []
    seen = set()
    for body in catalog:
        body_id = body["body_id"]
        if body_id in seen:
            raise ValueError(f"Duplicate body_id: {body_id}")
        seen.add(body_id)
        role = body["candidate_role"]
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
        if role == "PHYSICAL_BODY" and flags["surface_possible"] is True and physical is not None:
            gm, radius = physical["gm_km3_s2"], physical["mean_radius_km"]
            if (physical["status"] == parameters["gravity_source_status"]
                    and physical["source_id"] == parameters["gravity_source_id"]
                    and gm is not None and radius is not None
                    and math.isfinite(gm) and math.isfinite(radius)
                    and gm > 0 and radius > 0):
                gravity = 1000.0 * gm / (radius * radius)
                provenance["surface_gravity"] = {
                    "kind": "DERIVED_FROM_ENGINEERING_REFERENCE",
                    "source_table": "celestial_properties", "source_id": physical["source_id"],
                    "source_status": physical["status"], "gm_km3_s2": gm,
                    "mean_radius_km": radius,
                    "formula": "1000 * gm_km3_s2 / mean_radius_km**2", "unit": "m/s^2",
                }
        result.append({
            "body_id": body_id, "body_class": body_class, "candidate_role": role,
            **flags, "surface_gravity": gravity,
            **{field: None for field in UNKNOWN_FIELDS},
            "field_provenance": provenance,
        })
    return result


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def generate_bytes(db_path: Path, parameters: dict, *, source_sets: dict | None = None) -> tuple[bytes, bytes, bytes]:
    db_path = Path(db_path)
    source_sets = load_source_sets(ROOT) if source_sets is None else source_sets
    with open_world_db(db_path) as conn:
        catalog = build_catalog(conn)
    if db_path.resolve() == WORLD_DB.resolve():
        _probe_propagation(catalog, db_path)
    for row in catalog:
        body_id = row["body_id"]
        scene_acquisition = body_id in source_sets.get("solar_scene_acquisition_ids", set())
        display_fallback = body_id in source_sets.get("solar_scene_display_fallback_ids", set())
        navigator_acquisition = body_id in source_sets["navigator_acquisition_ids"]
        row["display_fallback_capability"] = display_fallback
        if row["propagation_capability"] is True:
            row["propagation_method"] = "PROVIDER_ANCHOR_MODEL"
        elif display_fallback:
            row["propagation_capability"] = True
            row["propagation_method"] = "SOLAR_SCENE_DISPLAY_FALLBACK"
        if scene_acquisition or navigator_acquisition:
            row["acquisition_capability"] = True
        evidence = row["source_evidence"]
        if body_id in source_sets["solar_scene_ids"]:
            evidence["solar_scene"] = "src/loom_solar_gis.py:EXPECTED_IDS/seed_reference_data"
        if row["direct_state_capability"]:
            evidence["direct_state"] = "src/loom_sqlite_celestial_provider.py:direct_state + qualified states row"
        if row["propagation_method"] == "PROVIDER_ANCHOR_MODEL":
            evidence["propagation_model"] = "src/loom_sqlite_celestial_provider.py:orbit_model_from_direct_anchor probe"
        if display_fallback:
            evidence["display_fallback"] = "src/loom_solar_gis.py:MOON_SYSTEMS/circular_local_fallback; display only"
        if scene_acquisition:
            evidence["solar_scene_acquisition"] = "src/loom_solar_gis.py:OBJECTS/MOON_OBJECTS provider requests"
        if navigator_acquisition:
            evidence["navigator_acquisition"] = "src/loom_navigator_core.py:BASE_MAP_OBJECTS/LOCAL_SYSTEMS acquisition plan"
    with open_world_db(db_path) as conn:
        audit = build_registry_audit(conn, source_sets, catalog)
    catalog_ids = {row["body_id"] for row in catalog}
    opportunity = build_opportunities(catalog, db_path, parameters)
    if source_sets["solar_scene_ids"] != catalog_ids or audit["conflicts"]:
        raise ValueError("Solar scene and SQLite celestial registry disagree; review before generation")
    if catalog_ids != {row["body_id"] for row in opportunity} or len(catalog) != len(opportunity):
        raise ValueError("Catalog and opportunity body IDs disagree")
    common = {
        "status": parameters["status"],
        "source_database": "data/LOOM_2226.sqlite3",
        "source_database_sha256": sha256(db_path),
        "baseline_main_sha": parameters["baseline_main_sha"],
        "registry_rule": REGISTRY_RULE,
        "body_count": len(catalog),
    }
    return (
        _json_bytes({**common, **audit}),
        _json_bytes({"schema": "loom-solar-emergence-v0-body-catalog-v2", **common,
                     "bodies": catalog}),
        _json_bytes({"schema": "loom-solar-emergence-v0-body-opportunities-v2", **common,
                     "opportunities": opportunity}),
    )


def main() -> int:
    parameters = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    actual = sha256(WORLD_DB)
    release = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
    registered = [item for item in release["artifacts"] if item["path"] == "data/LOOM_2226.sqlite3"]
    if len(registered) != 1 or actual != registered[0]["sha256"] or actual != parameters["world_db_sha256"]:
        raise ValueError("World DB hash does not match release authority and Run 1 parameters")
    audit, catalog, opportunity = generate_bytes(WORLD_DB, parameters)
    (HERE / "body_registry_audit.json").write_bytes(audit)
    (HERE / "body_catalog.json").write_bytes(catalog)
    (HERE / "body_opportunities.json").write_bytes(opportunity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
