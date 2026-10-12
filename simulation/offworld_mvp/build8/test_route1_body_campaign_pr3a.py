"""PR 3A: two-body, 201-year, TEST_ONLY funded research campaign controls."""
from collections import Counter, defaultdict
from decimal import Decimal as D
import json
from pathlib import Path
import unittest

from .route1_body_campaign import (
    BODIES, SETTINGS, SPONSORS, BodyCampaign, a1_draw,
    run_body_campaign, decade_counts,
)
from .route1_cast_payments import run_cast_payments
from .test_route1_horizon_pr2 import ledger_transactions, serialized_sha
from .sponsor_executor_network_trial import EXECUTORS, PUBLIC, PRIVATE

GOLDEN=Path(__file__).with_name('ROUTE1_HORIZON_MAIN_79a10e1_BASELINE.json')


class BodyCampaignPR3ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=json.loads(GOLDEN.read_text())
        cls.normal=run_body_campaign()
        cls.lifted=run_body_campaign(ceilings_enabled=False)
        cls.one_sponsor=run_body_campaign(participating_sponsors=('NASA',))
        cls.double_rate=run_body_campaign(max_stages_per_year=2)
        cls.failed=run_body_campaign(failures=(('PHOBOS','A1'),))

    def test_connected_years_sponsors_executors_two_bodies_and_no_second_four_body_history(self):
        r=self.normal;c=r['campaign']
        self.assertEqual(len(r['rows']),201*20)
        self.assertEqual({x['year'] for x in r['rows']},set(range(2026,2227)))
        self.assertEqual(len(r['executor_yearly']),201*16)
        self.assertEqual(r['eligible_executors'],set(EXECUTORS))
        self.assertEqual(len(SPONSORS),20)
        self.assertEqual(set(c['claims']),set(BODIES))
        self.assertEqual(c['claims'],{
            'EUROPA':'Australian Space Agency', 'PHOBOS':'Axiom'})
        self.assertEqual(set(a['body'] for a in c['receipts']),set(BODIES))
        self.assertEqual([(x['body'],x['stage'],x['year']) for x in c['receipts']],
                         [('EUROPA','A1',2036),('PHOBOS','A1',2036),
                          ('PHOBOS','A2',2037)])
        self.assertEqual(len(c['receipts']),3)
        self.assertEqual(len(c['studies']),2)
        self.assertEqual(c['no_a3'],('PHOBOS',))
        self.assertFalse({x['body'] for x in c['attempts']} &
                         {'MOON','MARS','CERES','BENNU'})
        self.assertEqual(len(r['deliveries']),20)  # original paid 2026 pilot remains
        self.assertEqual(len(r['kernel'].state.transactions),8287)
        self.assertEqual(len({(row['year'],row['sponsor']) for row in r['rows']}),
                         201*20)

    def test_review_is_pinned_hash_not_hidden_world_and_positive_only_earns_a2(self):
        c=self.normal['campaign']
        self.assertEqual(str(a1_draw('EUROPA')),
                         '0.6110510016917168358468180901')
        self.assertEqual(str(a1_draw('PHOBOS')),
                         '0.3592648676293149899316784012')
        self.assertEqual({e['body']:e['review'] for e in c['studies']},
                         {'EUROPA':'HOLD','PHOBOS':'ADVANCE'})
        self.assertEqual({e['body']:e['result'] for e in c['studies']},
                         {'EUROPA':'INSUFFICIENT','PHOBOS':'SUPPORTS_ADVANCE'})
        self.assertEqual({e['year'] for e in c['studies']},{2037})
        self.assertEqual({e['positive_threshold'] for e in c['studies']},{'0.50'})
        self.assertTrue(all(e['classification'].startswith('TEST_ONLY_SYNTHETIC')
                            for e in c['studies']))
        self.assertEqual(sum(r['body']=='EUROPA' and r['stage']=='A2' and
                             r['primary_blocker']=='A1_REVIEW_INSUFFICIENT'
                             for r in c['attempts']),1)
        self.assertFalse(any(r['stage']=='A3' for r in c['attempts']))
        self.assertFalse(any(r['physical_mission_claim'] for r in c['receipts']))
        self.assertEqual(len(self.failed['campaign']['receipts']),2)
        self.assertEqual(sum(e['delivery']=='FAILED'
                             for e in self.failed['campaign']['receipts']),1)
        self.assertFalse(any(e['body']=='PHOBOS' and e['stage']=='A2'
                             for e in self.failed['campaign']['receipts']))
        failed_review=next(e for e in self.failed['campaign']['studies']
                           if e['body']=='PHOBOS')
        self.assertEqual(failed_review['result'],'NO_RESULT')
        self.assertIsNone(failed_review['observation_id'])
        self.assertIsNone(failed_review['result_ref'])
        self.assertFalse(any(k.startswith('route1:campaign:observation:PHOBOS')
                             for k in self.failed['kernel'].observations))

    def test_effective_named_settings_limits_and_single_primary_blocker_decade_counts(self):
        c=self.normal['campaign']
        limits=c['limits']
        for key in ('CAMPAIGN_START_YEAR','CAMPAIGN_END_YEAR',
                    'MAX_NEW_STAGES_PER_SPONSOR_YEAR','MAX_CLAIMANTS_PER_BODY_CAMPAIGN',
                    'MAX_AUTHORED_STAGE','SPONSOR_CLAIM_ORDER','BODY_SELECTION_ORDER',
                    'A1_POSITIVE_REVIEW_FRACTION','A1_REVIEW_SEED',
                    'SPONSOR_REQUEST_CEILINGS','FINANCIER_SETTINGS',
                    'EXECUTOR_CAPABILITIES','PRIMARY_BLOCKER_ORDER'):
            self.assertIn(key,limits)
        self.assertEqual(limits['CAMPAIGN_START_YEAR'],2036)
        self.assertEqual(limits['MAX_NEW_STAGES_PER_SPONSOR_YEAR'],1)
        self.assertEqual(limits['MAX_CLAIMANTS_PER_BODY_CAMPAIGN'],1)
        self.assertEqual(limits['MAX_AUTHORED_STAGE'],'A2')
        self.assertEqual(len(limits['SPONSOR_REQUEST_CEILINGS']),20)
        self.assertEqual(limits['FINANCIER_SETTINGS']['max_concentration_fraction'],'0.80')
        self.assertEqual(limits['FINANCIER_RESOURCE_BELIEF'],'0.5')
        self.assertEqual(limits['FINANCIER_RESOURCE_PRIOR'],'0.5')
        self.assertEqual(limits['COUNTRY_ALLOCATION_SHARE'],'0.25')
        self.assertEqual(limits['FINANCIER_UNDERWRITING_FACTS'],dict(
            __import__('simulation.offworld_mvp.build8.route1_gate1',
                       fromlist=['EVIDENCE']).EVIDENCE))
        self.assertIsNone(limits['CARRY_CAP'])
        self.assertIsNone(limits['LIFETIME_SPENDING_CAP'])
        self.assertIsNone(limits['GLOBAL_PROJECT_CAP'])
        self.assertIsNone(limits['EXECUTOR_CAPACITY_CAP'])
        periods=c['decades']
        self.assertEqual(len(periods),20)
        self.assertEqual(periods[0],{
            'period':'2036-2045','attempted':5,'funded':3,
            'blockers':{'A1_REVIEW_INSUFFICIENT':1,
                        'MAX_NEW_STAGES_PER_SPONSOR_YEAR':1}})
        self.assertTrue(all(p['attempted']==p['funded']==0 and not p['blockers']
                            for p in periods[1:]))
        self.assertEqual(sum(p['attempted'] for p in periods),
                         sum(p['funded']+sum(p['blockers'].values()) for p in periods))
        for attempt in c['attempts']:
            if attempt['outcome']=='FUNDED':
                self.assertIsNone(attempt['primary_blocker'])
            else:
                self.assertIn(attempt['primary_blocker'],limits['PRIMARY_BLOCKER_ORDER'])
                self.assertIsInstance(attempt['balance_before'],str)
                self.assertIn('named_stage_limit',attempt)
        self.assertEqual(sum(x['attempted'] for x in c['annual']),5)
        self.assertEqual(sum(x['funded'] for x in c['annual']),3)
        self.assertEqual(len(c['annual']),191)
        self.assertEqual(sum(x['attempted']==0 for x in c['annual']),189)
        self.assertEqual(decade_counts(c['attempts']),periods)

    def test_old_decade_and_previously_paid_pilot_exactly_match_pre_pr3a_main(self):
        main=self.main;r=self.normal
        self.assertEqual(main['base_main_sha'],
                         '79a10e1f70f4992ff83fdbd2e4768c707318839d')
        prefix=[row for row in r['rows'] if row['year']<=2035]
        self.assertEqual(prefix,main['rows'])
        self.assertEqual(list(r['deliveries']),main['deliveries'])
        past=[t for t in ledger_transactions(r['kernel']) if t['year']<=2035]
        self.assertEqual(len(past),450)
        self.assertEqual(past,main['transactions'])
        self.assertEqual(serialized_sha(prefix),
                         '15fdc6b00df21d6b748a67a36fe9fbbca6d6fcb6156222ff1b5657eecca8b9cb')
        self.assertEqual(serialized_sha(past),
                         'f7e5ea74867d051e41bffab7f366bbfb5dd3e801fc4a9d324703eeed55fbea86')
        decade=run_cast_payments()
        self.assertEqual(decade['rows'],main['rows'])
        self.assertEqual(decade['kernel'].fingerprint(),main['fingerprint'])
        self.assertEqual(ledger_transactions(decade['kernel']),main['transactions'])

    def test_all_201_years_conserved_countries_sponsors_project_cash_and_suppliers(self):
        r=self.normal;k=r['kernel']
        years={y:[] for y in range(2026,2227)}
        rows={(row['year'],row['sponsor']):row for row in r['rows']}
        for tx in k.state.transactions:
            years[tx.year].append(tx)
        previous={s:D(0) for s in SPONSORS}
        funded_total=paid_total=D(0)
        origins=set()
        for year in range(2026,2227):
            transactions=years[year]
            country_sources={t.source_account for t in transactions
                             if t.source_account.startswith('route1:origin:')}
            origins.update(country_sources)
            self.assertEqual(len(country_sources),23)
            for source in country_sources:
                self.assertEqual(k.state.accounts[source].balance,D(0))
            for sponsor in SPONSORS:
                row=rows[year,sponsor]
                budget='route1:budget:'+sponsor
                allocated=sum((t.amount for t in transactions
                               if t.destination_account==budget and
                               t.source_account.startswith('route1:origin:')),D(0))
                funded=sum((t.amount for t in transactions
                            if t.source_account==budget and
                            t.purpose.value=='DISBURSE'),D(0))
                close=D(row['closing'])
                self.assertLessEqual(abs(previous[sponsor]+allocated-funded-close),
                                     D('1e-24'),(sponsor,year))
                self.assertEqual(D(row['opening']),
                                 allocated if year==2026 else previous[sponsor])
                if year>2026:
                    self.assertEqual(D(row['allocated']),allocated)
                if year>=2036:
                    self.assertEqual(D(row['campaign_spend']),funded)
                else:
                    self.assertNotIn('campaign_spend',row)
                previous[sponsor]=close
            disburse=sum((t.amount for t in transactions
                          if t.purpose.value=='DISBURSE'),D(0))
            payments=sum((t.amount for t in transactions
                          if t.source_account.startswith('route1:cash:') or
                          t.source_account.startswith('route1:campaign:cash:')
                          if t.purpose.value=='CAPEX'),D(0))
            self.assertEqual(disburse,payments,(year,'funding and payments'))
            funded_total+=disburse
            paid_total+=payments
        self.assertEqual(funded_total,paid_total)
        self.assertEqual(len(origins),23*201)
        self.assertEqual(funded_total,D('.395'))
        for sponsor in SPONSORS:
            self.assertEqual(k.state.accounts['route1:budget:'+sponsor].balance,
                             previous[sponsor])
        self.assertTrue(all(k.state.accounts['route1:campaign:cash:'+
                                                 receipt['body']+':'+receipt['sponsor']].balance==0
                            for receipt in r['campaign']['receipts']))
        for receipt in r['campaign']['receipts']:
            trans={tx.id:tx for tx in k.state.transactions}
            payment=trans[receipt['supplier_payment_id']]
            disburse=trans[receipt['disbursement_id']]
            self.assertEqual(payment.parent_ids,(disburse.id,))
            self.assertEqual(payment.amount,disburse.amount)
            self.assertEqual(payment.destination_account,
                             'route1:executor:'+receipt['executor'])
        k.assert_invariants()

    def test_repeated_body_projects_for_one_sponsor_and_stage_limit_is_measured(self):
        c=self.one_sponsor['campaign']
        self.assertEqual(c['claims'],{'EUROPA':'NASA','PHOBOS':'NASA'})
        self.assertEqual([(a['year'],a['body'],a['stage'])
                          for a in c['attempts'] if a['outcome']=='FUNDED'],
                         [(2036,'EUROPA','A1'),(2037,'PHOBOS','A1'),
                          (2038,'PHOBOS','A2')])
        self.assertEqual(c['decades'][0]['blockers'],{
            'A1_REVIEW_INSUFFICIENT':1,'MAX_NEW_STAGES_PER_SPONSOR_YEAR':1})
        # Raising our TEST_ONLY per-sponsor limit does not add a body,
        # but transfers the Phobos claim to the first sponsor.
        cap2=self.double_rate['campaign']
        self.assertEqual(cap2['claims'],{
            'EUROPA':'Australian Space Agency','PHOBOS':'Australian Space Agency'})
        self.assertEqual(len(cap2['receipts']),3)
        self.assertEqual(cap2['decades'][0]['blockers'],
                         {'A1_REVIEW_INSUFFICIENT':1})
        self.assertNotEqual(cap2['claims'],self.normal['campaign']['claims'])

    def test_ceiling_lift_changes_one_setting_only_and_fundability_is_measured(self):
        ordinary=self.normal['campaign']; lifted=self.lifted['campaign']
        initial=ordinary['limits']; alternative=lifted['limits']
        self.assertEqual({k for k in initial if initial[k]!=alternative[k]},
                         {'SPONSOR_REQUEST_CEILINGS_ENABLED'})
        self.assertEqual(initial['SPONSOR_REQUEST_CEILINGS_ENABLED'],True)
        self.assertEqual(alternative['SPONSOR_REQUEST_CEILINGS_ENABLED'],False)
        self.assertEqual(ordinary['claims'],lifted['claims'])
        self.assertEqual(len(ordinary['claims']),len(lifted['claims']),2)
        self.assertEqual(ordinary['decades'][0]['funded'],lifted['decades'][0]['funded'],3)
        self.assertEqual(ordinary['decades'][0]['blockers'],
                         lifted['decades'][0]['blockers'])
        self.assertEqual(len(ordinary['attempts']),len(lifted['attempts']))
        self.assertEqual(len(self.normal['kernel'].state.transactions),
                         len(self.lifted['kernel'].state.transactions))
        self.assertEqual([(x['year'],x['body'],x['stage'],x['sponsor'],
                           x['disbursement_id']) for x in ordinary['receipts']],
                         [(x['year'],x['body'],x['stage'],x['sponsor'],
                           x['disbursement_id']) for x in lifted['receipts']])
        self.assertEqual([x['closing'] for x in self.normal['rows']],
                         [x['closing'] for x in self.lifted['rows']])

    def test_full_campaign_replay_is_bitwise_reproducible(self):
        again=run_body_campaign()
        self.assertEqual(again['campaign'],self.normal['campaign'])
        self.assertEqual(again['rows'],self.normal['rows'])
        self.assertEqual(again['kernel'].fingerprint(),
                         self.normal['kernel'].fingerprint())
