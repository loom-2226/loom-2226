"""Build 8 only: complete four-body follow-on counterfactual experiment."""
import hashlib
import json
from collections import Counter
from decimal import Decimal as D
from pathlib import Path
import unittest
from .followon_four_body import run_four_body
from .followon_rules import FOUR_BODY_ORDER, four_body_rules
from .followon_trial import run_trial
from .route1_gate1 import run_gate1

BASELINE=Path(__file__).with_name('FOLLOWON_PR2_PILOT_BASELINE_698aec2c.json')
RUNS=(('A10','A','.10',True),('A25','A','.25',True),
      ('B10','B','.10',True),('B25','B','.25',True),
      ('B25_NO_OVERRIDES','B','.25',False))

def digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':'),
                    default=str).encode()).hexdigest()

class FourBodyFollowonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds={name:run_four_body(sc,D(share),on)
                    for name,sc,share,on in RUNS}

    def test_five_counterfactuals_have_eight_sponsors_and_2035_limit(self):
        for name,r in self.worlds.items():
            self.assertEqual(len(r['annual']),80,name)
            self.assertEqual(tuple(r['claim_order']),FOUR_BODY_ORDER)
            self.assertEqual(set(r['bodies']),{'MOON','MARS','CERES','BENNU'})
            self.assertEqual({x['year'] for x in r['annual']},set(range(2026,2036)))
            counts=Counter((x['sponsor'],x['year']) for x in r['annual'])
            self.assertEqual(set(counts.values()),{1})
            self.assertEqual(len(counts),80)
            self.assertTrue(all(x['failure_class'] in (None,'BUILT_IN','EMERGENT')
                                for x in r['annual']))
            for x in r['annual']:
                if x['failure_class']=='BUILT_IN':
                    self.assertGreater(D(four_body_rules(overrides=r['overrides'])
                                           ['rules'][x['sponsor']][x['stage'].lower()+'_price']),
                                       D(x['ceiling']))
                if x['disbursement']:
                    self.assertLessEqual(x['year'],2035)
            for s in FOUR_BODY_ORDER:
                rows=[x for x in r['annual'] if x['sponsor']==s]
                funded=[x for x in rows if x['disbursement']]
                self.assertLessEqual(len(funded),2)
                self.assertLessEqual(sum((D(x['requested']) for x in funded),D(0)),
                        D(rows[0]['lifetime_limit']))
            self.assertEqual(tuple(sorted(r['timeline'],
                key=lambda e:(D(e['time']),FOUR_BODY_ORDER.index(e['sponsor']),e['event']))),
                r['timeline'])

    def test_missing_scenario_a_evidence_stops_all_funding(self):
        for name in ('A10','A25'):
            r=self.worlds[name]
            self.assertFalse(any(x['disbursement'] for x in r['annual']))
            self.assertTrue(all(x['claimant'] is None for x in r['bodies'].values()))
            self.assertTrue(any(x['financier_reason']=='DEFER_MORE_INFORMATION'
                                for x in r['annual']))

    def test_funded_chains_and_control_override_off(self):
        for name in ('B10','B25'):
            r=self.worlds[name]
            self.assertEqual({b:v['claimant'] for b,v in r['bodies'].items()},
                             {'MOON':'NASA','BENNU':'CNSA','MARS':'ISRO','CERES':'ESA'})
            self.assertEqual(sum(bool(x['disbursement']) for x in r['annual']),7)
            self.assertIsNone(r['bodies']['MARS']['a2'])
            self.assertEqual(r['bodies']['MARS']['stop'],'FOLLOWON_BUILT_IN_CEILING')
            self.assertEqual(r['bodies']['CERES']['a2']['result'],'SUPPORTS_ADVANCE')
            self.assertEqual(r['bodies']['CERES']['stop'],'NO_NEXT_AUTHORED_ACTIVITY')
            self.assertEqual(r['bodies']['MOON']['stop'],'RESULT_INSUFFICIENT')
            self.assertEqual(r['bodies']['BENNU']['stop'],'RESULT_INSUFFICIENT')
        control=self.worlds['B25_NO_OVERRIDES']
        self.assertEqual(sum(bool(x['disbursement']) for x in control['annual']),4)
        self.assertIsNone(control['bodies']['CERES']['claimant'])
        self.assertIsNone(control['bodies']['MARS']['claimant'])
        self.assertEqual(control['bodies']['CERES']['stop'],'BUILT_IN_CEILING')
        self.assertEqual(control['bodies']['MARS']['stop'],'BUILT_IN_CEILING')
        for s,price in (('ESA',D('.200')),('ISRO',D('.120'))):
            self.assertEqual(D(next(x['ceiling'] for x in control['annual']
                             if x['sponsor']==s)),price)
            self.assertTrue(all(x['failure_class']=='BUILT_IN'
                         for x in control['annual'] if x['sponsor']==s))

    def test_late_initial_funding_retimes_studies_without_backdating(self):
        r=self.worlds['B10']
        self.assertEqual(r['bodies']['MOON']['a1']['funded_year'],2028)
        self.assertEqual(r['bodies']['CERES']['a1']['funded_year'],2029)
        self.assertEqual(r['bodies']['CERES']['a2']['funded_year'],2035)
        self.assertEqual(r['bodies']['CERES']['a1']['start'],'2029')
        self.assertEqual(r['bodies']['CERES']['a1']['completion'],'2035.00')
        for name,r in self.worlds.items():
            for body,summary in r['bodies'].items():
                for which in ('a1','a2'):
                    record=summary[which]
                    if record is None: continue
                    self.assertGreaterEqual(D(record['start']),D(record['funded_year']))
                    self.assertLessEqual(D(record['start']),D(record['completion']))
                    if which=='a2':
                        self.assertGreaterEqual(D(record['start']),
                                  D(summary['a1']['review_at']))
                        self.assertEqual(summary['a1']['result'],'SUPPORTS_ADVANCE')
                        self.assertEqual(summary['a1']['review'],'ADVANCE')
                        self.assertLessEqual(record['funded_year'],2035)

    def test_pr1_pilot_still_exact_against_real_main(self):
        saved=json.loads(BASELINE.read_text())
        self.assertEqual(saved['base_main_sha'],
                         '698aec2c16d90faeb8bf574797cc85e13f3619fc')
        pilot=run_trial()
        self.assertEqual(digest(pilot['yearly']),saved['yearly_sha256'])
        self.assertEqual(pilot['stops'],saved['stops'])
        self.assertEqual(list(pilot['claim_order']),saved['claim_order'])
        self.assertEqual(pilot['earth_fingerprint'],saved['earth_fingerprint'])
        self.assertEqual(pilot['a1_fingerprints'],saved['a1_fingerprints'])
        self.assertEqual(pilot['a2_fingerprints'],saved['a2_fingerprints'])
        self.assertEqual([(x['sponsor'],x['year'],x['activity'],x['requested'],
                           x['disbursement']) for x in pilot['yearly'] if x['disbursement']],
                         [tuple(x) for x in saved['funding']])

    def test_pr1_pilot_semantics_inside_eight_sponsor_world(self):
        r=self.worlds['B25']
        for body,sponsor,years,results in (
            ('MOON','NASA',(2026,2029),('SUPPORTS_ADVANCE','INSUFFICIENT')),
            ('BENNU','CNSA',(2026,2027),('SUPPORTS_ADVANCE','INSUFFICIENT'))):
            summary=r['bodies'][body]
            self.assertEqual(summary['claimant'],sponsor)
            self.assertEqual((summary['a1']['funded_year'],
                              summary['a2']['funded_year']),years)
            self.assertEqual((summary['a1']['result'],summary['a2']['result']),results)
            self.assertEqual((summary['a1']['activity'],summary['a2']['activity']),
                  (four_body_rules()['rules'][sponsor]['a1'],
                   four_body_rules()['rules'][sponsor]['a2']))

    def test_reversal_reports_any_changed_outcomes_and_collision(self):
        normal=self.worlds['B25']
        reverse=run_four_body('B',D('.25'),True,tuple(reversed(FOUR_BODY_ORDER)))
        def semantic(r):
            return {(x['sponsor'],x['year']):(x['decision'],x['financier_reason'],
                x['status'],bool(x['disbursement']),x['failure_class'])
                for x in r['annual']}
        changed=[k for k in sorted(semantic(normal)) if
                 semantic(normal)[k]!=semantic(reverse)[k]]
        # Reversal changes one *attempt*: CNES gets a futile built-in-ceiling
        # rejection before ESA claims Ceres, versus being skipped after ESA wins.
        # It does not change funding or the body claimant.
        self.assertEqual(changed,[('CNES',2027)],f'REVERSAL_CHANGED: {changed}')
        self.assertEqual({b:v['claimant'] for b,v in normal['bodies'].items()},
                         {b:v['claimant'] for b,v in reverse['bodies'].items()})
        self.assertEqual({(x['sponsor'],x['year'],x['activity'])
                          for x in normal['annual'] if x['disbursement']},
                         {(x['sponsor'],x['year'],x['activity'])
                          for x in reverse['annual'] if x['disbursement']})
        # Controlled collision proves the fixed order actually matters.
        cfg=four_body_rules()
        for sponsor in ('NASA','CNSA'):
            cfg['rules'][sponsor].update(body='BENNU',a1='BENNU-A1-RESOURCE',
                a2='BENNU-A2-CONCEPT',a1_price='0.15',a2_price='0.25')
        # Other six entries remain, but their claim paths cannot buy Bennu first
        # under the recorded / reversed priority because JAXA is concentration-blocked.
        winners=[]
        for order in (FOUR_BODY_ORDER,tuple(reversed(FOUR_BODY_ORDER))):
            cfg['order']=order
            rows,_=run_gate1(D('.25'),scenario='B',followon_trial=cfg)
            winners.append([r['sponsor'] for r in rows
                            if r['sponsor'] in ('NASA','CNSA') and r['disbursement']])
        self.assertEqual(winners,[['NASA'],['CNSA']])

if __name__=='__main__':
    unittest.main()
