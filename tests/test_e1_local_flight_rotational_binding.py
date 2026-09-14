import unittest

from engineering.experience_one.qualification.e1_local_flight_rotational_binding import build_local_flight_rotational_binding


class TestE1LocalFlightRotationalBinding(unittest.TestCase):
    def test_binding_consumes_closed_loop_gnc(self):
        report = build_local_flight_rotational_binding()
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["authority"]["instantaneous_attitude_reorientation_forbidden"])
        self.assertTrue(report["authority"]["closed_loop_attitude_response_consumed"])

    def test_hud_and_navigator_share_same_rotational_state(self):
        report = build_local_flight_rotational_binding()
        self.assertEqual(report["handoff"]["rotational_state_authority"], "PYTHON_E1_FLIGHT_DYNAMICS")
        self.assertEqual(report["handoff"]["hud_role"], "PRESENTATION_AND_INTENT_ONLY")
        self.assertEqual(report["handoff"]["navigator_role"], "TRANSLATIONAL_AND_ROUTE_AUTHORITY_WITH_EXPLICIT_ROTATIONAL_HANDOFF")

    def test_plume_and_mount_hardware_remain_open(self):
        report = build_local_flight_rotational_binding()
        self.assertIn("finite_plume_and_deployed_radiator_interference_closure", report["missing_required_evidence"])
        self.assertIn("structural_rcs_mount_load_qualification", report["missing_required_evidence"])


if __name__ == "__main__":
    unittest.main()
