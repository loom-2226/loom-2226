import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "src" / "loom" / "hud" / "demo"


class HudNavFlightPlanOverlayTests(unittest.TestCase):
    def test_overlay_reuses_existing_hud_and_governing_minimum_fields(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        js = (DEMO / "hud_nav_flight_plan_v01.js").read_text(encoding="utf-8")
        self.assertIn('id="navFlightPlan"', html)
        self.assertIn('id="world"', html)
        self.assertIn("SOLVED_TRANSLATIONAL_FEASIBILITY", js)
        for label in ("PHASE", "DURATION", "CUM ETA", "SPEED", "VEL REF", "PROPULSION", "NAV/EPH"):
            self.assertIn(label, js)

    def test_overlay_consumes_existing_rendezvous_payload_without_control_authority(self):
        js = (DEMO / "hud_nav_flight_plan_v01.js").read_text(encoding="utf-8")
        for field in ("burn1_s", "coast_s", "burn2_s", "attitude_transitions", "points", "mode", "frame", "navigation_grade"):
            self.assertIn(field, js)
        self.assertIn("loom-rendezvous-quality", js)
        self.assertNotIn("/control", js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("post(", js)

    def test_unsolved_payload_does_not_publish_phase_rows(self):
        js = (DEMO / "hud_nav_flight_plan_v01.js").read_text(encoding="utf-8")
        self.assertIn("NO SOLVED FLIGHT PLAN TABLE", js)
        self.assertIn("if(status!=='SOLVED_TRANSLATIONAL_FEASIBILITY')", js)

    def test_family_profile_marks_nav_plan_as_nav_emphasis_not_new_page(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        profile = (DEMO / "hud_family_profiles_v01.js").read_text(encoding="utf-8")
        self.assertIn("navplan", profile)
        self.assertIn("NAV / FLIGHT PLAN", profile)
        self.assertNotIn("family-nav.html", html)


if __name__ == "__main__":
    unittest.main()
