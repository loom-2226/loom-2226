import unittest

from src.loom_metric_domain_intersection import (
    ExclusionClass,
    MovingDomainSegment,
    TimedPosition,
    check_metric_trajectory,
)
from src.loom_metric_domain_routing import NavigationPreferences


class MetricDomainIntersectionTests(unittest.TestCase):
    def trajectory(self):
        return [TimedPosition(0.0, (0.0, 0.0, 0.0)), TimedPosition(10.0, (10.0, 0.0, 0.0))]

    def test_clear_path_is_admissible(self):
        domain = MovingDomainSegment("JUPITER_SYSTEM", ExclusionClass.PHYSICAL, 1.0, TimedPosition(0.0, (5.0, 5.0, 0.0)), TimedPosition(10.0, (5.0, 5.0, 0.0)))
        result = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences())
        self.assertTrue(result.admissible)
        self.assertEqual(result.blocking_domains, ())

    def test_stationary_physical_domain_blocks_crossing(self):
        domain = MovingDomainSegment("JUPITER_SYSTEM", ExclusionClass.PHYSICAL, 1.0, TimedPosition(0.0, (5.0, 0.0, 0.0)), TimedPosition(10.0, (5.0, 0.0, 0.0)))
        result = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences())
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_domains, ("JUPITER_SYSTEM",))

    def test_moving_domain_crossing_path_is_detected_between_endpoints(self):
        domain = MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 0.5, TimedPosition(0.0, (5.0, 5.0, 0.0)), TimedPosition(10.0, (5.0, -5.0, 0.0)))
        result = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences())
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_domains, ("EARTH",))

    def test_regulatory_override_ignores_regulatory_domain_only(self):
        domain = MovingDomainSegment("TRAFFIC_ZONE", ExclusionClass.REGULATORY, 1.0, TimedPosition(0.0, (5.0, 0.0, 0.0)), TimedPosition(10.0, (5.0, 0.0, 0.0)))
        normal = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences())
        override = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences(regulatory_override_requested=True))
        self.assertFalse(normal.admissible)
        self.assertTrue(override.admissible)

    def test_regulatory_override_never_ignores_physical_domain(self):
        domain = MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, TimedPosition(0.0, (5.0, 0.0, 0.0)), TimedPosition(10.0, (5.0, 0.0, 0.0)))
        result = check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences(regulatory_override_requested=True))
        self.assertFalse(result.admissible)

    def test_epoch_mismatch_fails_closed(self):
        domain = MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, TimedPosition(1.0, (5.0, 0.0, 0.0)), TimedPosition(10.0, (5.0, 0.0, 0.0)))
        with self.assertRaises(ValueError):
            check_metric_trajectory(self.trajectory(), [domain], NavigationPreferences())

    def test_negative_radius_fails_closed(self):
        with self.assertRaises(ValueError):
            MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, -1.0, TimedPosition(0.0, (5.0, 0.0, 0.0)), TimedPosition(10.0, (5.0, 0.0, 0.0)))


if __name__ == "__main__":
    unittest.main()
