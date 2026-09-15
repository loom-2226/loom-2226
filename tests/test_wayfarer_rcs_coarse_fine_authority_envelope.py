import unittest

from src.wayfarer_rcs_coarse_fine_authority_envelope import build_coarse_fine_authority_envelope


class CoarseFineAuthorityEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_coarse_fine_authority_envelope()

    def test_parameter_sweep_qualifies_without_selecting_hardware(self):
        r = self.result
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["disposition"], "COARSE_FINE_AUTHORITY_PARAMETER_ENVELOPE_QUALIFIED_HARDWARE_OPEN")
        self.assertGreaterEqual(len(r["parameter_sweep"]), 3)
        self.assertTrue(any(row["pass"] for row in r["parameter_sweep"]))
        self.assertFalse(r["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(r["authority"]["minimum_impulse_bit_certified"])
        self.assertEqual(r["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(r["authority"]["llm_calculation_authority"], "ZERO")

    def test_split_is_dimensionless_and_not_a_hardware_threshold(self):
        r = self.result
        contract = r["parameter_contract"]
        self.assertEqual(contract["coarse_activation_parameter"], "FRACTION_OF_CURRENT_MOUNT_THRUST_CAP")
        self.assertEqual(contract["fine_quantization_parameter"], "FRACTION_OF_CURRENT_SAMPLED_EXACT_TRACE_MIB_UPPER_BOUND")
        self.assertEqual(contract["interpretation"], "NUMERICAL_AUTHORITY_SPLIT_ENVELOPE_NOT_HARDWARE_SPECIFICATION")
        for row in r["parameter_sweep"]:
            self.assertGreater(row["coarse_activation_fraction"], 0.0)
            self.assertLess(row["coarse_activation_fraction"], 1.0)
            self.assertGreater(row["fine_quantization_fraction"], 0.0)
            self.assertLessEqual(row["fine_quantization_fraction"], 1.0)

    def test_closed_loop_replay_uses_realized_mount_wrench(self):
        r = self.result
        self.assertEqual(r["closed_loop_contract"]["state_advance_wrench"], "REALIZED_COARSE_PLUS_FINE_MOUNT_WRENCH_ONLY")
        self.assertEqual(r["closed_loop_contract"]["allocator_location"], "INSIDE_COUPLED_LOCAL_FLIGHT_TIME_LOOP")
        for row in r["parameter_sweep"]:
            self.assertEqual(set(row["cases"]), {"NOMINAL", "DEGRADED_A", "DEGRADED_B", "DEGRADED_C", "DEGRADED_D"})
            self.assertEqual(row["pass"], all(case["pass"] for case in row["cases"].values()))


if __name__ == "__main__":
    unittest.main()
