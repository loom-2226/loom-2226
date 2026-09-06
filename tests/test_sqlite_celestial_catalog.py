import math
import sqlite3
import tempfile
import unittest
from pathlib import Path

from loom.spatial.sqlite_celestial_catalog import (
    AU_KM,
    DAY_S,
    SQLiteCelestialCatalog,
    SQLiteCelestialCatalogError,
    osculating_elements_from_state,
)


class OsculatingElementTests(unittest.TestCase):
    def test_recovers_circular_equatorial_orbit(self):
        mu = 398600.435507
        radius = 7000.0
        speed = math.sqrt(mu / radius)
        elements = osculating_elements_from_state((radius, 0.0, 0.0), (0.0, speed, 0.0), mu)
        self.assertAlmostEqual(elements["semi_major_axis_km"], radius, places=6)
        self.assertLess(elements["eccentricity"], 1e-12)
        self.assertAlmostEqual(elements["inclination_deg"], 0.0, places=10)
        self.assertAlmostEqual(elements["mean_anomaly_deg"], 0.0, places=10)


class SQLiteCelestialCatalogTests(unittest.TestCase):
    def _db(self, *, nav_anchor=True):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "core.sqlite3"
        conn = sqlite3.connect(path)
        conn.executescript(
            """
            CREATE TABLE states(
              entity_id TEXT, epoch_utc TEXT, reference_frame TEXT, reference_plane TEXT,
              x_au REAL,y_au REAL,z_au REAL,vx_au_d REAL,vy_au_d REAL,vz_au_d REAL,
              source TEXT,navigation_grade INTEGER
            );
            CREATE TABLE celestial_properties(
              entity_id TEXT PRIMARY KEY,gm_km3_s2 REAL,mean_radius_km REAL,
              rotation_period_s REAL,source_id TEXT,status TEXT
            );
            CREATE TABLE celestial_dynamics(
              entity_id TEXT PRIMARY KEY,primary_gravity_parent_id TEXT,source TEXT,
              gm_km3_s2 REAL,metadata_status TEXT
            );
            CREATE TABLE ephemeris_states(
              entity_id TEXT,epoch_utc TEXT,center_entity_id TEXT,center_command TEXT,
              reference_frame TEXT,reference_plane TEXT,units TEXT,
              x REAL,y REAL,z REAL,vx REAL,vy REAL,vz REAL,
              source TEXT,ephemeris_status TEXT,navigation_grade INTEGER
            );
            """
        )
        epoch = "2226-06-15T10:00:00Z"
        conn.execute(
            "INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            ("EA", epoch, "J2000", "ECLIPTIC", 1.0, 0.0, 0.0, 0.0, 0.01720209895, 0.0, "DIRECT_PARENT", 1),
        )
        mu = 398600.435507
        conn.execute(
            "INSERT INTO celestial_properties VALUES(?,?,?,?,?,?)",
            ("EA", mu, 6378.1, 86164.0, "TEST_CONSTANTS", "TEST"),
        )
        conn.execute(
            "INSERT INTO celestial_dynamics VALUES(?,?,?,?,?)",
            ("LU", "EA", "TEST_DYNAMICS", None, "TEST"),
        )
        radius_km = 384400.0
        speed_km_s = math.sqrt(mu / radius_km)
        conn.execute(
            "INSERT INTO ephemeris_states VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "LU", "2200-01-01T00:00:00Z", "EA", "399", "J2000", "ECLIPTIC", "AU / AU-day",
                radius_km / AU_KM, 0.0, 0.0, 0.0, speed_km_s * DAY_S / AU_KM, 0.0,
                "JPL Horizons parent-centric vector", "JPL_HORIZONS_DIRECT" if nav_anchor else "APPROX_PERIOD_DISPLAY",
                1 if nav_anchor else 0,
            ),
        )
        conn.commit()
        conn.close()
        return td, path, epoch, radius_km

    def test_builds_propagated_moon_from_genuine_direct_anchor(self):
        td, path, epoch, radius_km = self._db(nav_anchor=True)
        self.addCleanup(td.cleanup)
        catalog = SQLiteCelestialCatalog(path)
        service = catalog.build_service(("EA", "LU"), epoch)
        earth = service.resolve("EA", epoch)
        moon = service.resolve("LU", epoch)
        self.assertTrue(earth.navigation_grade)
        self.assertFalse(moon.navigation_grade)
        self.assertEqual(moon.provenance["state_source"], "PROPAGATED_PARENT_CENTRIC_KEPLER")
        self.assertEqual(moon.provenance["parent_entity_id"], "EA")
        self.assertTrue(moon.provenance["model_provenance"]["anchor_navigation_grade"])
        separation = math.sqrt(sum((moon.position_km[i] - earth.position_km[i]) ** 2 for i in range(3)))
        self.assertAlmostEqual(separation, radius_km, delta=2.0)
        self.assertGreater(moon.uncertainty["anchor_age_days"], 9000.0)

    def test_display_only_anchor_is_never_promoted_to_physics(self):
        td, path, epoch, _ = self._db(nav_anchor=False)
        self.addCleanup(td.cleanup)
        catalog = SQLiteCelestialCatalog(path)
        with self.assertRaises(SQLiteCelestialCatalogError):
            catalog.orbit_model_from_direct_anchor("LU", epoch)
        service = catalog.build_service(("EA", "LU"), epoch)
        with self.assertRaises(Exception):
            service.resolve("LU", epoch)


if __name__ == "__main__":
    unittest.main()
