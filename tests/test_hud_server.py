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

    def test_earth_moon_page_is_responsive(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("@media(orientation:portrait)", text)
        self.assertIn("orientationchange", text)
        self.assertIn("window.addEventListener('resize'", text)

    def test_earth_moon_page_keeps_authority_boundary_visible(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("DERIVED / QUALIFICATION_ONLY", text)
        self.assertIn("NO NAV AUTHORITY", text)
        self.assertIn("FROZEN INERTIAL MIDPOINT", text)

    def test_earth_moon_page_exposes_verified_build_marker(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.6-earth-moon-2026"', text)
        self.assertIn("BUILD hud-v0.6-earth-moon-2026", text)

    def test_earth_moon_page_consumes_server_propagation(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("/earth-moon-qualification.json?epoch=2026-09-10T00:00:00Z&days=30", text)
        self.assertIn("moon_relative_to_observer_km", text)
        self.assertIn("moon_relative_velocity_km_s", text)
        self.assertIn("data.camera_basis", text)
        self.assertNotIn("propagate_parent_centric", text)

    def test_earth_moon_page_has_playback_controls(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('id="play"', text)
        self.assertIn('id="day" type="range"', text)
        self.assertIn("DAY ${idx}", text)

    def test_server_retains_live_endpoint_and_adds_qualification_endpoint(self):
        self.assertEqual(server.LIVE_ENDPOINT, "/flight-view.json")
        self.assertEqual(server.EARTH_MOON_ENDPOINT, "/earth-moon-qualification.json")


if __name__ == "__main__":
    unittest.main()
