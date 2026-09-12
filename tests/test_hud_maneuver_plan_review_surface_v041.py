import unittest

from loom.hud import server


class ManeuverPlanReviewSurfaceTests(unittest.TestCase):
    def test_browser_review_calls_validation_not_execution(self):
        js = (server.demo_root() / "hud_orbital_burn_v01.js").read_text(encoding="utf-8")
        self.assertIn("VALIDATE_MANEUVER_PLAN_REVIEW", js)
        self.assertIn("LOOM_HUD_MANEUVER_PLAN_REVIEW_RESPONSE_V1", js)
        self.assertIn("SERVER VALIDATED", js)
        self.assertIn("TARGET VECTOR NOT EXPOSED", js)
        self.assertNotIn("EXECUTE_MANEUVER_PLAN", js)

    def test_server_exposes_review_action_without_plan_execution_action(self):
        source = (server.repo_root() / "src" / "loom" / "hud" / "server.py").read_text(encoding="utf-8")
        self.assertIn('action == "VALIDATE_MANEUVER_PLAN_REVIEW"', source)
        self.assertIn("validate_maneuver_plan_review", source)
        self.assertIn("LOOM_HUD_MANEUVER_PLAN_REVIEW_RESPONSE_V1", source)
        self.assertNotIn('action == "EXECUTE_MANEUVER_PLAN"', source)


if __name__ == "__main__":
    unittest.main()
