import unittest

from loom.hud.realtime_flight_qualification import (
    ALLOWED_TIME_SCALES,
    ENGINEERING_SOURCE_COMMIT,
    INITIAL_REMASS_T,
    INITIAL_WET_MASS_T,
    MOON_RADIUS_KM,
    PROTECTED_WATER_RESERVE_T,
    TORCH_CARDS,
    WAYFARER_LENGTH_KM,
)
from loom.hud.wayfarer_engineering_state import load_wayfarer_engineering_state


class RealtimeFlightQualificationContractTests(unittest.TestCase):
    def test_physical_scale_constants_are_explicit(self):
        self.assertEqual(MOON_RADIUS_KM, 1737.4)
        self.assertEqual(WAYFARER_LENGTH_KM, 0.057)

    def test_wayfarer_mass_inputs_are_derived_from_pinned_engineering_handoff(self):
        engineering = load_wayfarer_engineering_state()
        self.assertEqual(ENGINEERING_SOURCE_COMMIT, engineering["source"]["commit"])
        self.assertEqual(INITIAL_REMASS_T, engineering["mass"]["normal_remass_allowance_t"])
        self.assertEqual(INITIAL_WET_MASS_T, engineering["mass"]["reference_wet_mass_t"])
        self.assertEqual(PROTECTED_WATER_RESERVE_T, engineering["mass"]["protected_water_reserve_t"])
        self.assertEqual(INITIAL_REMASS_T, 250.0)
        self.assertEqual(INITIAL_WET_MASS_T, 1158.5)
        self.assertEqual(PROTECTED_WATER_RESERVE_T, 50.0)

    def test_torch_working_cards_are_derived_from_engineering_object(self):
        engineering = load_wayfarer_engineering_state()
        source_cards = engineering["torch"]["mode_cards"]
        self.assertEqual(set(TORCH_CARDS), set(source_cards))
        for mode, card in TORCH_CARDS.items():
            self.assertEqual(card["acceleration_g"], source_cards[mode]["acceleration_g"])
            self.assertEqual(card["exhaust_velocity_km_s"], source_cards[mode]["exhaust_velocity_km_s"])
            self.assertEqual(source_cards[mode]["status"], "WORKING_ENGINEERING_CARD")

    def test_handoff_preserves_momentum_and_power_firewalls(self):
        engineering = load_wayfarer_engineering_state()
        self.assertTrue(engineering["torch"]["ordinary_momentum_exchange_required"])
        self.assertFalse(engineering["torch"]["jet_power_is_electrical_bus_power"])
        self.assertFalse(engineering["mobility_firewall"]["metric_ordinary_velocity_reset_allowed"])
        self.assertTrue(engineering["mobility_firewall"]["torch_terminal_state_matching_required_when_needed"])

    def test_time_scale_choices_are_bounded_and_include_realtime(self):
        self.assertEqual(ALLOWED_TIME_SCALES, (0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0))


if __name__ == "__main__":
    unittest.main()
