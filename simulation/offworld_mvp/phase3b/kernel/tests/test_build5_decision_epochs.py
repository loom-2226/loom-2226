import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_publication_fixture import (
    financier_snapshot_after_publication,
    publication_handoff_kernel,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    FinancingDecisionOutcome,
    PublicationDecisionOutcome,
    RuntimeObjectClass,
    SystemState,
)
from offworld_kernel.policy import build_decision_snapshot
from offworld_kernel.policy_runner import (
    public_publisher_contract_hash,
    public_publisher_policy_version,
    run_financier_policy,
    run_public_publisher_policy,
)
from offworld_kernel.policies.manifest import policy_source_bytes
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent


class Build5DecisionEpochTests(unittest.TestCase):
    def base(self, universe_id='RICH_PUBLIC_3', stock='20'):
        k,pub_snapshot,pub_request,manifest,obs,wip,draw,_=publication_handoff_kernel(
            universe_id,stock)

        stale_fin_snapshot,fin_request,table=financier_snapshot_after_publication(k,obs.id)

        k.add_system(SystemState(
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH','DECISION_ORCHESTRATION',set()))
        k.add_system(SystemState(
            'FINANCE_EXECUTOR_EPOCH','FINANCE_EXECUTION',
            {'accounts','commitments'}))

        holder={
            'pub_snapshot':pub_snapshot,
            'pub_request':pub_request,
            'manifest':manifest,
            'obs':obs,
            'wip':wip,
            'draw':draw,
            'stale_fin_snapshot':stale_fin_snapshot,
            'fin_request':fin_request,
            'table':table,
        }
        return k,holder

    def publication_epoch(self,k,h,epoch_id='EPOCH-1',chain_id='CHAIN-TEST-002B'):
        k.begin_decision_epoch(epoch_id,chain_id)

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
        snap_ref=k.scheduler.open_decision_window(snap.period_key,snap.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'epoch1-publication-decision',D('1'),Phase.DECISION_WINDOW,0,'PUB',
            'PUBLICATION_DECISION_ORCHESTRATOR',snapshot_ref=snap_ref))
        k.scheduler.schedule(ScheduledEvent(
            'epoch1-publication-transfer',D('2'),Phase.INFORMATION_UPDATE,0,'PUBINFO',
            'PUBLICATION_SYSTEM',parent_ids=('epoch1-publication-decision',)))

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
                2,'PUB',h['pub_request'].observation_id,h['pub_request'].audience,
                (('FIN','resource_exists',det,fp),))
            h['artifact']=a
            return '|'.join(('PUBLISHED',a.id,a.source_observation_id,a.signal))

        rt.register_policy_handler(
            'epoch1-publication-decision','PUB',snap,'PUB-EPOCH-KEY',policy)
        rt.register_handler('PUBLICATION_SYSTEM',publish)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h['epoch1_checks']=AccountingIdentityAuditor(k,before).check_all()
        h['epoch1_result']=result
        return result

    def financing_epoch(self,k,h,epoch_id='EPOCH-2'):
        fresh_snapshot,request,table=financier_snapshot_after_publication(k,h['obs'].id)
        h['fresh_fin_snapshot']=fresh_snapshot
        h['fin_request']=request
        h['table']=table

        k.begin_decision_epoch(epoch_id)

        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_EXECUTOR_EPOCH','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments'),('financing_decision',),
            ('accounts','commitments'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))

        snap_ref=k.scheduler.open_decision_window(fresh_snapshot.period_key,fresh_snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'epoch2-financier-decision',D('3'),Phase.DECISION_WINDOW,0,'FIN',
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH',snapshot_ref=snap_ref))
        k.scheduler.schedule(ScheduledEvent(
            'epoch2-finance-execute',D('4'),Phase.COMMITMENT_DISBURSEMENT,0,'FINANCE',
            'FINANCE_EXECUTOR_EPOCH',parent_ids=('epoch2-financier-decision',)))

        table_id=f'UNDERWRITING:{table.table_id}:{table.version}:{table.fingerprint()}'
        policy_id=(
            'POLICY:'+h['manifest'].policy_version_hash(policy_source_bytes())
            +':PARAMS:'+h['manifest'].parameter_manifest_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(table_id,),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_financier_policy(
                ctx.snapshot,request,h['manifest'],ctx.decision_key,
                allow_test_fixture=True)
            h['financier_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,r.policy_version))

        def execute(kernel,event):
            d=h['financier_policy'].decision
            if d.outcome==FinancingDecisionOutcome.APPROVE:
                kernel.add_commitment('C-EPOCH-2','FIN','P',d.amount)
                kernel.disburse(1,'C-EPOCH-2','fin_funds',d.amount)
                return 'FUNDED:'+str(d.amount)
            return 'NO_FUNDING:'+d.outcome.value

        rt.register_policy_handler(
            'epoch2-financier-decision','FIN',fresh_snapshot,'FIN-EPOCH-KEY',policy)
        rt.register_handler('FINANCE_EXECUTOR_EPOCH',execute)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h['epoch2_checks']=AccountingIdentityAuditor(k,before).check_all()
        h['epoch2_result']=result
        return result

    def full_chain(self,universe_id='RICH_PUBLIC_3',stock='20'):
        k,h=self.base(universe_id,stock)
        self.publication_epoch(k,h)
        self.financing_epoch(k,h)
        return k,h

    def test_two_epochs_share_one_persistent_kernel_and_fresh_information(self):
        k,h=self.full_chain()
        self.assertEqual(len(k.decision_epoch_records),2)
        self.assertEqual(k.decision_epoch_records[0].epoch_id,'EPOCH-1')
        self.assertEqual(k.decision_epoch_records[1].epoch_id,'EPOCH-2')
        self.assertEqual(
            k.decision_epoch_records[1].parent_result_fingerprint,
            h['epoch1_result'].result_fingerprint)
        self.assertIn(h['obs'].id,k.agents['FIN'].information)
        self.assertEqual(
            dict(h['fresh_fin_snapshot'].beliefs)['resource_exists'],D('0.5'))
        self.assertEqual(
            h['financier_policy'].decision.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('40'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('60'))
        self.assertFalse(k.strict_scheduled_execution)

    def test_epoch_records_pin_plan_state_execution_and_result_hashes(self):
        k,h=self.full_chain()
        for i,r in enumerate(k.decision_epoch_records,1):
            self.assertEqual(r.ordinal,i)
            self.assertRegex(r.plan_fingerprint,r'^[0-9a-f]{64}$')
            self.assertRegex(r.initial_fingerprint,r'^[0-9a-f]{64}$')
            self.assertRegex(r.final_fingerprint,r'^[0-9a-f]{64}$')
            self.assertRegex(r.execution_fingerprint,r'^[0-9a-f]{64}$')
            self.assertRegex(r.result_fingerprint,r'^[0-9a-f]{64}$')
        self.assertEqual(k.decision_epoch_records[0].parent_result_fingerprint,'')

    def test_direct_mutator_between_epochs_remains_blocked(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        with self.assertRaisesRegex(InvariantError,'decision-epoch chain'):
            k.add_commitment('ILLEGAL','FIN','P',D('1'))

    def test_raw_state_tamper_between_epochs_is_detected(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        k.state.accounts['fin_funds'].balance+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('EPOCH-2')

    def test_raw_state_tamper_after_epoch_open_is_detected_at_seal(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        fresh,_,_=financier_snapshot_after_publication(k,h['obs'].id)
        k.begin_decision_epoch('EPOCH-2')
        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        ref=k.scheduler.open_decision_window(fresh.period_key,fresh.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'epoch2-financier-decision',D('3'),Phase.DECISION_WINDOW,0,'FIN',
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH',snapshot_ref=ref))
        rt=ScheduledSimulationRuntime(k)
        rt.register_policy_handler(
            'epoch2-financier-decision','FIN',fresh,'KEY',lambda ctx:'NOOP')
        k.state.accounts['fin_funds'].balance+=D('1')
        with self.assertRaisesRegex(InvariantError,'persistent state changed before seal'):
            rt.seal()

    def test_stale_prepublication_snapshot_rejected_in_second_epoch(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        stale=h['stale_fin_snapshot']
        k.begin_decision_epoch('EPOCH-2')
        k.scheduler.register_coupling(CouplingSpec(
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        ref=k.scheduler.open_decision_window(stale.period_key,stale.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'epoch2-financier-decision',D('3'),Phase.DECISION_WINDOW,0,'FIN',
            'FINANCE_DECISION_ORCHESTRATOR_EPOCH',snapshot_ref=ref))
        rt=ScheduledSimulationRuntime(k)
        with self.assertRaisesRegex(InvariantError,'does not match current admitted agent-visible state'):
            rt.register_policy_handler(
                'epoch2-financier-decision','FIN',stale,'KEY',lambda ctx:'NOOP')

    def test_duplicate_epoch_id_and_chain_change_are_rejected(self):
        k,h=self.base()
        self.publication_epoch(k,h)
        with self.assertRaisesRegex(InvariantError,'duplicate decision epoch id'):
            k.begin_decision_epoch('EPOCH-1')
        with self.assertRaisesRegex(InvariantError,'chain id mismatch'):
            k.begin_decision_epoch('EPOCH-2','OTHER-CHAIN')

    def test_chain_replays_exactly(self):
        ak,ah=self.full_chain()
        bk,bh=self.full_chain()
        self.assertEqual(
            tuple(ak.decision_epoch_records),
            tuple(bk.decision_epoch_records))
        self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())
        self.assertEqual(
            ah['financier_policy'].decision,
            bh['financier_policy'].decision)

    def test_null_negative_chain_rejects_without_funding(self):
        k,h=self.full_chain('NULL_PUBLIC_1','0')
        self.assertEqual(
            h['financier_policy'].decision.outcome,FinancingDecisionOutcome.REJECT)
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('100'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(len(k.decision_epoch_records),2)


if __name__=='__main__':
    unittest.main()
