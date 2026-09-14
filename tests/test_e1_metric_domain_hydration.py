import unittest

from src.loom_metric_domain_hydration import (
    MetricDomainPolicy,
    MetricRouteSample,
    hydrate_metric_route,
)
from src.loom_metric_domain_intersection import ExclusionClass
from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError, SpatialState


class Resolver:
    def __init__(self, grade=True, frame=CANONICAL_FRAME):
        self.grade = grade
        self.frame = frame

    def resolve(self, entity_id, epoch_utc):
        hour = int(epoch_utc[11:13])
        return SpatialState(
            entity_id=entity_id,
            epoch_utc=epoch_utc,
            reference_frame=self.frame,
            position_km=(float(hour), 0.0, 0.0),
            velocity_km_s=(1.0, 0.0, 0.0),
            provenance={"state_source": "TEST"},
            navigation_grade=self.grade,
        )


class E1MetricDomainHydrationTests(unittest.TestCase):
    def test_hydrates_every_route_leg_from_shared_state_authority(self):
        samples = (
            MetricRouteSample("2226-08-22T00:00:00Z", (0, 0, 0)),
            MetricRouteSample("2226-08-22T01:00:00Z", (10, 0, 0)),
            MetricRouteSample("2226-08-22T02:00:00Z", (20, 0, 0)),
        )
        policies = (MetricDomainPolicy("NEPTUNE_DOMAIN", "NEPTUNE", ExclusionClass.PHYSICAL, 5.0),)
        hydrated = hydrate_metric_route(samples, policies, Resolver())
        self.assertEqual(len(hydrated.trajectory), 3)
        self.assertEqual(len(hydrated.domains), 2)
        self.assertEqual(hydrated.domains[0].start.position, (0.0, 0.0, 0.0))
        self.assertEqual(hydrated.domains[0].end.position, (1.0, 0.0, 0.0))
        self.assertEqual(hydrated.domains[1].end.position, (2.0, 0.0, 0.0))

    def test_metric_routing_requires_navigation_grade_centers(self):
        samples = (
            MetricRouteSample("2226-08-22T00:00:00Z", (0, 0, 0)),
            MetricRouteSample("2226-08-22T01:00:00Z", (1, 0, 0)),
        )
        policies = (MetricDomainPolicy("JUPITER_DOMAIN", "JUPITER", ExclusionClass.PHYSICAL, 5.0),)
        with self.assertRaises(CelestialStateError):
            hydrate_metric_route(samples, policies, Resolver(grade=False))

    def test_noncanonical_center_frame_fails_closed(self):
        samples = (
            MetricRouteSample("2226-08-22T00:00:00Z", (0, 0, 0)),
            MetricRouteSample("2226-08-22T01:00:00Z", (1, 0, 0)),
        )
        policies = (MetricDomainPolicy("JUPITER_DOMAIN", "JUPITER", ExclusionClass.PHYSICAL, 5.0),)
        with self.assertRaises(CelestialStateError):
            hydrate_metric_route(samples, policies, Resolver(frame="WRONG"))

    def test_duplicate_domain_ids_fail_closed(self):
        samples = (
            MetricRouteSample("2226-08-22T00:00:00Z", (0, 0, 0)),
            MetricRouteSample("2226-08-22T01:00:00Z", (1, 0, 0)),
        )
        policies = (
            MetricDomainPolicy("X", "A", ExclusionClass.PHYSICAL, 1.0),
            MetricDomainPolicy("X", "B", ExclusionClass.REGULATORY, 1.0),
        )
        with self.assertRaises(ValueError):
            hydrate_metric_route(samples, policies, Resolver())


if __name__ == "__main__":
    unittest.main()
