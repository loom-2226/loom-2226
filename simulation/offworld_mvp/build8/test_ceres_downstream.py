"""TEST_ONLY: one-body physical project atop Route 1, with no frozen edits."""
import unittest
from decimal import Decimal as D

from .ceres_downstream import (
    A, TEST_ONLY_TABLE, BODY, SPONSOR, EXECUTOR, NODE, PROJECT, ASSET,
    CASH, FIN_CASH, REINVEST, RESOURCE, BUDGET, SUPPLIER, CeresDownstream,
    run_ceres_downstream,
)
from .route1_all_body_campaign_pr3b import run_all_body_campaign

class CeresDownstreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = run_all_body_campaign(body_count=90)
        cls.first = run_ceres_downstream()
        cls.replay = run_ceres_downstream()

    def test_existing_full_campaign_not_changed(self):
        base = self.base
        funded = [r for r in base['campaign']['receipts']]
        blocked = [r for r in base['campaign']['attempts'] if r['outcome']=='BLOCKED']
        self.assertEqual((len(funded), len(base['kernel'].state.transactions),
                          len(blocked)), (249, 8779, 0))
        self.assertNotIn('P',base['kernel'].state.projects)
        self.assertNotIn('MINE-P',base['kernel'].state.assets)
        self.assertEqual(base['kernel'].state.accounts['earth_market'].balance,D('100'))

    def test_authored_values_are_single_labeled_table(self):
        self.assertEqual(len({key for key, _, _ in TEST_ONLY_TABLE}),len(TEST_ONLY_TABLE))
        self.assertTrue(all(key and value and basis for key,value,basis in TEST_ONLY_TABLE))
        self.assertEqual(A['body'],BODY)
        self.assertEqual(A['sponsor'],SPONSOR)
        self.assertEqual(A['executor'],EXECUTOR)
        self.assertEqual(
            sum((D(A[k]) for k in ('financier_return_share', 'local_reinvest_share',
                    'owner_return_share', 'reserve_share')), D(0)),D(1))
        self.assertEqual(D(A['physical_construction_cost']),
            D(A['construction_stage_1'])+D(A['construction_stage_2']))
        self.assertEqual(D(A['physical_construction_cost'])+D(A['operating_float']),
            D('0.080'))
        self.assertEqual(self.first['authored'], TEST_ONLY_TABLE)

    def test_studies_are_paid_once_before_distinct_construction(self):
        c = self.first['campaign']
        receipts = [r for r in c['receipts'] if r['body']==BODY]
        self.assertEqual([(r['stage'],r['year'],r['sponsor'],r['executor']) for r in receipts],
                         [('A1',2036,SPONSOR,'Airbus Defence and Space'),
                          ('A2',2037,SPONSOR,EXECUTOR)])
        reviews = [r for r in c['studies'] if r['body']==BODY]
        self.assertEqual([(r['stage'],r['year'],r['result']) for r in reviews],
                         [('A1',2037,'SUPPORTS_ADVANCE'),
                          ('A2',2038,'SUPPORTS_ADVANCE')])
        self.assertEqual({r['stage'] for r in receipts},{'A1','A2'})
        fin = next(r for r in c['physical'] if r['stage']=='FINANCE')
        self.assertEqual(fin['study_receipt'], receipts[1]['disbursement_id'])
        self.assertNotEqual(fin['disbursement_tx'],receipts[1]['disbursement_id'])
        self.assertEqual(self.first['kernel'].state.accounts['route1:campaign:cash:CERES:'+SPONSOR].balance,D(0))

    def test_five_stages_on_one_actual_route1_ledger(self):
        k = self.first['kernel']
        stages = {(r['stage'],r['year']) for r in self.first['campaign']['physical']}
        self.assertTrue({
            ('FINANCE',2039),('CONSTRUCTION',2039),('CONSTRUCTION',2040),
            ('COMMISSIONED',2040),('EXTRACTED',2041),('SOLD',2041),
            ('DISTRIBUTED',2041),('REINVESTED_INTO_OPERATIONS',2042),
            ('EXTRACTED',2042),('SOLD',2042),
        }.issubset(stages))
        self.assertEqual(k.state.projects[PROJECT].node_id,NODE)
        self.assertEqual(k.state.projects[PROJECT].status,'OPERATING')
        self.assertEqual(k.state.assets[ASSET].kind.value,'PRODUCTIVE')
        self.assertEqual(k.state.assets[ASSET].capacity,D(A['productive_capacity']))
        txid = {t.id:t for t in k.state.transactions}
        for row in self.first['campaign']['physical']:
            if row['stage'] in ('CONSTRUCTION','SOLD','EXTRACTED'):
                key = 'opex_tx' if row['stage']=='EXTRACTED' else 'tx'
                self.assertIn(row[key],txid)
        fin = next(r for r in self.first['campaign']['physical'] if r['stage']=='FINANCE')
        invest, disburse = txid[fin['investment_tx']],txid[fin['disbursement_tx']]
        self.assertEqual((invest.source_account,invest.destination_account),(BUDGET,FIN_CASH))
        self.assertEqual((disburse.source_account,disburse.destination_account),(FIN_CASH,CASH))
        self.assertEqual(invest.amount,disburse.amount)
        self.assertEqual((invest.amount,invest.purpose.value),(D('0.080'),'OTHER_INVESTMENT'))
        self.assertEqual(k.state.accounts[FIN_CASH].balance,D('0.020'))

    def test_physical_stock_buyer_cash_and_market_quantities(self):
        k = self.first['kernel']
        self.assertEqual(k.resources[RESOURCE].in_situ,D(A['in_situ']))
        self.assertEqual(k.resources[RESOURCE].accessible,D(A['accessible']))
        self.assertEqual(k.resources[RESOURCE].recoverable,D(A['recoverable']))
        self.assertEqual(k.resources[RESOURCE].remaining,D('4'))
        records = [r for r in k.extraction_resolution_records if r.project_id == PROJECT]
        sales = [r for r in k.market_clearing_records if r.project_id == PROJECT]
        self.assertEqual(len(records),2)
        self.assertEqual(len(sales),2)
        self.assertEqual(sum((r.actual_extracted for r in records),D(0)),D('4'))
        self.assertEqual(sum((r.cleared_quantity for r in sales),D(0)),D('4'))
        self.assertEqual(sum((r.transaction_value for r in sales),D(0)),D('.200'))
        self.assertEqual(k.colonies[NODE].resource_inventory,D(0))
        self.assertEqual(k.market_resource_inventory[('EARTH:USA',RESOURCE)],D('4'))
        buyer = k.state.accounts['earth_market']
        self.assertEqual(buyer.balance,D(A['buyer_endowment'])-D('.200'))
        self.assertTrue(all(D(x['before'])>=D(x['paid']) and D(x['after'])>=0
                            for x in self.first['campaign']['buyer_checks']))
        self.assertEqual([x['year'] for x in self.first['campaign']['buyer_checks']], [2041,2042])

    def test_return_and_reinvestment_fund_real_next_year_expense(self):
        k = self.first['kernel']
        physical = self.first['campaign']['physical']
        distribution=next(x for x in physical if x['stage']=='DISTRIBUTED')
        reinvest=next(x for x in physical if x['stage']=='REINVESTED_INTO_OPERATIONS')
        opex=next(x for x in physical if x['stage']=='EXTRACTED' and x['year']==2042)
        txid={t.id:t for t in k.state.transactions}
        transfer = txid[reinvest['transaction']]
        expense = txid[opex['opex_tx']]
        self.assertEqual((transfer.source_account,transfer.destination_account),(REINVEST,CASH))
        self.assertEqual((expense.source_account,expense.destination_account),(CASH,SUPPLIER))
        self.assertEqual(transfer.amount,expense.amount)
        self.assertEqual(transfer.purpose.value,'LOCAL_REINVESTMENT')
        self.assertEqual(expense.purpose.value,'OPEX')
        self.assertEqual(D(distribution['reinvestment']),D('.04'))
        self.assertEqual(k.state.accounts[REINVEST].balance,D('.02'))
        self.assertEqual(D(distribution['financier_return']),D('.02'))
        self.assertEqual(D(distribution['owner_return']),D('.02'))
        self.assertEqual(k.state.accounts[CASH].balance,D('.12'))
        self.assertTrue(any(r.source_commitment_ids==('ceres:physical:commitment',)
                            for r in k.financing_return_claims.values()))

    def test_underfunded_buyer_rejected_without_any_partial_sale(self):
        k=self.first['kernel']
        buyer=k.state.accounts['earth_market']
        colony=k.colonies[NODE]
        previous_cash, previous_inventory=buyer.balance,colony.resource_inventory
        before=(len(k.state.transactions),len(k.market_clearing_records),
                len(k.market_envelopes),len(self.first['campaign']['physical']))
        try:
            buyer.balance=D(0)
            colony.resource_inventory=D(A['demand_per_year'])
            with self.assertRaisesRegex(ValueError,'BLOCKED_AFFORDABILITY'):
                # Fresh calendar year, but guard MUST run before market registration.
                trial=CeresDownstream()
                trial._sell(k,2043)
            after=(len(k.state.transactions),len(k.market_clearing_records),
                   len(k.market_envelopes),len(self.first['campaign']['physical']))
            self.assertEqual(before,after)
            self.assertEqual(colony.resource_inventory,D(A['demand_per_year']))
        finally:
            buyer.balance=previous_cash
            colony.resource_inventory=previous_inventory

    def test_replay_exact_no_new_modes_or_rewrite(self):
        self.assertEqual(self.first['kernel'].fingerprint(),self.replay['kernel'].fingerprint())
        self.assertEqual(self.first['campaign']['physical'],self.replay['campaign']['physical'])
        self.assertEqual(self.first['campaign']['buyer_checks'],self.replay['campaign']['buyer_checks'])
        self.assertEqual(len(self.first['kernel'].state.transactions),8791)
        self.assertEqual(len(self.first['campaign']['receipts']),249)
        self.assertEqual(
            sum(x['outcome']=='BLOCKED' for x in self.first['campaign']['attempts']),0)

if __name__=='__main__':
    unittest.main()
