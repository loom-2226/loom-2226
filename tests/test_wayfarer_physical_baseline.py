import tempfile
import unittest
from pathlib import Path

from wayfarer_geometry import init_db, compile_geometry
from loom.wayfarer_physical_baseline import (
    BaselineStatus,
    WAYFARER_PHYSICAL_BASELINE_VERSION,
    WayfarerBaselineError,
    baseline_from_geometry_payload,
)


class WayfarerPhysicalBaselineTests(unittest.TestCase):
    def _baseline(self):
        root = Path(__file__).resolve().parents[1]
        seed = root / "geometry" / "wayfarer_geometry_seed.sql"
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        conn = init_db(Path(td.name) / "wayfarer.sqlite3", seed)
        self.addCleanup(conn.close)
        payload = compile_geometry(conn)
        return baseline_from_geometry_payload(payload), payload

    def test_contract_version(self):
        self.assertEqual(WAYFARER_PHYSICAL_BASELINE_VERSION, "LOOM_F_PB_WAYFARER_PHYSICAL_BASELINE_V1")

    def test_live_geometry_compiler_is_dimensional_source(self):
        baseline, payload = self._baseline()
        self.assertEqual(payload["schema"], "LOOM.Wayfarer.Geometry")
        self.assertAlmostEqual(baseline.length_m.value, 57.0)
        self.assertAlmostEqual(baseline.main_body_diameter_m.value, 9.0)
        self.assertEqual(baseline.length_m.status, BaselineStatus.CANON)
        self.assertEqual(baseline.main_body_diameter_m.status, BaselineStatus.CANON)

    def test_body_frame_preserves_existing_ship_coordinate_convention(self):
        baseline, _ = self._baseline()
        self.assertEqual(baseline.body_frame.frame_id, "WAYFARER_BODY")
        self.assertIn("bow datum x=0 m", baseline.body_frame.x_axis_description)
        self.assertIn("+Z launch-bay side", baseline.body_frame.z_axis_description)
        self.assertIn("-Z docking side", baseline.body_frame.z_axis_description)
        self.assertGreater(baseline.launch_bay_center_m[2], 0.0)
        self.assertLess(baseline.docking_collar_center_m[2], 0.0)

    def test_open_docking_geometry_is_not_promoted(self):
        baseline, _ = self._baseline()
        self.assertEqual(baseline.docking_geometry_status, BaselineStatus.OPEN)
        self.assertEqual(baseline.launch_geometry_status, BaselineStatus.DESIGN_BASELINE)

    def test_mass_states_preserve_configuration_dependence(self):
        baseline, _ = self._baseline()
        self.assertGreater(baseline.docked_mass.dry_mass_t, baseline.launch_absent_mass.dry_mass_t)
        self.assertGreater(baseline.docked_mass.wet_mass_t, baseline.launch_absent_mass.wet_mass_t)
        self.assertNotEqual(baseline.docked_mass.dry_com_m, baseline.launch_absent_mass.dry_com_m)
        self.assertNotEqual(baseline.docked_mass.wet_com_m, baseline.launch_absent_mass.wet_com_m)

    def test_configuration_vocabularies_are_reused_not_reinvented(self):
        baseline, _ = self._baseline()
        self.assertEqual(baseline.launch_states, ("DOCKED", "EXTRACTING", "ABSENT"))
        self.assertEqual(baseline.radiator_states, ("STOWED", "DEPLOYING", "DEPLOYED"))
        self.assertEqual(baseline.docking_states, ("FREE", "APPROACH", "SOFT_CAPTURE", "HARD_DOCKED"))
        self.assertEqual(baseline.torch_states, ("OFF", "SAFE", "ACTIVE"))

    def test_frame_drift_fails_closed(self):
        _, payload = self._baseline()
        payload = dict(payload)
        payload["coordinate_system"] = dict(payload["coordinate_system"])
        payload["coordinate_system"]["z"] = "arbitrary renderer axis"
        with self.assertRaises(WayfarerBaselineError):
            baseline_from_geometry_payload(payload)


if __name__ == "__main__":
    unittest.main()
