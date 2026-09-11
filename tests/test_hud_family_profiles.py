import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "src" / "loom" / "hud" / "demo"


class HudFamilyProfileTests(unittest.TestCase):
    def test_family_profiles_reuse_existing_hud_surface(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn('id="stage"', html)
        self.assertIn('id="world"', html)
        self.assertIn('id="readout"', html)
        self.assertIn('id="qualityPanel"', html)
        self.assertIn('id="hudFamily"', html)
        self.assertNotIn("family-tactical.html", html)
        self.assertNotIn("family-nav.html", html)

    def test_profile_controller_is_presentation_only(self):
        js = (DEMO / "hud_family_profiles_v01.js").read_text(encoding="utf-8")
        self.assertIn("data-family-role", js)
        self.assertIn("NAV / FLIGHT PLAN", js)
        self.assertIn("TACTICAL / TRACK", js)
        self.assertIn("SENSOR / WIDE", js)
        self.assertIn("NAV / METRIC", js)
        self.assertIn("RUNTIME PHASE DATA NOT PRESENT", js)
        self.assertNotIn("/control", js)
        self.assertNotIn("fetch(", js)

    def test_profile_css_deemphasizes_without_removing_controls(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn("family-secondary", html)
        self.assertIn("family-primary", html)
        self.assertIn("family-notice", html)
        self.assertNotIn("display:none!important", html)

    def test_mobile_profile_preserves_a_visible_viewport(self):
        js = (DEMO / "hud_family_profiles_v01.js").read_text(encoding="utf-8")
        self.assertIn("minHeight='32dvh'", js)
        self.assertIn("maxHeight='48dvh'", js)
        self.assertIn("overflowY='auto'", js)
        self.assertIn("visualViewport", js)


if __name__ == "__main__":
    unittest.main()
