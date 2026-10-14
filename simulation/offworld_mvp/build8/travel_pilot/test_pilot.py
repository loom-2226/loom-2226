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

    def test_authored_vehicle_10_10_km_s_not_price_calibration_or_canon(self):
        from .pilot import TECHNOLOGY_TABLE, TOF_SCAN_DAYS, CLOSED_AUDIT_SCAN_DAYS
        t=TECHNOLOGY_TABLE[0]
        self.assertEqual((t['max_departure_vinf_km_s'],
                          t['max_arrival_vinf_km_s']), (10.0,10.0))
        self.assertEqual(t['payload_tonnes'],2)
        self.assertEqual(t['from_year'],2026)
        self.assertIn('AUTHORED',t['standing'])
        self.assertIn('NOT_CANON',t['standing'])
        self.assertIn('heavier ships',t['reason'])
        self.assertEqual(self.data['technology_table'][0],t)
        self.assertEqual(TOF_SCAN_DAYS,2.0)
        self.assertEqual(CLOSED_AUDIT_SCAN_DAYS,.25)
        self.assertEqual(
            self.data['previous_price_anchor_maxima_historical_only'],
            dict(departure_vinf_km_s=73.430819,
                 arrival_vinf_km_s=56.091356,
                 status='HISTORICAL_PRICE_ANCHOR_LIMITS_NO_LONGER_IN_EFFECT'))

    def test_all_eight_known_mercury_weeks_are_now_recovered(self):
        known=('2026-04-23','2026-04-30','2026-05-07','2027-04-15',
               '2027-04-22','2031-05-15','2031-05-22','2031-05-29')
        self.assertEqual(tuple(self.data['known_mercury_weekly_witnesses']),known)
        for date in known:
            with self.subTest(departure=date):
                candidates=self.pilot.candidates('EARTH','MERCURY',date)
                self.assertTrue(candidates, 'known feasible Mercury week lost: '+date)
                self.assertTrue(all(0<=r['departure_vinf_km_s']<=10 and
                                    0<=r['arrival_vinf_km_s']<=10 for r in candidates))

    def test_independent_dense_closure_audits(self):
        from .pilot import CLOSED_AUDIT_SCAN_DAYS
        audited=self.data['dense_closure_audits']
        self.assertEqual(len(audited),9)
        self.assertEqual({(x['origin'],x['destination']) for x in audited},
                         set(PILOT_PAIRS))
        for row in audited:
            self.assertEqual(row['dense_step_days'],.25)
            self.assertGreater(row['checked_flight_durations'],5000)
            self.assertEqual(row['feasible_samples'],0)
            self.assertIn('NOT_CONTINUOUS_PROOF',row['conclusion'])
        # Independent actual flight-scan verification of one selected
        # 0.25-day sample per route. Result generation checks the other six.
        for origin,destination in PILOT_PAIRS:
            row=next(x for x in audited if (x['origin'],x['destination']) ==
                     (origin,destination))
            with self.subTest(route=(origin,destination),date=row['departure']):
                x=self.pilot.audit_closed_week(origin,destination,row['departure'])
                self.assertEqual(x['scan_step_days'],CLOSED_AUDIT_SCAN_DAYS)
                self.assertEqual(x['feasible_samples'],0)
                self.assertEqual(x['checked'],row['checked_flight_durations'])

    def test_no_returned_trajectory_violates_both_vehicle_limits(self):
        from .pilot import TECHNOLOGY_TABLE
        tech=TECHNOLOGY_TABLE[0]
        for route in self.data['route_summaries']:
            for label in ('cheapest_sample','costliest_sample',
                          'weekly_cheapest_sample','weekly_costliest_sample',
                          'first_sample','last_sample'):
                if label not in route:
                    continue
                candidate=route[label]
                self.assertLessEqual(candidate['departure_vinf_km_s'],
                                     tech['max_departure_vinf_km_s'])
                self.assertLessEqual(candidate['arrival_vinf_km_s'],
                                     tech['max_arrival_vinf_km_s'])
        for origin,destination in PILOT_PAIRS:
            # Test a separate live computation, not only saved samples.
            example=next(x['cheapest_sample']['departure'] for x in
                         self.data['route_summaries'] if
                         (x['origin'],x['destination'])==(origin,destination))
            rows=self.pilot.candidates(origin,destination,example)
            self.assertTrue(rows)
            for r in rows:
                self.assertLessEqual(r['departure_vinf_km_s'],10)
                self.assertLessEqual(r['arrival_vinf_km_s'],10)
    def test_actual_2026_to_2031_weekly_grid_plus_one_day_minimum_refinement(self):
        for summary in self.data['route_summaries']:
            self.assertIn((summary['origin'],summary['destination']),PILOT_PAIRS)
            self.assertGreaterEqual(summary['weekly_departures'],312)
            self.assertEqual(summary['feasible_weekly_departures'] +
                             summary['unavailable_weekly_departures'],
                             summary['weekly_departures'])
            self.assertGreater(summary['feasible_weekly_departures'],0)
            self.assertGreater(summary['unavailable_weekly_departures'],0)
            self.assertEqual(summary['flight_time_scan_days'],2.0)
            self.assertGreater(summary['refined_unique_departures'],0)
            self.assertGreater(summary['local_minima'],0)
            self.assertGreaterEqual(summary['candidate_count'],
                                    summary['feasible_weekly_departures'])
            for name in ('cheapest_sample','costliest_sample',
                         'weekly_cheapest_sample','weekly_costliest_sample',
                         'first_sample','last_sample'):
                r=summary[name]
                self.assertGreater(r['c3_km2_s2'],0)
                self.assertGreater(r['transfer_burden_km_s'],0)
                self.assertGreater(r['cost_usd_millions'],0)
                self.assertGreater(r['flight_days'],0)
                self.assertTrue(45 <= r['flight_days'] <= 1400)
                self.assertEqual(r['state_class_origin'],'DIRECT')
                self.assertEqual(r['state_class_destination'],'DIRECT')
                self.assertEqual(r['cost_standing'],
                                 'HELD_AT_2026_LEVEL_BY_ASSUMPTION_NOT_EMPIRICAL')
                self.assertEqual(
                    round((_day(r['arrival'])-_day(r['departure'])).total_seconds()/86400,5),
                    r['flight_days'])

    def test_mercury_and_mars_windows_remain_visible(self):
        for destination in ('MERCURY','MARS'):
            row=next(x for x in self.data['route_summaries']
                     if x['origin']=='EARTH' and x['destination']==destination)
            self.assertGreater(row['unavailable_weekly_departures'],0)
            lo=row['weekly_cheapest_sample']
            hi=row['weekly_costliest_sample']
            first=_day('2026-01-01')
            for sample in (lo,hi):
                self.assertEqual(
                    (_day(sample['departure'])-first).days % 7,0)
            # Tight Mercury feasibility produces narrow low-cost clusters;
            # cost spread alone is not the launch-window proof.
            self.assertGreater(hi['cost_usd_millions'],
                               lo['cost_usd_millions'])
            # Recheck the witnessed minima directly from qualified states.
            candidates=self.pilot.candidates('EARTH',destination,lo['departure'])
            self.assertTrue(candidates)
            self.assertTrue(all(self.pilot._admitted(r) for r in candidates))

    def test_any_moving_origin_and_arrival_position_truly_at_arrival(self):
        r=self.pilot.candidates('MARS','CERES','2029-06-28')[0]
        self.assertEqual((r['source_origin'],r['source_destination']),
                         ('JPL_MAR099','CERES_SPK_PHASE4B_2251'))
        self.assertNotEqual(r['departure'],r['arrival'])
        self.assertGreater(r['flight_days'],0)
        self.assertGreater(r['arrival_vinf_km_s'],0)

    def test_crossing_a_year_boundary(self):
        r=self.pilot.candidates('EARTH','MARS','2026-10-29')[0]
        self.assertTrue(r['departure'].startswith('2026-'))
        self.assertGreater(int(r['arrival'][:4]),2026)

    def test_pareto_frontier_cost_time_and_continuous_flight(self):
        results=self.pilot.candidates('EARTH','MARS','2026-10-29')
        self.assertGreaterEqual(len(results),1)
        self.assertLessEqual(len(results),4)
        self.assertEqual(results,sorted(results,key=lambda x:x['flight_days']))
        self.assertTrue(all(results[i]['cost_usd_millions']>results[i+1]['cost_usd_millions']
                            for i in range(len(results)-1)))
        self.assertTrue(all(0<r['flight_days']<1401 for r in results))
        self.assertTrue(all(self.pilot._admitted(r) for r in results))

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
        reference=self.pilot.candidates('EARTH','MARS','2026-10-29')
        replay=TravelPilot().candidates('EARTH','MARS','2026-10-29')
        self.assertTrue(reference)
        self.assertEqual(reference,replay)
        self.assertTrue(self.data['no_simulation_consumers'])


if __name__=='__main__':
    unittest.main()
