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
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("@media(orientation:landscape)", text)
        self.assertIn("orientationchange", text)
        self.assertIn("window.addEventListener('resize'", text)

    def test_demo_page_keeps_mock_authority_visible(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("QUALIFICATION_ONLY", text)
        self.assertIn("NO NAV AUTHORITY", text)
        self.assertIn("ATTITUDE UNAVAILABLE", text)
        self.assertIn("VEHICLE AUTH UNAVAILABLE", text)

    def test_demo_page_supports_pilot_and_ship_centered_3d_views(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('id="pilotTab"', text)
        self.assertIn('id="tacticalTab"', text)
        self.assertIn("PILOT / SHIP-FORWARD", text)
        self.assertIn("3D / SHIP-CENTERED", text)
        self.assertIn("function setView(v)", text)
        self.assertIn("state.view==='pilot'", text)
        self.assertIn("state.view!=='tactical'", text)

    def test_nav_is_visible_but_fail_closed(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('disabled title="Navigator integration not qualified"', text)

    def test_demo_page_keeps_larger_scene_symbology(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("width:78,height:60", text)
        self.assertIn("r:28,class:'station'", text)

    def test_tactical_view_has_ownship_anchor(self):
        text = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("class:'ship'", text)
        self.assertIn("class:'ship-axis'", text)


if __name__ == "__main__":
    unittest.main()
