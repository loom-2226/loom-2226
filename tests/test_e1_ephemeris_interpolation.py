import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.loom_ephemeris_interpolation import EphemerisAnchor, hermite_state
from src.loom_sqlite_interpolated_celestial_provider import SQLiteInterpolatedCelestialResolver
from src.loom_sqlite_celestial_provider import AU_KM, DAY_S
from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError


class E1EphemerisInterpolationTests(unittest.TestCase):
    def test_hermite_linear_motion_is_exact(self):
        a = EphemerisAnchor("2226-08-22T00:00:00Z", (0.0, 0.0, 0.0), (1.0, 2.0, 3.0))
        b = EphemerisAnchor("2226-08-22T01:00:00Z", (3600.0, 7200.0, 10800.0), (1.0, 2.0, 3.0))
        p, v = hermite_state(a, b, "2226-08-22T00:30:00Z")
        self.assertEqual(tuple(round(x, 9) for x in p), (1800.0, 3600.0, 5400.0))
        self.assertEqual(tuple(round(x, 9) for x in v), (1.0, 2.0, 3.0))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "e1.sqlite3"
        conn = sqlite3.connect(self.db)
        conn.execute("""
            CREATE TABLE states(
              entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT,
              x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,
              source TEXT,navigation_grade INTEGER
            )
        """)
        # 1 km/s linear motion along x represented in AU/day.
        v = DAY_S / AU_KM
        conn.execute("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            "CERES", "2226-08-22T01:00:00Z", "J2000", "ECLIPTIC",
            0.0,0.0,0.0,v,0.0,0.0,"ANCHOR_A",1))
        conn.execute("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            "CERES", "2226-08-22T02:00:00Z", "J2000", "ECLIPTIC",
            3600.0/AU_KM,0.0,0.0,v,0.0,0.0,"ANCHOR_B",1))
        conn.execute("INSERT INTO states VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            "CERES", "2226-08-22T01:30:00Z", "J2000", "ECLIPTIC",
            999.0,0.0,0.0,0.0,0.0,0.0,"DISPLAY_ONLY",0))
        conn.commit(); conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_interpolated_state_uses_only_navigation_grade_brackets(self):
        state = SQLiteInterpolatedCelestialResolver(self.db).resolve("CERES", "2226-08-22T01:30:00Z")
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertAlmostEqual(state.position_km[0], 1800.0, places=6)
        self.assertAlmostEqual(state.velocity_km_s[0], 1.0, places=9)
        self.assertTrue(state.navigation_grade)
        self.assertEqual(state.provenance["state_source"], "INTERPOLATED_NAVIGATION_GRADE")
        self.assertEqual(state.provenance["interpolation_method"], "CUBIC_HERMITE_POSITION_VELOCITY")
        self.assertEqual(state.provenance["before_epoch_utc"], "2226-08-22T01:00:00Z")
        self.assertEqual(state.provenance["after_epoch_utc"], "2226-08-22T02:00:00Z")

    def test_exact_direct_state_is_preferred(self):
        state = SQLiteInterpolatedCelestialResolver(self.db).resolve("CERES", "2226-08-22T01:00:00Z")
        self.assertEqual(state.provenance["state_source"], "ANCHOR_A")
        self.assertEqual(state.provenance["qualification"], "DIRECT_NAVIGATION_GRADE")

    def test_outside_available_bracket_fails_closed(self):
        with self.assertRaises(CelestialStateError):
            SQLiteInterpolatedCelestialResolver(self.db).resolve("CERES", "2226-08-22T03:00:00Z")

    def test_missing_body_fails_closed(self):
        with self.assertRaises(CelestialStateError):
            SQLiteInterpolatedCelestialResolver(self.db).resolve("NEPTUNE", "2226-08-22T01:30:00Z")

    def test_microsecond_epoch_is_preserved(self):
        state = SQLiteInterpolatedCelestialResolver(self.db).resolve("CERES", "2226-08-22T01:30:00.500000Z")
        self.assertEqual(state.epoch_utc, "2226-08-22T01:30:00.500000Z")


if __name__ == "__main__":
    unittest.main()
