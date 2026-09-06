import math
import sqlite3
import tempfile
import unittest
from pathlib import Path

from loom.spatial.gravity import GravitySource, evaluate_gravity
from loom.spatial.sqlite_celestial_catalog import AU_KM, DAY_S, SQLiteCelestialCatalog


class D2CCelestialGravityFunctionalTest(unittest.TestCase):
    def test_propagated_moon_state_feeds_shared_gravity_engine(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "core.sqlite3"
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
            earth_mu = 398600.435507
            moon_mu = 4902.800118
            earth_position_km = (AU_KM, 0.0, 0.0)
            conn.execute(
                "INSERT INTO states VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                ("EA", epoch, "J2000", "ECLIPTIC", 1.0, 0.0, 0.0, 0.0, 0.01720209895, 0.0, "DIRECT_EARTH", 1),
            )
            conn.execute(
                "INSERT INTO celestial_properties VALUES(?,?,?,?,?,?)",
                ("EA", earth_mu, 6378.1, 86164.0, "TEST", "TEST"),
            )
            conn.execute(
                "INSERT INTO celestial_properties VALUES(?,?,?,?,?,?)",
                ("LU", moon_mu, 1737.4, 2360591.0, "TEST", "TEST"),
            )
            conn.execute(
                "INSERT INTO celestial_dynamics VALUES(?,?,?,?,?)",
                ("LU", "EA", "TEST_DYNAMICS", moon_mu, "TEST"),
            )
            radius = 384400.0
            speed = math.sqrt(earth_mu / radius)
            conn.execute(
                "INSERT INTO ephemeris_states VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "LU", "2200-01-01T00:00:00Z", "EA", "399", "J2000", "ECLIPTIC", "AU / AU-day",
                    radius / AU_KM, 0.0, 0.0, 0.0, speed * DAY_S / AU_KM, 0.0,
                    "JPL Horizons parent-centric vector", "JPL_HORIZONS_DIRECT", 1,
                ),
            )
            conn.commit()
            conn.close()

            catalog = SQLiteCelestialCatalog(path)
            service = catalog.build_service(("EA", "LU"), epoch)
            earth = service.resolve("EA", epoch)
            moon = service.resolve("LU", epoch)

            source_earth = GravitySource("EA", earth, earth_mu, provenance={"source": "TEST"})
            source_moon = GravitySource("LU", moon, moon_mu, provenance={"source": "TEST"})
            ship = (
                earth_position_km[0] + 450000.0,
                earth_position_km[1] + 150000.0,
                0.0,
            )
            field = evaluate_gravity(ship, (source_earth, source_moon), epoch_utc=epoch)

            ids = {c.entity_id for c in field.contributions}
            self.assertEqual(ids, {"EA", "LU"})
            self.assertFalse(moon.navigation_grade)
            self.assertEqual(moon.provenance["state_source"], "PROPAGATED_PARENT_CENTRIC_KEPLER")
            moon_contribution = next(c for c in field.contributions if c.entity_id == "LU")
            self.assertFalse(moon_contribution.navigation_grade_state)
            self.assertGreater(moon_contribution.magnitude_km_s2, 0.0)
            self.assertTrue(all(math.isfinite(v) for v in field.total_acceleration_km_s2))


if __name__ == "__main__":
    unittest.main()
