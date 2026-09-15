import unittest
from fractions import Fraction

from src.wayfarer_e1_torch_remass_feed_nozzle import remass_feed_nozzle_envelope
from src.wayfarer_torch_mode_cards import MODE_CARDS, NORMAL_REMASS_KG, PROTECTED_WATER_KG


class TestWayfarerE1TorchRemassFeedNozzle(unittest.TestCase):
    def test_unresolved_physics_remain_explicit_holds(self):
        r = remass_feed_nozzle_envelope()
        self.assertIsNone(r.remass_species)
        self.assertIsNone(r.feed_hardware)
        self.assertIsNone(r.nozzle_efficiency)
        self.assertIsNone(r.feed_response_time_s)
        self.assertIsNone(r.feed_pressure_pa)
        self.assertIn("REMASS_SPECIES_OPEN", r.holds)
        self.assertIn("FEED_HARDWARE_OPEN", r.holds)
        self.assertIn("NOZZLE_EFFICIENCY_OPEN", r.holds)
        self.assertFalse(r.hardware_certified)

    def test_earned_inventory_and_exact_mode_flow_envelope_are_preserved(self):
        r = remass_feed_nozzle_envelope()
        expected = tuple((name, values[0], values[1]) for name, values in MODE_CARDS.items())
        self.assertEqual(r.normal_remass_kg, NORMAL_REMASS_KG)
        self.assertEqual(r.protected_water_kg, PROTECTED_WATER_KG)
        self.assertEqual(r.mode_flow_velocity, expected)
        self.assertEqual(r.min_mass_flow_kg_s, MODE_CARDS["ECON"][0])
        self.assertEqual(r.max_mass_flow_kg_s, MODE_CARDS["LIMIT"][0])
        self.assertEqual(r.turndown_ratio, Fraction(250))

    def test_protected_water_is_not_selected_as_normal_remass(self):
        r = remass_feed_nozzle_envelope()
        self.assertEqual(r.normal_remass_kg, Fraction(250_000))
        self.assertEqual(r.protected_water_kg, Fraction(50_000))
        self.assertIn("PROTECTED_WATER_NOT_NORMAL_REMASS", r.holds)

    def test_explicit_candidate_inputs_are_sensitivity_only(self):
        r = remass_feed_nozzle_envelope(
            remass_species="EXPLICIT_TEST_SPECIES",
            feed_hardware="EXPLICIT_TEST_FEED",
            nozzle_efficiency=Fraction(9, 10),
            feed_response_time_s=Fraction(1, 4),
            feed_pressure_pa=Fraction(2_000_000),
        )
        self.assertEqual(r.remass_species, "EXPLICIT_TEST_SPECIES")
        self.assertEqual(r.feed_hardware, "EXPLICIT_TEST_FEED")
        self.assertEqual(r.nozzle_efficiency, Fraction(9, 10))
        self.assertNotIn("REMASS_SPECIES_OPEN", r.holds)
        self.assertNotIn("FEED_HARDWARE_OPEN", r.holds)
        self.assertNotIn("NOZZLE_EFFICIENCY_OPEN", r.holds)
        self.assertFalse(r.hardware_certified)
        self.assertEqual(r.status, "SENSITIVITY_ONLY_EXPLICIT_INPUTS")

    def test_invalid_candidate_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            remass_feed_nozzle_envelope(nozzle_efficiency=Fraction(0))
        with self.assertRaises(ValueError):
            remass_feed_nozzle_envelope(feed_response_time_s=Fraction(-1))
        with self.assertRaises(ValueError):
            remass_feed_nozzle_envelope(feed_pressure_pa=Fraction(0))
        with self.assertRaises(ValueError):
            remass_feed_nozzle_envelope(remass_species="")
        with self.assertRaises(ValueError):
            remass_feed_nozzle_envelope(feed_hardware="")


if __name__ == "__main__":
    unittest.main()
