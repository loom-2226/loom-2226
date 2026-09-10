import math
import sqlite3
import tempfile
import unittest
from pathlib import Path

from loom.hud.earth_moon_qualification import build_earth_moon_qualification
from loom.spatial.sqlite_celestial_catalog import AU_KM, DAY_S


class EarthMoonQualificationTests(unittest.TestCase):
    def _data_root(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        path = root / "LOOM_2226.sqlite3"
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
        mu = 398600.435507
        radius_km = 384400.0
        speed_km_s = math.sqrt(mu / radius_km)
        conn.execute(
            "INSERT INTO celestial_properties VALUES(?,?,?,?,?,?)",
            ("EA", mu, 6378.1, 86164.0, "TEST_CONSTANTS", "TEST"),
        )
        conn.execute(
            "INSERT INTO celestial_dynamics VALUES(?,?,?,?,?)",
            ("LU", "EA", "TEST_DYNAMICS", None, "TEST"),
        )
        conn.execute(
            "INSERT INTO ephemeris_states VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "LU", "2026-09-10T00:00:00Z", "EA", "399", "J2000", "ECLIPTIC", "AU / AU-day",
                radius_km / AU_KM, 0.0, 0.0,
                0.0, speed_km_s * DAY_S / AU_KM, 0.0,
                "JPL Horizons parent-centric vector", "JPL_HORIZONS_DIRECT", 1,
            ),
        )
        conn.commit()
        conn.close()
        return td, root, radius_km

    def test_observer_is_exact_midpoint_and_frozen(self):
        td, root, radius = self._data_root()
        self.addCleanup(td.cleanup)
        payload = build_earth_moon_qualification(data_root=root, days=3)
        observer = payload["observer"]["position_earth_centered_km"]
        self.assertAlmostEqual(observer[0], radius / 2.0, places=6)
        self.assertAlmostEqual(observer[1], 0.0, places=6)
        self.assertAlmostEqual(observer[2], 0.0, places=6)
        for sample in payload["samples"]:
            self.assertEqual(
                sample["earth_relative_to_observer_km"],
                [-observer[0], -observer[1], -observer[2]],
            )

    def test_moon_moves_across_fixed_camera(self):
        td, root, _ = self._data_root()
        self.addCleanup(td.cleanup)
        payload = build_earth_moon_qualification(data_root=root, days=5)
        forward = payload["camera_basis"]["forward"]
        right = payload["camera_basis"]["right"]

        def bearing(sample):
            v = sample["moon_relative_to_observer_km"]
            f = sum(v[i] * forward[i] for i in range(3))
            r = sum(v[i] * right[i] for i in range(3))
            return math.degrees(math.atan2(r, f))

        self.assertAlmostEqual(bearing(payload["samples"][0]), 0.0, places=9)
        self.assertGreater(abs(bearing(payload["samples"][5])), 1.0)

    def test_authority_stays_qualification_only(self):
        td, root, _ = self._data_root()
        self.addCleanup(td.cleanup)
        payload = build_earth_moon_qualification(data_root=root, days=1)
        self.assertEqual(payload["status"], "QUALIFICATION_ONLY")
        self.assertFalse(payload["navigation_grade"])
        self.assertEqual(payload["moon_model"]["provenance"]["anchor_navigation_grade"], True)
        self.assertEqual(payload["source"]["data_access"], "READ_ONLY")

    def test_non_2026_epoch_is_rejected(self):
        td, root, _ = self._data_root()
        self.addCleanup(td.cleanup)
        with self.assertRaisesRegex(ValueError, "must be in 2026"):
            build_earth_moon_qualification(epoch_utc="2027-01-01T00:00:00Z", data_root=root)


if __name__ == "__main__":
    unittest.main()
