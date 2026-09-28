"""IM-1 precedent stays observed and cannot qualify IM-5 flight performance."""
from dataclasses import replace
import json
import unittest

from src.loom_spatial_state_authority import SpatialState

from .im1_reference import FIXTURE, SAMPLED_EVENTS, assess_im1, rerun_roover
from .roover_transport import SolarContext


def context(epoch):
    source = {'units': 'km,km/s', 'ephemeris_source_id': 'DE440'}
    earth = SpatialState('EARTH', epoch, 'J2000/ECLIPTIC', (0, 0, 0),
                         (0, 0, 0), source, True)
    moon = SpatialState('MOON', epoch, 'J2000/ECLIPTIC', (384000, 0, 0),
                        (0, 1, 0), source, True)
    return SolarContext(epoch, earth, moon, 'registry', 'manifest')


def contexts():
    events = {event['id']: event for event in json.loads(FIXTURE.read_text())['events']}
    return {name: context(events[name]['epoch_utc']) for name in SAMPLED_EVENTS}


class Im1ReferenceTests(unittest.TestCase):
    def test_provider_completed_launch_transfer_and_delivery(self):
        result = assess_im1(contexts())
        self.assertEqual(result['provider'], 'Intuitive Machines')
        self.assertEqual(result['lander'], 'Nova-C')
        self.assertEqual([segment['observed_outcome'] for segment in result['segments']],
                         ['OBSERVED_COMPLETE', 'OBSERVED_COMPLETE',
                          'OBSERVED_COMPLETE', 'OBSERVED_LIMITED'])
        self.assertTrue(all(segment['prospective_feasibility'] == 'NOT_ASSESSED'
                            for segment in result['segments']))

    def test_timing_respects_reported_precision(self):
        intervals = assess_im1(contexts())['derived_intervals']
        self.assertAlmostEqual(intervals['launch_to_approx_separation_hours'], 0.8)
        self.assertGreater(intervals['launch_to_landing_hours'], 7 * 24)
        self.assertLess(intervals['launch_to_landing_hours'], 8 * 24)
        self.assertIsNone(intervals['loi_to_landing_hours'])
        self.assertIsNone(intervals['landing_to_surface_end_hours'])

    def test_im1_mass_and_site_are_not_im5_capacity_or_site(self):
        limits = assess_im1(contexts())['does_not_establish']
        self.assertTrue(any('Nova-D' in item for item in limits))
        self.assertTrue(any('spare capacity' in item for item in limits))
        self.assertTrue(any('Mons Malapert' in item for item in limits))

    def test_unqualified_solar_state_fails_closed(self):
        values = contexts()
        values['landing'] = replace(values['landing'],
                                    moon=replace(values['landing'].moon, navigation_grade=False))
        with self.assertRaises(ValueError):
            assess_im1(values)

    def test_missing_context_fails_closed(self):
        values = contexts()
        del values['launch']
        with self.assertRaises(ValueError):
            assess_im1(values)

    def test_roover_rerun_preserves_unknown_transport(self):
        result = rerun_roover(context('2030-07-01T00:00:00Z'))
        self.assertEqual(result['status'], 'UNKNOWN')
        self.assertEqual({s['name']: s['status'] for s in result['segments']},
                         {'launch': 'UNKNOWN', 'transfer': 'UNKNOWN',
                          'lunar_delivery': 'FEASIBLE', 'site_operations': 'UNKNOWN'})


if __name__ == '__main__':
    unittest.main()
