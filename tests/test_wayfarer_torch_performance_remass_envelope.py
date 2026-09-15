import unittest

from src.wayfarer_torch_performance_remass_envelope import build_torch_performance_remass_envelope


class TestWayfarerTorchPerformanceRemassEnvelope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = build_torch_performance_remass_envelope()

    def test_authority_boundary(self):
        a = self.r["authority"]
        self.assertEqual(self.r["status"], "PASS")
        self.assertEqual(a["claim"], "E1_TORCH_PERFORMANCE_REMASS_REQUIREMENT_ENVELOPE_ONLY")
        self.assertFalse(a["reactor_cycle_certified"])
        self.assertFalse(a["thermal_efficiency_certified"])
        self.assertFalse(a["jet_power_promoted_to_electrical_load"])
        self.assertFalse(a["canon_changed"])
        self.assertEqual(a["campaign_state_mutation"], "ZERO")
        self.assertEqual(a["llm_calculation_authority"], "ZERO")

    def test_recovers_all_working_cards(self):
        cards = self.r["operating_cards"]
        self.assertEqual(set(cards), {"ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"})
        self.assertEqual(cards["ECON"]["acceleration_g"], 0.30)
        self.assertEqual(cards["CRUISE"]["acceleration_g"], 1.00)
        self.assertEqual(cards["EXPEDITE"]["acceleration_g"], 2.00)
        self.assertEqual(cards["FAST"]["acceleration_g"], 3.00)
        self.assertEqual(cards["HARD"]["acceleration_g"], 5.00)
        self.assertEqual(cards["LIMIT"]["acceleration_g"], 7.50)
        self.assertEqual(cards["ECON"]["exhaust_velocity_km_s"], 3000.0)
        self.assertEqual(cards["LIMIT"]["exhaust_velocity_km_s"], 300.0)

    def test_performance_is_deterministically_derived_from_mass_accel_and_ve(self):
        for card in self.r["operating_cards"].values():
            self.assertGreater(card["initial_thrust_N_at_reference_wet_mass"], 0.0)
            self.assertGreater(card["initial_mass_flow_kg_s_at_reference_wet_mass"], 0.0)
            self.assertGreater(card["initial_direct_jet_power_W_at_reference_wet_mass"], 0.0)
            self.assertAlmostEqual(
                card["initial_thrust_N_at_reference_wet_mass"],
                card["initial_mass_flow_kg_s_at_reference_wet_mass"] * card["exhaust_velocity_m_s"],
                places=5,
            )
            self.assertAlmostEqual(
                card["initial_direct_jet_power_W_at_reference_wet_mass"],
                0.5 * card["initial_thrust_N_at_reference_wet_mass"] * card["exhaust_velocity_m_s"],
                places=2,
            )

    def test_remass_burn_envelope_preserves_protected_reserve(self):
        remass = self.r["normal_remass_envelope"]
        self.assertEqual(remass["normal_remass_available_t"], 250.0)
        self.assertEqual(remass["protected_water_reserve_t"], 50.0)
        self.assertEqual(remass["reference_wet_mass_t"], 1158.5)
        self.assertEqual(remass["post_normal_remass_reference_mass_t"], 908.5)
        for mode, row in remass["constant_card_full_normal_remass_burn"].items():
            self.assertGreater(row["burn_duration_s"], 0.0, mode)
            self.assertGreater(row["ideal_delta_v_km_s"], 0.0, mode)
            self.assertEqual(row["normal_remass_consumed_t"], 250.0)
            self.assertEqual(row["protected_water_consumed_t"], 0.0)

    def test_next_step_closes_thermal_and_load_interfaces(self):
        self.assertEqual(
            self.r["qualified_next_step"],
            "DERIVE_TORCH_THERMAL_SHIELDING_AND_THRUST_FRAME_REQUIREMENT_ENVELOPES_WITH_REACTOR_CYCLE_STILL_OPEN",
        )


if __name__ == "__main__":
    unittest.main()
