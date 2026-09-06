import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wayfarer_geometry import init_db, compile_geometry, write_geometry


class WayfarerGeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "wayfarer.sqlite3"
        self.seed = ROOT / "geometry" / "wayfarer_geometry_seed.sql"
        self.conn = init_db(self.db, self.seed)
        self.payload = compile_geometry(self.conn)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_canon_topology(self):
        components = self.payload["components"]
        self.assertEqual(sum(c["id"].startswith("tank_") for c in components), 4)
        self.assertEqual(sum(c["id"].startswith("longeron_") for c in components), 4)
        self.assertEqual(sum(c["id"].startswith("radiator_") for c in components), 4)
        nozzle = [c for c in components if c["id"] == "magnetic_nozzle"]
        self.assertEqual(len(nozzle), 1)
        self.assertEqual(nozzle[0]["dimensions"]["count"], 1)

    def test_length_and_nozzle_do_not_exceed_canon(self):
        p = self.payload["parameters"]
        self.assertEqual(p["ship.length_m"]["value"], 57.0)
        self.assertEqual(p["nozzle.x_end_m"]["value"], 57.0)

    def test_mass_ledger_closes(self):
        docked = self.payload["mass_states"]["DOCKED"]
        self.assertAlmostEqual(docked["dry_mass_t"], 858.5, places=6)
        self.assertAlmostEqual(docked["wet_mass_t"], 1158.5, places=6)
        self.assertAlmostEqual(docked["dry_com_m"][0], 27.99056494, places=6)
        self.assertAlmostEqual(docked["wet_com_m"][0], 26.67665084, places=6)
        self.assertAlmostEqual(docked["dry_com_m"][2], 33.0*5.2/858.5, places=6)

    def test_boundary_surrogate_is_inside_regression_tolerance(self):
        v = self.payload["validation"]
        self.assertTrue(v["normal_boundary_pass"])
        self.assertAlmostEqual(v["normal_boundary_proxy_m2"], 1821.55, delta=1.0)
        self.assertLess(abs(v["normal_boundary_delta_fraction"]), 0.10)

    def test_open_radiator_area_not_misused_as_physical_geometry(self):
        radiators = [c for c in self.payload["components"] if c["group"] == "radiators"]
        self.assertTrue(all(c["status"] == "OPEN" for c in radiators))
        self.assertEqual(self.payload["parameters"]["radiator.metric_hard_equiv_area_900k_m2"]["value"], 719.0)
        self.assertNotIn("total_physical_area_m2", radiators[0]["dimensions"])

    def test_json_regeneration_is_deterministic(self):
        a = Path(self.tmp.name) / "a.json"
        b = Path(self.tmp.name) / "b.json"
        write_geometry(self.conn, a)
        write_geometry(self.conn, b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        json.loads(a.read_text())


if __name__ == "__main__":
    unittest.main()
