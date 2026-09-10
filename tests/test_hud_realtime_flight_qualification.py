import unittest

from loom.hud.realtime_flight_qualification import (
    ALLOWED_TIME_SCALES,
    INITIAL_REMASS_T,
    INITIAL_WET_MASS_T,
    MOON_RADIUS_KM,
    TORCH_CARDS,
    WAYFARER_LENGTH_KM,
)


class RealtimeFlightQualificationContractTests(unittest.TestCase):
    def test_physical_scale_constants_are_explicit(self):
        self.assertEqual(MOON_RADIUS_KM, 1737.4)
        self.assertEqual(WAYFARER_LENGTH_KM, 0.057)

    def test_wayfarer_mass_inputs_match_current_engineering_baseline(self):
        self.assertEqual(INITIAL_REMASS_T, 250.0)
        self.assertEqual(INITIAL_WET_MASS_T, 1158.5)

    def test_torch_working_cards_are_preserved(self):
        expected = {
            "ECON": (0.30, 3000.0),
            "CRUISE": (1.00, 2000.0),
            "EXPEDITE": (2.00, 1000.0),
            "FAST": (3.00, 700.0),
            "HARD": (5.00, 450.0),
            "LIMIT": (7.50, 300.0),
        }
        self.assertEqual(set(TORCH_CARDS), set(expected))
        for mode, (accel, exhaust) in expected.items():
            self.assertEqual(TORCH_CARDS[mode]["acceleration_g"], accel)
            self.assertEqual(TORCH_CARDS[mode]["exhaust_velocity_km_s"], exhaust)

    def test_time_scale_choices_are_bounded_and_include_realtime(self):
        self.assertEqual(ALLOWED_TIME_SCALES, (0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0))


if __name__ == "__main__":
    unittest.main()
