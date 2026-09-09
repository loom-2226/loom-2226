import tempfile
import unittest
from pathlib import Path

from loom.hud import server


class HudServerTests(unittest.TestCase):
    def test_checked_in_demo_page_exists(self):
        page = server.validate_assets()
        self.assertTrue(page.is_file())
        self.assertEqual(page.name, server.DEFAULT_PAGE)

    def test_missing_demo_page_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                server.validate_assets(Path(tmp))

    def test_default_port_is_valid(self):
        self.assertGreaterEqual(server.DEFAULT_PORT, 1)
        self.assertLessEqual(server.DEFAULT_PORT, 65535)

    def test_demo_page_has_responsive_orientation_contract(self):
        page = server.validate_assets()
        text = page.read_text(encoding="utf-8")
        self.assertIn("@media (orientation:portrait)", text)
        self.assertIn("@media (orientation:landscape)", text)
        self.assertIn("orientationchange", text)
        self.assertIn("ResizeObserver", text)
        self.assertIn("STATE", text)

    def test_demo_page_keeps_mock_authority_visible(self):
        page = server.validate_assets()
        text = page.read_text(encoding="utf-8")
        self.assertIn("QUALIFICATION_ONLY", text)
        self.assertIn("NO NAV AUTHORITY", text)
        self.assertIn("ATTITUDE UNAVAILABLE", text)
        self.assertIn("VEHICLE AUTH UNAVAILABLE", text)

    def test_demo_page_scene_first_controls_are_reduced(self):
        page = server.validate_assets()
        text = page.read_text(encoding="utf-8")
        self.assertIn("drag to look", text)
        self.assertIn("RESET = ship-forward camera", text)
        self.assertNotIn('id="up"', text)
        self.assertNotIn('id="down"', text)


if __name__ == "__main__":
    unittest.main()
