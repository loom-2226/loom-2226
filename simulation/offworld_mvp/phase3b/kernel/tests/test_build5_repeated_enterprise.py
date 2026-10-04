import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_repeated_enterprise_fixture import (
    enterprise_review_request,
    enterprise_review_snapshot,
    repeated_enterprise_kernel,
)
from offworld_kernel.enterprise import (
    EnterpriseReviewDecision,
    EnterpriseReviewDecisionOutcome,
    EnterpriseReviewReasonCode,
)
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    FinancingDecisionOutcome,
    OperatingCycleDecisionOutcome,
    RuntimeObjectClass,
)
from offworld_kernel.operating_protocol import build_operating_cycle_request
from offworld_kernel.policy import build_decision_snapshot
from offworld_kernel.policy_runner import (
    run_financier_policy,
    run_sponsor_enterprise_review_policy,
    run_sponsor_operating_policy,
    sponsor_enterprise_review_contract_hash,
    sponsor_enterprise_review_policy_version,
    sponsor_operating_contract_hash,
    sponsor_operating_policy_version,
)
from offworld_kernel.policies.manifest import policy_source_bytes
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.underwriting import UnderwritingInputKind, underwriting_snapshot_facts
from offworld_kernel.build5_operating_extraction_fixture import operating_snapshot
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_sale_market as market_tests
from tests import test_build5_sponsor_operator as sponsor_tests
from tests import test_build5_surplus_distribution as surplus_tests


