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

    def test_wayfarer_uses_high_contrast_presentation_materials(self):
        js = (DEMO / "hud_v0_15.js").read_text(encoding="utf-8")
        self.assertIn("function shipMaterial", js)
        self.assertIn("emissive", js)
        self.assertIn("SHIP CHASE", js)
        self.assertIn("SHIP / LOOK", js)
        self.assertIn("TRAJECTORY / OVERVIEW", js)

    def test_mobile_layout_preserves_viewport_and_scrollable_controls(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn("minmax(32dvh,1fr)", html)
        self.assertIn("max-height:48dvh", html)
        self.assertIn("overflow-y:auto", html)


if __name__ == "__main__":
    unittest.main()
