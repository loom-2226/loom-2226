import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_sponsor_fixture import (
    sponsor_operator_kernel,
    sponsor_request_for_epoch,
    sponsor_snapshot,
)
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    FinancingDecisionOutcome,
    PublicationDecisionOutcome,
    RuntimeObjectClass,
    SponsorProjectDecisionOutcome,
    SponsorProjectReasonCode,
)
from offworld_kernel.policy import build_decision_snapshot
from offworld_kernel.policy_runner import (
    public_publisher_contract_hash,
    public_publisher_policy_version,
    run_financier_policy,
    run_hostile_access_probe,
    run_public_publisher_policy,
    run_sponsor_operator_policy,
    sponsor_operator_contract_hash,
    sponsor_operator_policy_version,
)
from offworld_kernel.policies.manifest import policy_source_bytes
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.underwriting import underwriting_snapshot_facts


class Build5SponsorOperatorTests(unittest.TestCase):
    def base(self,universe_id='RICH_PUBLIC_3',stock='20',
             sponsor_capabilities=('REQUEST_FINANCE','DEVELOP'),
             sponsor_objectives=('RETURN',),
             initial_project_cash='0'):
        values=sponsor_operator_kernel(
            universe_id,stock,sponsor_capabilities,sponsor_objectives,
            initial_project_cash)
        k,pub_snapshot,pub_request,manifest,obs,wip,draw,table,sponsor_request=values
        h={
            'pub_snapshot':pub_snapshot,
            'pub_request':pub_request,
            'manifest':manifest,
            'obs':obs,
            'wip':wip,
            'draw':draw,
            'table':table,
            'sponsor_request':sponsor_request,
        }
        return k,h

    def publication_epoch(self,k,h,chain_id='CHAIN-SPONSOR-005A'):
        k.begin_decision_epoch('EPOCH-1-PUBLISH',chain_id)
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLICATION_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLICATION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('public_information','agent_information','agent_beliefs','events'),
            ('publication_decision','observation','publisher_information'),
            ('public_information','agent_information','agent_beliefs','events'),
            'EVENT',Phase.INFORMATION_UPDATE,perspective='WORLD_SIM'))

        snap=h['pub_snapshot']
        ref=k.scheduler.open_decision_window(snap.period_key,snap.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'sponsor-e1-publication-decision',D('1'),Phase.DECISION_WINDOW,0,'PUB',
            'PUBLICATION_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'sponsor-e1-publication-transfer',D('2'),Phase.INFORMATION_UPDATE,0,'PUBINFO',
            'PUBLICATION_SYSTEM',parent_ids=('sponsor-e1-publication-decision',)))

        policy_id=(
            'POLICY:'+public_publisher_policy_version()
            +':CONTRACT:'+public_publisher_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('NO_EXTERNAL_TABLES',),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_publisher_policy(
                ctx.snapshot,h['pub_request'],ctx.decision_key)
            h['publication_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,r.policy_version))

        def publish(kernel,event):
            d=h['publication_policy'].decision
            if d.outcome!=PublicationDecisionOutcome.PUBLISH:
                return 'NO_PUBLICATION:'+d.outcome.value
            det=h['manifest'].parameter('agent_detection_rate').value
            fp=h['manifest'].parameter('agent_false_positive_rate').value
            a=kernel.publish_observation(
                2,'PUB',h['obs'].id,h['pub_request'].audience,
                (
                    ('FIN','resource_exists',det,fp),
                    ('SPN','resource_exists',det,fp),
                ))
            h['artifact']=a
            return '|'.join(('PUBLISHED',a.id,a.signal,*a.recipient_ids))

        rt.register_policy_handler(
            'sponsor-e1-publication-decision','PUB',snap,'SPONSOR-PUB-KEY',policy)
        rt.register_handler('PUBLICATION_SYSTEM',publish)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h['epoch1_result']=result
        h['epoch1_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def sponsor_epoch(self,k,h,epoch_id,request_id,effective_time,
                      development_unknown=False):
        snapshot=sponsor_snapshot(
            k,h['table'],request_id,str(effective_time),
            development_unknown=development_unknown)
        request=sponsor_request_for_epoch(
            h['obs'].id,request_id,int(effective_time))
        h[epoch_id+'_snapshot']=snapshot
        h[epoch_id+'_request']=request

        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            'SPONSOR_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'SPONSOR_ACTION_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('financing_requests','project_state','events'),
            ('sponsor_project_decision',),
            ('financing_requests','project_state','events'),
            'EVENT',Phase.ACTION_VALIDATION))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        decision_event=epoch_id+'-decision'
        action_event=epoch_id+'-action'
        k.scheduler.schedule(ScheduledEvent(
            decision_event,D(str(effective_time)),Phase.DECISION_WINDOW,0,'SPN',
            'SPONSOR_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            action_event,D(str(effective_time)),Phase.ACTION_VALIDATION,0,'SPN-ACTION',
            'SPONSOR_ACTION_EXECUTOR',parent_ids=(decision_event,)))

        table_id=f'UNDERWRITING:{h["table"].table_id}:{h["table"].version}:{h["table"].fingerprint()}'
        policy_id=(
            'POLICY:'+sponsor_operator_policy_version()
            +':CONTRACT:'+sponsor_operator_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(table_id,),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_operator_policy(
                ctx.snapshot,request,ctx.decision_key)
            h[epoch_id+'_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.requested_financing),r.policy_version))

        def execute(kernel,event):
            d=h[epoch_id+'_policy'].decision
            if d.outcome==SponsorProjectDecisionOutcome.REQUEST_FINANCE:
                q=build_financing_request(
                    'FINREQ-005A',request.year,'SPN',request.project_id,
                    d.requested_financing,'DEVELOPMENT',(request.observation_id,))
                kernel.submit_financing_request(q,parent_ids=(d.id,))
                h['financing_request']=q
                return 'FINANCING_REQUESTED:'+str(q.amount)
            if d.outcome==SponsorProjectDecisionOutcome.ABANDON:
                kernel.transition_project_status(
                    request.year,'SPN',request.project_id,'ABANDONED',d.id)
                return 'PROJECT_ABANDONED'
            if d.outcome==SponsorProjectDecisionOutcome.DEVELOP:
                kernel.transition_project_status(
                    request.year,'SPN',request.project_id,'DEVELOPMENT',d.id)
                return 'PROJECT_TO_DEVELOPMENT'
            return 'NO_WORLD_ACTION:'+d.outcome.value

        rt.register_policy_handler(
            decision_event,'SPN',snapshot,'SPONSOR-'+epoch_id,policy)
        rt.register_handler('SPONSOR_ACTION_EXECUTOR',execute)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h[epoch_id+'_result']=result
        h[epoch_id+'_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def finance_epoch(self,k,h):
        q=h['financing_request']
        facts=underwriting_snapshot_facts(
            h['table'],'GENERIC_RESOURCE_PROJECT_MVP',1)
        snapshot=build_decision_snapshot(k,'FIN','FIN-EPOCH',D('4'),facts)
        h['fin_snapshot']=snapshot

        k.begin_decision_epoch('EPOCH-3-FINANCE')
        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_DECISION_ORCHESTRATOR_SPONSOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_EXECUTOR_SPONSOR','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments'),('financing_decision',),
            ('accounts','commitments'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'sponsor-e3-financier-decision',D('4'),Phase.DECISION_WINDOW,0,'FIN',
            'FINANCE_DECISION_ORCHESTRATOR_SPONSOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'sponsor-e3-finance-execute',D('4'),Phase.COMMITMENT_DISBURSEMENT,0,'FINANCE',
            'FINANCE_EXECUTOR_SPONSOR',parent_ids=('sponsor-e3-financier-decision',)))

        table_id=f'UNDERWRITING:{h["table"].table_id}:{h["table"].version}:{h["table"].fingerprint()}'
        policy_id=(
            'POLICY:'+h['manifest'].policy_version_hash(policy_source_bytes())
            +':PARAMS:'+h['manifest'].parameter_manifest_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(table_id,),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_financier_policy(
                ctx.snapshot,q,h['manifest'],ctx.decision_key,
                allow_test_fixture=True)
            h['financier_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,r.policy_version))

        def execute(kernel,event):
            d=h['financier_policy'].decision
            if d.outcome==FinancingDecisionOutcome.APPROVE:
                kernel.add_commitment('C-SPONSOR-005A','FIN','P',d.amount)
                kernel.disburse(1,'C-SPONSOR-005A','fin_funds',d.amount)
                return 'FUNDED:'+str(d.amount)
            return 'NO_FUNDING:'+d.outcome.value

        rt.register_policy_handler(
            'sponsor-e3-financier-decision','FIN',snapshot,'SPONSOR-FIN-KEY',policy)
        rt.register_handler('FINANCE_EXECUTOR_SPONSOR',execute)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h['epoch3_result']=result
        h['epoch3_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def positive_chain(self):
        k,h=self.base('RICH_PUBLIC_3','20')
        self.publication_epoch(k,h)
        self.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-005A-FINANCE',3)
        self.finance_epoch(k,h)
        self.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-005A-DEVELOP',5)
        return k,h

    def negative_chain(self):
        k,h=self.base('NULL_PUBLIC_1','0')
        self.publication_epoch(k,h)
        self.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-ABANDON','SPREQ-005A-ABANDON',3)
        return k,h

    def test_positive_chain_requests_finance_then_develops_after_funding(self):
        k,h=self.positive_chain()
        d1=h['EPOCH-2-SPONSOR-FINANCE_policy'].decision
        d2=h['EPOCH-4-SPONSOR-DEVELOP_policy'].decision
        self.assertEqual(d1.outcome,SponsorProjectDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(
            d1.reason_code,SponsorProjectReasonCode.POSITIVE_EVIDENCE_FINANCE_REQUIRED)
        self.assertEqual(d1.requested_financing,D('60'))
        self.assertEqual(h['financing_request'].amount,D('60'))
        self.assertEqual(h['financier_policy'].decision.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(d2.outcome,SponsorProjectDecisionOutcome.DEVELOP)
        self.assertEqual(
            d2.reason_code,SponsorProjectReasonCode.POSITIVE_EVIDENCE_FUNDED)
        self.assertEqual(k.state.projects['P'].status,'DEVELOPMENT')
        self.assertFalse(any(a.project_id=='P' for a in k.state.assets.values()))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('40'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('60'))
        request_events=[e for e in k.events if e.action.value=='REQUEST_FINANCE']
        develop_events=[e for e in k.events if e.action.value=='DEVELOP']
        self.assertIn(d1.id,request_events[-1].parent_ids)
        self.assertIn(d2.id,develop_events[-1].parent_ids)
        self.assertEqual(len(k.decision_epoch_records),4)

    def test_negative_chain_abandons_without_finance(self):
        k,h=self.negative_chain()
        d=h['EPOCH-2-SPONSOR-ABANDON_policy'].decision
        self.assertEqual(d.outcome,SponsorProjectDecisionOutcome.ABANDON)
        self.assertEqual(d.reason_code,SponsorProjectReasonCode.NONPOSITIVE_EVIDENCE)
        self.assertEqual(k.state.projects['P'].status,'ABANDONED')
        self.assertNotIn('financing_request',h)
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('100'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        abandon_events=[e for e in k.events if e.action.value=='ABANDON']
        self.assertIn(d.id,abandon_events[-1].parent_ids)
        self.assertEqual(len(k.decision_epoch_records),2)

    def test_requested_amount_is_exact_development_cash_shortfall(self):
        k,h=self.base('RICH_PUBLIC_3','20',initial_project_cash='20')
        self.publication_epoch(k,h)
        self.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-SHORTFALL',3)
        d=h['EPOCH-2-SPONSOR-FINANCE_policy'].decision
        self.assertEqual(d.outcome,SponsorProjectDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(d.requested_financing,D('40'))
        self.assertEqual(h['financing_request'].amount,D('40'))

    def test_unknown_development_cost_blocks_before_worker(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        self.sponsor_epoch(
            k,h,'EPOCH-2-SPONSOR-UNKNOWN','SPREQ-UNKNOWN',3,
            development_unknown=True)
        r=h['EPOCH-2-SPONSOR-UNKNOWN_policy']
        self.assertEqual(r.decision.outcome,SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(
            r.decision.reason_code,SponsorProjectReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN)
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
        self.assertNotIn('financing_request',h)

    def test_missing_capability_defers(self):
        k,h=self.base(sponsor_capabilities=('DEVELOP',))
        self.publication_epoch(k,h)
        self.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-CAP','SPREQ-CAP',3)
        d=h['EPOCH-2-SPONSOR-CAP_policy'].decision
        self.assertEqual(d.outcome,SponsorProjectDecisionOutcome.DEFER)
        self.assertEqual(
            d.reason_code,SponsorProjectReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_hidden_world_cannot_change_sponsor_before_publication(self):
        rk,rh=self.base('RICH_PUBLIC_3','20')
        nk,nh=self.base('NULL_PUBLIC_1','0')
        rs=sponsor_snapshot(rk,rh['table'],'PRE','1')
        ns=sponsor_snapshot(nk,nh['table'],'PRE','1')
        self.assertEqual(rs,ns)
        self.assertEqual(rh['sponsor_request'],nh['sponsor_request'])
        rr=run_sponsor_operator_policy(rs,rh['sponsor_request'],'SAME-KEY')
        nr=run_sponsor_operator_policy(ns,nh['sponsor_request'],'SAME-KEY')
        self.assertEqual(rr.decision,nr.decision)
        self.assertEqual(rr.decision.outcome,SponsorProjectDecisionOutcome.DEFER)
        self.assertEqual(rr.worker_fingerprint,nr.worker_fingerprint)

    def test_sponsor_policy_hostile_probe_has_no_hidden_access(self):
        k,h=self.base()
        snap=sponsor_snapshot(k,h['table'],'PRE','1')
        result,_=run_hostile_access_probe(snap)
        self.assertEqual({k:v for k,v in result.items() if v=='LEAK'},{})

    def test_policy_decision_does_not_mutate_project_or_cash(self):
        k,h=self.base('RICH_PUBLIC_3','20')
        self.publication_epoch(k,h)
        snap=sponsor_snapshot(k,h['table'],'TEST','3')
        req=sponsor_request_for_epoch(h['obs'].id,'SPREQ-NOMUTATE',3)
        status=k.state.projects['P'].status
        cash=k.state.accounts['project_cash'].balance
        r=run_sponsor_operator_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,SponsorProjectDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(k.state.projects['P'].status,status)
        self.assertEqual(k.state.accounts['project_cash'].balance,cash)
        self.assertNotIn('FINREQ-005A',k.financing_requests)

    def test_agent_capability_and_project_status_raw_tamper_are_epoch_guarded(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        k.agents['SPN'].capabilities.add('EXTRACT')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-CAP')

        k,h=self.base()
        self.publication_epoch(k,h)
        k.state.projects['P'].status='OPERATING'
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-STATUS')

    def test_all_sponsor_chain_epochs_preserve_accounting_identities(self):
        k,h=self.positive_chain()
        for key in (
            'epoch1_checks',
            'EPOCH-2-SPONSOR-FINANCE_checks',
            'epoch3_checks',
            'EPOCH-4-SPONSOR-DEVELOP_checks',
        ):
            self.assertEqual(
                tuple(sorted(h[key])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_positive_chain_replays_exactly(self):
        ak,ah=self.positive_chain()
        bk,bh=self.positive_chain()
        self.assertEqual(
            tuple(ak.decision_epoch_records),
            tuple(bk.decision_epoch_records))
        self.assertEqual(
            ah['EPOCH-2-SPONSOR-FINANCE_policy'].decision,
            bh['EPOCH-2-SPONSOR-FINANCE_policy'].decision)
        self.assertEqual(
            ah['financier_policy'].decision,
            bh['financier_policy'].decision)
        self.assertEqual(
            ah['EPOCH-4-SPONSOR-DEVELOP_policy'].decision,
            bh['EPOCH-4-SPONSOR-DEVELOP_policy'].decision)
        self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
