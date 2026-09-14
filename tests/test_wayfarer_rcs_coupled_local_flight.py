import unittest

from src.wayfarer_rcs_coupled_local_flight import build_coupled_local_flight_qualification


class CoupledLocalFlightTests(unittest.TestCase):
    def test_all_nominal_cases_pass(self):
        payload = build_coupled_local_flight_qualification()
        self.assertTrue(payload["nominal"]["all_cases_pass"])

    def test_all_one_cluster_out_cases_pass(self):
        payload = build_coupled_local_flight_qualification()
        self.assertTrue(all(case["all_cases_pass"] for case in payload["one_cluster_out"].values()))

    def test_translation_and_rotation_are_both_integrated(self):
        payload = build_coupled_local_flight_qualification()
        case = payload["nominal"]["cases"]["DOCKING_BRAKE_AND_ALIGN"]
        self.assertEqual(case["dynamics_model"], "COUPLED_TRANSLATION_PLUS_FULL_RIGID_BODY_ROTATION")
        self.assertIn("terminal_velocity_error_m_s", case)
        self.assertIn("terminal_attitude_error_deg", case)

    def test_hardware_authority_remains_open(self):
        payload = build_coupled_local_flight_qualification()
        self.assertFalse(payload["authority"]["mount_level_allocator_in_time_loop"])
        self.assertFalse(payload["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(payload["authority"]["plume_interference_certified"])

    def test_no_campaign_or_canon_mutation(self):
        payload = build_coupled_local_flight_qualification()
        self.assertEqual(payload["authority"]["campaign_state_mutation"], "ZERO")
        self.assertFalse(payload["authority"]["canon_changed"])


if __name__ == "__main__":
    unittest.main()
