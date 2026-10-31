"""Focused invariants for scratch laboratory. Run: .venv/bin/python -m unittest -v test_flightlab"""
import copy,json,math,unittest
from pathlib import Path
import numpy as np
from flightlab import mass_properties,run,allocation,rcs_wrench,torch_force,unit,qerror
ROOT=Path(__file__).resolve().parent
def cfg(name):return json.loads((ROOT/'configs'/(name+'.json')).read_text())
def ex(name):return json.loads((ROOT/'experiments'/(name+'.json')).read_text())
class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w=cfg('wayfarer')
        cls.sc=cfg('scout')
    def test_wayfarer_full_mass_closure(self):
        m,cg,I=mass_properties(self.w,{'remass':250000.})
        card=json.loads((ROOT/'fixtures/rev7/wayfarer_v05_card.json').read_text())
        s=card['states']['S1']
        self.assertAlmostEqual(m,s['mass_t']*1000,places=5)
        np.testing.assert_allclose(cg,s['cg_m'],atol=1e-8)
        np.testing.assert_allclose(I,s['inertia_tensor_kg_m2'],atol=1e-4)
    def test_wayfarer_empty_mass_closure(self):
        m,cg,I=mass_properties(self.w,{'remass':0.})
        card=json.loads((ROOT/'fixtures/rev7/wayfarer_v05_card.json').read_text())
        s=card['states']['S4']
        self.assertAlmostEqual(m,s['mass_t']*1000,places=5)
        np.testing.assert_allclose(cg,s['cg_m'],atol=1e-8)
        np.testing.assert_allclose(I,s['inertia_tensor_kg_m2'],atol=1e-4)
    def test_mass_properties_components(self):
        s=copy.deepcopy(self.sc);a=mass_properties(s,{'prop':10000.})
        s['components'].append({'mass_kg':1000.,'cg_m':[10,3,0]})
        b=mass_properties(s,{'prop':10000.})
        self.assertAlmostEqual(b[0]-a[0],1000.)
        self.assertGreater(b[1][0],a[1][0])
        self.assertFalse(np.allclose(a[2],b[2]))
    def test_empty_propellant_inventory(self):
        s=copy.deepcopy(self.sc);e=ex('burn120')
        s['tanks'][0]['initial_kg']=0.
        j=run(s,e,dt=1.,sample_s=20.)
        self.assertAlmostEqual(j['final_state']['mass_kg'],90000.)
        self.assertAlmostEqual(j['metrics']['final_speed_m_s'],0.)
        self.assertAlmostEqual(j['torch_impulse_Ns'],0.)
        self.assertIn('propellant depleted within step: thrust curtailed',j['warnings'])
    def test_allocation_force_zero(self):
        m,cg,I=mass_properties(self.w,{'remass':250000.})
        thr,A=rcs_wrench(self.w,cg)
        target=np.array([0,5e5,0.])
        u,s=allocation(A,target)
        np.testing.assert_allclose(A[:3]@u,np.zeros(3),atol=1e-5)
        np.testing.assert_allclose(A[3:]@u,target*s,atol=1e-4)
    def test_non180_turn(self):
        j=ex('reversal40');j['phases'][0]['angle_deg']=90
        result=run(self.w,j,dt=.2,sample_s=10.)
        self.assertEqual(result['qualification']['status'],'pass')
    def test_missing_wayfarer_rcs_propellant_is_unknown(self):
        j=run(self.w,ex('reversal40'),dt=.2,sample_s=5.)
        self.assertTrue(j['rcs_propellant_unresolved'])
        self.assertIsNone(j['metrics']['total_propellant_used_kg'])
        self.assertEqual(j['metrics']['known_propellant_used_kg'],0.)
        self.assertGreater(j['rcs_impulse_Ns'],0.)
    def test_torch_plus_rcs_propellant_is_partly_unknown(self):
        ship=cfg('wayfarer_twin_torch')
        j=run(ship,ex('burn120_rcs_hold'),dt=.4,sample_s=30.)
        self.assertIsNone(j['metrics']['total_propellant_used_kg'])
        self.assertGreater(j['metrics']['known_propellant_used_kg'],600.)
        self.assertTrue(j['rcs_propellant_unresolved'])
        self.assertEqual(j['qualification']['status'],'pass')
    def test_original_fixed300_terminal_and_gate(self):
        w=cfg('wayfarer_original_mount_300k')
        e=ex('reversal10')
        e['phases'][0]['post_hold_s']=4
        j=run(w,e,dt=.02,sample_s=2.)
        self.assertEqual(j['qualification']['status'],'pass')
        self.assertAlmostEqual(j['metrics']['attitude_error_deg'],.0462942780324,delta=.0002)
        self.assertAlmostEqual(j['metrics']['rate_deg_s'],.037623799509,delta=.0002)
        self.assertAlmostEqual(j['phases'][0]['gate_entry_s'],10.62,delta=.05)
    def test_original_fixed300_slow_actuator_regression(self):
        w=cfg('wayfarer_original_mount_300k')
        for thr in w['rcs']:thr['lag_s']=.2
        j=run(w,ex('reversal10'),dt=.02,sample_s=2.)
        self.assertEqual(j['qualification']['status'],'fail')
        self.assertAlmostEqual(j['metrics']['attitude_error_deg'],.162353566573,delta=.001)
        self.assertAlmostEqual(j['metrics']['rate_deg_s'],.131865164053,delta=.001)
    def test_wayfarer_rcs_turn(self):
        j=run(self.w,ex('reversal40'),dt=.2,sample_s=10.)
        self.assertEqual(j['qualification']['status'],'pass')
        self.assertLess(j['metrics']['attitude_error_deg'],.25)
    def test_rcs_translation(self):
        j=run(self.w,ex('translate20'),dt=.2,sample_s=5.)
        self.assertEqual(j['qualification']['status'],'pass')
        self.assertAlmostEqual(j['phases'][0]['translation_delta_v_achieved_m_s'][0],.5,delta=.02)
    def test_gimbal_rate_limit(self):
        from flightlab import gimbal_update
        now=np.array([1.,0.,0.]);a=math.radians(20)
        e={'direction':[1,0,0],'gimbal_target_direction':[math.cos(a),math.sin(a),0],
           'gimbal_limit_deg':25.,'gimbal_slew_deg_s':10.}
        nxt=gimbal_update(e,now,.5)
        self.assertAlmostEqual(math.degrees(math.acos(float(now@nxt))),5.,places=5)
    def test_scout_rcs_consumption(self):
        j=run(self.sc,ex('reversal40'),dt=.2,sample_s=10.)
        self.assertGreater(j['metrics']['total_propellant_used_kg'],0)
        self.assertLess(j['final_state']['mass_kg'],100000)
    def test_torch_rocket_equation(self):
        j=run(self.w,ex('burn120'),dt=.4,sample_s=20.)
        m0=1167680.; mf=j['final_state']['mass_kg'];ve=2000000.
        expected=ve*math.log(m0/mf)
        self.assertAlmostEqual(j['metrics']['final_speed_m_s'],expected,delta=.2)
        self.assertEqual(j['qualification']['status'],'pass')
    def test_torch_gimbal_limit_detected(self):
        j=run(cfg('wayfarer_twin_torch'),ex('burn120'),dt=.4,sample_s=20.)
        self.assertEqual(j['qualification']['status'],'fail')
        self.assertGreater(j['metrics']['torch_final_angular_rate_deg_s'],1.)
    def test_metric_epistemics(self):
        canon=run(self.w,ex('metric_canonical'),dt=1.,sample_s=20.)
        alt=run(self.w,ex('metric_experimental'),dt=1.,sample_s=20.)
        self.assertEqual(canon['qualification']['status'],'indeterminate')
        self.assertEqual(alt['qualification']['status'],'pass')
        self.assertAlmostEqual(canon['metrics']['metric_path_m'],alt['metrics']['metric_path_m'],places=3)
        self.assertIsNone(canon['final_state']['position_m'])
        self.assertGreater(alt['final_state']['position_m'][0],1e6)
    def test_metric_cannot_reenter_conventional_if_unclosed(self):
        j=ex('metric_canonical');j['phases'].append({'kind':'coast','duration_s':10})
        with self.assertRaisesRegex(ValueError,'arrival unresolved'):
            run(self.w,j,dt=1.)
    def test_combined_persistent_mass(self):
        j=run(self.w,ex('combined'),dt=.4,sample_s=1.)
        self.assertEqual(j['qualification']['status'],'pass')
        self.assertLess(j['final_state']['mass_kg'],1167680.)
        self.assertEqual(len(j['phases']),4)
        self.assertAlmostEqual(j['phases'][0]['mass_end_kg'],j['phases'][1]['mass_end_kg'],places=5)
        self.assertAlmostEqual(j['phases'][1]['mass_end_kg'],j['phases'][2]['mass_end_kg'],places=5)
if __name__=='__main__':unittest.main()
