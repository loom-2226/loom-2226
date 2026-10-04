import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_settlement_fixture import (
    RESEARCH_POPULATION_REF,
    RESEARCH_SETTLEMENT_REF,
    settlement_kernel,
    settlement_support_request,
    settlement_support_snapshot,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    ColonyState,
    RuntimeObjectClass,
    SettlementSupportDecision,
    SettlementSupportDecisionOutcome,
    SettlementSupportReasonCode,
)
from offworld_kernel.policy_runner import (
    public_settlement_contract_hash,
    public_settlement_policy_version,
    run_public_settlement_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.settlement import (
    SettlementInfrastructurePlan,
    derive_settlement_stage,
)
from offworld_kernel.settlement_protocol import build_settlement_support_request
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_sale_market as market_tests
from tests import test_build5_sponsor_operator as sponsor_tests
from tests import test_build5_surplus_distribution as surplus_tests


class Build5SettlementTests(unittest.TestCase):
    def reach_distribution(self,universe_id='RICH_PUBLIC_3',stock='20',
                           public_balance=None,earth_population=1000,
                           public_settlement_capabilities=True,
                           infrastructure_cost='10',habitat_capacity=10,
                           requested_residents=10,public_support_cost='10'):
        k,h=settlement_kernel(
            universe_id,stock,
            public_balance=public_balance,
            earth_population=earth_population,
            public_settlement_capabilities=public_settlement_capabilities,
            infrastructure_cost=infrastructure_cost,
            habitat_capacity=habitat_capacity,
            requested_residents=requested_residents,
            public_support_cost=public_support_cost)

        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-SETTLEMENT-011A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-011A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-011A-DEVELOP',5)

        l=lifecycle_tests.Build5ProjectLifecycleTests()
        l.lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')

        o=operating_tests.Build5OperatingExtractionTests()
        o.operating_request_epoch(k,h)
        o.operating_finance_epoch(k,h)
        o.operate_epoch(k,h)

        m=market_tests.Build5SaleMarketTests()
        m.sale_epoch(k,h)

        d=surplus_tests.Build5SurplusDistributionTests()
        d.distribution_epoch(k,h)
        return k,h

    def infrastructure_epoch(self,k,h):
        plan=h['settlement_infrastructure_plan']
        k.begin_decision_epoch('EPOCH-11-SETTLEMENT-INFRASTRUCTURE')
        k.scheduler.register_coupling(CouplingSpec(
            'SETTLEMENT_INFRASTRUCTURE_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','colonies','settlement_infrastructure_records','events'),
            ('settlement_infrastructure_plan','local_reinvestment_balance'),
            ('accounts','transactions','colonies','settlement_infrastructure_records','events'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.register_coupling(CouplingSpec(
            'SETTLEMENT_STAGE_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('colonies','assets','settlement_stage_records','events'),
            ('productive_assets','colony_state'),
            ('colonies','settlement_stage_records','events'),
            'EVENT',Phase.ACCOUNTING_CLOSE))
        k.scheduler.schedule(ScheduledEvent(
            'settlement-e11-infrastructure',D('11'),Phase.OPERATIONS,0,'SETTLEMENT-INFRA',
            'SETTLEMENT_INFRASTRUCTURE_SYSTEM'))
        k.scheduler.schedule(ScheduledEvent(
            'settlement-e11-stage',D('11'),Phase.ACCOUNTING_CLOSE,0,'SETTLEMENT-STAGE',
            'SETTLEMENT_STAGE_SYSTEM',
            parent_ids=('settlement-e11-infrastructure',)))

        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'SETTLEMENT_INFRA_PLAN:'+plan.fingerprint(),
                'RESEARCH_ADVISORY_POP:'+RESEARCH_POPULATION_REF,
                'RESEARCH_ADVISORY_SETTLEMENT:'+RESEARCH_SETTLEMENT_REF,
            ),
            policy_manifest_ids=('NO_POLICY_THIS_EPOCH',))
        rt=ScheduledSimulationRuntime(k,prov)

        def infrastructure(kernel,event):
            parent=(h['surplus_policy'].decision.id,)
            rec=kernel.execute_settlement_infrastructure(
                11,plan.id,'SPN',parent_ids=parent)
            h['settlement_infrastructure_record']=rec
            return '|'.join((
                rec.outcome,str(rec.cost),str(rec.habitat_capacity_added),
                rec.transaction_id))

        def stage(kernel,event):
            parent=(h['settlement_infrastructure_record'].event_id,)
            rec=kernel.update_settlement_stage(
                11,'OFF:T1',parent_ids=parent)
            h['settlement_stage_after_infrastructure']=rec
            return '|'.join((
                rec.prior_stage,rec.new_stage,
                str(rec.productive_capital),str(rec.production_capacity),
                str(rec.infrastructure),str(rec.habitat_capacity)))

        rt.register_handler('SETTLEMENT_INFRASTRUCTURE_SYSTEM',infrastructure)
        rt.register_handler('SETTLEMENT_STAGE_SYSTEM',stage)
        before=AccountingPeriodSnapshot.capture(k,11)
        rt.seal()
        result=rt.run()
        h['settlement_infrastructure_result']=result
        h['settlement_infrastructure_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def support_epoch(self,k,h,headroom_unknown=False):
        snapshot=settlement_support_snapshot(
            k,h,'SETTLEMENT-12','12',headroom_unknown=headroom_unknown)
        request=settlement_support_request(h)
        h['settlement_support_snapshot']=snapshot
        h['settlement_support_request']=request

        k.begin_decision_epoch('EPOCH-12-SETTLEMENT-SUPPORT')
        k.scheduler.register_coupling(CouplingSpec(
            'SETTLEMENT_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'SETTLEMENT_SUPPORT_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','colonies','population',
             'settlement_support_records','settlement_stage_records','events'),
            ('settlement_support_decision','population','habitat_headroom'),
            ('accounts','transactions','colonies','population',
             'settlement_support_records','settlement_stage_records','events'),
            'EVENT',Phase.OPERATIONS))

        ref=k.scheduler.open_decision_window(
            snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'settlement-e12-decision',D('12'),Phase.DECISION_WINDOW,0,'PUB',
            'SETTLEMENT_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'settlement-e12-support',D('12'),Phase.OPERATIONS,0,'SETTLEMENT-SUPPORT',
            'SETTLEMENT_SUPPORT_SYSTEM',
            parent_ids=('settlement-e12-decision',)))

        policy_id=(
            'POLICY:'+public_settlement_policy_version()
            +':CONTRACT:'+public_settlement_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'SETTLEMENT_INFRA_PLAN:'+h['settlement_infrastructure_plan'].fingerprint(),
                'RESEARCH_ADVISORY_POP:'+RESEARCH_POPULATION_REF,
                'RESEARCH_ADVISORY_SETTLEMENT:'+RESEARCH_SETTLEMENT_REF,
            ),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_settlement_policy(
                ctx.snapshot,request,ctx.decision_key)
            h['settlement_support_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.authorized_residents),str(d.support_amount)))

        def support(kernel,event):
            d=h['settlement_support_policy'].decision
            if d.outcome!=SettlementSupportDecisionOutcome.AUTHORIZE:
                return 'NO_SETTLEMENT_SUPPORT:'+d.outcome.value
            rec=kernel.execute_public_settlement_support(
                12,'PUB',request,d)
            h['settlement_support_record']=rec
            return '|'.join((
                'SETTLEMENT_SUPPORTED',str(rec.authorized_residents),
                str(rec.support_amount),rec.stage_event_id))

        rt.register_policy_handler(
            'settlement-e12-decision','PUB',snapshot,
            'SETTLEMENT-KEY-011A',policy)
        rt.register_handler('SETTLEMENT_SUPPORT_SYSTEM',support)
        before=AccountingPeriodSnapshot.capture(k,12)
        rt.seal()
        result=rt.run()
        h['settlement_support_result']=result
        h['settlement_support_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',**kw):
        k,h=self.reach_distribution(universe_id,stock,**kw)
        self.infrastructure_epoch(k,h)
        self.support_epoch(k,h)
        return k,h

    def test_rich_forms_dependent_settlement(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        infra=h['settlement_infrastructure_record']
        support=h['settlement_support_record']
        c=k.colonies['OFF:T1']
        self.assertEqual(infra.outcome,'INSTALLED')
        self.assertEqual(infra.cost,D('10'))
        self.assertEqual(c.infrastructure,D('10'))
        self.assertEqual(c.habitat_capacity,10)
        self.assertEqual(h['settlement_stage_after_infrastructure'].new_stage,'EXTRACTION_ENCLAVE')
        self.assertEqual(h['settlement_support_policy'].decision.outcome,
                         SettlementSupportDecisionOutcome.AUTHORIZE)
        self.assertEqual(support.authorized_residents,10)
        self.assertEqual(support.support_amount,D('10'))
        self.assertEqual(k.population.earth,990)
        self.assertEqual(k.population.offworld['OFF:T1'],10)
        self.assertEqual(k.population.total(),1000)
        self.assertEqual(c.population,10)
        self.assertEqual(c.external_subsidy,D('10'))
        self.assertEqual(c.cash,D('10'))
        self.assertEqual(c.stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual(k.state.accounts['local_reinvest_funds'].balance,D('0'))
        self.assertEqual(k.state.accounts['local_settlement_supplier'].balance,D('10'))
        self.assertEqual(k.state.accounts['public_funds'].balance,D('80'))
        self.assertEqual(k.state.accounts['settlement_support'].balance,D('10'))
        self.assertEqual(len(k.decision_epoch_records),12)

    def test_sparse_also_forms_bounded_dependent_settlement(self):
        k,h=self.full_case('SPARSE_PUBLIC_1','3')
        c=k.colonies['OFF:T1']
        self.assertEqual(h['settlement_infrastructure_record'].outcome,'INSTALLED')
        self.assertEqual(c.stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual(c.population,10)
        self.assertEqual(c.habitat_capacity,10)
        self.assertEqual(c.production_capacity,D('5'))
        self.assertEqual(k.population.total(),1000)

    def test_null_cannot_bootstrap_settlement_from_absent_reinvestment(self):
        k,h=self.full_case('NULL_FP_1','0')
        infra=h['settlement_infrastructure_record']
        d=h['settlement_support_policy'].decision
        c=k.colonies['OFF:T1']
        self.assertEqual(infra.outcome,'BLOCKED_INSUFFICIENT_FUNDS')
        self.assertEqual(infra.cost,D('0'))
        self.assertEqual(c.infrastructure,D('0'))
        self.assertEqual(c.habitat_capacity,0)
        self.assertEqual(c.stage,'EXTRACTION_ENCLAVE')
        self.assertEqual(d.outcome,SettlementSupportDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,SettlementSupportReasonCode.HABITAT_CAPACITY_LIMIT)
        self.assertNotIn('settlement_support_record',h)
        self.assertEqual(k.population.earth,1000)
        self.assertEqual(k.population.offworld['OFF:T1'],0)
        self.assertEqual(c.population,0)
        self.assertEqual(c.external_subsidy,D('0'))
        self.assertEqual(k.state.accounts['settlement_support'].balance,D('0'))

    def test_stage_rule_is_derived_not_capability_creating(self):
        self.assertEqual(
            derive_settlement_stage(D('0'),0,D('0'),0,D('0')),
            'PROSPECTING')
        self.assertEqual(
            derive_settlement_stage(D('5'),0,D('10'),10,D('10')),
            'EXTRACTION_ENCLAVE')
        self.assertEqual(
            derive_settlement_stage(D('5'),10,D('10'),9,D('10')),
            'EXTRACTION_ENCLAVE')
        self.assertEqual(
            derive_settlement_stage(D('5'),10,D('10'),10,D('0')),
            'EXTRACTION_ENCLAVE')
        self.assertEqual(
            derive_settlement_stage(D('5'),10,D('10'),10,D('10')),
            'DEPENDENT_SETTLEMENT')

    def test_infrastructure_requires_realized_local_reinvestment_cash(self):
        k,h=self.reach_distribution('NULL_FP_1','0')
        before_resource=k.resources['RES'].remaining
        before_population=k.population.total()
        self.infrastructure_epoch(k,h)
        r=h['settlement_infrastructure_record']
        self.assertEqual(r.outcome,'BLOCKED_INSUFFICIENT_FUNDS')
        self.assertEqual(k.resources['RES'].remaining,before_resource)
        self.assertEqual(k.population.total(),before_population)

    def test_duplicate_infrastructure_install_rejected(self):
        k,h=settlement_kernel()
        k.state.accounts['local_reinvest_funds'].balance=D('10')
        first=k.execute_settlement_infrastructure(
            11,h['settlement_infrastructure_plan'].id)
        self.assertEqual(first.outcome,'INSTALLED')
        with self.assertRaisesRegex(InvariantError,'already installed'):
            k.execute_settlement_infrastructure(
                11,h['settlement_infrastructure_plan'].id)

    def test_invalid_infrastructure_plan_values_rejected(self):
        with self.assertRaisesRegex(ValueError,'values invalid'):
            SettlementInfrastructurePlan(
                'BAD',11,'OFF:T1','local_reinvest_funds',
                'local_settlement_supplier',D('-1'),10,
                'TEST','TEST_ONLY').validate()
        with self.assertRaisesRegex(ValueError,'values invalid'):
            SettlementInfrastructurePlan(
                'BAD2',11,'OFF:T1','local_reinvest_funds',
                'local_settlement_supplier',D('1'),0,
                'TEST','TEST_ONLY').validate()

    def test_wrong_node_infrastructure_linkage_rejected(self):
        k,h=settlement_kernel()
        bad=SettlementInfrastructurePlan(
            'BAD-NODE',11,'OFF:T1','public_funds',
            'local_settlement_supplier',D('1'),1,
            'TEST','TEST_ONLY').validate()
        with self.assertRaisesRegex(InvariantError,'account/node mismatch'):
            k.register_settlement_infrastructure_plan(bad)

    def test_infrastructure_does_not_change_population_or_resource(self):
        k,h=self.reach_distribution()
        before=(k.population.total(),k.population.earth,
                k.resources['RES'].remaining,
                k.colonies['OFF:T1'].resource_inventory)
        self.infrastructure_epoch(k,h)
        after=(k.population.total(),k.population.earth,
               k.resources['RES'].remaining,
               k.colonies['OFF:T1'].resource_inventory)
        self.assertEqual(before,after)

    def test_unknown_habitat_headroom_blocks_before_worker(self):
        k,h=self.reach_distribution()
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(
            k,h,'UNKNOWN-HEADROOM','12',headroom_unknown=True)
        req=settlement_support_request(h)
        r=run_public_settlement_policy(snap,req,'UNKNOWN-HEADROOM')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,
                         ('settlement.HABITAT_HEADROOM',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_missing_public_settlement_capabilities_defers(self):
        k,h=self.reach_distribution(
            public_settlement_capabilities=False)
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(k,h,'NO-CAP','12')
        req=settlement_support_request(h)
        r=run_public_settlement_policy(snap,req,'NO-CAP')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,
                         SettlementSupportReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_insufficient_public_funding_defers(self):
        k,h=self.reach_distribution(public_balance='5')
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(k,h,'NO-FUNDS','12')
        req=settlement_support_request(h)
        r=run_public_settlement_policy(snap,req,'NO-FUNDS')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,
                         SettlementSupportReasonCode.INSUFFICIENT_PUBLIC_FUNDS)

    def test_request_above_habitat_headroom_defers(self):
        k,h=self.reach_distribution(requested_residents=11)
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(k,h,'TOO-MANY','12')
        req=settlement_support_request(h)
        r=run_public_settlement_policy(snap,req,'TOO-MANY')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,
                         SettlementSupportReasonCode.HABITAT_CAPACITY_LIMIT)

    def test_request_above_earth_population_defers(self):
        k,h=self.reach_distribution(earth_population=5)
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(k,h,'NO-PEOPLE','12')
        req=settlement_support_request(h)
        r=run_public_settlement_policy(snap,req,'NO-PEOPLE')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,
                         SettlementSupportReasonCode.ORIGIN_POPULATION_LIMIT)

    def test_policy_evaluation_alone_mutates_nothing(self):
        k,h=self.reach_distribution()
        self.infrastructure_epoch(k,h)
        snap=settlement_support_snapshot(k,h,'NO-MUTATE','12')
        req=settlement_support_request(h)
        before=(
            k.population.earth,k.population.offworld['OFF:T1'],
            k.colonies['OFF:T1'].population,
            k.colonies['OFF:T1'].external_subsidy,
            k.state.accounts['public_funds'].balance,
            k.state.accounts['settlement_support'].balance,
        )
        r=run_public_settlement_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,
                         SettlementSupportDecisionOutcome.AUTHORIZE)
        after=(
            k.population.earth,k.population.offworld['OFF:T1'],
            k.colonies['OFF:T1'].population,
            k.colonies['OFF:T1'].external_subsidy,
            k.state.accounts['public_funds'].balance,
            k.state.accounts['settlement_support'].balance,
        )
        self.assertEqual(before,after)

    def test_forged_authorization_cannot_exceed_real_habitat_headroom(self):
        # Pre-chain hostile fixture: exercise the system-side headroom check
        # without bypassing the decision-epoch mutation guard.
        k,h=settlement_kernel()
        k.colonies['OFF:T1']=ColonyState(
            'OFF:T1',population=0,productive_capital=D('60'),
            infrastructure=D('10'),habitat_capacity=10,
            production_capacity=D('5'),stage='EXTRACTION_ENCLAVE')
        req=build_settlement_support_request(
            'SETREQ-HOSTILE',12,'OFF:T1','settlement_support',11,D('10'))
        d=SettlementSupportDecision(
            'SETDEC-HOSTILE',req.id,'PUB',
            SettlementSupportDecisionOutcome.AUTHORIZE,
            11,D('10'),'hostile fixture',
            SettlementSupportReasonCode.SETTLEMENT_SUPPORT_AUTHORIZED,
            (), 'decision-snapshot:HOSTILE:fixture','HOSTILE_POLICY_V1'
        ).validate_protocol(req)
        with self.assertRaisesRegex(InvariantError,'exceeds habitat headroom'):
            k.execute_public_settlement_support(12,'PUB',req,d)

    def test_population_conservation_and_support_transaction(self):
        k,h=self.full_case()
        r=h['settlement_support_record']
        self.assertEqual(r.total_population_before,r.total_population_after)
        self.assertEqual(
            r.earth_population_before-r.earth_population_after,
            r.authorized_residents)
        self.assertEqual(
            r.offworld_population_after-r.offworld_population_before,
            r.authorized_residents)
        tx=next(t for t in k.state.transactions
                if t.id==r.support_transaction_id)
        self.assertEqual(tx.purpose.value,'PUBLIC_SUBSIDY')
        self.assertEqual(tx.amount,D('10'))
        self.assertEqual(tx.source_account,'public_funds')
        self.assertEqual(tx.destination_account,'settlement_support')

    def test_rich_sparse_null_settlement_epochs_preserve_A1_A9(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            _,h=self.full_case(uid,stock)
            for key in (
                'settlement_infrastructure_checks',
                'settlement_support_checks',
            ):
                self.assertEqual(
                    tuple(sorted(h[key])),
                    ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_stage_raw_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.colonies['OFF:T1'].stage='PROSPECTING'
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-STAGE')

    def test_habitat_capacity_raw_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.colonies['OFF:T1'].habitat_capacity+=1
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-HABITAT')

    def test_population_raw_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.population.earth-=1
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-POPULATION')

    def test_settlement_chain_replays_exactly(self):
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
                ah['settlement_infrastructure_record'],
                bh['settlement_infrastructure_record'])
            self.assertEqual(
                ah['settlement_support_policy'].decision,
                bh['settlement_support_policy'].decision)
            self.assertEqual(
                ak.settlement_support_records,
                bk.settlement_support_records)
            self.assertEqual(
                ak.settlement_stage_records,
                bk.settlement_stage_records)
            self.assertEqual(
                ak.methodology_fingerprint(),
                bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
