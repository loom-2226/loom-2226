import math
import unittest

from src.wayfarer_rcs_closed_loop_gnc import qualify_attitude_cases, simulate_axis_slew


class TestWayfarerRCSClosedLoopGNC(unittest.TestCase):
    def test_nominal_90_and_180_degree_cases_converge(self):
        report = qualify_attitude_cases(failed_cluster=None)
        self.assertTrue(report["all_cases_pass"])
        for case in report["cases"].values():
            self.assertLessEqual(case["terminal_attitude_error_deg"], 0.25)
            self.assertLessEqual(case["terminal_rate_deg_s"], 0.05)
            self.assertLessEqual(case["peak_torque_fraction"], 1.0 + 1e-9)

    def test_one_cluster_out_cases_converge(self):
        for cluster in "ABCD":
            report = qualify_attitude_cases(failed_cluster=cluster)
            self.assertTrue(report["all_cases_pass"], cluster)

    def test_full_tensor_is_used(self):
        case = simulate_axis_slew("pitch", 90.0, failed_cluster=None)
        tensor = case["inertia_tensor_kg_m2"]
        self.assertGreater(abs(tensor[0][2]), 1.0)
        self.assertEqual(case["dynamics_model"], "FULL_RIGID_BODY_EULER_PLUS_QUATERNION_KINEMATICS")

    def test_torque_is_saturated_to_requalified_envelope(self):
        case = simulate_axis_slew("roll", 180.0, failed_cluster="A")
        self.assertLessEqual(case["peak_torque_fraction"], 1.0 + 1e-9)
        self.assertEqual(case["torque_limit_Nm"]["roll"], 100000.0)

    def test_invalid_axis_rejected(self):
        with self.assertRaises(ValueError):
            simulate_axis_slew("banana", 90.0)


if __name__ == "__main__":
    unittest.main()
