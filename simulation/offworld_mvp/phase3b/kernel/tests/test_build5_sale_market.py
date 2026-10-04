import unittest
from dataclasses import replace
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_sale_market_fixture import (
    RESEARCH_ADVISORY_REF,
    sale_market_kernel,
    sale_request,
    sale_snapshot,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.market import CommodityMarketEnvelope
from offworld_kernel.model import AccountKind
from offworld_kernel.mvp_state import (
    ColonyState,
    RuntimeObjectClass,
    SaleDecision,
    SaleDecisionOutcome,
    SaleReasonCode,
)
from offworld_kernel.policy_runner import (
    run_hostile_access_probe,
    run_sponsor_sale_policy,
    sponsor_sale_contract_hash,
    sponsor_sale_policy_version,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_sponsor_operator as sponsor_tests


class Build5SaleMarketTests(unittest.TestCase):
    def reach_extracted(self,universe_id='RICH_PUBLIC_3',stock='20',
                        demand='4',price='20',
                        sponsor_capabilities=(
                            'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL')):
        k,h=sale_market_kernel(
            universe_id,stock,unit_price=price,demand_quantity=demand,
            sponsor_capabilities=sponsor_capabilities)

        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-SALE-009A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-009A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-009A-DEVELOP',5)

        l=lifecycle_tests.Build5ProjectLifecycleTests()
        l.lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')

        o=operating_tests.Build5OperatingExtractionTests()
        o.operating_request_epoch(k,h)
        o.operating_finance_epoch(k,h)
        o.operate_epoch(k,h)

        return k,h

    def sale_epoch(self,k,h,price_unknown=False,demand_unknown=False):
        envelope=h['market_envelope']
        snapshot=sale_snapshot(
            k,envelope,'SALE-10','10',
            price_unknown=price_unknown,demand_unknown=demand_unknown)
        request=sale_request(h['obs'].id,envelope.id)
        h['sale_snapshot']=snapshot
        h['sale_request']=request

        k.begin_decision_epoch('EPOCH-9-SALE')
        k.scheduler.register_coupling(CouplingSpec(
            'SALE_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'EARTH_MARKET_v0','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','colonies','market_resource_inventory',
             'market_clearing_records','boundary_net','events'),
            ('sale_decision','market_envelope','realized_inventory'),
            ('accounts','transactions','colonies','market_resource_inventory',
             'market_clearing_records','boundary_net','events'),
            'EVENT',Phase.MARKET_CLEARING))

        ref=k.scheduler.open_decision_window(
            snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'sale-e9-decision',D('10'),Phase.DECISION_WINDOW,0,'SPN',
            'SALE_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'sale-e9-clear',D('10'),Phase.MARKET_CLEARING,0,'EARTH-MARKET',
            'EARTH_MARKET_v0',parent_ids=('sale-e9-decision',)))

        policy_id=(
            'POLICY:'+sponsor_sale_policy_version()
            +':CONTRACT:'+sponsor_sale_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'MARKET_ENVELOPE:'+envelope.fingerprint(),
                'RESEARCH_ADVISORY:'+RESEARCH_ADVISORY_REF,
            ),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_sale_policy(
                ctx.snapshot,request,ctx.decision_key)
            h['sale_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.offered_quantity)))

        def clear(kernel,event):
            d=h['sale_policy'].decision
            if d.outcome!=SaleDecisionOutcome.OFFER:
                return 'NO_MARKET_CLEAR:'+d.outcome.value
            rec=kernel.clear_market_sale(10,'SPN',request,d)
            h['market_clearing_record']=rec
            return '|'.join((
                'CLEARED',str(rec.cleared_quantity),
                str(rec.transaction_value),rec.transaction_id))

        rt.register_policy_handler(
            'sale-e9-decision','SPN',snapshot,'SALE-KEY-009A',policy)
        rt.register_handler('EARTH_MARKET_v0',clear)
        before=AccountingPeriodSnapshot.capture(k,10)
        rt.seal()
        result=rt.run()
        h['sale_result']=result
        h['sale_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',
                  demand='4',price='20',
                  sponsor_capabilities=(
                      'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL')):
        k,h=self.reach_extracted(
            universe_id,stock,demand,price,sponsor_capabilities)
        self.sale_epoch(k,h)
        return k,h

    def synthetic_offer_decision(self,request,quantity):
        return SaleDecision(
            'SDEC-HOSTILE-009A',request.id,'SPN',
            SaleDecisionOutcome.OFFER,D(quantity),
            'hostile market boundary fixture',
            SaleReasonCode.MARKET_OFFER_AUTHORIZED,
            (), 'decision-snapshot:HOSTILE:fixture','HOSTILE_SALE_POLICY_V1'
        ).validate_protocol(request)

    def prechain_clearing_fixture(self,inventory='3',demand='2'):
        k,h=sale_market_kernel('RICH_PUBLIC_3','20',demand_quantity=demand)
        k.state.projects['P'].status='OPERATING'
        k.colonies.setdefault('OFF:T1',ColonyState('OFF:T1')).resource_inventory=D(inventory)
        k.agents['SPN'].information.add(h['obs'].id)
        return k,h

    def test_rich_demand_limited_sale_creates_revenue(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        d=h['sale_policy'].decision
        r=h['market_clearing_record']
        self.assertEqual(d.outcome,SaleDecisionOutcome.OFFER)
        self.assertEqual(d.offered_quantity,D('5'))
        self.assertEqual(r.cleared_quantity,D('4'))
        self.assertEqual(r.transaction_value,D('80'))
        self.assertEqual(r.local_inventory_before,D('5'))
        self.assertEqual(r.local_inventory_after,D('1'))
        self.assertEqual(r.market_inventory_before,D('0'))
        self.assertEqual(r.market_inventory_after,D('4'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('1'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('4'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('80'))
        self.assertEqual(k.state.accounts['earth_market'].balance,D('-80'))
        self.assertEqual(k.resources['RES'].remaining,D('15'))
        self.assertEqual(len(k.decision_epoch_records),9)

    def test_sparse_sale_clears_only_realized_inventory(self):
        k,h=self.full_case('SPARSE_PUBLIC_1','3')
        r=h['market_clearing_record']
        self.assertEqual(h['sale_policy'].decision.offered_quantity,D('3'))
        self.assertEqual(r.cleared_quantity,D('3'))
        self.assertEqual(r.transaction_value,D('60'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('0'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('3'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('60'))
        self.assertEqual(k.state.accounts['earth_market'].balance,D('-60'))
        self.assertEqual(k.resources['RES'].remaining,D('0'))

    def test_null_zero_output_defers_and_creates_no_revenue(self):
        k,h=self.full_case('NULL_FP_1','0')
        d=h['sale_policy'].decision
        self.assertEqual(d.outcome,SaleDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,SaleReasonCode.NO_SELLABLE_INVENTORY)
        self.assertNotIn('market_clearing_record',h)
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(k.state.accounts['earth_market'].balance,D('0'))
        self.assertEqual(k.market_remaining_demand('MARKET-009A-1'),D('4'))
        self.assertEqual(k.market_clearing_records,[])

    def test_smaller_demand_caps_sale_without_destroying_inventory(self):
        k,h=self.full_case('RICH_PUBLIC_3','20',demand='2')
        r=h['market_clearing_record']
        self.assertEqual(h['sale_policy'].decision.offered_quantity,D('5'))
        self.assertEqual(r.cleared_quantity,D('2'))
        self.assertEqual(r.transaction_value,D('40'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('3'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('2'))
        self.assertEqual(k.market_remaining_demand('MARKET-009A-1'),D('0'))

    def test_unknown_price_blocks_before_worker(self):
        k,h=self.reach_extracted()
        snap=sale_snapshot(
            k,h['market_envelope'],'SALE-UNKNOWN-PRICE','10',
            price_unknown=True)
        req=sale_request(h['obs'].id)
        r=run_sponsor_sale_policy(snap,req,'UNKNOWN-PRICE')
        self.assertEqual(r.decision.outcome,SaleDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('market.UNIT_PRICE',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_unknown_demand_blocks_before_worker(self):
        k,h=self.reach_extracted()
        snap=sale_snapshot(
            k,h['market_envelope'],'SALE-UNKNOWN-DEMAND','10',
            demand_unknown=True)
        req=sale_request(h['obs'].id)
        r=run_sponsor_sale_policy(snap,req,'UNKNOWN-DEMAND')
        self.assertEqual(r.decision.outcome,SaleDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('market.REMAINING_DEMAND',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_missing_sell_capability_defers(self):
        caps=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT')
        k,h=self.reach_extracted(
            sponsor_capabilities=caps)
        snap=sale_snapshot(k,h['market_envelope'],'SALE-NO-CAP','10')
        req=sale_request(h['obs'].id)
        r=run_sponsor_sale_policy(snap,req,'NO-CAP')
        self.assertEqual(r.decision.outcome,SaleDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,
                         SaleReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_non_operating_status_defers(self):
        k,h=self.reach_extracted()
        snap=sale_snapshot(
            k,h['market_envelope'],'SALE-NONOPERATING','10',
            status_override='DEVELOPMENT')
        req=sale_request(h['obs'].id)
        r=run_sponsor_sale_policy(snap,req,'NONOPERATING')
        self.assertEqual(r.decision.outcome,SaleDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,SaleReasonCode.PROJECT_STATE_BLOCK)

    def test_zero_price_or_zero_demand_defers(self):
        k,h=self.reach_extracted()
        req=sale_request(h['obs'].id)
        price_snap=sale_snapshot(
            k,h['market_envelope'],'SALE-ZERO-PRICE','10',price_override='0')
        price_result=run_sponsor_sale_policy(price_snap,req,'ZERO-PRICE')
        self.assertEqual(price_result.decision.reason_code,
                         SaleReasonCode.NO_POSITIVE_PRICE)

        demand_snap=sale_snapshot(
            k,h['market_envelope'],'SALE-ZERO-DEMAND','10',demand_override='0')
        demand_result=run_sponsor_sale_policy(demand_snap,req,'ZERO-DEMAND')
        self.assertEqual(demand_result.decision.reason_code,
                         SaleReasonCode.NO_MARKET_DEMAND)

    def test_policy_evaluation_alone_mutates_nothing(self):
        k,h=self.reach_extracted()
        snap=sale_snapshot(k,h['market_envelope'],'SALE-NOMUTATE','10')
        req=sale_request(h['obs'].id)
        before=(
            k.colonies['OFF:T1'].resource_inventory,
            k.state.accounts['project_cash'].balance,
            k.state.accounts['earth_market'].balance,
            len(k.market_clearing_records),
        )
        r=run_sponsor_sale_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,SaleDecisionOutcome.OFFER)
        after=(
            k.colonies['OFF:T1'].resource_inventory,
            k.state.accounts['project_cash'].balance,
            k.state.accounts['earth_market'].balance,
            len(k.market_clearing_records),
        )
        self.assertEqual(before,after)

    def test_forged_offer_is_capped_by_inventory_and_demand(self):
        k,h=self.prechain_clearing_fixture(inventory='3',demand='2')
        req=sale_request(h['obs'].id)
        d=self.synthetic_offer_decision(req,'99')
        rec=k.clear_market_sale(10,'SPN',req,d)
        self.assertEqual(rec.offered_quantity,D('99'))
        self.assertEqual(rec.cleared_quantity,D('2'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('1'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('2'))

    def test_inventory_cap_binds_when_demand_is_larger(self):
        k,h=self.prechain_clearing_fixture(inventory='3',demand='10')
        req=sale_request(h['obs'].id)
        d=self.synthetic_offer_decision(req,'99')
        rec=k.clear_market_sale(10,'SPN',req,d)
        self.assertEqual(rec.cleared_quantity,D('3'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('0'))
        self.assertEqual(k.market_remaining_demand('MARKET-009A-1'),D('7'))

    def test_wrong_resource_market_linkage_is_rejected(self):
        k,h=self.prechain_clearing_fixture()
        req=sale_request(
            h['obs'].id,resource_id='OTHER',request_id='SALEREQ-WRONG-RESOURCE')
        d=self.synthetic_offer_decision(req,'1')
        with self.assertRaisesRegex(InvariantError,'resource/market envelope mismatch'):
            k.clear_market_sale(10,'SPN',req,d)

    def test_wrong_buyer_account_kind_rejected_at_registration(self):
        k,h=sale_market_kernel()
        env=CommodityMarketEnvelope(
            'BAD-MARKET',10,'RES','project_cash',D('20'),D('4'),
            'MODEL_CURRENCY','MODEL_RESOURCE_UNIT_BY_FAMILY',
            'TEST','TEST_ONLY').validate()
        with self.assertRaisesRegex(InvariantError,'buyer must be EARTH_BOUNDARY'):
            k.register_market_envelope(env)

    def test_duplicate_decision_cannot_double_clear(self):
        k,h=self.prechain_clearing_fixture(inventory='3',demand='4')
        req=sale_request(h['obs'].id)
        d=self.synthetic_offer_decision(req,'1')
        first=k.clear_market_sale(10,'SPN',req,d)
        self.assertEqual(first.cleared_quantity,D('1'))
        with self.assertRaisesRegex(InvariantError,'already cleared'):
            k.clear_market_sale(10,'SPN',req,d)
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('2'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('1'))

    def test_policy_snapshot_and_market_contract_do_not_expose_hidden_resource(self):
        k,h=self.reach_extracted()
        snap=sale_snapshot(k,h['market_envelope'],'SALE-HOSTILE','10')
        probe,_=run_hostile_access_probe(snap)
        self.assertEqual({k:v for k,v in probe.items() if v=='LEAK'}, {})
        self.assertFalse(hasattr(h['market_envelope'],'hidden_resource'))
        self.assertFalse(hasattr(h['market_envelope'],'scenario_resource'))
        self.assertFalse(hasattr(h['market_envelope'],'resource_remaining'))

    def test_revenue_is_project_cash_not_direct_sponsor_cash(self):
        k,h=self.full_case()
        r=h['market_clearing_record']
        tx=next(t for t in k.state.transactions if t.id==r.transaction_id)
        self.assertEqual(tx.purpose.value,'REVENUE')
        self.assertEqual(tx.source_account,'earth_market')
        self.assertEqual(tx.destination_account,'project_cash')
        sponsor_account=k.agents['SPN'].account_id
        self.assertEqual(k.state.accounts[sponsor_account].balance,D('0'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('80'))

    def test_sale_preserves_A1_A9_and_physical_transfer_identity(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            k,h=self.full_case(uid,stock)
            self.assertEqual(
                tuple(sorted(h['sale_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))
            if 'market_clearing_record' in h:
                r=h['market_clearing_record']
                self.assertEqual(
                    r.local_inventory_before-r.local_inventory_after,
                    r.cleared_quantity)
                self.assertEqual(
                    r.market_inventory_after-r.market_inventory_before,
                    r.cleared_quantity)
                self.assertEqual(
                    r.transaction_value,
                    r.cleared_quantity*r.unit_price)

    def test_local_inventory_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.colonies['OFF:T1'].resource_inventory+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-LOCAL-INVENTORY')

    def test_market_inventory_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.market_resource_inventory[('EARTH:X','RES')]+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-MARKET-INVENTORY')

    def test_sale_chain_replays_exactly(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            ak,ah=self.full_case(uid,stock)
            bk,bh=self.full_case(uid,stock)
            self.assertEqual(
                tuple(ak.decision_epoch_records),
                tuple(bk.decision_epoch_records))
            self.assertEqual(
                ah['sale_policy'].decision,
                bh['sale_policy'].decision)
            self.assertEqual(
                ak.market_clearing_records,
                bk.market_clearing_records)
            self.assertEqual(
                ak.methodology_fingerprint(),
                bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
