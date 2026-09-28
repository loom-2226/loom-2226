"""Bounded Roo-ver segment screen; no trajectory or provider capacity proxy."""
from dataclasses import replace
import unittest

from src.loom_spatial_state_authority import SpatialState

from .roover_service import RooVerRequest
from .roover_transport import SolarContext, assess_roover_transport


EPOCH = '2030-07-01T00:00:00Z'


def context() -> SolarContext:
    provenance = {'units': 'km,km/s', 'ephemeris_source_id': 'DE440',
                  'state_source': 'LOCAL_SPICE'}
    earth = SpatialState('EARTH', EPOCH, 'J2000/ECLIPTIC', (0, 0, 0), (0, 0, 0),
                         provenance, True)
    moon = SpatialState('MOON', EPOCH, 'J2000/ECLIPTIC', (384000, 0, 0), (0, 1, 0),
                        provenance, True)
    return SolarContext(EPOCH, earth, moon, 'registry-hash', 'manifest-hash')


def statuses(result):
    return {segment.name: segment.status for segment in result.segments}


class RooVerTransportTests(unittest.TestCase):
    def test_named_mission_has_only_service_scoped_delivery_support(self):
        result = assess_roover_transport(RooVerRequest(required_surface_days=14), context())
        self.assertEqual(result.status, 'UNKNOWN')
        self.assertEqual(statuses(result), dict(launch='UNKNOWN', transfer='UNKNOWN',
                                                lunar_delivery='FEASIBLE',
                                                site_operations='UNKNOWN'))
        self.assertEqual(result.earth_moon_distance_km, 384000)
        self.assertEqual(result.earth_moon_relative_speed_km_s, 1)
        self.assertEqual(result.documented_rover_mass_kg_approx, 20)
        self.assertEqual(result.documented_manifested_suite_mass_kg_approx, 75)
        self.assertIn('not demonstrated flight success', result.segments[2].basis)

    def test_other_region_exceeds_named_delivery_scope(self):
        result = assess_roover_transport(
            RooVerRequest(destination_scope='LUNAR_EQUATOR'), context())
        self.assertEqual(statuses(result)['lunar_delivery'], 'INFEASIBLE')
        self.assertEqual(result.status, 'INFEASIBLE')

    def test_longer_operation_exceeds_documented_roover_plan(self):
        result = assess_roover_transport(RooVerRequest(required_surface_days=15), context())
        self.assertEqual(statuses(result)['site_operations'], 'INFEASIBLE')
        self.assertEqual(result.status, 'INFEASIBLE')

    def test_aggregate_75kg_is_not_provider_capacity(self):
        result = assess_roover_transport(RooVerRequest(payload_mass_kg=30), context())
        self.assertEqual(statuses(result)['lunar_delivery'], 'UNKNOWN')
        self.assertEqual(result.status, 'UNKNOWN')
        self.assertEqual(statuses(assess_roover_transport(
            RooVerRequest(payload_mass_kg=20), context()))['lunar_delivery'], 'UNKNOWN')

    def test_exact_site_is_not_inferred_from_regional_target(self):
        result = assess_roover_transport(
            RooVerRequest(exact_site_id='UNQUALIFIED_POLAR_SITE'), context())
        self.assertEqual(statuses(result)['lunar_delivery'], 'UNKNOWN')

    def test_different_actor_or_year_remains_unknown(self):
        for request in (RooVerRequest(actor_id='OTHER'), RooVerRequest(landing_year=2031)):
            self.assertEqual(statuses(assess_roover_transport(request, context()))
                             ['lunar_delivery'], 'UNKNOWN')

    def test_unqualified_state_cannot_be_used_as_transfer_evidence(self):
        base = context()
        bad_moon = replace(base.moon, navigation_grade=False)
        result = assess_roover_transport(RooVerRequest(), replace(base, moon=bad_moon))
        self.assertIsNone(result.earth_moon_distance_km)
        self.assertEqual(statuses(result)['transfer'], 'UNKNOWN')

    def test_deterministic_result_for_pinned_inputs(self):
        request, states = RooVerRequest(), context()
        self.assertEqual(assess_roover_transport(request, states),
                         assess_roover_transport(request, states))


if __name__ == '__main__':
    unittest.main()
