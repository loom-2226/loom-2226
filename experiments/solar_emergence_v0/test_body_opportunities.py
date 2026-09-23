"""Corrective Run 1: celestial registration is not a state cache."""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from body_opportunities import (
    build_catalog, build_opportunities, build_registry_audit, generate_bytes,
    load_source_sets, open_world_db,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD_DB = ROOT / "data" / "LOOM_2226.sqlite3"
PARAMETERS = json.loads((HERE / "parameters.json").read_text(encoding="utf-8"))
FIXTURE_SOURCES = {
    "solar_scene_ids": {"SOL", "XY77", "AZ9", "BC4", "NOEPH"},
    "navigator_target_ids": set(),
    "navigator_acquisition_ids": set(),
}


def fixture_db(path):
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            CREATE TABLE entities(entity_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                entity_class TEXT NOT NULL, parent_entity_id TEXT,
                source_command TEXT, provenance TEXT NOT NULL);
            CREATE TABLE ephemeris_states(entity_id TEXT NOT NULL, epoch_utc TEXT NOT NULL,
                source TEXT NOT NULL, ephemeris_status TEXT NOT NULL,
                navigation_grade INTEGER NOT NULL);
            CREATE TABLE states(entity_id TEXT NOT NULL, epoch_utc TEXT NOT NULL,
                reference_frame TEXT NOT NULL, reference_plane TEXT NOT NULL,
                navigation_grade INTEGER NOT NULL);
            CREATE TABLE celestial_dynamics(entity_id TEXT PRIMARY KEY,
                primary_gravity_parent_id TEXT);
            CREATE TABLE celestial_properties(entity_id TEXT PRIMARY KEY,
                gm_km3_s2 REAL, mean_radius_km REAL, source_id TEXT, status TEXT);
        """)
        conn.executemany("INSERT INTO entities VALUES (?,?,?,?,?,?)", [
            ("SOL", "Sun", "STAR", None, None, "HELIOCENTRIC_ORIGIN"),
            ("XY77", "Fixture asteroid", "ASTEROID", "SOL", "771;", "TEST_REGISTRY"),
            ("AZ9", "Fixture moon", "MOON", "XY77", "778", "TEST_REGISTRY"),
            ("BC4", "Fixture barycenter", "SYSTEM_BARYCENTER", "SOL", "79", "TEST_REGISTRY"),
            ("NOEPH", "Unmaterialized body", "DWARF_PLANET", "SOL", "999;", "TEST_REGISTRY"),
            ("REGION", "Unrelated region", "REGION", "SOL", None, "TEST_REGION"),
        ])
        conn.executemany("INSERT INTO ephemeris_states VALUES (?,?,?,?,?)", [
            ("XY77", "2026-01-01T00:00:00Z", "DIRECT", "DIRECT", 1),
            ("XY77", "2226-01-01T00:00:00Z", "DIRECT", "DIRECT", 1),
            ("AZ9", "2226-01-01T00:00:00Z", "DISPLAY", "DISPLAY", 0),
            ("BC4", "2226-01-01T00:00:00Z", "DIRECT", "DIRECT", 1),
        ])
        conn.execute("INSERT INTO states VALUES (?,?,?,?,?)",
                     ("SOL", "2226-01-01T00:00:00Z", "J2000", "ECLIPTIC", 1))
        conn.executemany("INSERT INTO celestial_properties VALUES (?,?,?,?,?)", [
            ("XY77", 100.0, 10.0, "REFERENCE_PHYSICAL_CONSTANTS_v0.1", "ENGINEERING_REFERENCE_NONCANON"),
            ("AZ9", 100.0, 10.0, "UNQUALIFIED", "ENGINEERING_REFERENCE_NONCANON"),
            ("BC4", 100.0, 10.0, "REFERENCE_PHYSICAL_CONSTANTS_v0.1", "ENGINEERING_REFERENCE_NONCANON"),
            ("SOL", 100.0, 10.0, "REFERENCE_PHYSICAL_CONSTANTS_v0.1", "ENGINEERING_REFERENCE_NONCANON"),
        ])


class CorrectedRegistryTests(unittest.TestCase):
    def test_live_registry_not_cache_and_sol_present(self):
        with open_world_db(WORLD_DB) as conn:
            cache = {r[0] for r in conn.execute("SELECT DISTINCT entity_id FROM ephemeris_states")}
            catalog = build_catalog(conn)
        ids = [r["body_id"] for r in catalog]
        self.assertEqual(len(cache), 48)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids) - cache, {"SOL"})
        self.assertEqual(len(ids), 49)
        sun = next(r for r in catalog if r["body_id"] == "SOL")
        self.assertEqual(sun["candidate_role"], "REFERENCE_BODY")
        self.assertFalse(sun["ephemeris_state_materialized"])

    def test_all_explicit_solar_registry_and_materialized_ids_covered(self):
        sources = load_source_sets(ROOT)
        with open_world_db(WORLD_DB) as conn:
            catalog = build_catalog(conn)
            cache = {r[0] for r in conn.execute("SELECT DISTINCT entity_id FROM ephemeris_states")}
            dynamics = {r[0] for r in conn.execute("SELECT DISTINCT entity_id FROM celestial_dynamics")}
            properties = {r[0] for r in conn.execute("SELECT DISTINCT entity_id FROM celestial_properties")}
        ids = {r["body_id"] for r in catalog}
        self.assertEqual(ids, sources["solar_scene_ids"])
        self.assertTrue(cache <= ids)
        self.assertTrue(dynamics <= ids)
        self.assertTrue(properties <= ids)
        self.assertEqual(len(ids), len(catalog))

    def test_acquisition_and_display_fallback_are_distinct_capabilities(self):
        sources = load_source_sets(ROOT)
        self.assertEqual(len(sources["solar_scene_acquisition_ids"]), 48)
        self.assertEqual(len(sources["solar_scene_display_fallback_ids"]), 28)
        _, catalog_bytes, _ = generate_bytes(WORLD_DB, PARAMETERS, source_sets=sources)
        catalog = json.loads(catalog_bytes)["bodies"]
        by_id = {row["body_id"]: row for row in catalog}
        self.assertFalse(by_id["SOL"]["acquisition_capability"])
        self.assertEqual(sum(row["acquisition_capability"] is True for row in catalog), 48)
        self.assertEqual(sum(row["display_fallback_capability"] is True for row in catalog), 28)
        self.assertEqual(sum(row["propagation_method"] == "SOLAR_SCENE_DISPLAY_FALLBACK"
                             for row in catalog), 12)
        self.assertEqual(sum(row["propagation_method"] == "PROVIDER_ANCHOR_MODEL"
                             for row in catalog), 36)

    def test_arbitrary_nonmaterialized_fixture_and_reference_roles(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            with open_world_db(db) as conn:
                catalog = build_catalog(conn)
                audit = build_registry_audit(conn, FIXTURE_SOURCES)
            ids = [r["body_id"] for r in catalog]
            self.assertEqual(ids, ["AZ9", "BC4", "NOEPH", "SOL", "XY77"])
            self.assertEqual(len(ids), len(set(ids)))
            self.assertFalse(next(r for r in catalog if r["body_id"] == "NOEPH")["ephemeris_state_materialized"])
            self.assertEqual({r["body_id"] for r in audit["bodies"]}, set(ids))
            self.assertNotIn("REGION", ids)
            self.assertEqual(next(r for r in catalog if r["body_id"] == "BC4")["candidate_role"], "SYSTEM_BARYCENTER")

    def test_conflicting_dynamics_parent_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            with sqlite3.connect(db) as conn:
                conn.execute("INSERT INTO celestial_dynamics VALUES (?,?)", ("XY77", "AZ9"))
            with open_world_db(db) as conn:
                audit = build_registry_audit(conn, FIXTURE_SOURCES)
            self.assertEqual(audit["conflicts"], [{
                "body_id": "XY77", "field": "parent_body_id",
                "sqlite": "SOL", "celestial_dynamics": "AZ9",
            }])

    def test_opportunity_set_unknowns_and_gravity_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            with open_world_db(db) as conn:
                catalog = build_catalog(conn)
            rows = build_opportunities(catalog, db, PARAMETERS)
            self.assertEqual({r["body_id"] for r in rows}, {r["body_id"] for r in catalog})
            self.assertEqual(len(rows), len(catalog))
            by_id = {r["body_id"]: r for r in rows}
            self.assertAlmostEqual(by_id["XY77"]["surface_gravity"], 1000.0)
            for body_id in ("AZ9", "BC4", "SOL", "NOEPH"):
                self.assertIsNone(by_id[body_id]["surface_gravity"])
            for field in ("radiation_environment", "thermal_environment", "solar_energy_potential",
                          "water_potential", "volatile_potential", "bulk_material_potential", "metal_potential"):
                self.assertTrue(all(r[field] is None for r in rows), field)
            self.assertFalse(by_id["SOL"]["surface_possible"])
            self.assertFalse(by_id["BC4"]["surface_possible"])
            self.assertIsNone(by_id["BC4"]["orbital_possible"])
            self.assertEqual(by_id["AZ9"]["field_provenance"]["surface_possible"]["kind"], "EXPERIMENTAL_CLASS_PRIOR")

    def test_read_only_determinism_and_run_two_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            before = hashlib.sha256(db.read_bytes()).hexdigest()
            with open_world_db(db) as conn:
                self.assertEqual(conn.execute("PRAGMA query_only").fetchone()[0], 1)
                with self.assertRaises(sqlite3.OperationalError):
                    conn.execute("INSERT INTO entities VALUES ('BAD','Bad','MOON',NULL,'1','TEST')")
            first = generate_bytes(db, PARAMETERS, source_sets=FIXTURE_SOURCES)
            self.assertEqual(first, generate_bytes(db, PARAMETERS, source_sets=FIXTURE_SOURCES))
            self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), before)
        self.assertFalse((HERE / "route_accessibility.py").exists())
        self.assertFalse((HERE / "accessibility.json").exists())
        self.assertFalse(any("accessibility" in key for key in PARAMETERS))

    def test_checked_in_artifacts_reproduce(self):
        audit, catalog, opportunities = generate_bytes(WORLD_DB, PARAMETERS)
        self.assertEqual((HERE / "body_registry_audit.json").read_bytes(), audit)
        self.assertEqual((HERE / "body_catalog.json").read_bytes(), catalog)
        self.assertEqual((HERE / "body_opportunities.json").read_bytes(), opportunities)


if __name__ == "__main__":
    unittest.main()
