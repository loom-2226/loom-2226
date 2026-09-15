import unittest

from src.wayfarer_rcs_actuator_architecture_candidate import build_actuator_architecture_candidate


class TestWayfarerRCSActuatorArchitectureCandidate(unittest.TestCase):
    def test_candidate_preserves_hardware_firewall(self):
        result = build_actuator_architecture_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["disposition"], "COMPOUND_COARSE_FINE_VECTORED_MOUNT_SELECTED_AS_NEXT_ENGINEERING_CANDIDATE")
        self.assertFalse(result["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(result["authority"]["working_fluid_certified"])
        self.assertFalse(result["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(result["authority"]["valve_dynamics_certified"])
        self.assertFalse(result["authority"]["vectoring_mechanism_certified"])

    def test_candidate_uses_corrected_case_bounded_demand_envelope(self):
        from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope

        result = build_actuator_architecture_candidate()
        aggregate = build_actuator_requirement_envelope()["aggregate_sampled_actuator_demand"]
        demand = result["qualified_demand_inputs"]
        for key in (
            "maximum_sampled_thrust_N", "maximum_sampled_thrust_step_N",
            "sampled_exact_trace_mib_upper_bound_Ns", "one_sample_average_direction_slew_lower_bound_deg_s",
            "maximum_sampled_direction_step_deg", "sample_period_s",
        ):
            self.assertAlmostEqual(demand[key], aggregate[key])
        self.assertEqual(demand["transition_series_identity"], "QUALIFICATION_CASE_PLUS_MOUNT_ID")

    def test_monolithic_gimbal_is_not_defaulted_without_using_stale_67_degree_claim(self):
        result = build_actuator_architecture_candidate()
        candidate = result["selected_candidate"]
        self.assertEqual(candidate["architecture"], "COMPOUND_COARSE_FINE_VECTORED_MOUNT")
        self.assertEqual(candidate["vehicle_interface"], "SINGLE_RESULTANT_FORCE_VECTOR_PER_HARDPOINT")
        self.assertIn("COARSE_HIGH_THRUST_ELEMENT", candidate["functional_elements"])
        self.assertIn("FINE_IMPULSE_VERNIER_ELEMENT", candidate["functional_elements"])
        rejected = result["rejected_as_default"]
        self.assertEqual(rejected["architecture"], "SINGLE_MONOLITHIC_MECHANICALLY_GIMBALLED_20_TO_25_KN_THRUSTER")
        self.assertFalse(any("67_DEG" in reason for reason in rejected["reason"]))


if __name__ == "__main__":
    unittest.main()
