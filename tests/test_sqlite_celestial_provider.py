import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.loom_sqlite_celestial_provider import AU_KM, DAY_S, SQLiteCelestialCatalog
from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError


class SQLiteCelestialProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "celestial.sqlite3"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            """
            CREATE TABLE states(
              entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT,
              x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,
              source TEXT,navigation_grade INTEGER
            );
            CREATE TABLE celestial_properties(entity_id TEXT, gm_km3_s2 REAL, source_id TEXT, status TEXT);
            CREATE TABLE celestial_dynamics(entity_id TEXT, primary_gravity_parent_id TEXT, gm_km3_s2 REAL, source TEXT, metadata_status TEXT);
            CREATE TABLE ephemeris_states(
              entity_id TEXT, center_entity_id TEXT, reference_frame TEXT, reference_plane TEXT,
              navigation_grade INTEGER, epoch_utc TEXT, units TEXT,
              x REAL,y REAL,z REAL,vx REAL,vy REAL,vz REAL,source TEXT,ephemeris_status TEXT
            );
            """
        )
        for epoch in ("2226-08-22T00:00:00Z", "2226-08-22T01:00:00Z"):
            conn.execute("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
                "EARTH", epoch, "J2000", "ECLIPTIC",
                1.0,2.0,3.0,0.1,0.2,0.3,"TEST_DIRECT",1))
        conn.execute("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            "DISPLAY", "2226-08-22T00:00:00Z", "J2000", "ECLIPTIC",
            9.0,9.0,9.0,0,0,0,"DISPLAY_ONLY",0))
        conn.execute("INSERT INTO celestial_properties VALUES (?,?,?,?)", ("EARTH",398600.4418,"TEST","QUALIFIED"))
        conn.execute("INSERT INTO celestial_dynamics VALUES (?,?,?,?,?)", ("MOON","EARTH",None,"TEST_DYN","QUALIFIED"))
        # A simple bound parent-centric Moon anchor, stored in AU / AU-day.
        r_au = 384400.0 / AU_KM
        v_au_d = 1.018 * DAY_S / AU_KM
        conn.execute("INSERT INTO ephemeris_states VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            "MOON","EARTH","J2000","ECLIPTIC",1,"2226-08-22T00:00:00Z","AU/AU-DAY",
            r_au,0,0,0,v_au_d,0,"TEST_ANCHOR","QUALIFIED"))
        conn.commit(); conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_direct_navigation_grade_state_is_resolved_and_converted(self):
        state = SQLiteCelestialCatalog(self.db).direct_state("EARTH", "2226-08-22T00:00:00Z")
        self.assertIsNotNone(state)
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertAlmostEqual(state.position_km[0], AU_KM)
        self.assertAlmostEqual(state.velocity_km_s[0], 0.1 * AU_KM / DAY_S)
        self.assertTrue(state.navigation_grade)

    def test_display_only_state_is_never_promoted(self):
        self.assertIsNone(SQLiteCelestialCatalog(self.db).direct_state("DISPLAY", "2226-08-22T00:00:00Z"))

    def test_read_only_provider_does_not_mutate_database(self):
        cat = SQLiteCelestialCatalog(self.db)
        cat.direct_state("EARTH", "2226-08-22T00:00:00Z")
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM states").fetchone()[0], 3)

    def test_service_propagates_child_from_genuine_anchor_but_not_navigation_grade(self):
        service = SQLiteCelestialCatalog(self.db).build_service(["EARTH","MOON"], "2226-08-22T01:00:00Z")
        moon = service.resolve("MOON", "2226-08-22T01:00:00Z")
        self.assertFalse(moon.navigation_grade)
        self.assertEqual(moon.provenance["parent_entity_id"], "EARTH")
        self.assertEqual(moon.reference_frame, CANONICAL_FRAME)

    def test_missing_genuine_anchor_fails_closed(self):
        cat = SQLiteCelestialCatalog(self.db)
        with self.assertRaises(CelestialStateError):
            cat.orbit_model_from_direct_anchor("NOPE", "2226-08-22T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
