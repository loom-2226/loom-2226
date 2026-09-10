import tempfile
import unittest
from pathlib import Path

from loom.hud import server


class HudServerTests(unittest.TestCase):
    def test_checked_in_default_qualification_page_exists(self):
        page = server.validate_assets()
        self.assertTrue(page.is_file())
        self.assertEqual(page.name, "earth_moon_qualification.html")

    def test_missing_demo_page_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                server.validate_assets(Path(tmp))

    def test_default_port_is_valid(self):
        self.assertGreaterEqual(server.DEFAULT_PORT, 1)
        self.assertLessEqual(server.DEFAULT_PORT, 65535)

    def test_realtime_page_is_responsive(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("@media(orientation:portrait)", text)
        self.assertIn("orientationchange", text)
        self.assertIn("window.addEventListener('resize'", text)

    def test_realtime_page_keeps_authority_boundary_visible(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("QUALIFICATION_ONLY", text)
        self.assertIn("CAMPAIGN WRITE NONE", text)
        self.assertIn("ATTITUDE FIXED / NO ROTATION", text)
        self.assertIn("NOT SPICE-qualified", text)

    def test_realtime_page_exposes_verified_build_marker(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.8-realtime-3d"', text)
        self.assertIn("BUILD hud-v0.8-realtime-3d", text)

    def test_realtime_page_uses_python_state_not_browser_ephemeris(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("/qualification-flight.json", text)
        self.assertIn("/qualification-flight/control", text)
        self.assertNotIn("propagate_parent_centric", text)
        self.assertNotIn("hermite_state", text)
        self.assertNotIn("G0_M_S2", text)

    def test_realtime_page_loads_scaled_nasa_moon_and_wayfarer(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("Moon_NASA_LRO_8k_Topo_Small.glb", text)
        self.assertIn("1737.4/sphere.radius", text)
        self.assertIn("/wayfarer-geometry.json", text)
        self.assertIn("0.057 km", text)
        self.assertIn("logarithmicDepthBuffer:true", text)

    def test_realtime_page_exposes_time_and_torch_controls(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        for rate in ("0", "1", "10", "100", "1000", "10000"):
            self.assertIn(f'data-rate="{rate}"', text)
        for mode in ("ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"):
            self.assertIn(mode, text)
        self.assertIn('id="burn"', text)
        self.assertIn('id="reset"', text)

    def test_server_retains_prior_endpoints_and_adds_realtime_endpoints(self):
        self.assertEqual(server.LIVE_ENDPOINT, "/flight-view.json")
        self.assertEqual(server.EARTH_MOON_ENDPOINT, "/earth-moon-qualification.json")
        self.assertEqual(server.REALTIME_ENDPOINT, "/qualification-flight.json")
        self.assertEqual(server.CONTROL_ENDPOINT, "/qualification-flight/control")
        self.assertEqual(server.WAYFARER_GEOMETRY_ENDPOINT, "/wayfarer-geometry.json")


if __name__ == "__main__":
    unittest.main()
