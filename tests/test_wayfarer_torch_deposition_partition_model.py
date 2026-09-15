import unittest

from src.wayfarer_torch_deposition_partition_model import (
    DIRECT_JET_POWER_W,
    evaluate_partition_candidate,
    build_requirement_model,
)


class TorchDepositionPartitionModelTests(unittest.TestCase):
    def test_requirement_model_preserves_authority_firewall(self):
        r = build_requirement_model()
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["authority"]["claim"], "E1_TORCH_DEPOSITION_PARTITION_AND_FAMILY_KILL_CRITERIA_ONLY")
        self.assertFalse(r["authority"]["deposition_partition_certified"])
        self.assertFalse(r["authority"]["reactor_cycle_certified"])
        self.assertEqual(r["power_firewall"]["rule"], "JET_KINETIC_POWER_IS_NOT_SOURCE_POWER_OR_VEHICLE_WASTE_HEAT")

    def test_no_default_efficiency_or_partition_is_invented(self):
        r = build_requirement_model()
        self.assertIsNone(r["candidate_inputs"]["directed_exhaust_fraction"])
        self.assertIsNone(r["candidate_inputs"]["vehicle_deposition_fraction"])
        self.assertIsNone(r["candidate_inputs"]["source_power_W"])

    def test_partition_must_close_before_candidate_can_survive(self):
        with self.assertRaises(ValueError):
            evaluate_partition_candidate({"directed_exhaust": 0.8, "neutrons": 0.1})

    def test_closed_partition_derives_source_power_without_calling_it_electrical_power(self):
        fractions = {
            "directed_exhaust": 0.80,
            "escaping_neutral_radiation": 0.10,
            "vehicle_deposition": 0.05,
            "other_accounted_loss": 0.05,
        }
        e = evaluate_partition_candidate(fractions, mode="LIMIT")
        self.assertAlmostEqual(e["partition_sum"], 1.0)
        self.assertAlmostEqual(e["required_source_power_W"], DIRECT_JET_POWER_W["LIMIT"] / 0.80)
        self.assertAlmostEqual(e["vehicle_deposition_power_W"], e["required_source_power_W"] * 0.05)
        self.assertFalse(e["source_power_is_electrical_load"])

    def test_family_kill_gates_keep_low_neutron_candidates_open_but_uncertified(self):
        r = build_requirement_model()
        gates = r["family_kill_gates"]
        self.assertEqual(gates["D_HE3_FRC_DIRECT_FUSION_MAGNETIC_NOZZLE"]["status"], "OPEN_NEEDS_PARTITION_BOUNDS")
        self.assertEqual(gates["PB11_DIRECT_FUSION_MAGNETIC_NOZZLE"]["status"], "OPEN_NEEDS_RADIATION_AND_GAIN_BOUNDS")
        self.assertEqual(gates["DT_DIRECT_FUSION_MAGNETIC_NOZZLE"]["status"], "HIGH_RISK_NEUTRON_PARTITION_HOLD")
        self.assertEqual(r["qualified_next_step"], "TORCH_REMASS_COUPLING_AND_MAGNETIC_NOZZLE_EFFICIENCY_ENVELOPE")


if __name__ == "__main__":
    unittest.main()
