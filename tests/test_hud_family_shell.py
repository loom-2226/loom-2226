import unittest

from loom.hud import server


class HudFamilyShellTests(unittest.TestCase):
    def test_family_control_is_visible_and_contains_governing_families(self):
        html = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.28-tactical-track"', html)
        self.assertIn('id="hudFamily"', html)
        for family in (
            "TACTICAL",
            "NAV / FLIGHT PLAN",
            "NAV / METRIC",
            "SENSOR / WIDE",
            "TACTICAL / TRACK",
        ):
            self.assertIn(family, html)
        self.assertIn("hud_family_control_v01.js", html)
        self.assertIn("hud_family_profiles_v01.js", html)
        self.assertIn("hud_nav_flight_plan_v01.js", html)
        self.assertIn("hud_tactical_track_v01.js", html)

    def test_manual_family_override_is_presentation_only(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertIn("MANUAL OVERRIDE / PRESENTATION ONLY", js)
        self.assertNotIn("/control", js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("post(", js)

    def test_known_qualification_contexts_switch_auto_family_without_claiming_metric_or_sensor_state(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertIn("STRATEGIC_PLANNING_PRESENTATION", js)
        self.assertIn("LOCAL_GEOMETRY_TACTICAL_QUALITY", js)
        self.assertIn("NAV / FLIGHT PLAN", js)
        self.assertIn("TACTICAL / TRACK", js)
        self.assertNotIn("setAutomatic('NAV / METRIC'", js)
        self.assertNotIn("setAutomatic('SENSOR / WIDE'", js)


if __name__ == "__main__":
    unittest.main()
