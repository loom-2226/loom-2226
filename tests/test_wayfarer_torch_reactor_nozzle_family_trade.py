import unittest

from src.wayfarer_torch_reactor_nozzle_family_trade import build_trade


class TorchReactorNozzleFamilyTradeTests(unittest.TestCase):
    def setUp(self):
        self.r = build_trade()

    def test_authority_firewall(self):
        a = self.r["authority"]
        self.assertEqual(a["claim"], "E1_TORCH_REACTOR_NOZZLE_TECHNOLOGY_FAMILY_TRADE_ONLY")
        self.assertFalse(a["reactor_cycle_certified"])
        self.assertFalse(a["fuel_cycle_certified"])
        self.assertFalse(a["magnetic_nozzle_component_design_certified"])
        self.assertFalse(a["archive_values_promoted_to_current_authority"])
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")

    def test_required_vehicle_envelope_is_preserved(self):
        e = self.r["required_vehicle_envelope"]
        self.assertAlmostEqual(e["initial_direct_jet_power_W"]["LIMIT"], 12781129528125.0)
        self.assertAlmostEqual(e["initial_axial_thrust_N"]["LIMIT"], 85207530.1875)
        self.assertEqual(e["exhaust_velocity_km_s_range"], [300.0, 3000.0])
        self.assertEqual(e["normal_remass_t"], 250.0)

    def test_trade_does_not_hide_reaction_products(self):
        for family in self.r["technology_families"].values():
            self.assertIn("reaction_product_partition_gate", family)
            self.assertIn("nozzle_coupling_gate", family)
            self.assertIn("physical_realizability_gate", family)

    def test_family_disposition_is_not_component_certification(self):
        self.assertEqual(self.r["technology_families"]["D_HE3_FRC_DIRECT_FUSION_MAGNETIC_NOZZLE"]["disposition"], "LEADING_RESEARCH_ANALOG_NOT_CERTIFIED")
        self.assertEqual(self.r["technology_families"]["DT_DIRECT_FUSION_MAGNETIC_NOZZLE"]["disposition"], "HOLD_NEUTRON_AND_THERMAL_PARTITION")
        self.assertEqual(self.r["technology_families"]["PB11_DIRECT_FUSION_MAGNETIC_NOZZLE"]["disposition"], "HOLD_REACTIVITY_AND_BREMSSTRAHLUNG_REALIZABILITY")

    def test_next_step_and_holds_survive(self):
        self.assertEqual(self.r["qualified_next_step"], "BUILD_TORCH_DEPOSITION_PARTITION_MODEL_AND_FAMILY_KILL_CRITERIA")
        self.assertIn("PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP", self.r["carried_rcs_integration_holds"])
        self.assertIn("plasma_detachment_and_nozzle_efficiency", self.r["remaining_open"])


if __name__ == "__main__":
    unittest.main()
