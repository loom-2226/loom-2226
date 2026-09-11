import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "src" / "loom" / "hud" / "demo"


class HudMobileTestDriveUxTests(unittest.TestCase):
    def test_engineering_overlay_is_compact_by_default_and_expandable(self):
        js = (DEMO / "hud_wayfarer_engineering_state_v01.js").read_text(encoding="utf-8")
        self.assertIn("ENGINEERING / TAP FOR DETAIL", js)
        self.assertIn("panel.dataset.expanded='false'", js)
        self.assertIn("panel.addEventListener('click'", js)
        self.assertIn("renderCompact", js)
        self.assertIn("renderExpanded", js)

    def test_view_modes_have_explicit_operator_cues(self):
        js = (DEMO / "hud_test_drive_ux_v01.js").read_text(encoding="utf-8")
        self.assertIn("SHIP / LOOK", js)
        self.assertIn("CHASE / OWN SHIP", js)
        self.assertIn("TRAJECTORY / OVERVIEW", js)
        self.assertIn("TRAJECTORY / LOAD PLAN", js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("/control", js)

    def test_mobile_layout_preserves_viewport_and_scrollable_controls(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn("minmax(32dvh,1fr)", html)
        self.assertIn("max-height:48dvh", html)
        self.assertIn("overflow-y:auto", html)
        self.assertIn("hud_test_drive_ux_v01.js", html)
        self.assertIn("drop-shadow", html)


if __name__ == "__main__":
    unittest.main()
