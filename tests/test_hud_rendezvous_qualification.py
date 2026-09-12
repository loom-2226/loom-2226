import unittest

from loom.hud.rendezvous_qualification import (
    CONTRACT,
    POSITION_TOLERANCE_KM,
    RELATIVE_SPEED_TOLERANCE_KM_S,
    MIN_SURFACE_CLEARANCE_KM,
    _attitude_transition_budget,
    _classify_solution,
    solve_moon_rendezvous_feasibility,
)


class HudRendezvousQualificationTests(unittest.TestCase):
    def test_contract_is_explicitly_qualification_only_surface(self):
        self.assertEqual(CONTRACT, "LOOM_HUD_RENDEZVOUS_FEASIBILITY_QUALIFICATION_V1")

    def test_invalid_mode_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="NOPE", standoff_altitude_km=1000.0
            )

    def test_invalid_horizon_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=100.0, mode="CRUISE", standoff_altitude_km=1000.0
            )

    def test_standoff_inside_validation_floor_fails_closed(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="CRUISE", standoff_altitude_km=50.0
            )

    def test_standoff_above_validation_ceiling_fails_closed(self):
        with self.assertRaises(ValueError):
            solve_moon_rendezvous_feasibility(
                None, max_time_s=21600.0, mode="CRUISE", standoff_altitude_km=100001.0
            )

    def test_quality_gate_requires_position_velocity_and_surface_clearance(self):
        good = _classify_solution(
            position_error_km=POSITION_TOLERANCE_KM * 0.5,
            relative_speed_km_s=RELATIVE_SPEED_TOLERANCE_KM_S * 0.5,
            min_surface_clearance_km=MIN_SURFACE_CLEARANCE_KM + 10.0,
            remass_t=10.0,
        )
        self.assertEqual(good["status"], "SOLVED_TRANSLATIONAL_FEASIBILITY")
        self.assertTrue(good["position_ok"])
        self.assertTrue(good["velocity_ok"])
        self.assertTrue(good["surface_clearance_ok"])
        self.assertTrue(good["remass_ok"])

        bad = _classify_solution(
            position_error_km=POSITION_TOLERANCE_KM * 2.0,
            relative_speed_km_s=RELATIVE_SPEED_TOLERANCE_KM_S * 2.0,
            min_surface_clearance_km=MIN_SURFACE_CLEARANCE_KM - 1.0,
            remass_t=0.0,
        )
        self.assertEqual(bad["status"], "NOT_SOLVED")
        self.assertFalse(bad["position_ok"])
        self.assertFalse(bad["velocity_ok"])
        self.assertFalse(bad["surface_clearance_ok"])
        self.assertFalse(bad["remass_ok"])

    def test_quality_thresholds_are_explicit_not_hidden(self):
        self.assertGreater(POSITION_TOLERANCE_KM, 0.0)
        self.assertGreater(RELATIVE_SPEED_TOLERANCE_KM_S, 0.0)
        self.assertGreaterEqual(MIN_SURFACE_CLEARANCE_KM, 0.0)

    def test_attitude_budget_makes_flip_finite(self):
        budget = _attitude_transition_budget(
            current_direction=(1.0, 0.0, 0.0),
            departure_direction=(1.0, 0.0, 0.0),
            braking_direction=(-1.0, 0.0, 0.0),
            degraded=False,
        )
        self.assertEqual(budget["initial_transition_s"], 0.0)
        self.assertGreater(budget["flip_transition_s"], 0.0)
        self.assertAlmostEqual(budget["flip_angle_deg"], 180.0)
        self.assertFalse(budget["instantaneous_attitude_reset_allowed"])

    def test_one_cluster_out_attitude_budget_is_slower(self):
        nominal = _attitude_transition_budget(
            current_direction=(1.0, 0.0, 0.0),
            departure_direction=(0.0, 1.0, 0.0),
            braking_direction=(-1.0, 0.0, 0.0),
            degraded=False,
        )
        degraded = _attitude_transition_budget(
            current_direction=(1.0, 0.0, 0.0),
            departure_direction=(0.0, 1.0, 0.0),
            braking_direction=(-1.0, 0.0, 0.0),
            degraded=True,
        )
        self.assertGreater(degraded["total_transition_s"], nominal["total_transition_s"])


if __name__ == "__main__":
    unittest.main()
