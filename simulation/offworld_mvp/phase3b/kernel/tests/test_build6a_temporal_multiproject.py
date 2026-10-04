import unittest
from decimal import Decimal as D

from offworld_kernel.build6a_temporal_multiproject_fixture import (
    temporal_multiproject_kernel,
    portfolio_snapshot,
    portfolio_request,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.policy_runner import (
    assert_policy_source_safe,
    run_sponsor_portfolio_policy,
    sponsor_portfolio_contract_hash,
    sponsor_portfolio_policy_version,
    sponsor_portfolio_source_bytes,
)
from offworld_kernel.project_activity import (
    ProjectActivityStatus,
    SponsorPortfolioDecisionOutcome,
    SponsorPortfolioReasonCode,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent


class Build6ATemporalMultiProjectTests(unittest.TestCase):
    CHAIN='CHAIN-BUILD6A-001A'

    def decision_epoch(self,k,epoch_id,effective_time,activity_ids,request_id,first=False,unknown_key=''):
        snapshot=portfolio_snapshot(
            k,f'{epoch_id}-SNAP',effective_time,activity_ids,unknown_key=unknown_key)
        request=portfolio_request(request_id,effective_time,activity_ids)
        k.begin_decision_epoch(epoch_id,chain_id=self.CHAIN if first else None)

        k.scheduler.register_coupling(CouplingSpec(
            'PORTFOLIO_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_ACTIVITY_AUTHORIZER','v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions'),
            ('portfolio_decision','projects','accounts','project_activities'),
            ('project_activities','activity_transitions'),
            'EVENT',Phase.ACTION_VALIDATION))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        de=f'{epoch_id}-decision'; ae=f'{epoch_id}-authorize'
        t=D(str(effective_time))
        k.scheduler.schedule(ScheduledEvent(
            de,t,Phase.DECISION_WINDOW,0,'SPN','PORTFOLIO_DECISION_ORCHESTRATOR',
            snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            ae,t,Phase.ACTION_VALIDATION,0,'PORTFOLIO-AUTH',
            'PROJECT_ACTIVITY_AUTHORIZER',parent_ids=(de,)))

        policy_id=(
            'POLICY:'+sponsor_portfolio_policy_version()
            +':CONTRACT:'+sponsor_portfolio_contract_hash())
        rt=ScheduledSimulationRuntime(
            k,ReplayProvenance.from_kernel(k,policy_manifest_ids=(policy_id,)))
        holder={}

        def policy(ctx):
            r=run_sponsor_portfolio_policy(ctx.snapshot,request,ctx.decision_key)
            holder['policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                d.selected_activity_id,str(d.reserved_capital)))

        def authorize(kernel,event):
            d=holder['policy'].decision
            if d.outcome!=SponsorPortfolioDecisionOutcome.AUTHORIZE:
                return 'NO_AUTHORIZATION:'+d.outcome.value+':'+d.reason_code.value
            rec=kernel.authorize_project_activity(t,d)
            holder['transition']=rec
            return '|'.join((
                rec.activity_id,rec.prior_status.value,rec.new_status.value,
                str(kernel.project_activity_available_capital('SPN'))))

        rt.register_policy_handler(
            de,'SPN',snapshot,f'KEY-{epoch_id}',policy)
        rt.register_handler('PROJECT_ACTIVITY_AUTHORIZER',authorize)
        rt.seal()
        holder['result']=rt.run()
        holder['snapshot']=snapshot
        holder['request']=request
        return holder

    def transition_epoch(self,k,epoch_id,process_id,phase,effective_time,handler,
                         stable_key='ACTIVITY'):
        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            process_id,'v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions','activity_information','agent_information'),
            ('project_activities','agents'),
            ('project_activities','activity_transitions','activity_information','agent_information'),
            'EVENT',phase))
        eid=f'{epoch_id}-event'
        k.scheduler.schedule(ScheduledEvent(
            eid,D(str(effective_time)),phase,0,stable_key,process_id))
        rt=ScheduledSimulationRuntime(k)
        rt.register_handler(process_id,handler)
        rt.seal()
        return rt.run()

    def start_epoch(self,k,epoch_id,activity_id,effective_time):
        return self.transition_epoch(
            k,epoch_id,'PROJECT_ACTIVITY_STARTER',Phase.OPERATIONS,effective_time,
            lambda kernel,event: (
                lambda r:'|'.join((r.activity_id,r.prior_status.value,r.new_status.value))
            )(kernel.start_project_activity(effective_time,activity_id)),
            stable_key='START:'+activity_id)

    def complete_and_admit_epoch(self,k,epoch_id,activity_id,complete_time,admit_time):
        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_ACTIVITY_COMPLETER','v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions'),
            ('project_activities',),
            ('project_activities','activity_transitions'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_ACTIVITY_INFORMATION_ADMISSION','v1',RuntimeObjectClass.SYSTEM,
            ('agent_information','activity_information'),
            ('project_activities','agents'),
            ('agent_information','activity_information'),
            'EVENT',Phase.INFORMATION_UPDATE))
        ce=f'{epoch_id}-complete'; ie=f'{epoch_id}-admit'
        k.scheduler.schedule(ScheduledEvent(
            ce,D(str(complete_time)),Phase.OPERATIONS,0,'COMPLETE:'+activity_id,
            'PROJECT_ACTIVITY_COMPLETER'))
        k.scheduler.schedule(ScheduledEvent(
            ie,D(str(admit_time)),Phase.INFORMATION_UPDATE,0,'ADMIT:'+activity_id,
            'PROJECT_ACTIVITY_INFORMATION_ADMISSION',parent_ids=(ce,)))
        rt=ScheduledSimulationRuntime(k)

        def complete(kernel,event):
            rec=kernel.complete_project_activity(
                complete_time,activity_id,f'INFO:{activity_id}:RESULT')
            return '|'.join((rec.activity_id,rec.new_status.value,rec.result_ref))

        def admit(kernel,event):
            rec=kernel.admit_project_activity_result(admit_time,activity_id,'SPN')
            return '|'.join((rec.activity_id,rec.agent_id,rec.result_ref,str(rec.admitted_at)))

        rt.register_handler('PROJECT_ACTIVITY_COMPLETER',complete)
        rt.register_handler('PROJECT_ACTIVITY_INFORMATION_ADMISSION',admit)
        rt.seal()
        return rt.run()

    def run_canonical(self):
        k,h=temporal_multiproject_kernel()
        trace=[]

        r=self.decision_epoch(
            k,'E01-AUTH-A','1',('ACT-C','ACT-B','ACT-A'),'REQ-A',first=True)
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.selected_activity_id,'ACT-A')
        self.assertEqual(k.project_activity_available_capital('SPN'),D('40'))

        trace.append(self.start_epoch(k,'E02-START-A','ACT-A','1').result_fingerprint)
        self.assertEqual(k.project_activities['ACT-A'].status,ProjectActivityStatus.ACTIVE)

        r=self.decision_epoch(
            k,'E03-AUTH-C','1.1',('ACT-B','ACT-C'),'REQ-C')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.selected_activity_id,'ACT-C')
        self.assertEqual(k.project_activities['ACT-C'].status,ProjectActivityStatus.WAITING_WINDOW)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('10'))

        r=self.decision_epoch(
            k,'E04-B-BLOCKED','1.2',('ACT-B',),'REQ-B-BLOCK')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.outcome,SponsorPortfolioDecisionOutcome.DEFER)
        self.assertEqual(
            r['policy'].decision.reason_code,
            SponsorPortfolioReasonCode.INSUFFICIENT_AVAILABLE_CAPITAL)
        self.assertEqual(k.project_activities['ACT-B'].status,ProjectActivityStatus.PROPOSED)

        # Result does not exist while A is merely active.
        self.assertEqual(k.project_activities['ACT-A'].result_ref,'')
        self.assertNotIn('INFO:ACT-A:RESULT',k.agents['SPN'].information)

        trace.append(self.complete_and_admit_epoch(
            k,'E05-COMPLETE-A','ACT-A','3','3.05').result_fingerprint)
        self.assertEqual(k.project_activities['ACT-A'].status,ProjectActivityStatus.COMPLETED)
        self.assertIn('INFO:ACT-A:RESULT',k.agents['SPN'].information)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('70'))

        r=self.decision_epoch(
            k,'E06-AUTH-B','3.1',('ACT-B',),'REQ-B')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.selected_activity_id,'ACT-B')
        self.assertEqual(k.project_activity_available_capital('SPN'),D('10'))

        trace.append(self.start_epoch(k,'E07-START-B','ACT-B','3.1').result_fingerprint)
        self.assertEqual(k.project_activities['ACT-B'].status,ProjectActivityStatus.ACTIVE)

        trace.append(self.start_epoch(k,'E08-START-C','ACT-C','4').result_fingerprint)
        self.assertEqual(k.project_activities['ACT-C'].status,ProjectActivityStatus.ACTIVE)
        self.assertEqual(k.project_activities['ACT-B'].status,ProjectActivityStatus.ACTIVE)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('10'))

        trace.append(self.complete_and_admit_epoch(
            k,'E09-COMPLETE-C','ACT-C','5','5.05').result_fingerprint)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('40'))

        trace.append(self.complete_and_admit_epoch(
            k,'E10-COMPLETE-B','ACT-B','7.1','7.15').result_fingerprint)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('100'))

        k.assert_methodology_invariants()
        return k,tuple(trace)

    def test_canonical_multi_project_timeline_capital_and_replay(self):
        k1,t1=self.run_canonical()
        k2,t2=self.run_canonical()
        self.assertEqual(t1,t2)
        self.assertEqual(k1.decision_epoch_state_fingerprint(),
                         k2.decision_epoch_state_fingerprint())
        self.assertEqual(
            [r.new_status.value for r in k1.project_activity_transition_records
             if r.activity_id=='ACT-A'],
            ['AUTHORIZED','ACTIVE','COMPLETED'])
        self.assertEqual(
            [r.new_status.value for r in k1.project_activity_transition_records
             if r.activity_id=='ACT-C'],
            ['WAITING_WINDOW','ACTIVE','COMPLETED'])
        self.assertEqual(
            [r.new_status.value for r in k1.project_activity_transition_records
             if r.activity_id=='ACT-B'],
            ['AUTHORIZED','ACTIVE','COMPLETED'])
        self.assertEqual(
            {r.result_ref for r in k1.project_activity_information_records},
            {'INFO:ACT-A:RESULT','INFO:ACT-B:RESULT','INFO:ACT-C:RESULT'})

    def test_candidate_input_order_does_not_change_selection(self):
        k,_=temporal_multiproject_kernel()
        s1=portfolio_snapshot(k,'S1','1',('ACT-A','ACT-B','ACT-C'))
        q1=portfolio_request('Q1','1',('ACT-A','ACT-B','ACT-C'))
        s2=portfolio_snapshot(k,'S2','1',('ACT-C','ACT-B','ACT-A'))
        q2=portfolio_request('Q2','1',('ACT-C','ACT-B','ACT-A'))
        d1=run_sponsor_portfolio_policy(s1,q1,'ORDER-1').decision
        d2=run_sponsor_portfolio_policy(s2,q2,'ORDER-2').decision
        self.assertEqual(d1.selected_activity_id,'ACT-A')
        self.assertEqual(d2.selected_activity_id,'ACT-A')
        self.assertEqual(d1.reserved_capital,D('60'))
        self.assertEqual(d2.reserved_capital,D('60'))

    def test_unknown_required_input_blocks_before_worker(self):
        k,_=temporal_multiproject_kernel()
        key='activity.ACT-A.COMMITMENT'
        snapshot=portfolio_snapshot(k,'UNKNOWN','1',('ACT-A',),unknown_key=key)
        request=portfolio_request('Q-UNKNOWN','1',('ACT-A',))
        r=run_sponsor_portfolio_policy(snapshot,request,'UNKNOWN-KEY')
        self.assertEqual(r.decision.outcome,SponsorPortfolioDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertIn(key,r.decision.unknown_input_keys)
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_opportunity_window_rejects_early_start(self):
        k,_=temporal_multiproject_kernel()
        r=self.decision_epoch(
            k,'E01-AUTH-C','1',('ACT-C',),'REQ-C',first=True)
        self.assertEqual(r['policy'].decision.outcome,SponsorPortfolioDecisionOutcome.AUTHORIZE)
        self.assertEqual(k.project_activities['ACT-C'].status,ProjectActivityStatus.WAITING_WINDOW)

        k.begin_decision_epoch('E02-EARLY-C')
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_ACTIVITY_STARTER','v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions'),
            ('project_activities',),('project_activities','activity_transitions'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.schedule(ScheduledEvent(
            'early-c',D('3.9'),Phase.OPERATIONS,0,'START:ACT-C',
            'PROJECT_ACTIVITY_STARTER'))
        rt=ScheduledSimulationRuntime(k)
        rt.register_handler(
            'PROJECT_ACTIVITY_STARTER',
            lambda kernel,event: kernel.start_project_activity('3.9','ACT-C'))
        rt.seal()
        with self.assertRaisesRegex(InvariantError,'outside opportunity window'):
            rt.run()

    def test_cancellation_releases_reservation_without_creating_cash(self):
        k,_=temporal_multiproject_kernel()
        self.decision_epoch(
            k,'E01-AUTH-A','1',('ACT-A',),'REQ-A',first=True)
        before=k.state.accounts['sponsor_funds'].balance
        self.assertEqual(k.project_activity_available_capital('SPN'),D('40'))

        self.transition_epoch(
            k,'E02-CANCEL-A','PROJECT_ACTIVITY_COMPLETER',Phase.OPERATIONS,'1.5',
            lambda kernel,event: kernel.cancel_project_activity(
                '1.5','ACT-A','SPN','TEST-CANCEL'))
        self.assertEqual(k.project_activities['ACT-A'].status,ProjectActivityStatus.CANCELED)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('100'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,before)
        self.assertEqual(len(k.state.transactions),0)

    def test_activity_state_tamper_is_detected_between_epochs(self):
        k,_=temporal_multiproject_kernel()
        self.decision_epoch(
            k,'E01-AUTH-A','1',('ACT-A',),'REQ-A',first=True)
        k.project_activities['ACT-A'].capital_commitment=D('1')
        with self.assertRaisesRegex(InvariantError,'persistent state tampered'):
            k.begin_decision_epoch('E02-TAMPER-CHECK')

    def test_same_time_scheduler_order_is_stable_not_insertion_order(self):
        def order(reverse):
            k,_=temporal_multiproject_kernel()
            k.begin_decision_epoch('E01-ORDER',chain_id=self.CHAIN)
            k.scheduler.register_coupling(CouplingSpec(
                'PROJECT_ACTIVITY_STARTER','v1',RuntimeObjectClass.SYSTEM,
                (),(),(),'EVENT',Phase.OPERATIONS))
            events=[
                ScheduledEvent('evt-z',D('2'),Phase.OPERATIONS,0,'B','PROJECT_ACTIVITY_STARTER'),
                ScheduledEvent('evt-a',D('2'),Phase.OPERATIONS,0,'A','PROJECT_ACTIVITY_STARTER'),
            ]
            for e in (reversed(events) if reverse else events):
                k.scheduler.schedule(e)
            rt=ScheduledSimulationRuntime(k)
            rt.register_handler('PROJECT_ACTIVITY_STARTER',lambda kernel,event:event.event_id)
            rt.seal()
            return rt.run().execution_log
        self.assertEqual(order(False),('evt-a','evt-z'))
        self.assertEqual(order(True),('evt-a','evt-z'))

    def test_policy_source_is_sandbox_safe_and_versioned(self):
        source=sponsor_portfolio_source_bytes()
        self.assertTrue(assert_policy_source_safe(source))
        self.assertTrue(sponsor_portfolio_policy_version(source).startswith('SPONSOR_PORTFOLIO_V1:0.1:'))
        self.assertEqual(len(sponsor_portfolio_contract_hash()),64)


if __name__=='__main__':
    unittest.main()
