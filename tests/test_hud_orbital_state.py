import math
import unittest

from loom.hud.orbital_state import EARTH_RADIUS_KM, earth_orbital_state


class HudOrbitalStateTests(unittest.TestCase):
    MU = 398600.435436

    def test_circular_400km_orbit_is_bound_and_nearly_circular(self):
        radius = EARTH_RADIUS_KM + 400.0
        speed = math.sqrt(self.MU / radius)
        state = earth_orbital_state((radius, 0, 0), (0, speed, 0), self.MU)
        self.assertEqual(state["classification"], "BOUND_ELLIPTIC")
        self.assertAlmostEqual(state["altitude_km"], 400.0, places=6)
        self.assertAlmostEqual(state["eccentricity"], 0.0, places=9)
        self.assertAlmostEqual(state["periapsis_altitude_km"], 400.0, places=6)
        self.assertAlmostEqual(state["apoapsis_altitude_km"], 400.0, places=6)
        self.assertGreater(state["period_s"], 5000.0)
        self.assertFalse(state["navigation_grade"])

    def test_escape_state_is_not_given_fake_apoapsis_or_period(self):
        radius = EARTH_RADIUS_KM + 400.0
        escape = math.sqrt(2.0 * self.MU / radius) * 1.01
        state = earth_orbital_state((radius, 0, 0), (0, escape, 0), self.MU)
        self.assertEqual(state["classification"], "ESCAPE_HYPERBOLIC")
        self.assertIsNone(state["apoapsis_altitude_km"])
        self.assertIsNone(state["period_s"])

    def test_radial_state_is_explicitly_degenerate(self):
        radius = EARTH_RADIUS_KM + 400.0
        state = earth_orbital_state((radius, 0, 0), (1.0, 0, 0), self.MU)
        self.assertEqual(state["classification"], "DEGENERATE_RADIAL")


if __name__ == "__main__":
    unittest.main()
