import unittest

from loom.hud import server


class HudManeuverPlanReviewV040Tests(unittest.TestCase):
    def test_orbital_burn_ui_exposes_nonexecuting_plan_review(self):
        js = (server.demo_root() / "hud_orbital_burn_v01.js").read_text(encoding="utf-8")
        self.assertIn("REVIEW PLAN", js)
        self.assertIn("LOOM_MANEUVER_PLAN_V1", js)
        self.assertIn("REVIEW_REQUIRED", js)
        self.assertIn("NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY", js)
        self.assertIn("BROWSER STAGED", js)
        self.assertNotIn("EXECUTE_MANEUVER_PLAN", js)

    def test_plan_review_uses_existing_burn_controls_without_new_physics(self):
        js = (server.demo_root() / "hud_orbital_burn_v01.js").read_text(encoding="utf-8")
        self.assertIn("orbitalBurnS", js)
        self.assertIn("orbitalBurnDirection", js)
        self.assertIn("torch_mode", js)
        self.assertIn("direction_reference", js)
        self.assertNotIn("target_direction_inertial:[", js)


if __name__ == "__main__":
    unittest.main()
