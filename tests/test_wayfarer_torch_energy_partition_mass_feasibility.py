import unittest
from src.wayfarer_torch_energy_partition_mass_feasibility import build_envelope, evaluate_candidate

class TorchEnergyPartitionMassFeasibilityTests(unittest.TestCase):
    def test_inputs_remain_unearned(self):
        r=build_envelope()
        for k in ("directed_fraction","deposition_fraction","escaping_neutral_fraction","other_loss_fraction","source_specific_power_W_kg"):
            self.assertIsNone(r["candidate_inputs"][k])

    def test_closed_partition_drives_source_and_mass(self):
        c=evaluate_candidate("LIMIT",0.8,0.01,0.15,0.04,1e8)
        self.assertAlmostEqual(c["partition_sum"],1.0)
        self.assertAlmostEqual(c["required_source_power_W"],12781129528125.0/0.8)
        self.assertAlmostEqual(c["source_mass_kg"],c["required_source_power_W"]/1e8)
        self.assertAlmostEqual(c["vehicle_deposition_W"],c["required_source_power_W"]*0.01)
        self.assertFalse(c["certified"])

    def test_partition_must_close(self):
        with self.assertRaises(ValueError): evaluate_candidate("FAST",0.8,0.01,0.1,0.01,1e8)

    def test_candidate_propulsion_allocation_is_not_source_budget(self):
        r=build_envelope()
        self.assertEqual(r["candidate_propulsion_allocation_t"],160.0)
        self.assertEqual(r["allocation_firewall"],"160_T_IS_A_CANDIDATE_TOTAL_PROPULSION_ALLOCATION_NOT_A_CERTIFIED_FUSION_SOURCE_MASS_BUDGET")

    def test_next_step_is_architecture_trade(self):
        self.assertEqual(build_envelope()["qualified_next_step"],"TORCH_SOURCE_ARCHITECTURE_BREAKTHROUGH_REQUIREMENTS_AND_ALTERNATIVES_TRADE")

if __name__=="__main__": unittest.main()
