"""Focused offline transfer screen tests: no conductor or WORLD mutations."""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .pilot import (
    ANCHORS, SOURCE_CLASS, PILOT_PAIRS, SERVICE, TECHNOLOGY,
    TravelPilot, _day, _add_months, price_table, MOON_LOCAL_LEG_DAYS)

RESULT = Path(__file__).with_name('pilot_result.json')


class TravelPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(RESULT.read_text())
        cls.pilot=TravelPilot()

    def test_2026_price_anchor_derivation_and_flat_assumption_through_2226(self):
        import csv, statistics
        with ANCHORS.open(newline='') as stream:
            rows=list(csv.DictReader(stream))
        candidate=[float(r['one_way_cost_usd_millions']) /
                   (float(r['departure_vinf_km_s'])+float(r['arrival_vinf_km_s']))
                   for r in rows if r['year']=='2026'
                   and r['mission_type']==SERVICE
                   and r['body_id']!='MOON' and r['one_way_cost_usd_millions']
                   and r['method'] in ('REFINED_GROUPED_LAMBERT_GRID','EXISTING_SCREEN_SINGLE_CANDIDATE')]
        self.assertEqual(len(candidate),87)
        rate=round(statistics.median(candidate),9)
        table=self.pilot.price_by_year
        self.assertEqual(len(table),201*6)
        for y in (2026,2035,2036,2140,2226):
            self.assertEqual(table[(y,SERVICE)]['usd_millions_per_km_s_burden'],rate)
            self.assertEqual(table[(y,SERVICE)]['standing'],
                             'HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL')
        self.assertEqual(self.data['rate_2026_by_service'][SERVICE]['anchor_count_2026'],87)
        self.assertEqual(self.data['pricing_2036_2226'],
                         'HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL')

    def test_actual_2026_to_2031_weekly_grid_plus_one_day_minimum_refinement(self):
        for summary in self.data['route_summaries']:
            self.assertIn((summary['origin'],summary['destination']),PILOT_PAIRS)
            self.assertGreaterEqual(summary['weekly_departures'],312)
            self.assertGreater(summary['refined_unique_departures'],0)
            self.assertGreater(summary['local_minima'],0)
            self.assertGreater(summary['candidate_count'],summary['weekly_departures'])
            for name in ('cheapest_sample','first_sample','last_sample'):
                r=summary[name]
                self.assertGreater(r['c3_km2_s2'],0)
                self.assertGreater(r['transfer_burden_km_s'],0)
                self.assertGreater(r['cost_usd_millions'],0)
                self.assertGreater(r['flight_days'],0)
                self.assertNotIn(r['flight_days'],(30,180,365,730,1460,2920))
                self.assertEqual(r['state_class_origin'],'DIRECT')
                self.assertEqual(r['state_class_destination'],'DIRECT')
                self.assertEqual(r['cost_standing'],
                                 'HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL')
                self.assertEqual(
                    round((_day(r['arrival'])-_day(r['departure'])).total_seconds()/86400,5),
                    r['flight_days'])

    def test_mercury_and_mars_phase_dependence_from_live_geometry(self):
        for dest in ('MERCURY','MARS'):
            costs=[]
            for dep in ('2026-01-15','2026-04-15','2026-07-15','2026-10-15'):
                rows=self.pilot.candidates('EARTH',dest,dep)
                if rows:
                    costs.append(min(r['cost_usd_millions'] for r in rows))
            self.assertGreaterEqual(len(costs),3)
            self.assertGreater(max(costs),1.1*min(costs),(dest,costs))

    def test_any_moving_origin_and_arrival_position_truly_at_arrival(self):
        r=self.pilot.candidates('MARS','CERES','2026-05-15')[0]
        self.assertEqual((r['source_origin'],r['source_destination']),
                         ('JPL_MAR099','CERES_SPK_PHASE4B_2251'))
        self.assertNotEqual(r['departure'],r['arrival'])
        self.assertGreater(r['flight_days'],0)
        self.assertGreater(r['arrival_vinf_km_s'],0)

    def test_crossing_a_year_boundary(self):
        r=self.pilot.candidates('EARTH','MARS','2026-12-15')[0]
        self.assertTrue(r['departure'].startswith('2026-'))
        self.assertGreater(int(r['arrival'][:4]),2026)

    def test_pareto_frontier_cost_time_and_continuous_flight(self):
        results=self.pilot.candidates('EARTH','MARS','2026-05-15')
        self.assertGreaterEqual(len(results),2)
        self.assertLessEqual(len(results),4)
        self.assertEqual(results,sorted(results,key=lambda x:x['flight_days']))
        self.assertTrue(all(results[i]['cost_usd_millions']>results[i+1]['cost_usd_millions']
                            for i in range(len(results)-1)))
        self.assertTrue(any(abs(r['flight_days']-round(r['flight_days']))>.0001
                            for r in results))

    def test_unsupported_missing_and_bennu_2140_switch_default_off(self):
        self.assertEqual(self.pilot.state_class('DACTYL','2140-01-01'),'MISSING')
        self.assertEqual(self.pilot.state_class('BENNU','2140-01-01'),'PROPAGATED')
        self.assertEqual(self.pilot.state_class('MARS','2140-01-01'),'DIRECT')
        with self.assertRaisesRegex(ValueError,'UNKNOWN_EPHEMERIS_MISSING'):
            self.pilot._solve('EARTH','DACTYL',_day('2140-01-01'),180)
        with self.assertRaisesRegex(ValueError,'UNKNOWN_EPHEMERIS_PROPAGATED'):
            self.pilot._solve('EARTH','BENNU',_day('2140-01-01'),180)
        approximate=TravelPilot(allow_approximation=True)._solve(
            'EARTH','BENNU',_day('2140-01-01'),365)
        self.assertEqual(approximate['state_class_destination'],'PROPAGATED')
        self.assertEqual(approximate['standing'],
                         'SCENARIO_APPROXIMATION_NOT_EXECUTABLE_AUTHORITY')
        self.assertEqual(approximate['source_destination'],
                         'PROP_BENNU_2101955_PHASE4D')

    def test_wait_twelve_and_thirty_months_cheapest_scripted_and_exhaustion(self):
        # Build actual choices from the two stored ready-date examples, plus a
        # solved 2027 candidate, so the test does not assume a synthetic cost curve.
        saved={r['wait_limit_months']:r for r in self.data['ready_date_examples']
               if r.get('origin')=='EARTH' and r.get('destination')=='MARS'}
        self.assertEqual(set(saved),{12,30})
        ready=_day('2027-01-15')
        self.assertEqual(saved[12]['status'],'AVAILABLE_PROVISIONAL_NOT_EXECUTABLE_AUTHORITY')
        self.assertEqual(saved[30]['status'],'AVAILABLE_PROVISIONAL_NOT_EXECUTABLE_AUTHORITY')
        self.assertGreater(_day(saved[30]['departure']),_add_months(ready,12))
        self.assertLess(saved[30]['cost_usd_millions'],saved[12]['cost_usd_millions'])
        for bound in (12,30):
            r=saved[bound]
            if r['status']=='AVAILABLE_PROVISIONAL_NOT_EXECUTABLE_AUTHORITY':
                self.assertEqual(r['policy'],'CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
                self.assertGreater(_day(r['departure']),ready)
                self.assertLessEqual(_day(r['departure']),_add_months(ready,bound))
        p=self.pilot
        p.options[('EARTH','MARS')]=tuple(
            r for r in [*saved.values()]
            if r.get('status')=='AVAILABLE_PROVISIONAL_NOT_EXECUTABLE_AUTHORITY')
        # Explicit empty window still fails closed, never silently extends.
        exhausted=p.travel_option('EARTH','MARS','2030-01-01',wait_limit_months=12)
        self.assertEqual(exhausted['status'],'WAIT_LIMIT_EXHAUSTED')
        self.assertEqual(exhausted['policy'],'CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
        for bound in (12,30):
            response=p.travel_option('EARTH','MARS','2027-01-15',wait_limit_months=bound)
            self.assertEqual(response['policy'],'CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
            if response['status'].startswith('AVAILABLE'):
                self.assertGreater(_day(response['departure']),ready)
                self.assertLessEqual(_day(response['departure']),_add_months(ready,bound))
        with self.assertRaisesRegex(ValueError,'INVALID_WAIT_LIMIT_MONTHS'):
            p.travel_option('EARTH','MARS','2027-01-15',wait_limit_months=0)

    def test_moon_mars_provisional_five_day_local_leg_not_180_days(self):
        moon=next(r for r in self.data['ready_date_examples']
                  if r.get('origin')=='MOON')
        self.assertEqual(moon['policy'],'CHEAPEST_WITHIN_WAIT_LIMIT_SCRIPTED')
        self.assertEqual(moon['local_leg']['days'],5)
        self.assertIn('PROVISIONAL',moon['local_leg']['standing'])
        self.assertEqual(MOON_LOCAL_LEG_DAYS,5)
        from .pilot import MOON_LOCAL_FLYBY_DAYS
        self.assertEqual(MOON_LOCAL_FLYBY_DAYS,3)
        self.assertGreater(moon['cost_usd_millions'],moon['local_leg']['cost_usd_millions'])
        self.assertEqual(
            round((_day(moon['transfer_departure_earth'])-_day(moon['departure'])).total_seconds()/86400,5),
            5)
        self.assertEqual(moon['state_class_origin'],'DIRECT')
        self.assertEqual(moon['state_class_destination'],'DIRECT')

    def test_deterministic_replay_of_real_lambert_solution(self):
        reference=self.pilot.candidates('EARTH','MARS','2026-07-15')
        replay=TravelPilot().candidates('EARTH','MARS','2026-07-15')
        self.assertEqual(reference,replay)
        self.assertTrue(self.data['no_simulation_consumers'])


if __name__=='__main__':
    unittest.main()
