"""Hardware evidence comparisons, not an independent hardware certificate."""
import copy
import unittest

import numpy as np

from flightlab import run
from hardware_assess import assess, finite_cone_sphere_clearance, wayfarer_envelopes
from test_flightlab import cfg


def declared_ship():
    return dict(name='HYPOTHETICAL unit fixture',
        base=dict(mass_kg=1000., cg_m=[0, 0, 0], inertia_kg_m2=np.diag([1000., 2000., 2000.]).tolist()),
        tanks=[dict(id='fuel', capacity_kg=2., initial_kg=2., cg_m=[0, 1, 0],
                    inertia_full_kg_m2=np.diag([1., 1., 1.]).tolist())], rcs=[],
        torch=[dict(id='engine', pos_m=[1, 1, 0], direction=[-1, 0, 0],
                    installed_mass_kg=10., installed_inertia_kg_m2=np.diag([1., 2., 3.]).tolist(),
                    tank='fuel', modes={'CRUISE': dict(max_N=100., ve_m_s=100.)})])


class HardwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship = declared_ship()
        cls.exp = dict(name='one second burn', phases=[dict(kind='torch', duration_s=1.)])
        cls.flight_result = run(cls.ship, cls.exp, dt=.1)

    def report(self, assumptions=None, ship=None, result=None):
        ship = ship or self.ship
        result = result or self.flight_result
        return assess(ship, self.exp, result, result['rcs_trace'], assumptions)

    def requirement(self, report, name):
        return next(r for r in report['requirements'] if r['requirement'] == name)

    def test_unknown_capacity_hold_known_demand(self):
        r = self.report()
        mount = self.requirement(r, 'mount.1,1,0.force_N')
        self.assertEqual(mount['status'], 'HOLD')
        self.assertIsNone(mount['capacity'])
        self.assertAlmostEqual(mount['demand'], 100.)
        self.assertFalse(r['hardware_certificate'])
        self.assertEqual(r['hardware_qualified'], 'HOLD')

    def test_numerical_margin_pass_and_insufficient_rating_fail(self):
        a = {'mount_ratings': {'default': {'force_N': 150., 'dynamic_factor': 1.2}}}
        r = self.requirement(self.report(a), 'mount.1,1,0.force_N')
        self.assertEqual(r['status'], 'PASS'); self.assertAlmostEqual(r['margin'], 30.)
        a['mount_ratings']['default']['force_N'] = 110.
        r = self.requirement(self.report(a), 'mount.1,1,0.force_N')
        self.assertEqual(r['status'], 'FAIL'); self.assertAlmostEqual(r['margin'], -10.)

    def test_flow_impulse_energy_and_full_tensor_response(self):
        r = self.report({'feed_ratings': {'by_id': {'fuel': {'peak_flow_kg_s': 1.1}}}})
        self.assertAlmostEqual(r['propellant']['total_used_kg'], 1.)
        self.assertAlmostEqual(r['propellant']['peak_total_flow_kg_s'], 1.)
        self.assertAlmostEqual(r['installation'][0]['impulse_Ns'], 100.)
        self.assertAlmostEqual(r['torch']['jet_energy_J'], 5000.)
        self.assertEqual(self.requirement(r, 'feed.fuel.flow_kg_s')['status'], 'PASS')
        self.assertEqual(self.requirement(r, 'mass.installation_model')['status'], 'PASS')
        self.assertAlmostEqual(r['mass_response']['added_declared_engine_mass_kg'], 10.)
        self.assertGreater(abs(r['mass_response']['engine_inertia_delta_kg_m2'][0][1]), 1.)
        self.assertNotEqual(r['mass_response']['start_cg_m'], r['mass_response']['end_cg_m'])
        self.assertEqual(self.requirement(r, 'mass.known_ledger_closure_kg')['status'], 'PASS')

    def test_unknown_exhaust_is_null_not_zero(self):
        s = copy.deepcopy(self.ship); s['torch'][0]['modes']['CRUISE'].pop('ve_m_s')
        j = run(s, self.exp, dt=.1)
        r = self.report(ship=s, result=j)
        self.assertIsNone(r['propellant']['total_used_kg'])
        self.assertIsNone(r['propellant']['peak_total_flow_kg_s'])
        self.assertGreater(r['installation'][0]['impulse_Ns'], 0)
        self.assertEqual(self.requirement(r, 'feed.exhaust_and_source')['status'], 'HOLD')
        # Even a positive numerical tail below a load-screen tolerance must
        # never turn unknown consumption into a physical zero.
        s['torch'][0]['modes']['CRUISE']['max_N'] = 1e-14
        j = run(s, self.exp, dt=.1)
        self.assertIsNone(self.report(ship=s, result=j)['propellant']['total_used_kg'])

    def test_depleted_feed_fails_requested_availability(self):
        s = copy.deepcopy(self.ship); s['tanks'][0]['initial_kg'] = .15
        j = run(s, self.exp, dt=.1)
        r = self.report(ship=s, result=j)
        self.assertEqual(self.requirement(r, 'tank.fuel.known_demand_kg')['status'], 'FAIL')
        self.assertAlmostEqual(r['propellant']['total_used_kg'], .15)

    def test_protected_water_excluded_even_when_rcs_fuel_unknown(self):
        s = cfg('wayfarer')
        exp = {'phases': [{'kind': 'rcs_turn', 'duration_s': .2, 'angle_deg': 1}]}
        j = run(s, exp, dt=.1); r = assess(s, exp, j, j['rcs_trace'])
        self.assertEqual(self.requirement(r, 'protected_water.excluded')['status'], 'PASS')
        self.assertEqual(r['propellant']['protected_reserve']['protected_water_kg'], 50000.)
        self.assertEqual(j['final_state']['tanks_kg'], {'remass': 250000.})
        self.assertIsNone(r['propellant']['total_used_kg'])
        # An attempted protected-water feed is detected, never authorized by assessment.
        s['tanks'].append(dict(id='protected_water', capacity_kg=50000., cg_m=[0, 0, 0]))
        s['rcs'][0].update(tank='protected_water', ve_m_s=1000.)
        j = run(s, exp, dt=.1); r = assess(s, exp, j, j['rcs_trace'])
        self.assertEqual(self.requirement(r, 'protected_water.excluded')['status'], 'FAIL')
        # Extra externally supplied hypothetical fuel is not automatically
        # charged against the protected water. Missing provenance holds.
        s['tanks'][-1]['id'] = 'aux'; s['rcs'][0]['tank'] = 'aux'
        j = run(s, exp, dt=.1); r = assess(s, exp, j, j['rcs_trace'])
        self.assertEqual(self.requirement(r, 'protected_water.excluded')['status'], 'HOLD')
        s['tanks'][-1]['fuel_source'] = 'HYPOTHETICAL separately loaded external fuel'
        j = run(s, exp, dt=.1); r = assess(s, exp, j, j['rcs_trace'])
        self.assertEqual(self.requirement(r, 'protected_water.excluded')['status'], 'PASS')
        self.assertEqual(r['hardware_qualified'], 'HOLD')

    def test_cone_not_just_axis_and_finite_end_caps(self):
        # The axis misses this sphere, but a 10 degree finite cone hits it.
        args = ([0, 0, 0], [1, 0, 0], 10.)
        self.assertGreater(finite_cone_sphere_clearance(*args, 0, [5, .8, 0], .1), 0)
        self.assertLess(finite_cone_sphere_clearance(*args, 10, [5, .8, 0], .1), 0)
        self.assertGreater(finite_cone_sphere_clearance(*args, 10, [-1, 0, 0], .1), 0)
        self.assertGreater(finite_cone_sphere_clearance(*args, 10, [11, 0, 0], .1), 0)
        with self.assertRaises(ValueError): finite_cone_sphere_clearance(*args, 90, [1, 0, 0], .1)

    def test_plume_intersection_fail_and_clear_screen_pass(self):
        a = dict(plume=dict(length_m=2., half_angle_deg=5.),
                 geometry=dict(sphere_envelopes=[dict(id='obstacle', center_m=[2, 1, 0], radius_m=.2)]))
        # Force -X means exhaust +X: this obstacle is downstream.
        r = self.report(a)
        self.assertEqual(self.requirement(r, 'plume.coarse_clearance')['status'], 'FAIL')
        a['geometry']['sphere_envelopes'][0]['center_m'] = [2, 10, 0]
        r = self.report(a)
        self.assertEqual(self.requirement(r, 'plume.coarse_clearance')['status'], 'PASS')
        self.assertGreater(self.requirement(r, 'plume.coarse_clearance')['margin'], 0)
        self.assertEqual(self.requirement(r, 'plume.physical_clearance')['status'], 'HOLD')

    def test_real_wayfarer_envelope_requires_deployment(self):
        self.assertEqual(wayfarer_envelopes(None), [])
        stowed = wayfarer_envelopes('stowed'); deployed = wayfarer_envelopes('torch')
        self.assertGreater(len(stowed), 100)
        self.assertGreater(next(x['radius_m'] for x in deployed if x['id'] == 'hotfin_40'),
                           next(x['radius_m'] for x in stowed if x['id'] == 'hotfin_40'))

    def test_declared_temperatures_do_not_claim_physics_or_certificate(self):
        a = {'thermal': {'default': {'peak_K': 700., 'rating_K': 800., 'load_W': 10., 'capacity_W': 20.}}}
        r = self.report(a)
        self.assertEqual(self.requirement(r, 'thermal.engine.temperature_K')['status'], 'PASS')
        self.assertEqual(r['hardware_qualified'], 'HOLD')
        a['thermal']['default']['rating_K'] = 600.
        self.assertEqual(self.requirement(self.report(a), 'thermal.engine.temperature_K')['status'], 'FAIL')

    def test_hash_mismatch_old_or_incomplete_trace_rejected(self):
        s = copy.deepcopy(self.ship); s['torch'][0]['installed_mass_kg'] = 20.
        with self.assertRaisesRegex(ValueError, 'hashes differ'): self.report(ship=s)
        trace = copy.deepcopy(self.flight_result['rcs_trace']); trace[0].pop('engine_samples')
        with self.assertRaisesRegex(ValueError, 'evidence missing'): assess(self.ship, self.exp, self.flight_result, trace)
        with self.assertRaisesRegex(ValueError, 'gap|full run'): assess(self.ship, self.exp, self.flight_result, self.flight_result['rcs_trace'][:-1])

    def test_assessment_is_read_only(self):
        before = copy.deepcopy((self.ship, self.exp, self.flight_result))
        self.report()
        self.assertEqual(before, (self.ship, self.exp, self.flight_result))


if __name__ == '__main__': unittest.main()
