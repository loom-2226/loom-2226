import unittest

from loom.hud import server


class ManeuverPlanReviewSurfaceTests(unittest.TestCase):
    def test_browser_requires_review_before_explicit_execution(self):
        js = (server.demo_root() / "hud_orbital_burn_v01.js").read_text(encoding="utf-8")
        self.assertIn("VALIDATE_MANEUVER_PLAN_REVIEW", js)
        self.assertIn("LOOM_HUD_MANEUVER_PLAN_REVIEW_RESPONSE_V1", js)
        self.assertIn("SERVER VALIDATED", js)
        self.assertIn("TARGET VECTOR NOT EXPOSED", js)
        self.assertIn("EXECUTE_VALIDATED_MANEUVER_PLAN", js)
        self.assertIn("EXECUTION REQUIRES EXPLICIT SECOND ACTION", js)
        self.assertIn("execution_ticket", js)
        self.assertNotIn("target_direction_inertial:[", js)

    def test_server_execution_requires_one_time_validated_ticket(self):
        source = (server.repo_root() / "src" / "loom" / "hud" / "server.py").read_text(encoding="utf-8")
        self.assertIn('action == "VALIDATE_MANEUVER_PLAN_REVIEW"', source)
        self.assertIn("validate_maneuver_plan_review", source)
        self.assertIn("LOOM_HUD_MANEUVER_PLAN_REVIEW_RESPONSE_V1", source)
        self.assertIn('action == "EXECUTE_VALIDATED_MANEUVER_PLAN"', source)
        self.assertIn("build_explicit_execution_plan_from_review", source)
        self.assertIn("execute_maneuver_plan", source)
        self.assertIn("validated_reviews.pop", source)
        self.assertIn("invalidate_validated_reviews", source)
        self.assertNotIn('action == "EXECUTE_MANEUVER_PLAN"', source)


if __name__ == "__main__":
    unittest.main()
