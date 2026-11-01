"""Proportional regressions for dynamic installations, fuel isolation and metric semantics."""
import copy,math,unittest
import numpy as np
from flightlab import run,mass_properties,exhaust_velocity,G0,dynamic_gimbals,initial_state,torch_force
from test_flightlab import cfg,ex

class CompletionTests(unittest.TestCase):
    def test_historical_dynamic_gimbal(self):
        j=run(cfg('wayfarer_gimbal_reference'),ex('gimbal12'),dt=.02,sample_s=1.)
        p=j['phases'][0]
        self.assertAlmostEqual(p['attitude_error_deg'],.028993430154763234,delta=1e-6)
        self.assertAlmostEqual(p['rate_deg_s'],.018693258888895222,delta=1e-6)
        self.assertAlmostEqual(p['peak_force_N'],7066.948852743456,delta=.1)
        self.assertAlmostEqual(p['peak_offaxis_torque_Nm'],71698.25114376447,delta=.1)
        self.assertAlmostEqual(p['gate_entry_s'],12.,places=6)
        angles=np.array([list(r['gimbal_angles_deg'].values()) for r in j['rcs_trace']])
        self.assertGreater(np.max(abs(angles[-1]-angles[0])),20.)
        self.assertLessEqual(np.max(abs(np.diff(angles,axis=0)))/.02,30.000001)
        self.assertLessEqual(np.max(abs(angles)),25.000001)
        self.assertEqual(j['physical_qualification']['status'],'indeterminate')
    def test_feedback_and_schedule_change_actual_vectors(self):
        s=cfg('scout_gimbal');state=initial_state(s,{})
        engines=[e for e in s['rcs'] if 'gimbal' in e]
        for _ in range(100):dynamic_gimbals(engines,state,np.array([0,0,0,0,1,0]),0,20,.02)
        before=state['gangle'][engines[0]['id']].copy()
        for _ in range(100):dynamic_gimbals(engines,state,np.array([0,0,0,0,-1,0]),0,20,.02)
        self.assertGreater(np.max(abs(state['gangle'][engines[0]['id']]-before)),.3)
        e=engines[0];e['gimbal'].update(policy='schedule',schedule=[{'time_s':1.,'angles_deg':[100,-100]}])
        rate,angle,limited=dynamic_gimbals([e],state,np.zeros(6),2,20,.1)
        self.assertLessEqual(rate,30.000001);self.assertLessEqual(angle,25.000001);self.assertGreater(limited,0)
    def test_engine_mass_and_full_tensor(self):
        s=cfg('scout');levels={'prop':10000.};m,c,I=mass_properties(s,levels)
        s['rcs'][0].update(installed_mass_kg=100.,pos_m=[8,3,2])
        mm,cc,II=mass_properties(s,levels)
        self.assertAlmostEqual(mm-m,100.)
        self.assertGreater(np.linalg.norm(cc-c),0)
        self.assertGreater(abs(II[0,1]-I[0,1]),100.)
    def test_isp_and_validation(self):
        self.assertAlmostEqual(exhaust_velocity({'isp_s':300}),300*G0)
        with self.assertRaisesRegex(ValueError,'inconsistent'):exhaust_velocity({'isp_s':300,'ve_m_s':100})
        with self.assertRaises(ValueError):exhaust_velocity({'isp_s':0})
    def test_separate_tank_exhaustion(self):
        s=cfg('scout_twin_empty');s['rcs']=[]
        j=run(s,{'phases':[{'kind':'torch','duration_s':1}],
                 'checks':{'propellant_available':{'min':1}}},dt=.1)
        self.assertAlmostEqual(j['final_state']['tanks_kg']['prop'],0.)
        self.assertLess(j['final_state']['tanks_kg']['aux'],100.)
        self.assertGreater(j['torch_impulse_Ns'],0.)
        self.assertEqual(j['qualification']['status'],'fail')
        initial_mass=mass_properties(s,{t['id']:t.get('initial_kg',t['capacity_kg']) for t in s['tanks']})[0]
        self.assertAlmostEqual(initial_mass-j['final_state']['mass_kg'],j['metrics']['known_propellant_used_kg'],places=7)
        self.assertNotEqual(j['phases'][0]['cg_end_m'],mass_properties(s,{t['id']:t.get('initial_kg',t['capacity_kg']) for t in s['tanks']})[1].tolist())
    def test_unknown_torch_consumption_is_indeterminate(self):
        s=cfg('scout');s['torch'][0]['modes']['CRUISE']['ve_m_s']=None;s['torch'][0]['tank']=None
        j=run(s,{'phases':[{'kind':'torch','duration_s':1}],
                 'checks':{'total_propellant_used_kg':{'max':100}}},dt=.1)
        self.assertEqual(j['qualification']['status'],'indeterminate')
        self.assertIsNone(j['metrics']['total_propellant_used_kg'])
        self.assertGreater(j['torch_impulse_Ns'],0.)
    def test_torch_caps_and_continuous_tail(self):
        s=cfg('scout_offset_torch');s['rcs']=[];e=s['torch'][0]
        f,*_=torch_force(e,'CRUISE',100000.,10.,np.zeros(3))
        self.assertLessEqual(f,e['max_N'])
        exp={'phases':[{'kind':'torch','duration_s':1,'throttle':10.}, {'kind':'coast','duration_s':1}]}
        j=run(s,exp,dt=.05,sample_s=.05);a,b=j['phases']
        self.assertGreater(a['throttle_clamp_steps'],0)
        self.assertGreater(a['slew_limit_steps'],0)
        self.assertLessEqual(a['peak_command_slew_fullscale_s'],2.000001)
        self.assertEqual(a['state_end'],b['state_start'])
        self.assertEqual(a['actuators_end'],b['actuators_start'])
        self.assertGreater(b['propellant_used_kg'],0)
        self.assertGreater(a['phase_attitude_drift_deg'],.1)
    def test_tvc_rate_bound(self):
        s=cfg('scout');s['torch'][0].update(pos_m=[6.5,1,0],tvc_rate_deg_s=.2,gimbal_limit_deg=20.)
        j=run(s,{'phases':[{'kind':'torch','duration_s':2}]},dt=.1)
        self.assertLessEqual(j['phases'][0]['peak_gimbal_rate_deg_s'],.200001)
        self.assertGreater(j['phases'][0]['phase_attitude_drift_deg'],.1)
    def test_shutdown_tail_can_be_stabilized_during_coast(self):
        experiment={'phases':[{'kind':'torch','duration_s':2.,'hold_attitude':True},
                              {'kind':'coast','duration_s':2.,'hold_attitude':True}],
                    'checks':{'final_angular_rate_deg_s':{'max':.05}}}
        j=run(cfg('scout_offset_torch'),experiment,dt=.05)
        self.assertEqual(j['qualification']['status'],'pass')
        self.assertLess(j['phases'][1]['phase_attitude_drift_deg'],.1)
    def test_distinct_metric_maps_and_canonical_unknowns(self):
        ship=cfg('scout_metric_models')
        a=run(ship,ex('metric_shift_compare'),dt=1.)
        b=run(ship,ex('metric_rotation_compare'),dt=1.)
        c=run(ship,ex('metric_canonical_compare'),dt=1.)
        np.testing.assert_allclose(a['final_state']['velocity_m_s'],[10,0,0],atol=1e-9)
        np.testing.assert_allclose(b['final_state']['velocity_m_s'],[0,10,0],atol=1e-9)
        np.testing.assert_allclose(b['final_state']['position_m'],[0,1800,0],atol=1e-8)
        self.assertGreater(a['final_state']['position_m'][0],1e9)
        self.assertAlmostEqual(a['final_state']['mass_kg'],b['final_state']['mass_kg'])
        self.assertIsNone(c['metrics']['final_speed_m_s']);self.assertIsNone(c['metrics']['total_propellant_used_kg'])
        self.assertTrue(all(h['position_m'] is None for h in c['history']))
    def test_sequence_constraints(self):
        ship=cfg('scout_offset_metric');experiment=ex('continuous')
        experiment['phases']=[{'kind':'torch','duration_s':1}, {'kind':'metric','model':'experimental_shift','mode':'NORMAL','duration_s':80}]
        with self.assertRaisesRegex(ValueError,'sequence'):run(ship,experiment)
        experiment={'phases':[{'kind':'torch','duration_s':1}, {'kind':'metric','model':'experimental_shift','mode':'NORMAL','duration_s':80}],
                    'sequence_constraints':{'metric_entry_max_throttle':1e-6}}
        with self.assertRaisesRegex(ValueError,'idle propulsion'):run(ship,experiment)
    def test_target_time_exact_with_fractional_timestep(self):
        experiment={'phases':[{'kind':'rcs_turn','duration_s':1.,'post_hold_s':.4,'angle_deg':10.}],
                    'allow_coarse_rcs_dt_for_sensitivity_study':True}
        j=run(cfg('scout'),experiment,dt=.3)
        self.assertAlmostEqual(j['phases'][0]['at_target_time']['t_s'],1.,places=12)
        self.assertAlmostEqual(j['final_state']['time_s'],1.4,places=12)
    def test_physical_and_actuator_state_continuity(self):
        experiment={'phases':[{'kind':'torch','duration_s':1.,'hold_attitude':True},
                              {'kind':'coast','duration_s':2.},
                              {'kind':'rcs_turn','duration_s':2.,'angle_deg':10.},
                              {'kind':'coast','duration_s':2.},
                              {'kind':'metric','duration_s':80.,'model':'experimental_rotation','mode':'NORMAL'},
                              {'kind':'coast','duration_s':1.}],
                    'sequence_constraints':{'metric_entry_max_throttle':.001}}
        j=run(cfg('scout_offset_metric'),experiment,dt=.1,sample_s=1.)
        for a,b in zip(j['phases'],j['phases'][1:]):
            self.assertEqual(a['state_end'],b['state_start'])
            self.assertEqual(a['actuators_end'],b['actuators_start'])
            self.assertAlmostEqual(a['mass_end_kg'],b['mass_start_kg'],places=8)
    def test_phase_check_is_binding(self):
        j=run(cfg('scout'),{'phases':[{'kind':'coast','duration_s':1,'checks':{'mass_end_kg':{'max':1}}}]},dt=.1)
        self.assertEqual(j['qualification']['status'],'fail')
    def test_unknown_constraint_keeps_known_checks(self):
        j=run(cfg('wayfarer'),{'phases':[{'kind':'rcs_translate','duration_s':1,'delta_v_body_m_s':[.01,0,0]}],
                 'checks':{'propellant_available':{'min':1},'peak_throttle':{'max':1.000001}}},dt=.1)
        self.assertEqual(j['qualification']['status'],'indeterminate')
        self.assertEqual(j['qualification']['checks'][1]['status'],'pass')
    def test_canonical_unknowns_do_not_hide_known_failure(self):
        experiment=ex('metric_canonical_compare')
        experiment['checks']={'metric_path_m':{'max':1.},'final_speed_m_s':{'max':1.}}
        j=run(cfg('scout_metric_models'),experiment,dt=1.)
        self.assertEqual(j['qualification']['status'],'fail')
        self.assertEqual(j['qualification']['checks'][1]['status'],'indeterminate')
if __name__=='__main__':unittest.main()
