import unittest

from loom.hud import server


class HudFamilyShellTests(unittest.TestCase):
    def test_family_control_is_visible_and_contains_governing_families(self):
        html = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.29-runtime-family-auto"', html)
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

    def test_runtime_events_drive_known_auto_contexts_without_claiming_metric_or_sensor_state(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertIn("loom-rendezvous-quality", js)
        self.assertIn("loom-live-qualification", js)
        self.assertIn("STRATEGIC_PLANNING_SOLVED_TRANSLATIONAL_FEASIBILITY", js)
        self.assertIn("LOCAL_GEOMETRY_TACTICAL_QUALITY", js)
        self.assertIn("NAV / FLIGHT PLAN", js)
        self.assertIn("TACTICAL / TRACK", js)
        self.assertNotIn("setAutomatic('NAV / METRIC'", js)
        self.assertNotIn("setAutomatic('SENSOR / WIDE'", js)

    def test_clicks_do_not_claim_auto_operational_state(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertNotIn("STRATEGIC_PLANNING_PRESENTATION", js)
        self.assertNotIn("for(const id of ['preview','solve','rendezvous'])", js)
        self.assertNotIn("getElementById('liveView')?.addEventListener", js)
        self.assertNotIn("getElementById('reset')?.addEventListener", js)


if __name__ == "__main__":
    unittest.main()
