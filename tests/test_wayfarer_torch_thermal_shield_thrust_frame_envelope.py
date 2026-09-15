import unittest

from src.wayfarer_torch_thermal_shield_thrust_frame_envelope import build_envelope


class TorchThermalShieldThrustFrameEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.payload = build_envelope()

    def test_authority_firewall(self):
        a = self.payload["authority"]
        self.assertEqual(a["claim"], "E1_TORCH_THERMAL_SHIELDING_AND_THRUST_FRAME_REQUIREMENT_ENVELOPE_ONLY")
        self.assertFalse(a["reactor_cycle_certified"])
        self.assertFalse(a["waste_heat_fraction_certified"])
        self.assertFalse(a["radiation_partition_certified"])
        self.assertFalse(a["shadow_shield_stack_certified"])
        self.assertFalse(a["thrust_frame_design_certified"])
        self.assertFalse(a["physical_radiator_geometry_certified"])
        self.assertFalse(a["archive_values_promoted_to_current_authority"])
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")

    def test_current_and_candidate_sources_are_separated(self):
        s = self.payload["source_status"]
        self.assertEqual(s["current_authority"]["radiator_count"], 4)
        self.assertEqual(s["current_authority"]["high_drive_reject_interface_K"], 900.0)
        self.assertEqual(s["candidate_packaging"]["shadow_shield_x_m"], [38.0, 43.0])
        self.assertEqual(s["candidate_packaging"]["reactor_thrust_frame_x_m"], [43.0, 50.0])
        self.assertEqual(s["candidate_packaging"]["magnetic_nozzle_x_m"], [50.0, 57.0])
        self.assertEqual(s["archived_provenance"]["status"], "SENSITIVITY_INPUT_ONLY_NOT_CURRENT_AUTHORITY")

    def test_mode_loads_are_inherited_from_qualified_performance_envelope(self):
        modes = self.payload["thrust_frame_requirement_envelope"]["modes"]
        self.assertAlmostEqual(modes["LIMIT"]["initial_axial_thrust_N"], 85207530.1875)
        self.assertAlmostEqual(modes["ECON"]["initial_axial_thrust_N"], 3408301.2075)
        self.assertEqual(self.payload["thrust_frame_requirement_envelope"]["governing_known_axial_load_mode"], "LIMIT")
        self.assertIsNone(self.payload["thrust_frame_requirement_envelope"]["structural_design_factor"])

    def test_thermal_result_is_sensitivity_not_certification(self):
        t = self.payload["thermal_requirement_envelope"]
        self.assertEqual(t["jet_power_interpretation"], "KINETIC_EXHAUST_POWER_NOT_ELECTRICAL_LOAD_OR_WASTE_HEAT")
        self.assertIsNone(t["certified_torch_deposition_fraction"])
        self.assertTrue(t["archived_deposition_sensitivity"]["non_governing"])
        self.assertGreater(t["archived_deposition_sensitivity"]["cases"]["LIMIT_100_PPM"]["initial_deposition_W"], 1e9)

    def test_open_items_and_rcs_holds_survive(self):
        self.assertIn("reactor_cycle_and_fusion_architecture", self.payload["remaining_open"])
        self.assertIn("shadow_shield_materials_and_layering", self.payload["remaining_open"])
        self.assertIn("thrust_frame_structural_design_factor_and_local_stress", self.payload["remaining_open"])
        self.assertIn("PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP", self.payload["carried_rcs_integration_holds"])
        self.assertEqual(len(self.payload["carried_rcs_integration_holds"]), 5)


if __name__ == "__main__":
    unittest.main()
