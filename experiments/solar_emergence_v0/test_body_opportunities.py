"""Run 1 contract tests for the read-only Solar body opportunity export."""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from body_opportunities import build_catalog, build_opportunities, generate_bytes, open_world_db


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORLD_DB = ROOT / "data" / "LOOM_2226.sqlite3"
PARAMETERS = json.loads((HERE / "parameters.json").read_text(encoding="utf-8"))


def fixture_db(path):
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            CREATE TABLE entities(entity_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                entity_class TEXT NOT NULL, parent_entity_id TEXT, provenance TEXT NOT NULL);
            CREATE TABLE ephemeris_states(entity_id TEXT NOT NULL, epoch_utc TEXT NOT NULL,
                source TEXT NOT NULL, ephemeris_status TEXT NOT NULL,
                navigation_grade INTEGER NOT NULL);
            CREATE TABLE celestial_properties(entity_id TEXT PRIMARY KEY,
                gm_km3_s2 REAL, mean_radius_km REAL, source_id TEXT, status TEXT);
        """)
        conn.executemany("INSERT INTO entities VALUES (?,?,?,?,?)", [
            ("XY77", "Fixture asteroid", "ASTEROID", "SOL", "FIXTURE"),
            ("AZ9", "Fixture moon", "MOON", "XY77", "FIXTURE"),
            ("BC4", "Fixture barycenter", "SYSTEM_BARYCENTER", "SOL", "FIXTURE"),
            ("NOEPH", "No ephemeris", "PLANET", "SOL", "FIXTURE"),
        ])
        conn.executemany("INSERT INTO ephemeris_states VALUES (?,?,?,?,?)", [
            ("XY77", "2026-01-01T00:00:00Z", "FIXTURE_DIRECT", "DIRECT", 1),
            ("XY77", "2226-01-01T00:00:00Z", "FIXTURE_DIRECT", "DIRECT", 1),
            ("AZ9", "2226-01-01T00:00:00Z", "FIXTURE_DISPLAY", "DISPLAY", 0),
            ("BC4", "2226-01-01T00:00:00Z", "FIXTURE_DIRECT", "DIRECT", 1),
        ])
        conn.execute("INSERT INTO celestial_properties VALUES (?,?,?,?,?)",
                     ("XY77", 100.0, 10.0, "REFERENCE_PHYSICAL_CONSTANTS_v0.1", "ENGINEERING_REFERENCE_NONCANON"))


class BodyOpportunityTests(unittest.TestCase):
    def test_current_catalog_equals_complete_ephemeris_register(self):
        with open_world_db(WORLD_DB) as conn:
            expected = {row[0] for row in conn.execute(
                "SELECT DISTINCT entity_id FROM ephemeris_states")}
            catalog = build_catalog(conn)
        actual = [row["body_id"] for row in catalog]
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), 48)
        self.assertEqual(len({row["body_id"] for row in build_opportunities(catalog, WORLD_DB, PARAMETERS)}), 48)

    def test_arbitrary_registered_fixture_bodies_and_display_rows_are_included(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            with open_world_db(db) as conn:
                catalog = build_catalog(conn)
            self.assertEqual([row["body_id"] for row in catalog], ["AZ9", "BC4", "XY77"])
            self.assertEqual(len(catalog), 3)
            self.assertEqual(catalog[0]["ephemeris"]["navigation_grade"], False)
            self.assertEqual(catalog[2]["ephemeris"]["state_count"], 2)
            opportunities = build_opportunities(catalog, db, PARAMETERS)
            self.assertEqual({r["body_id"] for r in opportunities}, {"AZ9", "BC4", "XY77"})
            self.assertAlmostEqual(next(r for r in opportunities if r["body_id"] == "XY77")["surface_gravity"], 1000.0)
            self.assertIsNone(next(r for r in opportunities if r["body_id"] == "BC4")["surface_gravity"])

    def test_unknowns_remain_null_and_priors_are_marked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            with open_world_db(db) as conn:
                rows = build_opportunities(build_catalog(conn), db, PARAMETERS)
            moon = next(r for r in rows if r["body_id"] == "AZ9")
            for field in ("surface_gravity", "radiation_environment", "thermal_environment",
                          "solar_energy_potential", "water_potential", "volatile_potential",
                          "bulk_material_potential", "metal_potential"):
                self.assertIsNone(moon[field], field)
            self.assertEqual(moon["field_provenance"]["surface_possible"]["kind"], "EXPERIMENTAL_CLASS_PRIOR")
            self.assertEqual(moon["field_provenance"]["orbital_possible"]["kind"], "EXPERIMENTAL_CLASS_PRIOR")

    def test_database_connection_is_read_only_and_generation_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "fixture.sqlite3"
            fixture_db(db)
            before = hashlib.sha256(db.read_bytes()).hexdigest()
            with open_world_db(db) as conn:
                self.assertEqual(conn.execute("PRAGMA query_only").fetchone()[0], 1)
                with self.assertRaises(sqlite3.OperationalError):
                    conn.execute("INSERT INTO entities VALUES ('BAD','Bad','MOON',NULL,'TEST')")
            first = generate_bytes(db, PARAMETERS)
            second = generate_bytes(db, PARAMETERS)
            self.assertEqual(first, second)
            self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(), before)

    def test_checked_in_artifacts_match_current_database_and_parameters(self):
        catalog, opportunities = generate_bytes(WORLD_DB, PARAMETERS)
        self.assertEqual((HERE / "body_catalog.json").read_bytes(), catalog)
        self.assertEqual((HERE / "body_opportunities.json").read_bytes(), opportunities)

    def test_run_two_accessibility_is_absent(self):
        self.assertFalse((HERE / "route_accessibility.py").exists())
        self.assertFalse((HERE / "accessibility.json").exists())
        self.assertFalse(any("accessibility" in row for row in PARAMETERS))


if __name__ == "__main__":
    unittest.main()
