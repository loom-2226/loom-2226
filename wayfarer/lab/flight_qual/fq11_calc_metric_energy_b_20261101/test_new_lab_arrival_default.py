"""CCR-2026-0003 default selection test; no legacy qualification mutation."""
import copy, json, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'wayfarer/lab/flight'))
from metric_arrival_v1 import calculate_fq11,new_lab_metric_arrival_rule

class LabMetricDefaultTests(unittest.TestCase):
    def test_omitted_new_lab_rule_resolves_to_energy_b(self):
        case=json.loads((HERE/'FQ11_INPUT.json').read_text())
        ship=json.loads((ROOT/'wayfarer/lab/flight_qual/fq_house_power_20261101/current_fq1_fq4_fixture.json').read_text())
        card=json.loads((HERE/'METRIC_LAB_CARD.json').read_text())
        ident=card.pop('id');inherit=card.pop('inherit_modes_from')
        card['modes']={x:copy.deepcopy(ship['metric'][inherit]['modes'][x]) for x in card.pop('allowed_modes')}
        ship['metric'][ident]=card
        experiment={'enable_metric_arrival_law_v1':True,'phases':[
            {'kind':'torch','mode':'CRUISE','duration_s':1.},
            {'kind':'metric','mode':'NORMAL','model':'lab_energy_v1','duration_s':1.},
            {'kind':'arrival_match','duration_s':1.}],
            'metric_arrival_v1':{'main_commit':case['main_commit'],'source_snapshot':case,
              'source_id':'EA','destination_id':'MA','rcs_reserve_kg':case['rcs_reserve_kg'],
              'arrival_match_tolerance_m_s':case['arrival_match_tolerance_m_s']}}
        phase=experiment['phases'][1]
        self.assertNotIn('arrival_rule',phase)
        self.assertEqual(new_lab_metric_arrival_rule(phase),'ENERGY_ORBIT_RELATIVE_B')
        implicit=calculate_fq11(ship,experiment)
        explicit=copy.deepcopy(experiment)
        explicit['phases'][1]['arrival_rule']='ENERGY_ORBIT_RELATIVE_B'
        self.assertEqual(implicit,calculate_fq11(ship,explicit))
        self.assertEqual(implicit['phases'][1]['arrival_rule'],'ENERGY_ORBIT_RELATIVE_B')
        self.assertNotIn('arrival_rule',phase)  # no mutation of source fixture
        self.assertEqual(ship['metric']['canonical']['law'],'canonical_envelope')
        other=copy.deepcopy(experiment)
        other['phases'][1]['arrival_rule']='IDENTITY_DIAGNOSTIC'
        with self.assertRaisesRegex(ValueError,'requires the ENERGY B'):
            calculate_fq11(ship,other)

if __name__=='__main__':unittest.main()
