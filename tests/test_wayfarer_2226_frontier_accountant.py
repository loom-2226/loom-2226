import unittest
from fractions import Fraction

from src.wayfarer_2226_frontier_accountant import (
    SCENARIOS,
    radiator_flux_w_m2,
    conversion_chain,
    assess_frontier_case,
)


class FrontierAccountantTests(unittest.TestCase):
    def test_scenarios_are_bounded_and_below_perfection(self):
        self.assertEqual(set(SCENARIOS), {"CONSERVATIVE_2226", "MVP_2226", "AGGRESSIVE_2226"})
        for case in SCENARIOS.values():
            self.assertGreater(case.conversion_efficiency, 0)
            self.assertLess(case.conversion_efficiency, 1)
            self.assertGreater(case.pmad_efficiency, 0)
            self.assertLess(case.pmad_efficiency, 1)
            self.assertGreater(case.radiator_emissivity, 0)
            self.assertLess(case.radiator_emissivity, 1)

    def test_conversion_chain_preserves_losses_as_heat(self):
        r = conversion_chain(Fraction(1_000_000), "MVP_2226")
        self.assertEqual(r["load_power_w"] + r["conversion_loss_w"] + r["pmad_loss_w"], Fraction(1_000_000))
        self.assertGreater(r["conversion_loss_w"], 0)
        self.assertGreater(r["pmad_loss_w"], 0)

    def test_radiator_flux_obeys_stefan_boltzmann(self):
        q900 = radiator_flux_w_m2(Fraction(900), Fraction(9, 10))
        q1000 = radiator_flux_w_m2(Fraction(1000), Fraction(9, 10))
        self.assertGreater(q1000, q900)
        self.assertEqual(q1000 / q900, Fraction(1000**4, 900**4))

    def test_unearned_inputs_remain_unresolved(self):
        r = assess_frontier_case("MVP_2226")
        self.assertIsNone(r["large_system_continuous_field_t"])
        self.assertIsNone(r["fusion_source_specific_power_w_kg"])
        self.assertIsNone(r["rcs_exhaust_velocity_m_s"])
        self.assertIsNone(r["e2_momentum_partner"])
        self.assertIsNone(r["metric_constitutive_law"])

    def test_accountant_exposes_cross_frontier_heat_and_dependencies(self):
        r = assess_frontier_case("MVP_2226", source_electrical_power_w=Fraction(100_000_000), radiator_temperature_k=Fraction(900))
        self.assertGreater(r["pmad_and_conversion_heat_w"], 0)
        self.assertGreater(r["radiator_area_for_pmad_and_conversion_m2"], 0)
        self.assertIn("F2_POWER", r["consumed_frontiers"])
        self.assertIn("F5_THERMAL", r["consumed_frontiers"])
        self.assertIn("F1_FIELD_REQUIRES_COUPLED_MODEL", r["holds"])


if __name__ == "__main__":
    unittest.main()
