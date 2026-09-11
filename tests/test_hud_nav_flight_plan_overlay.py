import unittest
from pathlib import Path

from loom.hud.rendezvous_qualification import _build_flight_plan_display


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "src" / "loom" / "hud" / "demo"


class HudNavFlightPlanOverlayTests(unittest.TestCase):
    def test_solved_display_contains_governing_minimum_fields(self):
        best = {
            "quality": {"status": "SOLVED_TRANSLATIONAL_FEASIBILITY"},
            "burn1_s": 10.0,
            "coast_s": 20.0,
            "burn2_s": 30.0,
            "attitude_budget": {"initial_transition_s": 2.0, "flip_transition_s": 3.0},
        }
        trial = {
            "points": [
                {"phase": "ROTATE_DEPARTURE", "elapsed_s": 2.0, "wayfarer_velocity_earth_centered_km_s": [1.0, 0.0, 0.0], "state_source": "JPL+HERMITE"},
                {"phase": "BURN", "elapsed_s": 12.0, "wayfarer_velocity_earth_centered_km_s": [2.0, 0.0, 0.0], "state_source": "JPL+HERMITE"},
                {"phase": "COAST", "elapsed_s": 32.0, "wayfarer_velocity_earth_centered_km_s": [2.5, 0.0, 0.0], "state_source": "JPL+HERMITE"},
                {"phase": "ROTATE_BRAKE", "elapsed_s": 35.0, "wayfarer_velocity_earth_centered_km_s": [2.4, 0.0, 0.0], "state_source": "JPL+HERMITE"},
                {"phase": "BRAKE", "elapsed_s": 65.0, "wayfarer_velocity_earth_centered_km_s": [1.1, 0.0, 0.0], "state_source": "JPL+HERMITE"},
            ]
        }
        display = _build_flight_plan_display(best=best, trial=trial, mode="CRUISE")
        self.assertEqual(display["status"], "SOLVED_TRANSLATIONAL_FEASIBILITY")
        self.assertEqual(len(display["phases"]), 5)
        self.assertEqual(display["phases"][-1]["cumulative_eta_s"], 65.0)
        self.assertEqual(display["phases"][1]["propulsion_mode"], "TORCH CRUISE")
        for row in display["phases"]:
            for key in ("phase", "duration_s", "cumulative_eta_s", "speed_km_s", "velocity_reference", "propulsion_mode", "nav_ephemeris_quality"):
                self.assertIn(key, row)

    def test_unsolved_result_does_not_publish_solved_phase_table(self):
        display = _build_flight_plan_display(
            best={"quality": {"status": "NOT_SOLVED"}, "burn1_s": 1.0, "coast_s": 1.0, "burn2_s": 1.0, "attitude_budget": {"initial_transition_s": 0.0, "flip_transition_s": 0.0}},
            trial={"points": []},
            mode="CRUISE",
        )
        self.assertEqual(display["status"], "NOT_SOLVED")
        self.assertEqual(display["phases"], [])

    def test_overlay_reuses_existing_hud_and_has_no_control_authority(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        js = (DEMO / "hud_nav_flight_plan_v01.js").read_text(encoding="utf-8")
        self.assertIn('id="navFlightPlan"', html)
        self.assertIn('id="world"', html)
        self.assertIn("flight_plan_display", js)
        self.assertIn("PHASE", js)
        self.assertIn("CUM ETA", js)
        self.assertIn("NAV/EPH", js)
        self.assertNotIn("/control", js)
        self.assertNotIn("fetch(", js)


if __name__ == "__main__":
    unittest.main()
