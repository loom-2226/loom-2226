import unittest

from src.wayfarer_rcs_inertia_requalification import build_rcs_inertia_requalification


class WayfarerRcsInertiaRequalificationTests(unittest.TestCase):
    def test_nominal_and_degraded_cases_are_present(self):
        result = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        self.assertIn("NOMINAL", result["cases"])
        for cluster in ("A", "B", "C", "D"):
            self.assertIn(f"ONE_CLUSTER_OUT_{cluster}", result["cases"])

    def test_every_case_uses_same_configuration_aware_tensor(self):
        result = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        expected = result["mass_inertia_state"]["inertia_tensor_kg_m2"]
        for case in result["cases"].values():
            self.assertEqual(case["inertia_tensor_kg_m2"], expected)

    def test_degraded_authority_is_lower_than_nominal(self):
        result = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        nominal = result["cases"]["NOMINAL"]
        degraded = result["cases"]["ONE_CLUSTER_OUT_A"]
        self.assertLess(degraded["torque_authority_Nm"]["roll"], nominal["torque_authority_Nm"]["roll"])
        self.assertLess(degraded["torque_authority_Nm"]["pitch"], nominal["torque_authority_Nm"]["pitch"])
        self.assertLess(degraded["translation_thrust_N"], nominal["translation_thrust_N"])

    def test_slew_times_are_finite_positive_and_degraded_slower(self):
        result = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        nominal = result["cases"]["NOMINAL"]["slew_time_s_with_20pct_settle_margin"]
        degraded = result["cases"]["ONE_CLUSTER_OUT_A"]["slew_time_s_with_20pct_settle_margin"]
        for key, value in nominal.items():
            self.assertGreater(value, 0.0)
            self.assertGreater(degraded[key], value)

    def test_depletion_changes_dynamic_response(self):
        full = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        empty = build_rcs_inertia_requalification(normal_remass_t=0.0, protected_water_t=50.0, launch_docked=True)
        self.assertNotEqual(
            full["cases"]["NOMINAL"]["angular_accel_rad_s2"],
            empty["cases"]["NOMINAL"]["angular_accel_rad_s2"],
        )

    def test_authority_boundaries_remain_explicit(self):
        result = build_rcs_inertia_requalification(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True)
        self.assertFalse(result["authority"]["closed_loop_gnc_certified"])
        self.assertFalse(result["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(result["authority"]["structural_mount_loads_certified"])
        self.assertEqual(result["torque_source_status"], "RECOVERED_Q4_ENGINEERING_ENVELOPE_REQUIRES_EXACT_HEAD_QUALIFICATION")


if __name__ == "__main__":
    unittest.main()
