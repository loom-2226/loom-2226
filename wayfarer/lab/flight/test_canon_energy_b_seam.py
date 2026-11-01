"""Canon II §§7.1a/b: scoped velocity law, not environmental/collapse approval."""
import copy,json,sys,unittest
from pathlib import Path
import numpy as np
from flightlab import canonical_metric_operation,run
from metric_arrival_v1 import planetary_state,phi,norm,AU_KM

ROOT=Path(__file__).resolve().parents[3]
CASE=json.loads((ROOT/'wayfarer/lab/flight_qual/fq12_inbound_metric_energy_b_20261101/FQ12_INPUT.json').read_text())

class CanonArrivalSeamTests(unittest.TestCase):
    def phase(self):
        return {'mode':'NORMAL','kind':'metric','arrival_rule':'ENERGY_ORBIT_RELATIVE_B',
           'support_scenario':'MVP_2226',
           'canon_arrival':{'regime':'ORDINARY_SOLAR_SYSTEM',
             'source_body':CASE['jupiter'],'destination_body':CASE['earth'],
             'sun_gm_km3_s2':CASE['sun_gm_km3_s2'],
             'sun_mass_kg':CASE['sun_mass_kg'],
             'solar_reflex_approx_km_s':CASE['solar_reflex_approx_km_s']}}
    def pre(self):
        j,v=planetary_state(CASE['jupiter'],CASE['sun_gm_km3_s2'],0.)
        v=v+np.asarray(CASE['solar_reflex_approx_km_s'])
        return {'time_s':0.,'position_m':(j*1000).tolist(),
                'velocity_m_s':(v*1000).tolist(),'mass_kg':1167680.,
                'tanks_kg':{'remass':250000.}}
    def test_velocity_only_closed_ledger_no_capture(self):
        out=canonical_metric_operation(self.phase(),self.pre(),{'torch_centerline':0.})
        self.assertEqual(out['execution_status'],'ARRIVAL_VELOCITY_RESOLVED')
        self.assertIsNone(out['terminal_state']['position_m'])
        self.assertIsNone(out['terminal_state']['mass_kg'])
        self.assertIsNotNone(out['terminal_state']['velocity_m_s'])
        self.assertEqual(out['held_request'],'METRIC_COLLAPSE_CERTIFICATION_AND_CAPTURE')
        self.assertTrue(all(v['status']=='HOLD' for v in out['gates'].values()))
        r=out['arrival_velocity_resolution']
        self.assertFalse(r['position_certified'])
        self.assertFalse(r['capture_certified'])
        self.assertFalse(r['environment_certified'])
        self.assertAlmostEqual(r['relative_mismatch_m_s'],10392,delta=100)
        self.assertAlmostEqual(r['E_p_L_IDENTITIES_BY_CONSTRUCTION']['energy_residual_J'],0.,delta=.001)
        json.dumps(out,allow_nan=False)
    def test_undeclared_or_out_of_scope_stays_hold(self):
        for item in ({'arrival_rule':None},{'canon_arrival':None},
                     {'canon_arrival':{'regime':'OTHER'}}):
            phase=self.phase();phase.update(item)
            with self.subTest(item=item):
                if phase.get('arrival_rule') is None or phase.get('canon_arrival') is None:
                    self.assertEqual(canonical_metric_operation(phase,self.pre(),{})['execution_status'],'HOLD')
                else:
                    self.assertEqual(canonical_metric_operation(phase,self.pre(),{})['execution_status'],'HOLD')
    def test_scoped_implicit_default_parity_without_legacy_promotion(self):
        explicit=self.phase()
        implicit=copy.deepcopy(explicit);implicit.pop('arrival_rule')
        pre=self.pre()
        a=canonical_metric_operation(explicit,pre,{})
        b=canonical_metric_operation(implicit,pre,{})
        self.assertEqual(b['execution_status'],'ARRIVAL_VELOCITY_RESOLVED')
        self.assertEqual(b['terminal_state']['velocity_m_s'],a['terminal_state']['velocity_m_s'])
        self.assertEqual(b['arrival_velocity_resolution']['arrival_rule'],'ENERGY_ORBIT_RELATIVE_B')
        self.assertIsNone(b['terminal_state']['position_m'])
        self.assertEqual(b['physical_status'],'INDETERMINATE')
        self.assertTrue(all(g['status']=='HOLD' for g in b['gates'].values()))
        for change in ('no_regime','other_regime','explicit_none'):
            legacy=copy.deepcopy(implicit)
            if change=='no_regime':legacy.pop('canon_arrival')
            if change=='other_regime':legacy['canon_arrival']['regime']='OTHER'
            if change=='explicit_none':legacy['arrival_rule']=None
            with self.subTest(change=change):
                result=canonical_metric_operation(legacy,pre,{})
                self.assertEqual(result['execution_status'],'HOLD')
                self.assertIsNone(result['arrival_velocity_resolution'])

    def test_flightlab_dispatch_resolves_only_velocity(self):
        from test_flightlab import cfg
        ship=cfg('wayfarer')
        phase={**self.phase(),'model':'canonical','duration_s':100.}
        pre=self.pre()
        ex={'name':'scoped natural arrival, no certified collapse',
            'phases':[phase],
            'initial':{'position_m':pre['position_m'],
                       'velocity_m_s':pre['velocity_m_s']}}
        out=run(ship,ex,dt=1.,sample_s=100.)
        op=out['phases'][0]['canonical_operation']
        self.assertEqual(op['execution_status'],'ARRIVAL_VELOCITY_RESOLVED')
        self.assertEqual(out['history'][0]['operating_state'],'VELOCITY_RESOLVED_PHYSICAL_HOLD')
        self.assertIsNotNone(op['terminal_state']['velocity_m_s'])
        self.assertIsNone(out['final_state']['velocity_m_s'])
        self.assertIsNone(out['final_state']['position_m'])
        self.assertEqual(out['qualification']['status'],'indeterminate')

    def test_energetically_forbidden_outbound_fails_closed(self):
        p=self.phase();p['canon_arrival'].update(source_body=CASE['earth'],destination_body=CASE['jupiter'])
        q,_=planetary_state(CASE['earth'],CASE['sun_gm_km3_s2'],0.)
        _,v=planetary_state(CASE['earth'],CASE['sun_gm_km3_s2'],0.)
        pre=self.pre();pre['position_m']=(q*1000).tolist()
        pre['velocity_m_s']=((v+np.asarray(CASE['solar_reflex_approx_km_s']))*1000).tolist()
        with self.assertRaisesRegex(ValueError,'ENERGY-FORBIDDEN'):
            canonical_metric_operation(p,pre,{})

if __name__=='__main__':unittest.main()