class Build5RepeatedEnterpriseTests(unittest.TestCase):
    CAPS=(
        'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT',
        'SELL','DISTRIBUTE_SURPLUS','CLOSE_PROJECT',
    )

    def reach_distribution(self,universe_id='RICH_PUBLIC_3',stock='20',caps=None):
        k,h=repeated_enterprise_kernel(
            universe_id,stock,sponsor_capabilities=self.CAPS if caps is None else caps)
        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-ENTERPRISE-014A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-014A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-014A-DEVELOP',5)
        lifecycle_tests.Build5ProjectLifecycleTests().lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')
        o=operating_tests.Build5OperatingExtractionTests()
        o.operating_request_epoch(k,h)
        o.operating_finance_epoch(k,h)
        o.operate_epoch(k,h)
        market_tests.Build5SaleMarketTests().sale_epoch(k,h)
        surplus_tests.Build5SurplusDistributionTests().distribution_epoch(k,h)
        return k,h

    def review_epoch(self,k,h,extraction,cycle,year,**snapshot_kw):
        epoch=f'EPOCH-{10+2*cycle}-REVIEW-{cycle}'
        snapshot=enterprise_review_snapshot(
            k,extraction,f'ENTERPRISE-REVIEW-{cycle}',str(year),**snapshot_kw)
        request=enterprise_review_request(
            extraction,f'ERREQ-014A-{cycle}',year)
        h[f'review_snapshot_{cycle}']=snapshot
        h[f'review_request_{cycle}']=request
        k.begin_decision_epoch(epoch)
        k.scheduler.register_coupling(CouplingSpec(
            'ENTERPRISE_REVIEW_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'ENTERPRISE_REVIEW_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('projects','events','enterprise_review_records'),
            ('enterprise_review_decision','extraction_resolution_record'),
            ('projects','events','enterprise_review_records'),
            'EVENT',Phase.ACTION_VALIDATION))
        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        dec_event=f'enterprise-review-{cycle}-decision'
        exec_event=f'enterprise-review-{cycle}-execute'
        k.scheduler.schedule(ScheduledEvent(
            dec_event,D(str(year)),Phase.DECISION_WINDOW,0,'SPN',
            'ENTERPRISE_REVIEW_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            exec_event,D(str(year)),Phase.ACTION_VALIDATION,0,'ENTERPRISE-REVIEW',
            'ENTERPRISE_REVIEW_EXECUTOR',parent_ids=(dec_event,)))
        policy_id=(
            'POLICY:'+sponsor_enterprise_review_policy_version()
            +':CONTRACT:'+sponsor_enterprise_review_contract_hash())
        prov=ReplayProvenance.from_kernel(k,policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_enterprise_review_policy(ctx.snapshot,request,ctx.decision_key)
            h[f'review_policy_{cycle}']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value))

        def execute(kernel,event):
            d=h[f'review_policy_{cycle}'].decision
            if d.outcome not in {EnterpriseReviewDecisionOutcome.CONTINUE,
                                 EnterpriseReviewDecisionOutcome.CLOSE}:
                return 'NO_ENTERPRISE_REVIEW_EXECUTION:'+d.outcome.value
            rec=kernel.execute_enterprise_review(year,'SPN',request,d)
            h[f'review_record_{cycle}']=rec
            return '|'.join((rec.outcome.value,rec.status_before,rec.status_after,rec.event_id))

        rt.register_policy_handler(dec_event,'SPN',snapshot,f'ENTERPRISE-REVIEW-KEY-{cycle}',policy)
        rt.register_handler('ENTERPRISE_REVIEW_EXECUTOR',execute)
        before=AccountingPeriodSnapshot.capture(k,year)
        rt.seal(); result=rt.run()
        h[f'review_result_{cycle}']=result
        h[f'review_checks_{cycle}']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def operating_cycle_epoch(self,k,h,cycle,year):
        snapshot=operating_snapshot(k,h['operating_table'],f'OPERATE-{year}-{cycle}',str(year))
        request=build_operating_cycle_request(
            f'OPREQ-014A-{cycle}',year,'P','RES','MINE-P',h['obs'].id)
        h[f'cycle_snapshot_{cycle}']=snapshot
        h[f'cycle_request_{cycle}']=request
        epoch=f'EPOCH-{11+2*cycle}-OPERATE-{cycle}'
        k.begin_decision_epoch(epoch)
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_COST_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','resource_constraints','events','operating_cost_records'),
            ('operating_decision','project_state','productive_asset','operating_cost'),
            ('accounts','transactions','resource_constraints','events','operating_cost_records'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.register_coupling(CouplingSpec(
            'EXTRACTION_RESOLUTION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('resources','colonies','events','extraction_resolution_records'),
            ('operating_decision','operating_cost_record','scenario_resource'),
            ('resources','colonies','events','extraction_resolution_records'),
            'EVENT',Phase.OPERATIONS,perspective='WORLD_SIM'))
        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        d_event=f'cycle-{cycle}-decision'; o_event=f'cycle-{cycle}-opex'; x_event=f'cycle-{cycle}-extract'
        k.scheduler.schedule(ScheduledEvent(
            d_event,D(str(year)),Phase.DECISION_WINDOW,0,'SPN',
            'OPERATING_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            o_event,D(str(year)),Phase.OPERATIONS,0,'OPEX',
            'OPERATING_COST_SYSTEM',parent_ids=(d_event,)))
        k.scheduler.schedule(ScheduledEvent(
            x_event,D(str(year)),Phase.OPERATIONS,1,'EXTRACT',
            'EXTRACTION_RESOLUTION_SYSTEM',parent_ids=(d_event,o_event)))
        policy_id=(
            'POLICY:'+sponsor_operating_policy_version()
            +':CONTRACT:'+sponsor_operating_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_operating_policy(ctx.snapshot,request,ctx.decision_key)
            h[f'cycle_policy_{cycle}']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,
                             str(d.requested_financing),str(d.planned_quantity),str(d.authorized_opex)))

        def opex(kernel,event):
            d=h[f'cycle_policy_{cycle}'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.OPERATE:
                return 'NO_OPERATING_COST:'+d.outcome.value
            unit=h['operating_table'].get(
                'GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.OPERATING_COST).value
            rec=kernel.spend_operating_cycle(year,'SPN',request,d,'earth_supplier',unit)
            h[f'cycle_cost_{cycle}']=rec
            return '|'.join(('OPEX_SPENT',rec.transaction_id,str(rec.total_opex)))

        def extract(kernel,event):
            d=h[f'cycle_policy_{cycle}'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.OPERATE:
                return 'NO_EXTRACTION:'+d.outcome.value
            rec=kernel.resolve_operating_extraction(
                year,'SPN',request,d,h[f'cycle_cost_{cycle}'])
            h[f'extraction_{cycle}']=rec
            return '|'.join(('EXTRACTION_RESOLVED',str(rec.actual_extracted),rec.extraction_event_id))

        rt.register_policy_handler(d_event,'SPN',snapshot,f'OPERATE-KEY-014A-{cycle}',policy)
        rt.register_handler('OPERATING_COST_SYSTEM',opex)
        rt.register_handler('EXTRACTION_RESOLUTION_SYSTEM',extract)
        before=AccountingPeriodSnapshot.capture(k,year)
        rt.seal(); result=rt.run()
        h[f'cycle_result_{cycle}']=result
        h[f'cycle_checks_{cycle}']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def recap_request_epoch(self,k,h,year=12):
        cycle=3
        snapshot=operating_snapshot(k,h['operating_table'],'RECAP-REQUEST-12',str(year))
        request=build_operating_cycle_request(
            'OPREQ-014A-RECAP',year,'P','RES','MINE-P',h['obs'].id)
        h['recap_operating_snapshot']=snapshot; h['recap_operating_request']=request
        k.begin_decision_epoch('EPOCH-15-RECAP-REQUEST')
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_ACTION_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('financing_requests','events'),('operating_decision',),
            ('financing_requests','events'),'EVENT',Phase.ACTION_VALIDATION))
        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'recap-decision',D(str(year)),Phase.DECISION_WINDOW,0,'SPN',
            'OPERATING_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'recap-request',D(str(year)),Phase.ACTION_VALIDATION,0,'SPN-RECAP',
            'OPERATING_ACTION_EXECUTOR',parent_ids=('recap-decision',)))
        policy_id='POLICY:'+sponsor_operating_policy_version()+':CONTRACT:'+sponsor_operating_contract_hash()
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_operating_policy(ctx.snapshot,request,ctx.decision_key)
            h['recap_operating_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,str(d.requested_financing)))

        def action(kernel,event):
            d=h['recap_operating_policy'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.REQUEST_FINANCE:
                return 'NO_RECAP_REQUEST:'+d.outcome.value
            q=build_financing_request(
                'FINREQ-014A-RECAP',year,'SPN','P',d.requested_financing,
                'OPERATING',(request.observation_id,))
            kernel.submit_financing_request(q,parent_ids=(d.id,))
            h['recap_financing_request']=q
            return 'RECAP_REQUESTED:'+str(q.amount)

        rt.register_policy_handler('recap-decision','SPN',snapshot,'RECAP-REQUEST-KEY-014A',policy)
        rt.register_handler('OPERATING_ACTION_EXECUTOR',action)
        before=AccountingPeriodSnapshot.capture(k,year)
        rt.seal(); result=rt.run()
        h['recap_request_result']=result
        h['recap_request_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def recap_finance_epoch(self,k,h,year=12):
        q=h['recap_financing_request']
        facts=underwriting_snapshot_facts(h['operating_table'],'GENERIC_RESOURCE_PROJECT_MVP',year)
        snapshot=build_decision_snapshot(k,'FIN','RECAP-FINANCE-12',D(str(year)),facts)
        h['recap_financier_snapshot']=snapshot
        k.begin_decision_epoch('EPOCH-16-RECAP-FINANCE')
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_FINANCE_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments'),('financing_decision',),
            ('accounts','commitments'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))
        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'recap-finance-decision',D(str(year)),Phase.DECISION_WINDOW,0,'FIN',
            'OPERATING_FINANCE_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'recap-finance-execute',D(str(year)),Phase.COMMITMENT_DISBURSEMENT,0,'FINANCE',
            'OPERATING_FINANCE_EXECUTOR',parent_ids=('recap-finance-decision',)))
        policy_id=(
            'POLICY:'+h['manifest'].policy_version_hash(policy_source_bytes())
            +':PARAMS:'+h['manifest'].parameter_manifest_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_financier_policy(ctx.snapshot,q,h['manifest'],ctx.decision_key,allow_test_fixture=True)
            h['recap_financier_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,str(d.amount)))

        def execute(kernel,event):
            d=h['recap_financier_policy'].decision
            if d.outcome!=FinancingDecisionOutcome.APPROVE:
                return 'NO_RECAP_FUNDING:'+d.outcome.value
            kernel.add_commitment('C-RECAP-014A','FIN','P',d.amount)
            kernel.disburse(year,'C-RECAP-014A','fin_funds',d.amount)
            return 'RECAP_FUNDED:'+str(d.amount)

        rt.register_policy_handler(
            'recap-finance-decision','FIN',snapshot,'RECAP-FINANCE-KEY-014A',policy)
        rt.register_handler('OPERATING_FINANCE_EXECUTOR',execute)
        before=AccountingPeriodSnapshot.capture(k,year)
        rt.seal(); result=rt.run()
        h['recap_finance_result']=result
        h['recap_finance_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id,stock):
        k,h=self.reach_distribution(universe_id,stock)
        first=h['extraction_record']
        self.review_epoch(k,h,first,1,10)
        if k.state.projects['P'].status=='CLOSED':
            return k,h
        self.operating_cycle_epoch(k,h,2,11)
        self.review_epoch(k,h,h['extraction_2'],2,11)
        if universe_id=='RICH_PUBLIC_3' and k.state.projects['P'].status=='OPERATING':
            self.recap_request_epoch(k,h,12)
            self.recap_finance_epoch(k,h,12)
        return k,h

    def synthetic_review_decision(self,request,outcome):
        reason=(EnterpriseReviewReasonCode.ZERO_OUTPUT_CLOSE
                if outcome==EnterpriseReviewDecisionOutcome.CLOSE
                else EnterpriseReviewReasonCode.POSITIVE_OUTPUT_CONTINUE)
        return EnterpriseReviewDecision(
            'ERDEC-HOSTILE',request.id,'SPN',outcome,'hostile fixture',reason,(),
            'decision-snapshot:HOSTILE:fixture','HOSTILE_ENTERPRISE_POLICY').validate_protocol(request)

    def test_rich_repeats_from_reserve_then_requests_and_receives_recapitalization(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        self.assertEqual(h['review_policy_1'].decision.outcome,EnterpriseReviewDecisionOutcome.CONTINUE)
        self.assertEqual(h['extraction_2'].actual_extracted,D('5'))
        self.assertEqual(h['review_policy_2'].decision.outcome,EnterpriseReviewDecisionOutcome.CONTINUE)
        self.assertEqual(k.state.projects['P'].status,'OPERATING')
        self.assertEqual(h['cycle_policy_2'].decision.outcome,OperatingCycleDecisionOutcome.OPERATE)
        self.assertEqual(h['recap_operating_policy'].decision.outcome,OperatingCycleDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(h['recap_operating_policy'].decision.requested_financing,D('20'))
        self.assertEqual(h['recap_financier_policy'].decision.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(k.state.accounts['project_cash'].balance,D('20'))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('30'))
        self.assertEqual([r.actual_extracted for r in k.extraction_resolution_records],[D('5'),D('5')])

    def test_sparse_partial_then_reserve_funded_zero_then_closes(self):
        k,h=self.full_case('SPARSE_PUBLIC_1','3')
        self.assertEqual(h['extraction_record'].actual_extracted,D('3'))
        self.assertEqual(h['review_policy_1'].decision.outcome,EnterpriseReviewDecisionOutcome.CONTINUE)
        self.assertEqual(h['cycle_policy_2'].decision.outcome,OperatingCycleDecisionOutcome.OPERATE)
        self.assertEqual(h['extraction_2'].actual_extracted,D('0'))
        self.assertEqual(h['review_policy_2'].decision.outcome,EnterpriseReviewDecisionOutcome.CLOSE)
        self.assertEqual(k.state.projects['P'].status,'CLOSED')
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertNotIn('recap_operating_policy',h)

    def test_null_zero_closes_immediately_and_never_runs_second_cycle(self):
        k,h=self.full_case('NULL_FP_1','0')
        self.assertEqual(h['extraction_record'].actual_extracted,D('0'))
        self.assertEqual(h['review_policy_1'].decision.outcome,EnterpriseReviewDecisionOutcome.CLOSE)
        self.assertEqual(k.state.projects['P'].status,'CLOSED')
        self.assertNotIn('extraction_2',h)
        self.assertEqual(len(k.extraction_resolution_records),1)

    def test_review_policy_sees_realized_output_not_hidden_resource_remaining(self):
        cases=[self.reach_distribution('RICH_PUBLIC_3','20'),
               self.reach_distribution('SPARSE_PUBLIC_1','3'),
               self.reach_distribution('NULL_FP_1','0')]
        actual=[]
        for i,(k,h) in enumerate(cases):
            x=h['extraction_record']; snap=enterprise_review_snapshot(k,x,f'ISO-{i}','10')
            req=enterprise_review_request(x,f'ERREQ-ISO-{i}',10)
            result=run_sponsor_enterprise_review_policy(snap,req,'ISO')
            keys={f.key for f in snap.admitted_facts}
            self.assertNotIn('resource.REMAINING',keys)
            self.assertNotIn('scenario.RESOURCE_TRUTH',keys)
            actual.append((x.actual_extracted,result.decision.outcome))
        self.assertEqual(actual,[(D('5'),EnterpriseReviewDecisionOutcome.CONTINUE),
                                 (D('3'),EnterpriseReviewDecisionOutcome.CONTINUE),
                                 (D('0'),EnterpriseReviewDecisionOutcome.CLOSE)])

    def test_unknown_actual_output_blocks_before_worker(self):
        k,h=self.reach_distribution('RICH_PUBLIC_3','20')
        x=h['extraction_record']
        snap=enterprise_review_snapshot(k,x,'UNKNOWN-ACTUAL','10',actual_unknown=True)
        req=enterprise_review_request(x,'ERREQ-UNKNOWN',10)
        r=run_sponsor_enterprise_review_policy(snap,req,'UNKNOWN')
        self.assertEqual(r.decision.outcome,EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('cycle.ACTUAL_OUTPUT',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_policy_evaluation_alone_mutates_nothing(self):
        k,h=self.reach_distribution('SPARSE_PUBLIC_1','3')
        x=h['extraction_record']; snap=enterprise_review_snapshot(k,x,'NO-MUTATE','10')
        req=enterprise_review_request(x,'ERREQ-NO-MUTATE',10)
        before=k.decision_epoch_state_fingerprint()
        r=run_sponsor_enterprise_review_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,EnterpriseReviewDecisionOutcome.CONTINUE)
        self.assertEqual(k.decision_epoch_state_fingerprint(),before)
        self.assertEqual(k.enterprise_review_records,[])

    def test_missing_close_capability_defers_zero_output(self):
        caps=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL','DISTRIBUTE_SURPLUS')
        k,h=self.reach_distribution('NULL_FP_1','0',caps=caps)
        x=h['extraction_record']; snap=enterprise_review_snapshot(k,x,'NO-CLOSE-CAP','10')
        req=enterprise_review_request(x,'ERREQ-NO-CLOSE',10)
        r=run_sponsor_enterprise_review_policy(snap,req,'NO-CLOSE')
        self.assertEqual(r.decision.outcome,EnterpriseReviewDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,EnterpriseReviewReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)
        self.assertEqual(k.state.projects['P'].status,'OPERATING')

    def test_forged_close_on_positive_output_rejected_by_execution_boundary(self):
        k,h=self.reach_distribution('RICH_PUBLIC_3','20')
        x=h['extraction_record']; req=enterprise_review_request(x,'ERREQ-FORGE-CLOSE',10)
        d=self.synthetic_review_decision(req,EnterpriseReviewDecisionOutcome.CLOSE)
        # Decision epoch chain blocks direct mutation first; use scheduled context semantics
        # through a one-event runtime would be redundant here, so test the policy boundary above
        # and the kernel rule on a fresh direct fixture below.
        k2,h2=repeated_enterprise_kernel('RICH_PUBLIC_3','20',sponsor_capabilities=self.CAPS)
        k2.state.projects['P'].status='OPERATING'
        k2.extraction_resolution_records.append(x)
        with self.assertRaisesRegex(InvariantError,'CLOSE not supported'):
            k2.execute_enterprise_review(10,'SPN',req,d)

    def test_forged_continue_on_zero_output_rejected_by_execution_boundary(self):
        k,h=self.reach_distribution('NULL_FP_1','0')
        x=h['extraction_record']; req=enterprise_review_request(x,'ERREQ-FORGE-CONTINUE',10)
        d=self.synthetic_review_decision(req,EnterpriseReviewDecisionOutcome.CONTINUE)
        k2,h2=repeated_enterprise_kernel('NULL_FP_1','0',sponsor_capabilities=self.CAPS)
        k2.state.projects['P'].status='OPERATING'
        k2.extraction_resolution_records.append(x)
        with self.assertRaisesRegex(InvariantError,'CONTINUE not supported'):
            k2.execute_enterprise_review(10,'SPN',req,d)

    def test_duplicate_review_of_same_extraction_is_rejected(self):
        k,h=self.reach_distribution('NULL_FP_1','0')
        x=h['extraction_record']; req=enterprise_review_request(x,'ERREQ-DUP',10)
        d=self.synthetic_review_decision(req,EnterpriseReviewDecisionOutcome.CLOSE)
        k2,h2=repeated_enterprise_kernel('NULL_FP_1','0',sponsor_capabilities=self.CAPS)
        k2.state.projects['P'].status='OPERATING'; k2.extraction_resolution_records.append(x)
        k2.execute_enterprise_review(10,'SPN',req,d)
        with self.assertRaisesRegex(InvariantError,'already executed'):
            k2.execute_enterprise_review(10,'SPN',req,d)

    def test_closed_project_blocks_later_operating_cycle(self):
        k,h=self.full_case('NULL_FP_1','0')
        snap=operating_snapshot(k,h['operating_table'],'CLOSED-OPERATE','11')
        req=build_operating_cycle_request('OPREQ-CLOSED',11,'P','RES','MINE-P',h['obs'].id)
        r=run_sponsor_operating_policy(snap,req,'CLOSED')
        self.assertEqual(r.decision.outcome,OperatingCycleDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code.value,'PROJECT_STATE_BLOCK')

    def test_review_state_tamper_is_detected_at_next_epoch_boundary(self):
        k,h=self.reach_distribution('SPARSE_PUBLIC_1','3')
        self.review_epoch(k,h,h['extraction_record'],1,10)
        k.enterprise_review_records.clear()
        with self.assertRaisesRegex(InvariantError,'persistent state tampered'):
            k.begin_decision_epoch('EPOCH-HOSTILE-TAMPER')

    def test_deterministic_replay_for_all_three_worlds(self):
        for uid,stock in [('RICH_PUBLIC_3','20'),('SPARSE_PUBLIC_1','3'),('NULL_FP_1','0')]:
            k1,h1=self.full_case(uid,stock); k2,h2=self.full_case(uid,stock)
            self.assertEqual(k1.methodology_fingerprint(),k2.methodology_fingerprint())
            self.assertEqual(k1.enterprise_review_records,k2.enterprise_review_records)
            self.assertEqual(k1.state.projects['P'].status,k2.state.projects['P'].status)


if __name__=='__main__':
    unittest.main()
