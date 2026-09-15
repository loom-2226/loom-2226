import unittest
from fractions import Fraction

from src.wayfarer_2226_frontier_consumers import build_consumer_exercise


class FrontierConsumerExerciseTests(unittest.TestCase):
    def test_canon_and_e1_are_both_consumed(self):
        r = build_consumer_exercise("MVP_2226")
        self.assertIn("CANON_II_V2_4", r["authority_inputs"])
        self.assertIn("CANON_II_WAYFARER_SCHEMATIC_V2_4A", r["authority_inputs"])
        self.assertIn("E1_RCS_FROZEN_INTERFACE", r["authority_inputs"])
        self.assertIn("E1_TORCH_T5_FROZEN_INTERFACE", r["authority_inputs"])

    def test_canon_metric_load_is_fixed_and_upstream_power_pays_losses(self):
        r = build_consumer_exercise("MVP_2226")
        hard = r["metric"]["HARD"]
        load = Fraction(23_900_000)
        self.assertEqual(hard["canon_cryo_electrical_w"], load)
        self.assertEqual(hard["frontier_delivered_load_w"], load)
        self.assertGreater(hard["frontier_required_upstream_electrical_w"], load)
        self.assertEqual(
            hard["frontier_distribution_heat_w"],
            hard["frontier_required_upstream_electrical_w"] - load,
        )
        self.assertGreater(hard["frontier_distribution_radiator_area_m2"], 0)
        self.assertEqual(r["metric"]["shared_bank_j"], Fraction(2_000_000_000))
        self.assertEqual(r["metric"]["node_count"], 208)

    def test_torch_requirements_are_preserved_without_fake_source_closure(self):
        r = build_consumer_exercise("MVP_2226")
        t = r["torch"]
        self.assertEqual(t["wet_mass_kg"], Fraction(1_158_500))
        self.assertEqual(t["normal_remass_kg"], Fraction(250_000))
        self.assertEqual(t["protected_water_kg"], Fraction(50_000))
        self.assertEqual(t["feed_turndown_ratio"], Fraction(250))
        self.assertEqual(t["radiator_count"], 4)
        self.assertEqual(t["reject_temperature_k"], Fraction(900))
        self.assertIsNone(t["source_specific_power_w_kg"])
        self.assertIsNone(t["source_directed_fraction"])
        self.assertIsNone(t["magnetic_nozzle_field_t"])

    def test_rcs_requirements_are_preserved_without_selecting_hardware(self):
        r = build_consumer_exercise("MVP_2226")
        x = r["rcs"]
        self.assertEqual(x["mount_count"], 16)
        self.assertEqual(x["mount_force_cap_n"], Fraction(25_000))
        self.assertEqual(x["nominal_translation_n"], Fraction(100_000))
        self.assertEqual(x["degraded_translation_n"], Fraction(75_000))
        self.assertEqual(x["max_sampled_mount_thrust_n"], Fraction("20844.756650298394"))
        self.assertIsNone(x["working_fluid"])
        self.assertIsNone(x["exhaust_velocity_m_s"])
        self.assertIsNone(x["hardware_mib_n_s"])

    def test_packaging_and_mutual_exclusion_are_not_lost(self):
        r = build_consumer_exercise("MVP_2226")
        self.assertEqual(r["packaging"]["launch_bay_x_m"], (Fraction(16), Fraction(28)))
        self.assertEqual(r["packaging"]["main_body_diameter_m"], Fraction(9))
        self.assertTrue(r["operating_rules"]["torch_high_metric_mutually_exclusive"])
        self.assertEqual(r["packaging"]["aft_rcs_x_m"], Fraction("44.5"))


if __name__ == "__main__":
    unittest.main()
