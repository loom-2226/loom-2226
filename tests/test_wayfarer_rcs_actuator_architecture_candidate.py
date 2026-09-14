import unittest

from src.wayfarer_rcs_actuator_architecture_candidate import build_actuator_architecture_candidate


class TestWayfarerRCSActuatorArchitectureCandidate(unittest.TestCase):
    def test_candidate_preserves_hardware_firewall(self):
        result = build_actuator_architecture_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["disposition"],
            "COMPOUND_COARSE_FINE_VECTORED_MOUNT_SELECTED_AS_NEXT_ENGINEERING_CANDIDATE",
        )
        self.assertFalse(result["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(result["authority"]["working_fluid_certified"])
        self.assertFalse(result["authority"]["minimum_impulse_bit_certified"])
        self.assertFalse(result["authority"]["valve_dynamics_certified"])
        self.assertFalse(result["authority"]["vectoring_mechanism_certified"])

    def test_candidate_is_driven_by_qualified_demand(self):
        result = build_actuator_architecture_candidate()
        demand = result["qualified_demand_inputs"]
        self.assertAlmostEqual(demand["maximum_sampled_thrust_N"], 20844.756650298394)
        self.assertAlmostEqual(demand["sampled_exact_trace_mib_upper_bound_Ns"], 9.281346527990696)
        self.assertAlmostEqual(demand["one_sample_average_direction_slew_lower_bound_deg_s"], 67.30273777540819)
        self.assertEqual(demand["sample_period_s"], 1.0)

    def test_monolithic_gimbal_is_not_defaulted(self):
        result = build_actuator_architecture_candidate()
        candidate = result["selected_candidate"]
        self.assertEqual(candidate["architecture"], "COMPOUND_COARSE_FINE_VECTORED_MOUNT")
        self.assertEqual(candidate["vehicle_interface"], "SINGLE_RESULTANT_FORCE_VECTOR_PER_HARDPOINT")
        self.assertIn("COARSE_HIGH_THRUST_ELEMENT", candidate["functional_elements"])
        self.assertIn("FINE_IMPULSE_VERNIER_ELEMENT", candidate["functional_elements"])
        self.assertEqual(
            result["rejected_as_default"]["architecture"],
            "SINGLE_MONOLITHIC_MECHANICALLY_GIMBALLED_20_TO_25_KN_THRUSTER",
        )


if __name__ == "__main__":
    unittest.main()
