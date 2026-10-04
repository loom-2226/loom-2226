import unittest
from dataclasses import replace
from decimal import Decimal as D

from offworld_kernel.build6b_staged_prospecting_fixture import (
    staged_prospecting_kernel,
    portfolio_snapshot,
    portfolio_request,
    study_review_snapshot,
    study_review_request,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import AssetKind
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.policy_runner import (
    assert_policy_source_safe,
    run_sponsor_portfolio_policy,
    run_sponsor_study_review_policy,
    sponsor_portfolio_contract_hash,
    sponsor_portfolio_policy_version,
    sponsor_study_review_contract_hash,
    sponsor_study_review_policy_version,
    sponsor_study_review_source_bytes,
)
from offworld_kernel.project_activity import (
    ProjectActivityStatus,
    SponsorPortfolioDecisionOutcome,
    SponsorPortfolioReasonCode,
)
from offworld_kernel.project_study import (
    ProjectStudyMaturity,
    ProjectStudyPlan,
    ProjectStudyResultStanding,
    ProjectStudyReviewOutcome,
    ProjectStudyReviewReasonCode,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent


class Build6BStagedProspectingTests(unittest.TestCase):
    CHAIN='CHAIN-BUILD6B-001A'

    def portfolio_epoch(self,k,epoch_id,effective_time,activity_ids,request_id,first=False):
        snapshot=portfolio_snapshot(k,f'{epoch_id}-SNAP',effective_time,activity_ids)
        request=portfolio_request(request_id,effective_time,activity_ids)
        k.begin_decision_epoch(epoch_id,chain_id=self.CHAIN if first else None)

        k.scheduler.register_coupling(CouplingSpec(
            'PORTFOLIO_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_STUDY_AUTHORIZER','v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions'),
            ('portfolio_decision','projects','accounts','project_activities','project_study_state'),
            ('project_activities','activity_transitions'),
            'EVENT',Phase.ACTION_VALIDATION))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        de=f'{epoch_id}-decision'; ae=f'{epoch_id}-authorize'
        t=D(str(effective_time))
        k.scheduler.schedule(ScheduledEvent(
            de,t,Phase.DECISION_WINDOW,0,'SPN','PORTFOLIO_DECISION_ORCHESTRATOR',
            snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            ae,t,Phase.ACTION_VALIDATION,0,'STUDY-AUTH',
            'PROJECT_STUDY_AUTHORIZER',parent_ids=(de,)))

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
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,
                             d.selected_activity_id,str(d.reserved_capital)))

        def authorize(kernel,event):
            d=holder['policy'].decision
            if d.outcome!=SponsorPortfolioDecisionOutcome.AUTHORIZE:
                return 'NO_AUTHORIZATION:'+d.outcome.value+':'+d.reason_code.value
            rec=kernel.authorize_project_study_activity(t,d)
            holder['transition']=rec
            return '|'.join((rec.activity_id,rec.prior_status.value,rec.new_status.value,
                             str(kernel.project_activity_available_capital('SPN'))))

        rt.register_policy_handler(de,'SPN',snapshot,f'KEY-{epoch_id}',policy)
        rt.register_handler('PROJECT_STUDY_AUTHORIZER',authorize)
        rt.seal()
        holder['result']=rt.run()
        return holder

    def one_event_epoch(self,k,epoch_id,process_id,phase,effective_time,handler,stable_key):
        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            process_id,'v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions','project_study_state',
             'project_study_expense','project_study_results','study_review_records',
             'agent_information','projects','accounts','transactions','assets'),
            ('project_activities','project_study_state','agents','accounts'),
            ('project_activities','activity_transitions','project_study_state',
             'project_study_expense','project_study_results','study_review_records',
             'agent_information','projects','accounts','transactions','assets'),
            'EVENT',phase))
        eid=f'{epoch_id}-event'
        k.scheduler.schedule(ScheduledEvent(
            eid,D(str(effective_time)),phase,0,stable_key,process_id))
        rt=ScheduledSimulationRuntime(k)
        rt.register_handler(process_id,handler)
        rt.seal()
        return rt.run()

    def start_and_spend_epoch(self,k,epoch_id,activity_id,effective_time):
        def handler(kernel,event):
            start=kernel.start_project_activity(effective_time,activity_id)
            expense=kernel.spend_project_study_activity(effective_time,activity_id)
            return '|'.join((
                start.activity_id,start.new_status.value,str(expense.amount),
                expense.exploration_transaction_id,expense.wip_asset_id,
                str(kernel.state.accounts['sponsor_funds'].balance),
                str(kernel.project_activity_available_capital('SPN'))))
        return self.one_event_epoch(
            k,epoch_id,'PROJECT_STUDY_STARTER',Phase.OPERATIONS,effective_time,
            handler,'START-SPEND:'+activity_id)

    def cancel_epoch(self,k,epoch_id,activity_id,effective_time):
        return self.one_event_epoch(
            k,epoch_id,'PROJECT_STUDY_CANCELLER',Phase.OPERATIONS,effective_time,
            lambda kernel,event: kernel.cancel_project_activity(
                effective_time,activity_id,'SPN','BUILD6B-REDESIGN'),
            'CANCEL:'+activity_id)

    def complete_and_admit_epoch(self,k,epoch_id,activity_id,complete_time,admit_time,standing):
        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            'PROJECT_STUDY_COMPLETER','v1',RuntimeObjectClass.SYSTEM,
            ('project_activities','activity_transitions','project_study_results','assets'),
            ('project_activities','project_study_expense'),
            ('project_activities','activity_transitions','project_study_results','assets'),
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
            'PROJECT_STUDY_COMPLETER'))
        k.scheduler.schedule(ScheduledEvent(
            ie,D(str(admit_time)),Phase.INFORMATION_UPDATE,0,'ADMIT:'+activity_id,
            'PROJECT_ACTIVITY_INFORMATION_ADMISSION',parent_ids=(ce,)))
        rt=ScheduledSimulationRuntime(k)

        def complete(kernel,event):
            rec=kernel.complete_project_study_activity(
                complete_time,activity_id,standing,f'INFO:{activity_id}:RESULT')
            return '|'.join((rec.activity_id,rec.standing.value,rec.result_ref,
                             rec.knowledge_asset_id))

        def admit(kernel,event):
            rec=kernel.admit_project_activity_result(
                admit_time,activity_id,'SPN')
            return '|'.join((rec.activity_id,rec.agent_id,rec.result_ref,
                             str(rec.admitted_at)))

        rt.register_handler('PROJECT_STUDY_COMPLETER',complete)
        rt.register_handler('PROJECT_ACTIVITY_INFORMATION_ADMISSION',admit)
        rt.seal()
        return rt.run()

    def review_epoch(self,k,epoch_id,activity_id,effective_time,unknown_key='',
                     tamper_outcome=None):
        snapshot=study_review_snapshot(
            k,f'{epoch_id}-SNAP',effective_time,activity_id,unknown_key=unknown_key)
        request=study_review_request(f'REQ-{epoch_id}',k,activity_id)
        k.begin_decision_epoch(epoch_id)

        k.scheduler.register_coupling(CouplingSpec(
            'STUDY_REVIEW_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'STUDY_REVIEW_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('project_study_state','projects','study_review_records'),
            ('study_review_decision','project_study_results','agent_information'),
            ('project_study_state','projects','study_review_records'),
            'EVENT',Phase.ACTION_VALIDATION))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        de=f'{epoch_id}-decision'; xe=f'{epoch_id}-execute'
        t=D(str(effective_time))
        k.scheduler.schedule(ScheduledEvent(
            de,t,Phase.DECISION_WINDOW,0,'SPN','STUDY_REVIEW_ORCHESTRATOR',
            snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            xe,t,Phase.ACTION_VALIDATION,0,'STUDY-REVIEW',
            'STUDY_REVIEW_EXECUTOR',parent_ids=(de,)))

        policy_id=(
            'POLICY:'+sponsor_study_review_policy_version()
            +':CONTRACT:'+sponsor_study_review_contract_hash())
        rt=ScheduledSimulationRuntime(
            k,ReplayProvenance.from_kernel(k,policy_manifest_ids=(policy_id,)))
        holder={}

        def policy(ctx):
            r=run_sponsor_study_review_policy(ctx.snapshot,request,ctx.decision_key)
            holder['policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value))

        def execute(kernel,event):
            d=holder['policy'].decision
            if tamper_outcome is not None:
                d=replace(
                    d,outcome=ProjectStudyReviewOutcome(tamper_outcome),
                    reason_code=ProjectStudyReviewReasonCode.SUPPORTS_DECLARED_ADVANCE)
            if d.outcome==ProjectStudyReviewOutcome.BLOCKED_UNKNOWN:
                return 'NO_EXECUTION:BLOCKED_UNKNOWN'
            rec=kernel.execute_project_study_review(t,request,d)
            holder['execution']=rec
            return '|'.join((rec.project_id,rec.activity_id,rec.outcome.value,
                             rec.prior_maturity.value,rec.resulting_maturity.value,
                             rec.project_status_after))

        rt.register_policy_handler(de,'SPN',snapshot,f'KEY-{epoch_id}',policy)
        rt.register_handler('STUDY_REVIEW_EXECUTOR',execute)
        rt.seal()
        holder['result']=rt.run()
        return holder

    def run_canonical(self):
        k,h=staged_prospecting_kernel()
        trace=[]

        # B's expensive future-window plan ties up 80.
        r=self.portfolio_epoch(k,'E01-AUTH-BWAIT','1',('ACT-B-WAIT',),'Q-BWAIT',first=True)
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(k.project_activities['ACT-B-WAIT'].status,
                         ProjectActivityStatus.WAITING_WINDOW)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('70'))

        # A can still take a 30 study. Once spent, the reservation disappears but cash is gone.
        r=self.portfolio_epoch(k,'E02-AUTH-A1','1.1',('ACT-A-REMOTE',),'Q-A1')
        trace.append(r['result'].result_fingerprint)
        trace.append(self.start_and_spend_epoch(
            k,'E03-START-A1','ACT-A-REMOTE','1.1').result_fingerprint)
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('120'))
        self.assertEqual(k.project_activity_available_capital('SPN'),D('40'))

        # C needs 50 and is temporarily capital blocked by B's unspent reservation.
        r=self.portfolio_epoch(k,'E04-C-BLOCKED','1.2',('ACT-C-REMOTE',),'Q-C-BLOCK')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.outcome,SponsorPortfolioDecisionOutcome.DEFER)
        self.assertEqual(r['policy'].decision.reason_code,
                         SponsorPortfolioReasonCode.INSUFFICIENT_AVAILABLE_CAPITAL)

        # Cancel B's unspent design, releasing reservation without refund magic.
        trace.append(self.cancel_epoch(
            k,'E05-CANCEL-BWAIT','ACT-B-WAIT','1.3').result_fingerprint)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('120'))

        # C now executes. Its result will later be insufficient.
        r=self.portfolio_epoch(k,'E06-AUTH-C1','1.4',('ACT-C-REMOTE',),'Q-C1')
        trace.append(r['result'].result_fingerprint)
        trace.append(self.start_and_spend_epoch(
            k,'E07-START-C1','ACT-C-REMOTE','1.4').result_fingerprint)
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('70'))

        # B redesigns to a cheaper study and executes.
        r=self.portfolio_epoch(k,'E08-AUTH-B2','1.5',('ACT-B-REDESIGN',),'Q-B2')
        trace.append(r['result'].result_fingerprint)
        trace.append(self.start_and_spend_epoch(
            k,'E09-START-B2','ACT-B-REDESIGN','1.5').result_fingerprint)
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('50'))

        # A earns REMOTE_CHARACTERIZED.
        trace.append(self.complete_and_admit_epoch(
            k,'E10-COMPLETE-A1','ACT-A-REMOTE','2.1','2.15',
            ProjectStudyResultStanding.SUPPORTS_ADVANCE).result_fingerprint)
        r=self.review_epoch(k,'E11-REVIEW-A1','ACT-A-REMOTE','2.2')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(k.project_study_states['P-A'].maturity,
                         ProjectStudyMaturity.REMOTE_CHARACTERIZED)

        # C spends 50 but insufficient evidence earns no maturity.
        trace.append(self.complete_and_admit_epoch(
            k,'E12-COMPLETE-C1','ACT-C-REMOTE','2.4','2.45',
            ProjectStudyResultStanding.INSUFFICIENT).result_fingerprint)
        r=self.review_epoch(k,'E13-REVIEW-C1','ACT-C-REMOTE','2.5')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.outcome,ProjectStudyReviewOutcome.DEFER)
        self.assertEqual(k.project_study_states['P-C'].maturity,
                         ProjectStudyMaturity.SCREENED)

        # B's cheaper redesign comes back negative; spent capital stays spent.
        trace.append(self.complete_and_admit_epoch(
            k,'E14-COMPLETE-B2','ACT-B-REDESIGN','2.5','2.55',
            ProjectStudyResultStanding.NEGATIVE).result_fingerprint)
        r=self.review_epoch(k,'E15-REVIEW-B2','ACT-B-REDESIGN','2.6')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(r['policy'].decision.outcome,ProjectStudyReviewOutcome.ABANDON)
        self.assertEqual(k.state.projects['P-B'].status,'ABANDONED')
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('50'))

        # A buys two additional consecutive knowledge tranches.
        r=self.portfolio_epoch(k,'E16-AUTH-A2','2.7',('ACT-A-SURFACE',),'Q-A2')
        trace.append(r['result'].result_fingerprint)
        trace.append(self.start_and_spend_epoch(
            k,'E17-START-A2','ACT-A-SURFACE','2.7').result_fingerprint)
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('25'))

        trace.append(self.complete_and_admit_epoch(
            k,'E18-COMPLETE-A2','ACT-A-SURFACE','4.2','4.25',
            ProjectStudyResultStanding.SUPPORTS_ADVANCE).result_fingerprint)
        r=self.review_epoch(k,'E19-REVIEW-A2','ACT-A-SURFACE','4.3')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(k.project_study_states['P-A'].maturity,
                         ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED)

        r=self.portfolio_epoch(k,'E20-AUTH-A3','4.4',('ACT-A-ASSESS',),'Q-A3')
        trace.append(r['result'].result_fingerprint)
        trace.append(self.start_and_spend_epoch(
            k,'E21-START-A3','ACT-A-ASSESS','4.4').result_fingerprint)
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('5'))

        trace.append(self.complete_and_admit_epoch(
            k,'E22-COMPLETE-A3','ACT-A-ASSESS','5.4','5.45',
            ProjectStudyResultStanding.SUPPORTS_ADVANCE).result_fingerprint)
        r=self.review_epoch(k,'E23-REVIEW-A3','ACT-A-ASSESS','5.5')
        trace.append(r['result'].result_fingerprint)
        self.assertEqual(k.project_study_states['P-A'].maturity,
                         ProjectStudyMaturity.RESOURCE_ASSESSMENT)

        k.assert_methodology_invariants()
        return k,tuple(trace)

    def test_canonical_staged_spending_maturity_abandonment_and_replay(self):
        k1,t1=self.run_canonical()
        k2,t2=self.run_canonical()
        self.assertEqual(t1,t2)
        self.assertEqual(k1.decision_epoch_state_fingerprint(),
                         k2.decision_epoch_state_fingerprint())

        self.assertEqual(k1.state.accounts['sponsor_funds'].balance,D('5'))
        self.assertEqual(k1.state.accounts['study_supplier'].balance,D('145'))
        self.assertEqual(k1.project_activity_available_capital('SPN'),D('5'))
        self.assertEqual(len(k1.project_activity_expense_records),5)
        self.assertEqual(sum((r.amount for r in k1.project_activity_expense_records),D('0')),D('145'))
        self.assertEqual(len(k1.state.transactions),10)
        self.assertEqual(len(k1.project_study_result_records),5)
        self.assertEqual(len(k1.project_study_review_records),5)

        knowledge=[a for a in k1.state.assets.values() if a.kind==AssetKind.KNOWLEDGE]
        self.assertEqual(len(knowledge),5)
        self.assertEqual(sum((a.book_value for a in knowledge),D('0')),D('145'))

        self.assertEqual(k1.state.projects['P-A'].status,'EXPLORING')
        self.assertEqual(k1.project_study_states['P-A'].maturity,
                         ProjectStudyMaturity.RESOURCE_ASSESSMENT)
        self.assertEqual(k1.state.projects['P-B'].status,'ABANDONED')
        self.assertEqual(k1.project_study_states['P-B'].maturity,
                         ProjectStudyMaturity.SCREENED)
        self.assertEqual(k1.project_study_states['P-C'].maturity,
                         ProjectStudyMaturity.SCREENED)

    def test_non_adjacent_study_plan_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'exactly one maturity edge'):
            ProjectStudyPlan(
                'BAD','ACT','P',
                ProjectStudyMaturity.SCREENED,
                ProjectStudyMaturity.PREFEASIBILITY,
                'supplier','RESULT').validate()

    def test_later_stage_cannot_authorize_before_predecessor_maturity(self):
        k,_=staged_prospecting_kernel()
        # Generic portfolio policy can select the candidate, but the study-specific
        # SYSTEM executor must independently reject its maturity.
        snapshot=portfolio_snapshot(k,'BAD-STAGE','1',('ACT-A-SURFACE',))
        request=portfolio_request('Q-BAD-STAGE','1',('ACT-A-SURFACE',))
        d=run_sponsor_portfolio_policy(snapshot,request,'BAD-STAGE').decision
        self.assertEqual(d.outcome,SponsorPortfolioDecisionOutcome.AUTHORIZE)
        with self.assertRaisesRegex(InvariantError,'predecessor maturity'):
            k.authorize_project_study_activity('1',d)

    def test_spending_twice_is_rejected_and_no_refund_occurs(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1',('ACT-A-REMOTE',),'QA',first=True)
        self.start_and_spend_epoch(k,'E02-S','ACT-A-REMOTE','1')
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('120'))
        with self.assertRaisesRegex(InvariantError,'already spent'):
            k.spend_project_study_activity('1.1','ACT-A-REMOTE')
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('120'))

    def test_unknown_review_input_blocks_before_worker(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1',('ACT-A-REMOTE',),'QA',first=True)
        self.start_and_spend_epoch(k,'E02-S','ACT-A-REMOTE','1')
        self.complete_and_admit_epoch(
            k,'E03-C','ACT-A-REMOTE','2','2.05',
            ProjectStudyResultStanding.SUPPORTS_ADVANCE)
        r=self.review_epoch(
            k,'E04-R','ACT-A-REMOTE','2.1',unknown_key='study.RESULT_STANDING')
        self.assertEqual(r['policy'].decision.outcome,
                         ProjectStudyReviewOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r['policy'].sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_result_not_admitted_before_completion(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1',('ACT-A-REMOTE',),'QA',first=True)
        self.start_and_spend_epoch(k,'E02-S','ACT-A-REMOTE','1')
        self.assertNotIn('INFO:ACT-A-REMOTE:RESULT',k.agents['SPN'].information)
        self.assertEqual(k.project_activities['ACT-A-REMOTE'].result_ref,'')

    def test_duplicate_review_is_rejected(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1',('ACT-A-REMOTE',),'QA',first=True)
        self.start_and_spend_epoch(k,'E02-S','ACT-A-REMOTE','1')
        self.complete_and_admit_epoch(
            k,'E03-C','ACT-A-REMOTE','2','2.05',
            ProjectStudyResultStanding.SUPPORTS_ADVANCE)
        self.review_epoch(k,'E04-R','ACT-A-REMOTE','2.1')
        # Same completed activity cannot be reviewed a second time.
        snapshot=study_review_snapshot(k,'DUP','2.2','ACT-A-REMOTE')
        request=study_review_request('Q-DUP',k,'ACT-A-REMOTE')
        d=run_sponsor_study_review_policy(snapshot,request,'DUP').decision
        with self.assertRaisesRegex(InvariantError,'duplicate project study review'):
            k.execute_project_study_review('2.2',request,d)

    def test_forged_advance_against_negative_result_is_rejected(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1.5',('ACT-B-REDESIGN',),'QB',first=True)
        self.start_and_spend_epoch(k,'E02-S','ACT-B-REDESIGN','1.5')
        self.complete_and_admit_epoch(
            k,'E03-C','ACT-B-REDESIGN','2.5','2.55',
            ProjectStudyResultStanding.NEGATIVE)
        with self.assertRaisesRegex(InvariantError,'decision/result standing mismatch'):
            self.review_epoch(
                k,'E04-R','ACT-B-REDESIGN','2.6',
                tamper_outcome=ProjectStudyReviewOutcome.ADVANCE)

    def test_study_state_tamper_is_detected_between_epochs(self):
        k,_=staged_prospecting_kernel()
        self.portfolio_epoch(k,'E01-A','1',('ACT-A-REMOTE',),'QA',first=True)
        k.project_study_states['P-A'].maturity=ProjectStudyMaturity.FEASIBILITY
        with self.assertRaisesRegex(InvariantError,'persistent state tampered'):
            k.begin_decision_epoch('E02-TAMPER')

    def test_policy_source_safe_and_versioned(self):
        source=sponsor_study_review_source_bytes()
        self.assertTrue(assert_policy_source_safe(source))
        self.assertTrue(
            sponsor_study_review_policy_version(source).startswith(
                'SPONSOR_STUDY_REVIEW_V1:0.1:'))
        self.assertEqual(len(sponsor_study_review_contract_hash()),64)


if __name__=='__main__':
    unittest.main()
