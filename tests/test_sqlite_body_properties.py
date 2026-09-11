from pathlib import Path
import unittest

from loom.spatial.sqlite_body_properties import SQLiteBodyPropertyCatalog

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"


class SQLiteBodyPropertyCatalogTests(unittest.TestCase):
    def test_earth_and_moon_radius_and_gm_come_from_world_read_only(self):
        catalog = SQLiteBodyPropertyCatalog(WORLD)
        earth = catalog.get("EA")
        moon = catalog.get("LU")
        self.assertAlmostEqual(earth["radius_km"], 6371.0084, places=4)
        self.assertAlmostEqual(earth["mu_km3_s2"], 398600.4355, places=4)
        self.assertAlmostEqual(moon["radius_km"], 1737.4, places=4)
        self.assertAlmostEqual(moon["mu_km3_s2"], 4902.8001, places=4)
        self.assertIn("celestial_properties", earth["source"])
        self.assertIn("celestial_properties", moon["source"])

    def test_unknown_body_fails_closed(self):
        catalog = SQLiteBodyPropertyCatalog(WORLD)
        with self.assertRaises(Exception):
            catalog.get("NO-SUCH-BODY")


if __name__ == "__main__":
    unittest.main()
