import unittest

from src.loom_metric_domain_intersection import (
    ExclusionClass,
    MovingDomainSegment,
    TimedPosition,
    check_metric_route,
)
from src.loom_metric_domain_routing import NavigationPreferences


class MetricDomainRouteSequenceTests(unittest.TestCase):
    def p(self, t, x, y=0.0, z=0.0):
        return TimedPosition(t, (x, y, z))

    def test_multisegment_route_checks_every_leg(self):
        route = [self.p(0, 0), self.p(10, 10), self.p(20, 20)]
        domains = [
            MovingDomainSegment("JUPITER", ExclusionClass.PHYSICAL, 1.0, self.p(0, 50), self.p(10, 50)),
            MovingDomainSegment("JUPITER", ExclusionClass.PHYSICAL, 1.0, self.p(10, 15), self.p(20, 15)),
        ]
        result = check_metric_route(route, domains, NavigationPreferences())
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_domains, ("JUPITER",))
        self.assertEqual(result.blocking_segment_indexes, (1,))

    def test_authorized_origin_boundary_crossing_is_exempt_only_on_first_leg(self):
        route = [self.p(0, 0), self.p(10, 10), self.p(20, 20)]
        domains = [
            MovingDomainSegment("CERES", ExclusionClass.PHYSICAL, 2.0, self.p(0, 0), self.p(10, 0)),
            MovingDomainSegment("CERES", ExclusionClass.PHYSICAL, 2.0, self.p(10, 15), self.p(20, 15)),
        ]
        result = check_metric_route(route, domains, NavigationPreferences(), origin_domain_id="CERES")
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_segment_indexes, (1,))

    def test_destination_boundary_contact_is_allowed_on_final_leg(self):
        route = [self.p(0, 0), self.p(10, 10), self.p(20, 20)]
        domains = [
            MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, self.p(0, 20), self.p(10, 20)),
            MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, self.p(10, 20), self.p(20, 20)),
        ]
        result = check_metric_route(route, domains, NavigationPreferences(), destination_domain_id="EARTH")
        self.assertTrue(result.admissible)

    def test_destination_is_not_exempt_on_an_earlier_leg(self):
        route = [self.p(0, 0), self.p(10, 10), self.p(20, 20)]
        domains = [
            MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, self.p(0, 5), self.p(10, 5)),
            MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, self.p(10, 20), self.p(20, 20)),
        ]
        result = check_metric_route(route, domains, NavigationPreferences(), destination_domain_id="EARTH")
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_segment_indexes, (0,))

    def test_reports_exclusion_class_and_clearance(self):
        route = [self.p(0, 0), self.p(10, 10)]
        domains = [MovingDomainSegment("TRAFFIC", ExclusionClass.REGULATORY, 2.0, self.p(0, 5, 1), self.p(10, 5, 1))]
        result = check_metric_route(route, domains, NavigationPreferences())
        self.assertEqual(len(result.encounters), 1)
        hit = result.encounters[0]
        self.assertEqual(hit.exclusion_class, ExclusionClass.REGULATORY)
        self.assertAlmostEqual(hit.minimum_clearance, -1.0)
        self.assertAlmostEqual(hit.closest_fraction, 0.5)

    def test_domain_segments_must_cover_route_legs_exactly(self):
        route = [self.p(0, 0), self.p(10, 10), self.p(20, 20)]
        domains = [MovingDomainSegment("EARTH", ExclusionClass.PHYSICAL, 1.0, self.p(0, 5), self.p(20, 5))]
        with self.assertRaises(ValueError):
            check_metric_route(route, domains, NavigationPreferences())


if __name__ == "__main__":
    unittest.main()
