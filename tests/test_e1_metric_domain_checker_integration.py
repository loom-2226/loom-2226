import unittest

from src.loom_metric_domain_hydration import MetricDomainPolicy, MetricRouteSample, hydrate_metric_route
from src.loom_metric_domain_intersection import ExclusionClass, check_metric_route
from src.loom_metric_domain_routing import NavigationPreferences
from src.loom_spatial_state_authority import CANONICAL_FRAME, SpatialState


class StaticResolver:
    def __init__(self, centers):
        self.centers = centers

    def resolve(self, entity_id, epoch_utc):
        return SpatialState(
            entity_id=entity_id,
            epoch_utc=epoch_utc,
            reference_frame=CANONICAL_FRAME,
            position_km=self.centers[entity_id],
            velocity_km_s=(0, 0, 0),
            provenance={"state_source": "E1_TEST"},
            navigation_grade=True,
        )


class E1MetricDomainCheckerIntegrationTests(unittest.TestCase):
    def test_ceres_departure_neptune_arrival_and_intermediate_blocker_semantics(self):
        samples = (
            MetricRouteSample("2226-08-22T00:00:00Z", (0, 0, 0)),
            MetricRouteSample("2226-08-22T01:00:00Z", (10, 0, 0)),
            MetricRouteSample("2226-08-22T02:00:00Z", (20, 0, 0)),
        )
        policies = (
            MetricDomainPolicy("CERES_DOMAIN", "CERES", ExclusionClass.PHYSICAL, 1.0),
            MetricDomainPolicy("JUPITER_DOMAIN", "JUPITER", ExclusionClass.PHYSICAL, 1.0),
            MetricDomainPolicy("NEPTUNE_DOMAIN", "NEPTUNE", ExclusionClass.PHYSICAL, 1.0),
        )
        resolver = StaticResolver({"CERES": (0, 0, 0), "JUPITER": (15, 0, 0), "NEPTUNE": (20, 0, 0)})
        hydrated = hydrate_metric_route(samples, policies, resolver)
        result = check_metric_route(
            hydrated.trajectory,
            hydrated.domains,
            NavigationPreferences(),
            origin_domain_id="CERES_DOMAIN",
            destination_domain_id="NEPTUNE_DOMAIN",
        )
        self.assertFalse(result.admissible)
        self.assertEqual(result.blocking_domains, ("JUPITER_DOMAIN",))


if __name__ == "__main__":
    unittest.main()
