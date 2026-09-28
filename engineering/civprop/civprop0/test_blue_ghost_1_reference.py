"""Completed-mission evidence and calculation boundaries for one CLPS flight."""
from dataclasses import replace
import json
import unittest

from src.loom_spatial_state_authority import SpatialState

from .blue_ghost_1_reference import FIXTURE, SAMPLED_EVENTS, assess_blue_ghost_1
from .roover_transport import SolarContext


def contexts():
    events = {event['id']: event for event in json.loads(FIXTURE.read_text())['events']}
    source = {'units': 'km,km/s', 'ephemeris_source_id': 'DE440'}
    result = {}
    for name in SAMPLED_EVENTS:
        epoch = events[name]['epoch_utc']
        earth = SpatialState('EARTH', epoch, 'J2000/ECLIPTIC', (0, 0, 0),
                             (0, 0, 0), source, True)
        moon = SpatialState('MOON', epoch, 'J2000/ECLIPTIC', (384000, 0, 0),
                            (0, 1, 0), source, True)
        result[name] = SolarContext(epoch, earth, moon, 'registry', 'manifest')
    return result


class BlueGhostReferenceTests(unittest.TestCase):
    def test_completion_is_not_prospective_feasibility(self):
        result = assess_blue_ghost_1(contexts())
        self.assertEqual([segment['name'] for segment in result['segments']],
                         ['launch', 'transfer', 'lunar_delivery', 'site_operations'])
        self.assertTrue(all(segment['observed_outcome'] == 'OBSERVED_COMPLETE' and
                            segment['prospective_feasibility'] == 'NOT_ASSESSED'
                            for segment in result['segments']))

    def test_elapsed_times_come_from_precise_reported_events(self):
        intervals = assess_blue_ghost_1(contexts())['derived_intervals']
        self.assertEqual(intervals['launch_to_orbit_separation_hours'], 1.1)
        self.assertGreater(intervals['launch_to_landing_hours'], 46 * 24)
        self.assertLess(intervals['launch_to_landing_hours'], 47 * 24)
        self.assertGreater(intervals['loi_burn_start_to_landing_hours'], 16 * 24)
        self.assertEqual(intervals['last_data_precision'], 'APPROX_REPORTED_MINUTE')

    def test_date_only_tli_does_not_gain_a_clock_time(self):
        result = assess_blue_ghost_1(contexts())
        self.assertIsNone(result['derived_intervals']['tli_to_loi_burn_start_hours'])
        self.assertEqual(result['source_reported_approximate_phase_days'],
                         {'earth_orbit': 25, 'lunar_transit': 4, 'lunar_orbit': 16})

    def test_geometry_is_context_not_spacecraft_route(self):
        result = assess_blue_ghost_1(contexts())
        self.assertEqual(result['solar_geometry']['launch']['earth_moon_distance_km'], 384000)
        self.assertIn('not spacecraft position', result['solar_geometry']['launch']['meaning'])
        self.assertIn('transfer delta-v', result['does_not_establish'])
        self.assertIn('Roo-ver/IM-5 launch or flight performance', result['does_not_establish'])

    def test_missing_or_mismatched_solar_state_fails_closed(self):
        values = contexts()
        del values['landing']
        with self.assertRaises(ValueError):
            assess_blue_ghost_1(values)
        values = contexts()
        values['landing'] = replace(values['landing'], reference_epoch_utc='2025-03-03T00:00:00Z')
        with self.assertRaises(ValueError):
            assess_blue_ghost_1(values)

    def test_unqualified_state_fails_closed(self):
        values = contexts()
        values['launch'] = replace(values['launch'],
                                   moon=replace(values['launch'].moon, navigation_grade=False))
        with self.assertRaises(ValueError):
            assess_blue_ghost_1(values)

    def test_pinned_inputs_replay_identically(self):
        values = contexts()
        self.assertEqual(assess_blue_ghost_1(values), assess_blue_ghost_1(values))


if __name__ == '__main__':
    unittest.main()
