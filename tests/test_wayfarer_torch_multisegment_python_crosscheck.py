import unittest
from src.wayfarer_torch_feed_dynamics_nozzle import MODES


def outputs(mode):
    mdot, ve = MODES[mode]
    return mdot, mdot * ve, 0.5 * mdot * ve * ve


class MultiSegmentPythonCrosscheck(unittest.TestCase):
    def test_high_thrust_power_window_uniquely_selects_fast(self):
        feasible = []
        for mode in MODES:
            _, thrust, power = outputs(mode)
            if thrust >= 30_000_000 and power <= 12_000_000_000_000:
                feasible.append(mode)
        self.assertEqual(feasible, ["FAST"])

    def test_three_segment_plan_has_at_least_one_middle_card_and_reserve(self):
        fast_mdot, _, _ = outputs("FAST")
        middle = []
        for mode in MODES:
            mdot, thrust, power = outputs(mode)
            if thrust >= 10_000_000 and power <= 11_500_000_000_000:
                remaining_t = 250 - (fast_mdot * 300 + mdot * 1200 + fast_mdot * 300) / 1000
                if remaining_t >= 180:
                    middle.append((mode, remaining_t))
        self.assertTrue(middle)

    def test_one_hour_limit_cannot_keep_200_t(self):
        mdot, _, _ = outputs("LIMIT")
        remaining_t = 250 - mdot * 3600 / 1000
        self.assertLess(remaining_t, 200)


if __name__ == "__main__":
    unittest.main()
