import unittest

from src.wayfarer_rcs_coarse_fine_authority_envelope import (
    PIXEL_QUALIFICATION_CASES,
    PIXEL_QUALIFICATION_PARAMETERS,
    _realize_mount_wrench,
    build_coarse_fine_authority_envelope,
)


class CoarseFineAuthorityEnvelopeTests(unittest.TestCase):
    def test_pixel_contract_is_bounded_but_keeps_nominal_and_degraded_closed_loop_replay(self):
        self.assertEqual(len(PIXEL_QUALIFICATION_PARAMETERS), 1)
        self.assertEqual(
            PIXEL_QUALIFICATION_CASES,
            ("NOMINAL_MIXED_TRANSLATION_ATTITUDE", "DEGRADED_MIXED_TRANSLATION_ATTITUDE_A"),
        )

    def test_mount_realization_quantizes_only_fine_channel(self):
        commands = {
            "M1": {
                "commanded_thrust_N": 6000.0,
                "commanded_force_unit_ship": [1.0, 0.0, 0.0],
                "position_m": [1.0, 0.0, 0.0],
            }
        }
        wrench, telemetry = _realize_mount_wrench(
            commands,
            com=[0.0, 0.0, 0.0],
            coarse_activation_fraction=0.20,
            fine_quantization_fraction=0.50,
            trace_mib_upper_bound_ns=100.0,
        )
        self.assertAlmostEqual(telemetry["coarse_activation_threshold_N"], 5000.0)
        self.assertAlmostEqual(telemetry["fine_force_quantum_N"], 50.0)
        self.assertAlmostEqual(wrench[0], 6000.0)
        self.assertEqual(wrench[1:], [0.0] * 5)

    @classmethod
    def setUpClass(cls):
        cls.result = build_coarse_fine_authority_envelope()

    def test_parameter_probe_qualifies_without_selecting_hardware(self):
        r = self.result
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["disposition"], "COARSE_FINE_AUTHORITY_PIXEL_PROBE_QUALIFIED_HARDWARE_OPEN")
        self.assertEqual(len(r["parameter_sweep"]), 1)
        self.assertTrue(r["parameter_sweep"][0]["pass"])
        self.assertFalse(r["authority"]["final_thruster_hardware_certified"])
        self.assertFalse(r["authority"]["minimum_impulse_bit_certified"])
        self.assertEqual(r["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(r["authority"]["llm_calculation_authority"], "ZERO")

    def test_split_is_dimensionless_and_not_a_hardware_threshold(self):
        r = self.result
        contract = r["parameter_contract"]
        self.assertEqual(contract["coarse_activation_parameter"], "FRACTION_OF_CURRENT_MOUNT_THRUST_CAP")
        self.assertEqual(contract["fine_quantization_parameter"], "FRACTION_OF_CURRENT_SAMPLED_EXACT_TRACE_MIB_UPPER_BOUND")
        self.assertEqual(contract["interpretation"], "NUMERICAL_AUTHORITY_SPLIT_PROBE_NOT_HARDWARE_SPECIFICATION")
        row = r["parameter_sweep"][0]
        self.assertGreater(row["coarse_activation_fraction"], 0.0)
        self.assertLess(row["coarse_activation_fraction"], 1.0)
        self.assertGreater(row["fine_quantization_fraction"], 0.0)
        self.assertLessEqual(row["fine_quantization_fraction"], 1.0)

    def test_closed_loop_probe_uses_realized_mount_wrench(self):
        r = self.result
        self.assertEqual(r["closed_loop_contract"]["state_advance_wrench"], "REALIZED_COARSE_PLUS_FINE_MOUNT_WRENCH_ONLY")
        self.assertEqual(r["closed_loop_contract"]["allocator_location"], "INSIDE_COUPLED_LOCAL_FLIGHT_TIME_LOOP")
        row = r["parameter_sweep"][0]
        self.assertEqual(tuple(row["cases"]), PIXEL_QUALIFICATION_CASES)
        self.assertEqual(row["pass"], all(case["pass"] for case in row["cases"].values()))
        self.assertEqual(r["exploration_contract"]["full_parameter_sweep_authority"], "NOT_EXECUTED_BY_PIXEL_QUALIFICATION")


if __name__ == "__main__":
    unittest.main()
