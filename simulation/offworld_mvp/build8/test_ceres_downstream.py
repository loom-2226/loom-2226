"""Ceres TEST_ONLY treasury returns, authorized operator, and replayed funding."""
import unittest
from decimal import Decimal as D

from offworld_kernel.model import AccountKind, TxPurpose
from .ceres_downstream import (
    A, TEST_ONLY_TABLE, BODY, SPONSOR, EXECUTOR, PROJECT, ASSET,
    CASH, FIN_CASH, REINVEST, RESOURCE, BUDGET, SUPPLIER, CeresDownstream,
    AGENCY_OWNER_TYPES, OPERATOR_GRANTS, APPROPRIATIONS, run_ceres_downstream)
from .return_routing import (
    DESTINATIONS, SOURCE, agency_owner_type, apply_operator_grants, resolve_destination)
from .route1_all_body_campaign_pr3b import run_all_body_campaign
from .route1_gate1 import run_gate1


class CeresDownstreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = run_all_body_campaign(body_count=90)
        cls.first = run_ceres_downstream()
        cls.replay = run_ceres_downstream()

    def test_legacy_mode_has_zero_grants_and_pinned_90_body_baseline(self):
        base = self.base
        self.assertEqual((len(base['campaign']['receipts']),
                          len(base['kernel'].state.transactions),
                          sum(r['outcome'] == 'BLOCKED' for r in base['campaign']['attempts'])),
                         (249, 8779, 0))
        self.assertFalse(any(cap.startswith('OPERATE_PROJECT:')
                             for agent in base['kernel'].agents.values()
                             for cap in agent.capabilities))
        self.assertNotIn(PROJECT, base['kernel'].state.projects)
        # Standalone Gate 1 remains empty too, not just the 90-body subclass.
        _, pilot = run_gate1()
        self.assertFalse(any(cap.startswith('OPERATE_PROJECT:')
                             for agent in pilot.agents.values()
                             for cap in agent.capabilities))

    def test_authored_source_rows_and_missing_owner_type_fail_closed(self):
        self.assertEqual(len({key for key,_,_ in TEST_ONLY_TABLE}), len(TEST_ONLY_TABLE))
        self.assertTrue(all(k and v and reason for k,v,reason in TEST_ONLY_TABLE))
        self.assertEqual(self.first['authored'], TEST_ONLY_TABLE)
        self.assertEqual(agency_owner_type('ISRO', AGENCY_OWNER_TYPES), 'public_agency')
        with self.assertRaisesRegex(ValueError, 'missing'):
            agency_owner_type('ISRO', ())
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            agency_owner_type('ISRO', AGENCY_OWNER_TYPES + AGENCY_OWNER_TYPES)
        self.assertEqual(len(OPERATOR_GRANTS), 1)
        self.assertEqual(len(APPROPRIATIONS), 2)

    def test_operator_grants_are_authored_and_validate_existing_project(self):
        k = self.first['kernel']
        reported = self.first['campaign']['operator_grants']
        self.assertEqual(len(reported), len(OPERATOR_GRANTS))
        self.assertEqual({(r['agency'], r['project'], r['owner'], r['reason'])
                          for r in reported}, set(OPERATOR_GRANTS))
        self.assertEqual(k.state.projects[PROJECT].owners, {'STATE:IND': D(1)})
        for r in reported:
            self.assertIn(r['project'], k.state.projects)
            self.assertIn(r['agency'], k.agents)
            self.assertIn(r['owner'], k.state.projects[r['project']].owners)
            self.assertIn(r['capability'], k.agents[r['agency']].capabilities)
        self.assertNotIn(SPONSOR, k.state.projects[PROJECT].owners)
        self.assertEqual({(a,cap) for a,agent in k.agents.items()
                          for cap in agent.capabilities if cap.startswith('OPERATE_PROJECT:')},
                         {(SPONSOR, 'OPERATE_PROJECT:'+PROJECT)})
        with self.assertRaisesRegex(ValueError,'invalid authored'):
            apply_operator_grants(k, ((SPONSOR,'MISSING','STATE:IND','invalid'),))
        with self.assertRaisesRegex(ValueError,'duplicate'):
            apply_operator_grants(k, OPERATOR_GRANTS + OPERATOR_GRANTS)

    def test_destination_table_resolution_general_without_other_physical_runs(self):
        k = self.first['kernel']
        self.assertEqual(set(DESTINATIONS), {(SOURCE,t) for t in
                                             ('public_agency','private_company','financier')})
        self.assertEqual(resolve_destination(k,SOURCE,'public_agency','STATE:IND',SPONSOR)['account'],
                         'treasury:IND')
        self.assertEqual(resolve_destination(k,SOURCE,'private_company',SPONSOR,SPONSOR)['account'],
                         BUDGET)
        self.assertEqual(resolve_destination(k,SOURCE,'private_company',SPONSOR,SPONSOR,
                             overrides=((SOURCE,'private_company',SPONSOR,
                                         'company_funds',0),))['account'], BUDGET)
        claim=k.financing_return_claims['ceres:physical:return_claim']
        self.assertEqual(resolve_destination(k,SOURCE,'financier',claim.financier_id,SPONSOR,
                                             financing_claim=claim)['account'], FIN_CASH)
        with self.assertRaisesRegex(ValueError,'missing return destination'):
            resolve_destination(k,'UNKNOWN','public_agency','STATE:IND',SPONSOR)
        with self.assertRaisesRegex(ValueError,'matching validated claim'):
            resolve_destination(k,SOURCE,'financier',claim.financier_id,SPONSOR)
        with self.assertRaisesRegex(ValueError,'mismatch'):
            resolve_destination(k,SOURCE,'public_agency','STATE:USA',SPONSOR)

    def test_owner_treasury_account_unique_nonagent_and_direct_returns(self):
        k=self.first['kernel']; treasury=k.state.accounts['treasury:IND']
        self.assertNotIn('STATE:IND',k.agents)
        self.assertEqual((treasury.owner_id,treasury.kind,treasury.node_id),
                         ('STATE:IND',AccountKind.FUNDS,'EARTH:IND'))
        self.assertEqual(len([a for a in k.state.accounts.values()
                              if a.owner_id=='STATE:IND' and a.kind==AccountKind.FUNDS]),1)
        rows=k.surplus_distribution_records
        self.assertEqual([(r.year,r.owner_distribution,r.financier_return,
                           r.local_reinvestment,r.reserve) for r in rows],
                         [(2041,D('.020'),D('.020'),D('.040'),D('.020')),
                          (2042,D('.040'),D(0),D('.040'),D('.040'))])
        self.assertEqual([(r.owner_allocations[0].destination_account_id,
                           r.owner_allocations[0].amount) for r in rows],
                         [('treasury:IND',D('.020')),('treasury:IND',D('.040'))])
        for r in rows:
            for owner in r.owner_allocations:
                tx=next(t for t in k.state.transactions if t.id==owner.transaction_id)
                self.assertEqual((tx.destination_account,tx.purpose),
                                 ('treasury:IND',TxPurpose.OWNER_DISTRIBUTION))
        self.assertEqual(k.financing_return_remaining('ceres:physical:return_claim'),D(0))
        self.assertEqual(k.state.accounts[FIN_CASH].balance,D('.020'))

    def test_original_study_and_construction_are_separate(self):
        c=self.first['campaign']
        receipts=[r for r in c['receipts'] if r['body']==BODY]
        self.assertEqual([(r['stage'],r['year'],r['sponsor']) for r in receipts],
                         [('A1',2036,SPONSOR),('A2',2037,SPONSOR)])
        self.assertEqual([r['year'] for r in c['studies'] if r['body']==BODY and r['stage']=='A2'],
                         [2038])
        stages=[r for r in c['physical'] if r['stage']=='CONSTRUCTION']
        self.assertEqual([(r['year'],D(r['amount'])) for r in stages],
                         [(2039,D('.030')),(2040,D('.030'))])

    def test_four_operations_sale_stock_and_buyer_conservation(self):
        k=self.first['kernel']
        extraction=[r for r in k.extraction_resolution_records if r.project_id==PROJECT]
        sales=[r for r in k.market_clearing_records if r.project_id==PROJECT]
        self.assertEqual([(r.year,r.actual_extracted) for r in extraction],
                         [(2041,D(2)),(2042,D(2)),(2043,D(2)),(2044,D(2))])
        self.assertEqual((k.resources[RESOURCE].in_situ,k.resources[RESOURCE].accessible,
                          k.resources[RESOURCE].recoverable,k.resources[RESOURCE].remaining),
                         (D(20),D(10),D(8),D(0)))
        self.assertEqual([(r.year,r.transaction_value) for r in sales],
                         [(2041,D('.100')),(2042,D('.100'))])
        self.assertEqual(k.state.accounts['earth_market'].balance,D('99.800'))
        self.assertEqual(k.state.accounts[CASH].balance,D('.020'))
        self.assertEqual(k.colonies['OFF:ROUTE1:CERES'].resource_inventory,D(4))
        self.assertEqual(k.market_resource_inventory[('EARTH:USA',RESOURCE)],D(4))

    def test_2043_reserve_no_hidden_fallback_and_2044_scripted_cost(self):
        k=self.first['kernel']; c=self.first['campaign']; tx={t.id:t for t in k.state.transactions}
        self.assertEqual([(r['year'],r['stage']) for r in c['physical']
                          if r['stage'] in ('PROJECT_RESERVE_FUNDED_OPERATIONS',
                          'APPROPRIATION_FUNDED_OPERATIONS_SCRIPTED')],
                         [(2043,'PROJECT_RESERVE_FUNDED_OPERATIONS'),
                          (2044,'APPROPRIATION_FUNDED_OPERATIONS_SCRIPTED')])
        expense_2043=next(r for r in c['physical'] if
                          r['stage']=='EXTRACTED' and r['year']==2043)
        self.assertEqual((tx[expense_2043['opex_tx']].source_account,
                          tx[expense_2043['opex_tx']].amount),
                         (CASH,D('.020')))
        self.assertFalse(any(t.year==2043 and t.source_location.startswith('EARTH:')
                             and t.destination_location.startswith('OFF:') and
                             t.purpose in (TxPurpose.OTHER_INVESTMENT,TxPurpose.DISBURSE,
                                           TxPurpose.PUBLIC_SUBSIDY)
                             for t in k.state.transactions))
        spent=c['return_spends']
        self.assertEqual(len(spent),1)
        flow=spent[0]
        self.assertEqual((flow['year'],D(flow['amount']),flow['classification']),
                         (2044,D('.020'),'SCRIPTED_NOT_A_DECISION'))
        appropriation=tx[flow['source_appropriation_tx']]
        owner_return=tx[flow['source_return_tx']]
        sale=tx[flow['source_sale_tx']]
        capital=tx[flow['funding_tx']]
        expense=tx[flow['expense_tx']]
        self.assertEqual((sale.year,owner_return.year,appropriation.year,
                          capital.year,expense.year),(2041,2041,2044,2044,2044))
        self.assertEqual((sale.purpose,owner_return.purpose,appropriation.purpose,
                          capital.purpose,expense.purpose),
                         (TxPurpose.REVENUE,TxPurpose.OWNER_DISTRIBUTION,
                          TxPurpose.PUBLIC_SUBSIDY,TxPurpose.OTHER_INVESTMENT,TxPurpose.OPEX))
        self.assertEqual((appropriation.source_account,appropriation.destination_account),
                         ('treasury:IND',BUDGET))
        self.assertEqual((capital.source_account,capital.destination_account),(BUDGET,CASH))
        self.assertEqual((expense.source_account,expense.destination_account),(CASH,SUPPLIER))
        self.assertTrue({sale.id,owner_return.id}<=set(appropriation.parent_ids))
        self.assertTrue({sale.id,owner_return.id,appropriation.id}<=set(capital.parent_ids))
        self.assertEqual((capital.amount,expense.amount),(D('.020'),D('.020')))

    def test_delayed_2044_2045_appropriations_2045_unspent(self):
        k=self.first['kernel']; c=self.first['campaign']; tx={t.id:t for t in k.state.transactions}
        rows=c['appropriations']
        self.assertEqual([(r['receipt_year'],r['eligible_year'],r['paid_year'],
                           D(r['amount']),D(r['spent_on_ceres']),D(r['unspent_amount']))
                          for r in rows],
                         [(2041,2044,2044,D('.020'),D('.020'),D(0)),
                          (2042,2045,2045,D('.040'),D(0),D('.040'))])
        for r in rows:
            self.assertTrue(r['scripted'])
            self.assertGreaterEqual(r['paid_year'],r['eligible_year'])
            self.assertEqual(D(r['amount']),D(r['spent_on_ceres'])+D(r['unspent_amount']))
            t=tx[r['tx']]
            self.assertEqual((t.year,t.source_account,t.destination_account),
                             (r['paid_year'],'treasury:IND',BUDGET))
            self.assertIn(r['source_return_tx'],t.parent_ids)
        self.assertFalse(any(r['paid_year']==2043 for r in rows))
        self.assertEqual(k.state.accounts['treasury:IND'].balance,D(0))
        self.assertTrue(any(r['year']==2045 and r['stage']=='TREASURY_APPROPRIATION'
                            and D(r['unspent_amount'])==D('.040') for r in c['physical']))
        self.assertGreaterEqual(k.state.accounts[BUDGET].balance,D('.040'))

    def test_gauge_provenance_account_free_and_full_reconciliation(self):
        r=self.first; gauge=r['earth_gauge']
        self.assertEqual(len(gauge),80*201)
        india={x['year']:x for x in gauge if x['country']=='IND'}
        expected={2038:('.030','0','0'),2039:('.095','0','0'),
                  2040:('.015','0','0'),2041:('0','0','.040'),
                  2042:('0','0','.040'),2043:('0','0','0'),
                  2044:('0','.020','0'),2045:('0','0','0')}
        for year,(new,recycled,returned) in expected.items():
            row=india[year]
            self.assertEqual((D(row['new_capital_draw']),
                              D(row['recycled_returned_cash_spent']),
                              D(row['returns_received'])),
                             (D(new),D(recycled),D(returned)))
        shadow=r['kernel'].state.earth_impact.capital_diverted_to_offworld
        for row in gauge:
            n,re,draw=(D(row[k]) for k in
                       ('new_capital_draw','recycled_returned_cash_spent','offworld_draw'))
            self.assertEqual(n+re,draw)
            self.assertEqual(draw,D(shadow.get(('EARTH:'+row['country'],row['year']),D(0))))
        definition=r['earth_gauge_definition']
        self.assertIn('not account names',definition['draw_definition'])
        self.assertIn('UNCHANGED kernel',definition['draw_definition'])
        self.assertTrue(all(D(x['recycled_returned_cash_spent'])==0
                            for x in gauge if (x['country'],x['year'])!=('IND',2044)))

    def test_replay_and_actual_transaction_count(self):
        first, replay = self.first, self.replay
        self.assertEqual(first['kernel'].fingerprint(),replay['kernel'].fingerprint())
        for key in ('physical','return_receipts','return_spends',
                    'operator_grants','agency_owner_types','appropriations','return_policy'):
            self.assertEqual(first['campaign'][key],replay['campaign'][key])
        self.assertEqual(first['earth_gauge'],replay['earth_gauge'])
        self.assertEqual(len(first['kernel'].state.transactions),8798)
        self.assertEqual(len(first['campaign']['receipts']),249)
        self.assertEqual(sum(r['outcome']=='BLOCKED' for r in
                             first['campaign']['attempts']),0)

    def test_underfunded_buyer_rejected_without_partial_sale(self):
        k=self.first['kernel']; buyer=k.state.accounts['earth_market']
        inventory=k.colonies['OFF:ROUTE1:CERES']
        old_cash,old_inventory=buyer.balance,inventory.resource_inventory
        initial=(len(k.state.transactions),len(k.market_clearing_records),
                 len(k.market_envelopes))
        try:
            buyer.balance=D(0)
            inventory.resource_inventory=D(A['demand_per_year'])
            with self.assertRaisesRegex(ValueError,'BLOCKED_AFFORDABILITY'):
                CeresDownstream()._sell(k,2045)
            self.assertEqual((len(k.state.transactions),len(k.market_clearing_records),
                              len(k.market_envelopes)),initial)
        finally:
            buyer.balance,inventory.resource_inventory=old_cash,old_inventory


if __name__ == '__main__':
    unittest.main()
