import unittest

from loom.hud import server


class HudFamilyShellTests(unittest.TestCase):
    def test_family_control_is_visible_and_contains_governing_families(self):
        html = server.validate_assets().read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.31-orbital-sandbox"', html)
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

    def test_runtime_events_consume_server_stamped_family_selection(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertIn("hud_family_selection", js)
        self.assertIn("loom-rendezvous-quality", js)
        self.assertIn("loom-live-qualification", js)
        self.assertNotIn("relative_to_wayfarer_km", js)
        self.assertNotIn("velocity_earth_centered_km_s", js)
        self.assertNotIn("SOLVED_TRANSLATIONAL_FEASIBILITY", js)
        self.assertNotIn("hasLiveTrack", js)

    def test_server_stamps_live_and_rendezvous_family_payloads(self):
        source = (server.repo_root() / "src" / "loom" / "hud" / "server.py").read_text(encoding="utf-8")
        self.assertIn("live_qualification_selection_payload", source)
        self.assertIn("rendezvous_selection_payload", source)
        self.assertIn('"hud_family_selection"', source)

    def test_solved_nav_selection_is_held_against_live_poll_until_return_live(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertIn("planningHold", js)
        self.assertIn("NAV / FLIGHT PLAN", js)
        self.assertIn("if(planningHold)return", js)
        self.assertIn("RETURN_LIVE_RELEASE", js)
        self.assertIn("liveView.addEventListener('click'", js)

    def test_clicks_do_not_claim_auto_operational_state(self):
        js = (server.demo_root() / "hud_family_control_v01.js").read_text(encoding="utf-8")
        self.assertNotIn("STRATEGIC_PLANNING_PRESENTATION", js)
        self.assertNotIn("for(const id of ['preview','solve','rendezvous'])", js)
        self.assertNotIn("rendezvous.addEventListener", js)
        self.assertNotIn("preview.addEventListener", js)
        self.assertNotIn("solve.addEventListener", js)


if __name__ == "__main__":
    unittest.main()
