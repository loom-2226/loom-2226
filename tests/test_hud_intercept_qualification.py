import math
import unittest

from loom.hud.intercept_qualification import CONTRACT, _unit, solve_moon_intercept


class HudInterceptQualificationTests(unittest.TestCase):
    def test_contract_is_explicitly_qualification_only_surface(self):
        self.assertEqual(CONTRACT, "LOOM_HUD_INTERCEPT_PREVIEW_QUALIFICATION_V1")

    def test_unit_vector_helper(self):
        v = _unit((3.0, 4.0, 0.0))
        self.assertAlmostEqual(v[0], 0.6)
        self.assertAlmostEqual(v[1], 0.8)
        self.assertAlmostEqual(math.sqrt(sum(x*x for x in v)), 1.0)

    def test_zero_direction_fails_closed(self):
        with self.assertRaises(ValueError):
            _unit((0.0, 0.0, 0.0))

    def test_invalid_mode_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_intercept(None, max_time_s=3600.0, mode="NOPE")

    def test_invalid_horizon_rejected_before_session_access(self):
        with self.assertRaises(ValueError):
            solve_moon_intercept(None, max_time_s=100.0, mode="CRUISE")


if __name__ == "__main__":
    unittest.main()
