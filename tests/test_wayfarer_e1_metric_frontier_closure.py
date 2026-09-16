import unittest
from fractions import Fraction

from src.wayfarer_e1_metric_frontier_closure import build_metric_closure


class MetricFrontierClosureTests(unittest.TestCase):
    def test_governing_metric_card_is_preserved(self):
        out = build_metric_closure("MVP_2226")
        self.assertEqual(out["status"], "E1_METRIC_INTERFACE_CLOSED_WITH_PHYSICS_VALIDATION_HOLDS")
        self.assertEqual(out["plant"]["mass_kg"], Fraction(88_000))
        self.assertEqual(out["plant"]["mc299m_kg"], Fraction(10))
        self.assertEqual(out["plant"]["nodes"], 208)
        self.assertEqual(out["plant"]["shared_bank_j"], Fraction(2_000_000_000))
        self.assertEqual(out["modes"]["HARD"]["beta"], Fraction(595, 1000))
        self.assertEqual(out["modes"]["HARD"]["cold_load_w"], Fraction(136_000))
        self.assertEqual(out["modes"]["HARD"]["delivered_electrical_w"], Fraction(23_900_000))
        self.assertEqual(out["modes"]["HARD"]["canon_900k_equivalent_area_m2"], Fraction(719))

    def test_frontier_pays_upstream_losses_without_rewriting_canon_load(self):
        out = build_metric_closure("MVP_2226")
        hard = out["modes"]["HARD"]
        self.assertEqual(hard["delivered_electrical_w"], Fraction(23_900_000))
        self.assertGreater(hard["required_upstream_electrical_w"], hard["delivered_electrical_w"])
        self.assertEqual(hard["distribution_heat_w"], hard["required_upstream_electrical_w"] - hard["delivered_electrical_w"])

    def test_frontier_does_not_rederive_metric_mechanism(self):
        out = build_metric_closure("MVP_2226")
        physics = out["physics_authority"]
        self.assertEqual(physics["constitutive_law"], "CANON_PHYSICS_AUTHORITY_ONLY")
        self.assertEqual(physics["mc299m_properties"], "CANON_PHYSICS_AUTHORITY_ONLY")
        self.assertIsNone(physics["large_system_continuous_field_t"])
        self.assertFalse(out["component_hardware_certified"])

    def test_open_holds_are_validation_not_e1_interface_blockers(self):
        out = build_metric_closure("MVP_2226")
        self.assertEqual(out["open_blocking_e1"], ())
        self.assertIn("FULL_TIME_DEPENDENT_4D_FINITE_RSET_BENCHMARK", out["physics_validation_holds"])
        self.assertIn("METRIC_ENVIRONMENT_CORRECTION_POWER_AND_THERMAL_CALIBRATION", out["physics_validation_holds"])
        self.assertIn("PATH_DEPENDENT_ORDINARY_STATE_PROPAGATOR_CALIBRATION", out["physics_validation_holds"])
        self.assertTrue(out["operating_rules"]["torch_high_metric_mutually_exclusive"])
        self.assertTrue(out["operating_rules"]["ftl_metric_black"])

    def test_producer_provenance_is_pinned(self):
        out = build_metric_closure("MVP_2226")
        self.assertTrue(out["producer_version_hash"])
        self.assertEqual(out["frontier_authority"], "FROZEN_SUPPORT_PRODUCERS_CONSUMED_WITHOUT_NEW_PHYSICS")


if __name__ == "__main__":
    unittest.main()
