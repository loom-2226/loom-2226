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

    def test_demo_page_is_responsive(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("@media(orientation:portrait)", text)
        self.assertIn("@media(orientation:landscape)", text)
        self.assertIn("orientationchange", text)
        self.assertIn("window.addEventListener('resize'", text)

    def test_demo_page_keeps_mock_authority_visible(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("QUALIFICATION_ONLY", text)
        self.assertIn("NO NAV AUTHORITY", text)
        self.assertIn("no canonical physics in browser", text)

    def test_demo_page_exposes_verified_build_marker(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.4-synthvision"', text)
        self.assertIn("BUILD hud-v0.4-synthvision", text)

    def test_demo_page_has_three_synthetic_vision_modes(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('data-mode="optical"', text)
        self.assertIn('data-mode="tactical"', text)
        self.assertIn('data-mode="hybrid"', text)

    def test_demo_page_has_reference_frame_selector(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        for frame in ("INERTIAL", "VELOCITY", "HILL_LVLH", "BODY", "TARGET"):
            self.assertIn(f'data-frame="{frame}"', text)

    def test_demo_page_contains_projection_and_operational_overlays(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("function project(p,w,h,fovy=60)", text)
        self.assertIn("function edge(q,w,h)", text)
        self.assertIn("const trajectory=", text)
        self.assertIn("cmd=[", text)
        self.assertIn("BEARING", text)
        self.assertIn("CLOSURE", text)

    def test_nav_is_visible_but_fail_closed(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("<button disabled>NAV</button>", text)


if __name__ == "__main__":
    unittest.main()
