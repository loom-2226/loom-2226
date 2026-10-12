"""Targeted Build 8 opt-in result-triggered pilot tests, not source qualification."""
import unittest
from collections import Counter
from decimal import Decimal as D

from .followon_trial import run_trial, compare_order, _classify
from .followon_rules import trial_rules, FIXED_CLAIM_ORDER
from .route1_gate1 import run_gate1

class FollowonTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trial=run_trial()

    def test_two_results_actually_gate_financed_followons(self):
        r=self.trial
        self.assertEqual(r['claim_order'],('NASA','CNSA'))
        self.assertEqual(r['stops'],
                         {'NASA':'RESULT_INSUFFICIENT','CNSA':'RESULT_INSUFFICIENT'})
        for sponsor,years in (('NASA',(2026,2029)),('CNSA',(2026,2027))):
            funded=[x for x in r['yearly']
                    if x['sponsor']==sponsor and x['disbursement']]
            self.assertEqual(tuple(x['year'] for x in funded),years)
            self.assertEqual(tuple(x['stage'] for x in funded),('A1','A2'))
            a1,a2=r['a1'][sponsor],r['a2'][sponsor]
            self.assertEqual(a1['result'].standing.value,'SUPPORTS_ADVANCE')
            self.assertEqual(a1['review'].outcome.value,'ADVANCE')
            self.assertLess(a1['admitted'].admitted_at,a1['review'].effective_time)
            self.assertLess(a1['review'].effective_time,a2['start'])
            self.assertEqual(a2['result'].standing.value,'INSUFFICIENT')
            self.assertEqual(a2['review'].outcome.value,'DEFER')
            self.assertEqual(a2['kernel'].event_log[0]['funding_transaction'],
                             funded[1]['disbursement'])
            self.assertEqual(a2['kernel'].event_log[0]['prior_result_ref'],
                             a1['result'].result_ref)

    def test_annual_report_bounds_replay_cash_and_classification(self):
        r=self.trial
        self.assertEqual(len(r['yearly']),20)
        self.assertEqual(set(x['year'] for x in r['yearly']),set(range(2026,2036)))
        pairs=Counter((x['sponsor'],x['year']) for x in r['yearly'])
        self.assertTrue(all(v==1 for v in pairs.values()))
        for sponsor in ('NASA','CNSA'):
            rows=[x for x in r['yearly'] if x['sponsor']==sponsor]
            paid=sum((D(x['requested']) for x in rows if x['disbursement']),D(0))
            self.assertLessEqual(paid,D(rows[0]['lifetime_limit']))
            self.assertLessEqual(sum(x['stage']=='A2' and x['event']=='REQUEST'
                                     for x in rows if x['year']==2029),1)
            self.assertTrue(all(x['failure_class'] in (None,'BUILT_IN','EMERGENT')
                                for x in rows))
            self.assertEqual(rows[-1]['chain_stop'],'RESULT_INSUFFICIENT')
        replay=run_trial()
        self.assertEqual(r['yearly'],replay['yearly'])
        self.assertEqual(r['earth_fingerprint'],replay['earth_fingerprint'])
        self.assertEqual(r['a1_fingerprints'],replay['a1_fingerprints'])
        self.assertEqual(r['a2_fingerprints'],replay['a2_fingerprints'])

    def test_reversed_recorded_order_reports_no_change_without_collision(self):
        comparison=compare_order()
        self.assertEqual(comparison['recorded_order'],FIXED_CLAIM_ORDER)
        self.assertEqual(comparison['reversed_order'],('CNSA','NASA'))
        self.assertFalse(comparison['outcome_changed'],comparison)

    def test_reversing_order_changes_winner_when_claims_collide(self):
        # Controlled counterfactual: BOTH sponsors can fund BENNU A1 in 2026.
        # Only the claim ordering changes. No new sponsor/body assignment is canon.
        cfg=trial_rules()
        for sponsor in cfg['rules']:
            cfg['rules'][sponsor]['body']='BENNU'
            cfg['rules'][sponsor]['a1']='BENNU-A1-RESOURCE'
            cfg['rules'][sponsor]['a2']='BENNU-A2-CONCEPT'
            cfg['rules'][sponsor]['a1_price']='0.15'
            cfg['rules'][sponsor]['a2_price']='0.25'
        winners=[]
        for order in (('NASA','CNSA'),('CNSA','NASA')):
            cfg['order']=order
            rows,_=run_gate1(D('.25'),scenario='B',followon_trial=cfg)
            pair={r['sponsor']:r for r in rows if r['sponsor'] in cfg['rules']}
            funded=[s for s in order if pair[s]['disbursement']]
            self.assertEqual(funded,[order[0]])
            self.assertEqual(pair[order[1]]['status'],'WAIT_CLAIMED_BY_OTHER')
            winners.append(funded[0])
        self.assertEqual(winners,['NASA','CNSA'])

    def test_builtin_vs_emergent_are_not_mixed(self):
        self.assertEqual(_classify({'status':'WAIT_CEILING_BELOW_PRICE',
            'policy':'APPROVE','reason':'APPROVED_POLICY_RULE'}),
            ('BUILT_IN','ASSIGNED_PRICE_OVER_SPONSOR_CEILING'))
        self.assertEqual(_classify({'status':'WAIT_POLICY','policy':'REJECT',
            'reason':'CONCENTRATION'}),
            ('EMERGENT','FINANCIER_CONCENTRATION'))
        self.assertEqual(_classify({'status':'WAIT_CUMULATIVE_LIMIT',
            'policy':'APPROVE','reason':'APPROVED_POLICY_RULE'}),
            ('EMERGENT','WAIT_CUMULATIVE_LIMIT'))
        cfg=trial_rules()
        cfg['rules']['CNSA']['a1_price']='0.70'
        rows,_=run_gate1(D('.25'),scenario='B',followon_trial=cfg)
        c=next(x for x in rows if x['sponsor']=='CNSA')
        self.assertFalse(c['disbursement'])
        self.assertEqual(c['status'],'WAIT_CEILING_BELOW_PRICE')

    def test_no_result_means_no_followon_even_with_cash(self):
        cfg=trial_rules()
        rows,_=run_gate1(D('.25'),scenario='B',followon_trial=cfg)
        self.assertEqual(sum(r['sponsor'] in cfg['rules'] and bool(r['disbursement'])
                             for r in rows),2)
        # The externally supplied result is not a priced authorization.
        # Until admitted evidence exists the sponsor cannot buy its A2.
        from .route1_gate2 import run_gate2
        ledger,_=run_gate2(D('.25'),carry_cap=2,end_year=2035,
                            followon_trial=cfg)
        for sponsor in cfg['rules']:
            self.assertEqual(len([x for x in ledger if x['sponsor']==sponsor
                                  and x['disbursement']]),1)
            self.assertEqual(next(x['reason'] for x in ledger
                                  if x['sponsor']==sponsor and x['year']==2035),
                             'WAIT_RESULT')
if __name__=='__main__':
    unittest.main()
