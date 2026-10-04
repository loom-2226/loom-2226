import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_surplus_distribution_fixture import (
    RESEARCH_ADVISORY_REF,
    surplus_distribution_kernel,
    surplus_request,
    surplus_snapshot,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    RuntimeObjectClass,
    SurplusDistributionDecision,
    SurplusDistributionDecisionOutcome,
    SurplusDistributionReasonCode,
)
from offworld_kernel.policy_runner import (
    run_sponsor_surplus_policy,
    sponsor_surplus_contract_hash,
    sponsor_surplus_policy_version,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_sale_market as market_tests
from tests import test_build5_sponsor_operator as sponsor_tests


class Build5SurplusDistributionTests(unittest.TestCase):
    def reach_sale(self,universe_id='RICH_PUBLIC_3',stock='20',
                   demand='4',price='20',owners=None,
                   claim_project_id='P',
                   sponsor_capabilities=(
                       'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT',
                       'SELL','DISTRIBUTE_SURPLUS')):
        k,h=surplus_distribution_kernel(
            universe_id,stock,demand_quantity=demand,unit_price=price,
            owners=owners,claim_project_id=claim_project_id,
            sponsor_capabilities=sponsor_capabilities)

        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-SURPLUS-010A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-010A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-010A-DEVELOP',5)

        l=lifecycle_tests.Build5ProjectLifecycleTests()
        l.lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')

        o=operating_tests.Build5OperatingExtractionTests()
        o.operating_request_epoch(k,h)
        o.operating_finance_epoch(k,h)
        o.operate_epoch(k,h)

        m=market_tests.Build5SaleMarketTests()
        m.sale_epoch(k,h)
        return k,h

    def distribution_epoch(self,k,h,**snapshot_kw):
        snapshot=surplus_snapshot(k,h,'SURPLUS-10','10',**snapshot_kw)
        request=surplus_request(h['financing_return_claim'].id)
        h['surplus_snapshot']=snapshot
        h['surplus_request']=request

        k.begin_decision_epoch('EPOCH-10-SURPLUS-DISTRIBUTION')
        k.scheduler.register_coupling(CouplingSpec(
            'SURPLUS_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'SURPLUS_DISTRIBUTION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','surplus_distribution_records','events'),
            ('surplus_distribution_decision','financing_return_claim',
             'project_ownership','project_cash'),
            ('accounts','transactions','surplus_distribution_records','events'),
            'EVENT',Phase.ACCOUNTING_CLOSE))

        ref=k.scheduler.open_decision_window(
            snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'surplus-e10-decision',D('10'),Phase.DECISION_WINDOW,0,'SPN',
            'SURPLUS_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'surplus-e10-execute',D('10'),Phase.ACCOUNTING_CLOSE,0,'SURPLUS',
            'SURPLUS_DISTRIBUTION_SYSTEM',
            parent_ids=('surplus-e10-decision',)))

        claim=h['financing_return_claim']
        policy_id=(
            'POLICY:'+sponsor_surplus_policy_version()
            +':CONTRACT:'+sponsor_surplus_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'FINANCING_RETURN_CLAIM:'+claim.fingerprint(),
                'RESEARCH_ADVISORY:'+RESEARCH_ADVISORY_REF,
            ),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_surplus_policy(
                ctx.snapshot,request,ctx.decision_key)
            h['surplus_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.reserve),str(d.financier_return),
                str(d.local_reinvestment),str(d.owner_distribution)))

        def execute(kernel,event):
            d=h['surplus_policy'].decision
            if d.outcome!=SurplusDistributionDecisionOutcome.DISTRIBUTE:
                return 'NO_SURPLUS_DISTRIBUTION:'+d.outcome.value
            rec=kernel.execute_surplus_distribution(
                10,'SPN',request,d,'local_reinvest_funds')
            h['surplus_distribution_record']=rec
            return '|'.join((
                'SURPLUS_ALLOCATED',str(rec.reserve),
                str(rec.financier_return),str(rec.local_reinvestment),
                str(rec.owner_distribution)))

        rt.register_policy_handler(
            'surplus-e10-decision','SPN',snapshot,
            'SURPLUS-KEY-010A',policy)
        rt.register_handler('SURPLUS_DISTRIBUTION_SYSTEM',execute)
        before=AccountingPeriodSnapshot.capture(k,10)
        rt.seal()
        result=rt.run()
        h['surplus_result']=result
        h['surplus_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',owners=None,
                  sponsor_capabilities=(
                      'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT',
                      'SELL','DISTRIBUTE_SURPLUS')):
        k,h=self.reach_sale(
            universe_id,stock,owners=owners,
            sponsor_capabilities=sponsor_capabilities)
        self.distribution_epoch(k,h)
        return k,h

    def direct_fixture(self,owners=None,claim_project_id='P'):
        k,h=surplus_distribution_kernel(
            owners=owners,claim_project_id=claim_project_id)
        k.state.projects['P'].status='OPERATING'
        k.add_commitment('C-SPONSOR-005A','FIN','P',D('60'))
        k.disburse(1,'C-SPONSOR-005A','fin_funds',D('60'))
        k.add_commitment('C-OPERATING-008A','FIN','P',D('20'))
        k.disburse(1,'C-OPERATING-008A','fin_funds',D('20'))
        return k,h

    def synthetic_decision(self,request,reserve='20',financier='30',
                           reinvest='10',owner='20'):
        return SurplusDistributionDecision(
            'DDEC-HOSTILE-010A',request.id,'SPN',
            SurplusDistributionDecisionOutcome.DISTRIBUTE,
            D(reserve),D(financier),D(reinvest),D(owner),
            'hostile distribution boundary fixture',
            SurplusDistributionReasonCode.DISTRIBUTION_AUTHORIZED,
            (), 'decision-snapshot:HOSTILE:fixture','HOSTILE_SURPLUS_POLICY_V1'
        ).validate_protocol(request)

    def test_rich_allocation_reserve_financier_reinvest_owner(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        d=h['surplus_policy'].decision
        r=h['surplus_distribution_record']
        self.assertEqual(d.outcome,SurplusDistributionDecisionOutcome.DISTRIBUTE)
        self.assertEqual(
            (d.reserve,d.financier_return,d.local_reinvestment,d.owner_distribution),
            (D('20'),D('30'),D('10'),D('20')))
        self.assertEqual(r.opening_project_cash,D('80'))
        self.assertEqual(r.closing_project_cash,D('20'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('20'))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('50'))
        self.assertEqual(k.state.accounts['local_reinvest_funds'].balance,D('10'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('20'))
        self.assertEqual(k.financing_return_remaining('FRC-010A-1'),D('0'))
        self.assertEqual(k.state.projects['P'].owners,{'SPN':D('1')})
        self.assertEqual(len(k.decision_epoch_records),10)

    def test_sparse_allocates_no_owner_residual(self):
        k,h=self.full_case('SPARSE_PUBLIC_1','3')
        d=h['surplus_policy'].decision
        r=h['surplus_distribution_record']
        self.assertEqual(
            (d.reserve,d.financier_return,d.local_reinvestment,d.owner_distribution),
            (D('20'),D('30'),D('10'),D('0')))
        self.assertEqual(r.opening_project_cash,D('60'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('20'))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('50'))
        self.assertEqual(k.state.accounts['local_reinvest_funds'].balance,D('10'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('0'))
        self.assertEqual(k.financing_return_remaining('FRC-010A-1'),D('0'))

    def test_null_has_no_cash_and_defers(self):
        k,h=self.full_case('NULL_FP_1','0')
        d=h['surplus_policy'].decision
        self.assertEqual(d.outcome,SurplusDistributionDecisionOutcome.DEFER)
        self.assertEqual(
            d.reason_code,SurplusDistributionReasonCode.NO_DISTRIBUTABLE_CASH)
        self.assertNotIn('surplus_distribution_record',h)
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('20'))
        self.assertEqual(k.state.accounts['local_reinvest_funds'].balance,D('0'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('0'))
        self.assertEqual(k.financing_return_remaining('FRC-010A-1'),D('30'))

    def test_unknown_reserve_blocks_before_worker(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(k,h,'UNKNOWN-RESERVE','10',reserve_unknown=True)
        req=surplus_request()
        r=run_sponsor_surplus_policy(snap,req,'UNKNOWN-RESERVE')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('project.RESERVE_REQUIREMENT',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_unknown_claim_blocks_before_worker(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(k,h,'UNKNOWN-CLAIM','10',claim_unknown=True)
        req=surplus_request()
        r=run_sponsor_surplus_policy(snap,req,'UNKNOWN-CLAIM')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('financing.RETURN_CLAIM_REMAINING',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_unknown_reinvestment_blocks_before_worker(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(k,h,'UNKNOWN-REINVEST','10',reinvest_unknown=True)
        req=surplus_request()
        r=run_sponsor_surplus_policy(snap,req,'UNKNOWN-REINVEST')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('project.REINVESTMENT_REQUIREMENT',))

    def test_missing_distribution_capability_defers(self):
        caps=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL')
        k,h=self.reach_sale(sponsor_capabilities=caps)
        snap=surplus_snapshot(k,h,'NO-DIST-CAP','10')
        req=surplus_request()
        r=run_sponsor_surplus_policy(snap,req,'NO-DIST-CAP')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.DEFER)
        self.assertEqual(
            r.decision.reason_code,
            SurplusDistributionReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_non_operating_project_defers(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(
            k,h,'NONOPERATING','10',status_override='DEVELOPMENT')
        req=surplus_request()
        r=run_sponsor_surplus_policy(snap,req,'NONOPERATING')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.DEFER)
        self.assertEqual(
            r.decision.reason_code,SurplusDistributionReasonCode.PROJECT_STATE_BLOCK)

    def test_negative_allocation_input_is_rejected_by_worker(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(
            k,h,'NEGATIVE-CLAIM','10',claim_override='-1')
        req=surplus_request()
        with self.assertRaisesRegex(RuntimeError,'policy worker failed'):
            run_sponsor_surplus_policy(snap,req,'NEGATIVE')

    def test_policy_evaluation_alone_mutates_no_cash(self):
        k,h=self.reach_sale()
        snap=surplus_snapshot(k,h,'NO-MUTATE','10')
        req=surplus_request()
        before=tuple(sorted((aid,a.balance) for aid,a in k.state.accounts.items()))
        r=run_sponsor_surplus_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,SurplusDistributionDecisionOutcome.DISTRIBUTE)
        after=tuple(sorted((aid,a.balance) for aid,a in k.state.accounts.items()))
        self.assertEqual(before,after)
        self.assertEqual(k.surplus_distribution_records,[])

    def test_forged_distribution_above_current_cash_rejected(self):
        k,h=self.direct_fixture()
        req=surplus_request()
        d=self.synthetic_decision(req,reserve='20',financier='30',reinvest='10',owner='21')
        with self.assertRaisesRegex(InvariantError,'no longer matches current project cash'):
            k.execute_surplus_distribution(10,'SPN',req,d,'local_reinvest_funds')

    def test_wrong_claim_project_linkage_rejected(self):
        k,h=self.direct_fixture(claim_project_id='EXP')
        req=surplus_request()
        d=self.synthetic_decision(req)
        with self.assertRaisesRegex(InvariantError,'claim/project mismatch'):
            k.execute_surplus_distribution(10,'SPN',req,d,'local_reinvest_funds')

    def test_wrong_financier_destination_rejected_at_claim_registration(self):
        with self.assertRaisesRegex(InvariantError,'destination ownership mismatch'):
            surplus_distribution_kernel(
                claim_destination_account='sponsor_funds')

    def test_financier_return_cannot_exceed_remaining_claim(self):
        k,h=self.direct_fixture()
        req=surplus_request()
        d=self.synthetic_decision(
            req,reserve='20',financier='31',reinvest='10',owner='19')
        with self.assertRaisesRegex(InvariantError,'exceeds remaining claim'):
            k.execute_surplus_distribution(10,'SPN',req,d,'local_reinvest_funds')

    def test_owner_distribution_is_pro_rata_and_separate_from_financing_return(self):
        k,h=self.full_case(
            'RICH_PUBLIC_3','20',
            owners={'SPN':D('0.5'),'FIN':D('0.5')})
        r=h['surplus_distribution_record']
        alloc={a.owner_id:a.amount for a in r.owner_allocations}
        self.assertEqual(alloc,{'FIN':D('10.0'),'SPN':D('10.0')})
        # FIN receives 30 as financier + 10 as owner; the semantics remain separate.
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('60.0'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('10.0'))
        fin_tx=[
            t for t in k.state.transactions
            if t.purpose.value=='FINANCIER_RETURN'
        ]
        owner_tx=[
            t for t in k.state.transactions
            if t.purpose.value=='OWNER_DISTRIBUTION'
        ]
        self.assertEqual(sum((t.amount for t in fin_tx),D('0')),D('30'))
        self.assertEqual(sum((t.amount for t in owner_tx),D('0')),D('20'))

    def test_invalid_fixture_ownership_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'owners must sum to one'):
            surplus_distribution_kernel(
                owners={'SPN':D('0.8'),'FIN':D('0.3')})

    def test_duplicate_distribution_decision_rejected(self):
        k,h=self.direct_fixture()
        req=surplus_request()
        d=self.synthetic_decision(req)
        first=k.execute_surplus_distribution(
            10,'SPN',req,d,'local_reinvest_funds')
        self.assertEqual(first.owner_distribution,D('20'))
        with self.assertRaisesRegex(InvariantError,'already executed'):
            k.execute_surplus_distribution(
                10,'SPN',req,d,'local_reinvest_funds')

    def test_distribution_does_not_change_resource_or_inventory(self):
        k,h=self.reach_sale()
        before=(
            k.resources['RES'].remaining,
            k.colonies['OFF:T1'].resource_inventory,
            k.market_resource_inventory.get(('EARTH:X','RES'),D('0')),
        )
        self.distribution_epoch(k,h)
        after=(
            k.resources['RES'].remaining,
            k.colonies['OFF:T1'].resource_inventory,
            k.market_resource_inventory.get(('EARTH:X','RES'),D('0')),
        )
        self.assertEqual(before,after)

    def test_rich_sparse_null_distribution_epochs_preserve_A1_A9(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            _,h=self.full_case(uid,stock)
            self.assertEqual(
                tuple(sorted(h['surplus_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_distribution_transactions_have_distinct_semantics(self):
        k,h=self.full_case()
        r=h['surplus_distribution_record']
        tx=[t for t in k.state.transactions if t.id in r.transaction_ids]
        purposes=sorted(t.purpose.value for t in tx)
        self.assertEqual(
            purposes,
            ['FINANCIER_RETURN','LOCAL_REINVESTMENT','OWNER_DISTRIBUTION'])
        self.assertEqual(
            sum((t.amount for t in tx),D('0')),D('60'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('20'))

    def test_financing_return_requires_actual_disbursement_lineage(self):
        k,h=surplus_distribution_kernel()
        k.state.projects['P'].status='OPERATING'
        k.state.accounts['project_cash'].balance=D('80')
        k.add_commitment('C-SPONSOR-005A','FIN','P',D('60'))
        k.add_commitment('C-OPERATING-008A','FIN','P',D('20'))
        req=surplus_request()
        d=self.synthetic_decision(req)
        with self.assertRaisesRegex(InvariantError,'no disbursed capital'):
            k.execute_surplus_distribution(
                10,'SPN',req,d,'local_reinvest_funds')

    def test_post_distribution_account_tamper_is_detected(self):
        k,h=self.full_case()
        k.state.accounts['project_cash'].balance+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-DISTRIBUTION-CASH')

    def test_distribution_chain_replays_exactly(self):
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
                ah['surplus_policy'].decision,
                bh['surplus_policy'].decision)
            self.assertEqual(
                ak.surplus_distribution_records,
                bk.surplus_distribution_records)
            self.assertEqual(
                ak.methodology_fingerprint(),
                bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
