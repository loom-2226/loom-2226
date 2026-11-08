"""Focused source-constrained operating requests; no physical calibration fixtures."""
import copy, json, unittest
from flightlab import run, canonical_metric_operation
from test_flightlab import cfg, ex


class CanonMetricOperationTests(unittest.TestCase):
    def setUp(self):
        self.ship=cfg('wayfarer')
        self.experiment=ex('wayfarer_canonical_operation')
        self.phase=self.experiment['phases'][0]

    def operation(self):
        return canonical_metric_operation(self.phase,{'explicit_known_state':'preserved'}, {})

    def test_valid_source_sequence_holds_before_field(self):
        op=self.operation()
        self.assertEqual(op['sequence_status'],'VALID')
        self.assertEqual(op['execution_status'],'HOLD')
        self.assertEqual(op['last_accepted_state'],'RELATIONAL_READY')
        self.assertEqual(op['held_request'],'METRIC_RAMP')
        self.assertEqual([r['status'] for r in op['phase_trace']],
                         ['REQUEST_ACCEPTED','REQUEST_ACCEPTED','HOLD']+['NOT_ENTERED']*4)
        self.assertEqual(op['phase_trace'][1]['g10_state'],'METRIC_PREP')
        self.assertEqual(op['phase_trace'][3]['e1_state'],'METRIC_CRUISE')
        self.assertIsNone(op['illustrative_profile'])
        self.assertTrue(all(g['status']=='HOLD' for g in op['gates'].values()))

    def test_all_four_source_modes_and_support(self):
        expected={'NORMAL':(.268,10,20000,3500000), 'FAST':(.437,12,38100,6700000),
                  'EXPEDITE':(.519,15,63500,11200000), 'HARD':(.595,30,136000,23900000)}
        for name,(beta,ramp,cold,power) in expected.items():
            with self.subTest(mode=name):
                self.phase['mode']=name
                self.phase['operating_sequence'][2]['duration_s']=ramp
                op=self.operation();row=op['mode_requirements'][name]
                self.assertEqual(op['sequence_status'],'VALID')
                self.assertEqual((row['beta'],row['ramp_s'],row['cold_load_w'],row['delivered_electrical_w']),
                                 (beta,ramp,cold,power))
                self.assertAlmostEqual(row['required_upstream_electrical_w'],power/(.98*.96))
                self.assertIn('build_metric_closure',op['requirement_provenance']['mode_card'])
                self.assertEqual(len(op['producer_version_hash']),64)

    def test_illegal_transition_midfield_loom_and_overlap(self):
        for index,state in ((1,'TORCH_ACTIVE'),(4,'LOOM_FORMATION'),(5,'COAST')):
            p=copy.deepcopy(self.phase);p['operating_sequence'][index]['state']=state
            with self.subTest(state=state), self.assertRaisesRegex(ValueError,'illegal canonical transition'):
                canonical_metric_operation(p,{}, {})
        with self.assertRaisesRegex(ValueError,'torch/high metric overlap'):
            canonical_metric_operation(self.phase,{}, {'main':1e-12})
        self.phase['operating_sequence'][3]['major_torch_active']=True
        with self.assertRaisesRegex(ValueError,'torch/high metric overlap'):self.operation()

    def test_missing_times_and_wrong_ramp(self):
        for index in (1,4,5):
            p=copy.deepcopy(self.phase);p['operating_sequence'][index].pop('duration_s')
            op=canonical_metric_operation(p,{}, {})
            self.assertEqual(op['sequence_status'],'INDETERMINATE')
            self.assertEqual(op['execution_status'],'HOLD')
            self.assertTrue(op['input_holds'])
        self.phase['operating_sequence'][2]['duration_s']=11
        with self.assertRaisesRegex(ValueError,'source-derived mode'):self.operation()

    def test_ftl_saturation_veto_degradation_and_insufficient_support(self):
        for beta,reason in ((1.,'FTL metric BLACK'),(.678,'uncertified'),(.3,'uncertified')):
            p={**self.phase,'beta':beta}
            with self.subTest(beta=beta), self.assertRaisesRegex(ValueError,reason):
                canonical_metric_operation(p,{}, {})
        p={**self.phase,'mode':'HARD','degraded_critical_node_sector':True}
        with self.assertRaisesRegex(ValueError,'degraded critical'):canonical_metric_operation(p,{}, {})
        p={**self.phase,'hard_veto':'experiment-supplied veto'}
        with self.assertRaisesRegex(ValueError,'hard veto'):canonical_metric_operation(p,{}, {})
        self.phase['declared_capacities']['cold_load_w']=100
        op=self.operation()
        self.assertEqual(op['declared_load_checks'][0]['status'],'FAIL')
        self.assertEqual(op['execution_status'],'HOLD')

    def test_gate_booleans_stale_wrong_lot_and_u_hyp_cannot_pass(self):
        scope={'ship_id':'Wayfarer','array_id':'array','lot_id':'lot',
               'environment_class':'clean','ramp_family':'declared family'}
        self.phase.update(certification_scope=scope,certification_time_s=50)
        record={**scope,'mode':'NORMAL','ramp_s':10,'status':'PASS','revoked':False,
                'standard_version':'experiment','record_id':'U-HYP','authority':'user hypothesis',
                'signature':'unverified string','provenance':'experiment only',
                'valid_from_s':0,'valid_until_s':100,'cache_age_s':0,'max_cache_age_s':1}
        self.phase['gates']={key:copy.deepcopy(record) for key in self.operation()['gates']}
        op=self.operation()
        self.assertEqual(op['physical_status'],'INDETERMINATE')
        self.assertTrue(all(g['status']=='HOLD' for g in op['gates'].values()))
        self.assertIn('PATH_DEPENDENT_ORDINARY_STATE_PROPAGATOR_CALIBRATION',op['physics_validation_holds'])
        self.phase['gates']['environment'].update(valid_until_s=10,lot_id='other',revoked=True)
        self.phase['gates']['plant']=True
        op=self.operation();reasons=op['gates']['environment']['reasons']
        self.assertIn('stale/not yet valid',reasons)
        self.assertIn('not applicable: lot_id',reasons)
        self.assertIn('non-revocation not established',reasons)
        self.assertIn('booleans do not certify',op['gates']['plant']['reasons'][0])

    def test_no_spurious_arrival_preserves_explicit_prestate(self):
        result=run(self.ship,self.experiment,dt=1.)
        op=result['phases'][0]['canonical_operation']
        pre=op['pre_metric_state']
        for key in ('position_m','velocity_m_s','q_body_to_inertial','omega_rad_s'):
            self.assertEqual(pre[key],self.experiment['initial'][key])
            self.assertIsNone(result['final_state'][key])
        self.assertEqual(pre['experiment_initial_inputs'],self.experiment['initial'])
        self.assertEqual(pre['tanks_kg'],{'remass':250000.})
        self.assertAlmostEqual(pre['mass_kg'],1167680.)
        self.assertTrue(all(value is None for value in op['terminal_state'].values()))
        self.assertIsNone(result['final_state']['mass_kg'])
        self.assertIsNone(result['final_state']['tanks_kg'])
        self.assertIsNone(result['final_state']['remass_kg'])
        self.assertIsNone(result['final_state']['matching_delta_v_m_s'])
        self.assertIsNone(result['metrics']['metric_path_m'])
        self.assertIsNone(result['metrics']['total_propellant_used_kg'])
        self.assertEqual(result['qualification']['status'],'indeterminate')
        self.assertEqual(result['final_state']['time_s'],0.)
        json.dumps(result,allow_nan=False)
        self.experiment['phases'].append({'kind':'coast','duration_s':1})
        with self.assertRaisesRegex(ValueError,'arrival unresolved'):run(self.ship,self.experiment)
        self.experiment['phases'][-1]={'kind':'metric','duration_s':80,
                                     'model':'experimental_shift','mode':'NORMAL'}
        with self.assertRaisesRegex(ValueError,'arrival unresolved'):run(self.ship,self.experiment)

    def test_premetric_conventional_state_is_retained(self):
        coast={'kind':'coast','duration_s':2}
        before=run(self.ship,{**self.experiment,'phases':[coast]},dt=.5)
        self.experiment['phases'].insert(0,coast)
        after=run(self.ship,self.experiment,dt=.5)
        pre=after['phases'][1]['canonical_operation']['pre_metric_state']
        for key in ('position_m','velocity_m_s','mass_kg','tanks_kg','q_body_to_inertial','omega_rad_s'):
            self.assertEqual(pre[key],before['final_state'][key])


if __name__=='__main__':unittest.main()
