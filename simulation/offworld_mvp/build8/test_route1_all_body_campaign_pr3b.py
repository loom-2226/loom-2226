"""PR 3B: 90/90 connected body states, paid retries and protected history."""
from collections import Counter, defaultdict
from decimal import Decimal as D
import json
from pathlib import Path
import unittest

from .route1_all_body_campaign_pr3b import (
    ALL_BODIES, AUTHORING, PR3B_SETTINGS, REFERENCE_STATUS, AllBodyCampaign,
    review_draw, run_all_body_campaign,
)
from .route1_body_campaign import SPONSORS, SETTINGS, decade_counts, a1_draw
from .sponsor_executor_network_trial import EXECUTORS
from .test_route1_horizon_pr2 import ledger_transactions, serialized_sha

GOLDEN = Path(__file__).with_name('ROUTE1_HORIZON_MAIN_79a10e1_BASELINE.json')


class Route1NinetyBodyPR3BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ordered checkpoint first. Each scenario owns one conserved ledger.
        cls.half = run_all_body_campaign(body_count=45)
        cls.full = run_all_body_campaign(body_count=90)
        cls.baseline = json.loads(GOLDEN.read_text())

    def test_45_body_checkpoint_and_authored_results(self):
        c = self.half['campaign']
        self.assertEqual(c['body_count'], 45)
        self.assertEqual(len(c['body_yearly']), 45*201)
        self.assertEqual(len({(x['body'],x['year']) for x in c['body_yearly']}),45*201)
        self.assertEqual({x['year'] for x in c['body_yearly']},set(range(2026,2227)))
        self.assertEqual(len(self.half['rows']), 201*20)
        self.assertEqual(len(self.half['executor_yearly']), 201*16)
        self.assertEqual(set(AUTHORING),set(c['eligible_body_ids']) & set(AUTHORING))
        authored = {body: [(r['stage'],r['result'],r['year'])
                           for r in c['studies'] if r['body']==body]
                    for body in AUTHORING}
        self.assertEqual(authored, {
            'BENNU':[('A1','SUPPORTS_ADVANCE',2037),('A2','INSUFFICIENT',2038)],
            'CERES':[('A1','SUPPORTS_ADVANCE',2037),('A2','SUPPORTS_ADVANCE',2038)],
            'MARS':[('A1','SUPPORTS_ADVANCE',2037),('A2','INSUFFICIENT',2038)],
            'MOON':[('A1','SUPPORTS_ADVANCE',2037),('A2','INSUFFICIENT',2038)]})
        self.assertTrue(all(r['year']==2036 for r in c['receipts']
                            if r['body'] in AUTHORING and r['stage']=='A1'))
        self.assertTrue(all(r['draw'] is None for r in c['studies']
                            if r['body'] in AUTHORING))
        self.assertEqual(len(c['runtime_decades']),21)
        self.assertGreater(c['runtime_total_seconds'],0)

    def test_full_90_body_201_year_20_sponsor_16_executor_coverage(self):
        c=self.full['campaign']
        self.assertEqual(len(ALL_BODIES),90)
        self.assertEqual(tuple(c['eligible_body_ids']),ALL_BODIES)
        self.assertEqual(len(c['body_yearly']),90*201)
        self.assertEqual(len({(x['body'],x['year']) for x in c['body_yearly']}),18090)
        self.assertEqual(Counter(x['year'] for x in c['body_yearly']),
                         Counter({year:90 for year in range(2026,2227)}))
        self.assertEqual(len(self.full['rows']),20*201)
        self.assertEqual(Counter(x['year'] for x in self.full['rows']),
                         Counter({year:20 for year in range(2026,2227)}))
        self.assertEqual(set(x['sponsor'] for x in self.full['rows']),SPONSORS)
        self.assertEqual(len(self.full['executor_yearly']),16*201)
        self.assertEqual(Counter(x['year'] for x in self.full['executor_yearly']),
                         Counter({year:16 for year in range(2026,2227)}))
        self.assertEqual({x['executor'] for x in self.full['executor_yearly']},
                         set(EXECUTORS))
        self.assertEqual(len(c['claims']),90)
        self.assertEqual({r['body'] for r in c['receipts']},set(ALL_BODIES))
        self.assertEqual({r['body'] for r in c['receipts'] if r['stage']=='A2'},
                         set(ALL_BODIES))
        self.assertTrue(all(r['year']>=2036 for r in c['receipts']))
        self.assertEqual(len(self.full['deliveries']),20)

    def test_exact_seven_unknown_accessibility_but_still_funded(self):
        c=self.full['campaign']
        unknown={'DACTYL','HYDRA','KERBEROS','NIX','PROTEUS','SELAM','STYX'}
        self.assertEqual({b for b,v in c['accessibility'].items()
                          if v=='ACCESS_UNKNOWN'},unknown)
        self.assertEqual(len([r for r in c['body_yearly']
                              if r['accessibility']=='ACCESS_UNKNOWN']),7*201)
        self.assertEqual({r['body'] for r in c['receipts']}&unknown,unknown)
        self.assertEqual(set(REFERENCE_STATUS),set(ALL_BODIES))
        self.assertEqual(Counter(REFERENCE_STATUS.values()),
                         Counter({'DERIVABLE':83,'UNKNOWN':7}))
        self.assertFalse(any('TRAJECTORY' in str(x['output'])
                             for x in c['receipts']))

    def test_a1_insufficient_reopens_with_separate_paid_transactions(self):
        c=self.full['campaign']
        self.assertTrue(c['reopened_bodies'])
        self.assertTrue(all(n>=2 for b,n in c['a1_attempt_counts'].items()
                            if b in c['reopened_bodies']))
        for body in c['reopened_bodies']:
            receipts=[r for r in c['receipts'] if r['body']==body
                      and r['stage']=='A1']
            self.assertEqual(len(receipts),c['a1_attempt_counts'][body])
            self.assertEqual({r['study_attempt'] for r in receipts},
                             set(range(1,len(receipts)+1)))
            self.assertEqual(len({r['disbursement_id'] for r in receipts}),
                             len(receipts))
            self.assertEqual(len({r['supplier_payment_id'] for r in receipts}),
                             len(receipts))
            studies=[x for x in c['studies'] if x['body']==body
                     and x['stage']=='A1']
            self.assertEqual(len(studies),len(receipts))
            self.assertEqual(studies[-1]['review'],'ADVANCE')
            self.assertTrue(any(s['review']=='HOLD' for s in studies[:-1]))
            self.assertEqual(len({s['result_ref'] for s in studies}),len(studies))
        self.assertEqual(review_draw('EUROPA',1),a1_draw('EUROPA'))
        self.assertEqual(review_draw('PHOBOS',1),a1_draw('PHOBOS'))
        self.assertNotEqual(review_draw('EUROPA',1),review_draw('EUROPA',2))

    def test_paid_failure_reopens_without_manufacturing_evidence(self):
        # A single specifically identified failed A1 must not corrupt its retry.
        run=run_all_body_campaign(body_count=45,failures=(('AMUN','A1',1),))
        c=run['campaign']
        a1=[r for r in c['receipts'] if r['body']=='AMUN' and r['stage']=='A1']
        self.assertGreaterEqual(len(a1),2)
        self.assertEqual(a1[0]['delivery'],'FAILED')
        self.assertEqual(a1[1]['delivery'],'DELIVERED')
        s=next(x for x in c['studies'] if x['body']=='AMUN'
               and x['stage']=='A1' and x['attempt']==1)
        self.assertEqual((s['result'],s['review']),('NO_RESULT','HOLD'))
        self.assertIsNone(s['observation_id'])
        self.assertIsNone(s['result_ref'])
        self.assertNotEqual(a1[0]['disbursement_id'],a1[1]['disbursement_id'])
        self.assertFalse(any(o.startswith('route1:pr3b:observation:AMUN:A1:1:')
                             for o in run['kernel'].observations))
        self.assertEqual(len(c['body_yearly']),45*201)
        run['kernel'].assert_invariants()

    def test_named_limits_decade_primary_blockers_no_hidden_governor(self):
        c=self.full['campaign']
        l=c['limits']
        self.assertIsNone(l['MAX_NEW_STAGES_PER_SPONSOR_YEAR'])
        self.assertEqual(l['SPONSOR_ALLOCATION_ORDER'],'REPEATED_CAST_ID_ROUNDS')
        self.assertIsNone(l['A1_RETRY_LIMIT'])
        self.assertIsNone(l['GLOBAL_PROJECT_CAP'])
        self.assertIsNone(l['EXECUTOR_CAPACITY_CAP'])
        self.assertIsNone(l['CARRY_CAP'])
        self.assertIsNone(l['LIFETIME_SPENDING_CAP'])
        self.assertEqual(l['MAX_ACTIVE_CLAIMANTS_PER_BODY'],1)
        self.assertEqual(l['A1_REOPEN_ON'],('INSUFFICIENT','NO_RESULT'))
        self.assertEqual(l['MAX_AUTHORED_STAGE'],'A2')
        self.assertEqual(l['SPONSOR_REQUEST_CEILINGS'],SETTINGS['SPONSOR_REQUEST_CEILINGS'])
        self.assertEqual(len(c['decades']),20)
        self.assertEqual(c['decades'],decade_counts(c['attempts']))
        self.assertEqual(len(c['attempts']),sum(d['attempted'] for d in c['decades']))
        self.assertEqual(sum(a['outcome']=='FUNDED' for a in c['attempts']),
                         len(c['receipts']))
        for decade in c['decades']:
            self.assertEqual(decade['attempted'],
                             decade['funded']+sum(decade['blockers'].values()))
        for row in c['attempts']:
            self.assertEqual(row['outcome']=='BLOCKED',
                             row['primary_blocker'] is not None)
            if row['primary_blocker'] is not None:
                self.assertIn(row['primary_blocker'],l['PRIMARY_BLOCKER_ORDER'])
        self.assertTrue(all(r['named_stage_limit'] is None for r in c['attempts']))

    def test_real_blocked_request_has_one_named_primary_reason(self):
        from unittest.mock import patch
        from .route1_cast_payments import run_cast_payments
        fixture = run_cast_payments(end_year=2035)
        k = fixture['kernel']
        campaign = AllBodyCampaign(body_count=45)
        before = len(k.state.transactions)
        with patch.object(campaign, 'quote', return_value=None):
            event = campaign.attempt(k, 'NASA', 'AMUN', 'A1', 2036)
        self.assertEqual(event['outcome'], 'BLOCKED')
        self.assertEqual(event['primary_blocker'], 'COMPARABLE_EXECUTOR_QUOTE')
        self.assertIsNone(event['policy_reason'])
        self.assertEqual(len(k.state.transactions), before)
        counts = decade_counts(campaign.attempts)
        self.assertEqual((counts[0]['attempted'], counts[0]['funded']),
                         (1, 0))
        self.assertEqual(counts[0]['blockers'],
                         {'COMPARABLE_EXECUTOR_QUOTE': 1})
        self.assertTrue(all(x['attempted']==0 for x in counts[1:]))

    def test_first_decade_old_201_year_money_and_suppliers_conserved(self):
        r=self.full;c=r['campaign'];k=r['kernel']
        old=self.baseline
        first=[row for row in r['rows'] if row['year']<=2035]
        self.assertEqual(first,old['rows'])
        self.assertEqual(list(r['deliveries']),old['deliveries'])
        self.assertEqual([t for t in ledger_transactions(k) if t['year']<=2035],
                         old['transactions'])
        self.assertEqual(serialized_sha(first),
                         '15fdc6b00df21d6b748a67a36fe9fbbca6d6fcb6156222ff1b5657eecca8b9cb')
        by_year=defaultdict(list)
        id_map={}
        for tx in k.state.transactions:
            by_year[tx.year].append(tx)
            id_map[tx.id]=tx
        rows={(row['year'],row['sponsor']):row for row in r['rows']}
        previous={s:D(0) for s in SPONSORS}
        origins=set()
        for year in range(2026,2227):
            txs=by_year[year]
            source_ids={t.source_account for t in txs if
                        t.source_account.startswith('route1:origin:')}
            self.assertEqual(len(source_ids),23)
            origins.update(source_ids)
            self.assertTrue(all(k.state.accounts[s].balance==0 for s in source_ids))
            allocations=defaultdict(lambda:D(0))
            spent=defaultdict(lambda:D(0))
            paid=disb=D(0)
            for tx in txs:
                if tx.source_account.startswith('route1:origin:'):
                    allocations[tx.destination_account.removeprefix('route1:budget:')]+=tx.amount
                if tx.purpose.value=='DISBURSE':
                    spent[tx.source_account.removeprefix('route1:budget:')]+=tx.amount
                    disb+=tx.amount
                if (tx.purpose.value=='CAPEX' and
                    (tx.source_account.startswith('route1:cash:') or
                     tx.source_account.startswith('route1:campaign:cash:'))):
                    paid+=tx.amount
            self.assertEqual(disb,paid,(year,'supplier payments'))
            for sponsor in SPONSORS:
                row=rows[year,sponsor]
                close=D(row['closing'])
                self.assertLessEqual(abs(previous[sponsor]+allocations[sponsor]-
                                         spent[sponsor]-close),D('1e-24'))
                if year>=2036:
                    self.assertEqual(D(row['campaign_spend']),spent[sponsor])
                previous[sponsor]=close
        self.assertEqual(len(origins),23*201)
        self.assertEqual(len({(x['year'],x['body']) for x in c['body_yearly']}),90*201)
        for receipt in c['receipts']:
            tx=id_map[receipt['disbursement_id']]
            payment=id_map[receipt['supplier_payment_id']]
            self.assertEqual(payment.parent_ids,(tx.id,))
            self.assertEqual(tx.amount,payment.amount)
            self.assertEqual(payment.destination_account,
                             'route1:executor:'+receipt['executor'])
            self.assertEqual(k.state.accounts['route1:campaign:cash:'+
                             receipt['body']+':'+receipt['sponsor']].balance,D(0))
        k.assert_invariants()

    def test_runtime_each_decade_total_and_receipt_accounting(self):
        c=self.full['campaign']
        self.assertEqual(c['runtime_years'],201)
        self.assertEqual(len(c['runtime_decades']),21)
        self.assertGreater(c['runtime_total_seconds'],0)
        self.assertGreater(sum(x['seconds'] for x in c['runtime_decades']),0)
        self.assertLessEqual(sum(x['seconds'] for x in c['runtime_decades']),
                             c['runtime_total_seconds']+1)
        self.assertEqual(c['runtime_decades'][0]['period'],'2026-2035')
        self.assertEqual(c['runtime_decades'][-1]['period'],'2226-2226')
        self.assertEqual(sum(int(x['period'].split('-')[1]) -
                             int(x['period'].split('-')[0])+1 for x in
                             c['runtime_decades']),201)
        self.assertEqual(sum(r['campaign_stages'] for r in self.full['rows']
                             if r['year']>=2036),len(c['receipts']))
        self.assertEqual(sum(D(r['campaign_spend']) for r in self.full['rows']
                             if r['year']>=2036),
                         sum(D(r['amount']) for r in c['receipts']))

    def test_exact_replay_of_90_body_world_without_runtime_fields(self):
        replay=run_all_body_campaign(body_count=90)
        for k in ('eligible_body_ids','body_yearly','accessibility','attempts',
                  'receipts','studies','claims','decades','annual',
                  'a1_attempt_counts','reopened_bodies','source_standings'):
            self.assertEqual(self.full['campaign'][k],replay['campaign'][k],k)
        self.assertEqual(self.full['rows'],replay['rows'])
        self.assertEqual(self.full['executor_yearly'],replay['executor_yearly'])
        self.assertEqual(self.full['kernel'].fingerprint(),
                         replay['kernel'].fingerprint())
