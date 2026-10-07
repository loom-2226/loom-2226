import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_surface_prospecting_fixture import (
    remote_snapshot_and_request,
    surface_prospecting_kernel,
    surface_snapshot_and_request,
)
from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    ExplorationDecisionOutcome,
    ExplorationReasonCode,
    Observation,
    RuntimeObjectClass,
)
from offworld_kernel.policy import FactState, SnapshotFact, build_decision_snapshot
from offworld_kernel.policy_runner import (
    public_explorer_contract_hash,
    public_explorer_policy_version,
    public_surface_prospector_contract_hash,
    public_surface_prospector_policy_version,
    run_hostile_access_probe,
    run_public_explorer_policy,
    run_public_surface_prospector_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent


class Build5SurfaceProspectingTests(unittest.TestCase):
    def remote_epoch(self,k,h,chain_id='CHAIN-SURFACE-007A'):
        snapshot,request=remote_snapshot_and_request(k,h['remote_cost'])
        h['remote_snapshot']=snapshot
        h['remote_request']=request

        k.begin_decision_epoch('EPOCH-1-REMOTE',chain_id)
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLIC_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLIC_FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments','resource_constraints'),('exploration_decision',),
            ('accounts','commitments','resource_constraints'),'EVENT',
            Phase.COMMITMENT_DISBURSEMENT))
        k.scheduler.register_coupling(CouplingSpec(
            'REMOTE_OBSERVATION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','assets','observations','agent_information','agent_beliefs',
             'earth_impact','resource_constraints','events'),
            ('exploration_decision','scenario_resource'),
            ('accounts','transactions','assets','observations','agent_information','agent_beliefs',
             'earth_impact','resource_constraints','events'),
            'EVENT',Phase.OPERATIONS,perspective='WORLD_SIM'))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'surface-e1-remote-decision',D('1'),Phase.DECISION_WINDOW,0,'PUB',
            'PUBLIC_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'surface-e1-remote-finance',D('1.01'),Phase.COMMITMENT_DISBURSEMENT,0,'PUB-FIN',
            'PUBLIC_FINANCE_EXECUTOR',parent_ids=('surface-e1-remote-decision',)))
        k.scheduler.schedule(ScheduledEvent(
            'surface-e1-remote-observation',D('1.02'),Phase.OPERATIONS,0,'PUB-REMOTE',
            'REMOTE_OBSERVATION_SYSTEM',
            parent_ids=('surface-e1-remote-decision','surface-e1-remote-finance')))

        policy_id=(
            'POLICY:'+public_explorer_policy_version()
            +':CONTRACT:'+public_explorer_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('NO_EXTERNAL_TABLES',),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_explorer_policy(ctx.snapshot,request,ctx.decision_key)
            h['remote_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,str(d.authorized_cost)))

        def finance(kernel,event):
            d=h['remote_policy'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_REMOTE_FINANCE:'+d.outcome.value
            kernel.add_commitment('C-PUB-REMOTE-007A','PUB','EXP',d.authorized_cost)
            kernel.disburse(1,'C-PUB-REMOTE-007A','public_funds',d.authorized_cost)
            kernel.reserve_earth_supply('EARTH:X',1,d.authorized_cost)
            return 'REMOTE_FUNDED:'+str(d.authorized_cost)

        def observe(kernel,event):
            d=h['remote_policy'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_REMOTE_OBSERVATION:'+d.outcome.value
            obs,asset,draw=kernel.explore_paid(
                1,'PUB','RES','EXP','earth_supplier',d.authorized_cost,
                'REMOTE',False,D('0.20'),D('0.20'))
            h['remote_observation']=obs
            h['remote_asset']=asset
            h['remote_draw']=draw
            return '|'.join(('REMOTE',obs.id,obs.signal,str(draw)))

        rt.register_policy_handler(
            'surface-e1-remote-decision','PUB',snapshot,'REMOTE-KEY-007A',policy)
        rt.register_handler('PUBLIC_FINANCE_EXECUTOR',finance)
        rt.register_handler('REMOTE_OBSERVATION_SYSTEM',observe)
        before=AccountingPeriodSnapshot.capture(k,1)
        rt.seal()
        result=rt.run()
        h['remote_result']=result
        h['remote_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def surface_epoch(self,k,h,cost_known=True):
        prior=h['remote_observation'].id
        snapshot,request=surface_snapshot_and_request(
            k,h['surface_cost'],prior,cost_known=cost_known)
        h['surface_snapshot']=snapshot
        h['surface_request']=request

        k.begin_decision_epoch('EPOCH-2-SURFACE')
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLIC_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLIC_FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments','resource_constraints'),('exploration_decision',),
            ('accounts','commitments','resource_constraints'),'EVENT',
            Phase.COMMITMENT_DISBURSEMENT))
        k.scheduler.register_coupling(CouplingSpec(
            'SURFACE_PROSPECTING_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','assets','observations','agent_information',
             'earth_impact','resource_constraints','events','surface_prospecting_records'),
            ('exploration_decision','scenario_resource','prior_remote_observation','surface_model'),
            ('accounts','transactions','assets','observations','agent_information',
             'earth_impact','resource_constraints','events','surface_prospecting_records'),
            'EVENT',Phase.OBSERVATION,perspective='WORLD_SIM'))
        k.scheduler.register_coupling(CouplingSpec(
            'SURFACE_INFORMATION_UPDATE_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('agent_beliefs','events','observation_belief_update_records'),
            ('surface_observation','agent_likelihood_model'),
            ('agent_beliefs','events','observation_belief_update_records'),
            'EVENT',Phase.INFORMATION_UPDATE,perspective='AGENT:PUB'))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'surface-e2-decision',D('2'),Phase.DECISION_WINDOW,0,'PUB',
            'PUBLIC_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'surface-e2-finance',D('2.01'),Phase.COMMITMENT_DISBURSEMENT,0,'PUB-FIN',
            'PUBLIC_FINANCE_EXECUTOR',parent_ids=('surface-e2-decision',)))
        k.scheduler.schedule(ScheduledEvent(
            'surface-e2-observation',D('2.02'),Phase.OBSERVATION,0,'SURFACE-OBS',
            'SURFACE_PROSPECTING_SYSTEM',
            parent_ids=('surface-e2-decision','surface-e2-finance')))
        k.scheduler.schedule(ScheduledEvent(
            'surface-e2-information-update',D('2.03'),Phase.INFORMATION_UPDATE,0,'SURFACE-INFO',
            'SURFACE_INFORMATION_UPDATE_SYSTEM',
            parent_ids=('surface-e2-observation',)))

        policy_id=(
            'POLICY:'+public_surface_prospector_policy_version()
            +':CONTRACT:'+public_surface_prospector_contract_hash())
        model_id='SURFACE_MODEL:'+h['model'].model_id+':'+h['model'].fingerprint()
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(model_id,),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_surface_prospector_policy(
                ctx.snapshot,request,ctx.decision_key)
            h['surface_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,str(d.authorized_cost)))

        def finance(kernel,event):
            d=h['surface_policy'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_SURFACE_FINANCE:'+d.outcome.value
            kernel.add_commitment('C-PUB-SURFACE-007A','PUB','EXP',d.authorized_cost)
            kernel.disburse(2,'C-PUB-SURFACE-007A','public_funds',d.authorized_cost)
            kernel.reserve_earth_supply('EARTH:X',2,d.authorized_cost)
            return 'SURFACE_FUNDED:'+str(d.authorized_cost)

        def observe(kernel,event):
            d=h['surface_policy'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_SURFACE_OBSERVATION:'+d.outcome.value
            obs,asset,draw,record=kernel.surface_prospect_paid(
                2,'PUB','RES','EXP','earth_supplier',d.authorized_cost,
                request.prerequisite_observation_id,h['model'],
                parent_ids=(d.id,))
            h['surface_observation']=obs
            h['surface_asset']=asset
            h['surface_draw']=draw
            h['surface_world_record']=record
            return '|'.join(('SURFACE',obs.id,obs.signal,str(draw)))

        def info(kernel,event):
            if 'surface_observation' not in h:
                return 'NO_SURFACE_INFORMATION_UPDATE'
            model=h['model']
            rec=kernel.update_agent_belief_from_observation(
                2,'PUB',h['surface_observation'].id,'RES',
                model.agent_detection_rate,model.agent_false_positive_rate,
                model.model_id,model.source_ref)
            h['surface_belief_update']=rec
            return '|'.join((
                'BELIEF_UPDATED',rec.observation_id,str(rec.prior),str(rec.posterior)))

        rt.register_policy_handler(
            'surface-e2-decision','PUB',snapshot,'SURFACE-KEY-007A',policy)
        rt.register_handler('PUBLIC_FINANCE_EXECUTOR',finance)
        rt.register_handler('SURFACE_PROSPECTING_SYSTEM',observe)
        rt.register_handler('SURFACE_INFORMATION_UPDATE_SYSTEM',info)
        before=AccountingPeriodSnapshot.capture(k,2)
        rt.seal()
        result=rt.run()
        h['surface_result']=result
        h['surface_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',balance='100',
                  surface_capability=True):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel(
            universe_id,stock,balance=balance,surface_capability=surface_capability)
        h={'model':model,'remote_cost':remote_cost,'surface_cost':surface_cost}
        self.remote_epoch(k,h)
        self.surface_epoch(k,h)
        return k,h

    def test_rich_surface_prospecting_confirms_and_sharpens_belief(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        self.assertEqual(h['remote_observation'].signal,'POSITIVE')
        self.assertEqual(h['surface_snapshot'].beliefs,(('RES',D('0.50')),))
        self.assertEqual(h['surface_observation'].signal,'POSITIVE')
        self.assertEqual(h['surface_belief_update'].prior,D('0.50'))
        self.assertEqual(h['surface_belief_update'].posterior,D('0.95'))
        self.assertEqual(k.agents['PUB'].beliefs['RES'],D('0.95'))
        self.assertEqual(k.resources['RES'].remaining,D('20'))
        self.assertEqual(k.state.accounts['public_funds'].balance,D('65'))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('35'))
        self.assertEqual(k.state.accounts['explore_cash'].balance,D('0'))
        self.assertEqual(len(k.decision_epoch_records),2)

    def test_in_situ_observation_precedes_unknown_recovery(self):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel('RICH_PUBLIC_3','20')
        resource=k.resources['RES']
        resource.accessible=resource.recoverable=resource.remaining=None
        h={'model':model,'remote_cost':remote_cost,'surface_cost':surface_cost}
        self.remote_epoch(k,h)
        self.assertEqual(h['remote_observation'].signal,'POSITIVE')
        self.surface_epoch(k,h)
        self.assertEqual(h['surface_observation'].signal,'POSITIVE')
        self.assertIsNone(resource.recoverable)
        self.assertIsNone(resource.remaining)
        self.assertIn(h['surface_observation'].id,k.agents['PUB'].information)
        self.assertFalse(any(v=='LEAK' for v in run_hostile_access_probe(h['surface_snapshot'])[0].values()))
        ek,_,_,_=surface_prospecting_kernel('RICH_PUBLIC_3','20')
        er=ek.resources['RES'];er.accessible=er.recoverable=er.remaining=None
        with self.assertRaisesRegex(InvariantError,'BLOCKED_UNKNOWN_RECOVERY'):
            ek.extract_bounded(1,'PUB','RES',D('1'))

    def test_null_remote_false_positive_is_corrected_by_surface_negative(self):
        k,h=self.full_case('NULL_SURFACE_1','0')
        self.assertLess(h['remote_draw'],D('0.20'))
        self.assertEqual(h['remote_observation'].signal,'POSITIVE')
        self.assertEqual(dict(h['surface_snapshot'].beliefs)['RES'],D('0.50'))
        self.assertGreaterEqual(h['surface_draw'],D('0.05'))
        self.assertEqual(h['surface_observation'].signal,'NEGATIVE')
        self.assertEqual(h['surface_belief_update'].prior,D('0.50'))
        self.assertEqual(h['surface_belief_update'].posterior,D('0.05'))
        self.assertEqual(k.agents['PUB'].beliefs['RES'],D('0.05'))
        self.assertEqual(k.resources['RES'].remaining,D('0'))

    def test_identical_remote_positive_state_gives_identical_surface_decision_before_truth_diverges(self):
        rk,rh=self.full_case('RICH_PUBLIC_3','20')
        nk,nh=self.full_case('NULL_SURFACE_1','0')
        self.assertEqual(rh['surface_snapshot'],nh['surface_snapshot'])
        self.assertEqual(rh['surface_request'],nh['surface_request'])
        self.assertEqual(rh['surface_policy'].decision,nh['surface_policy'].decision)
        self.assertEqual(rh['surface_policy'].worker_fingerprint,nh['surface_policy'].worker_fingerprint)
        self.assertNotEqual(rh['surface_observation'].signal,nh['surface_observation'].signal)
        self.assertNotEqual(rk.agents['PUB'].beliefs['RES'],nk.agents['PUB'].beliefs['RES'])

    def test_surface_model_is_structurally_higher_quality_than_remote_fixture(self):
        _,model,_,_=surface_prospecting_kernel()
        self.assertLess(model.world_false_positive,model.remote_world_false_positive_reference)
        self.assertLess(model.world_false_negative,model.remote_world_false_negative_reference)
        self.assertEqual(model.world_false_positive,D('0.05'))
        self.assertEqual(model.world_false_negative,D('0.05'))
        self.assertEqual(model.agent_detection_rate,D('0.95'))
        self.assertEqual(model.agent_false_positive_rate,D('0.05'))

    def test_surface_policy_requires_possessed_prior_observation(self):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel()
        snapshot=build_decision_snapshot(
            k,'PUB','SURFACE-PRE',D('1'),
            (SnapshotFact('exploration.SURFACE_COST',FactState.KNOWN,str(surface_cost),'TEST'),))
        request=build_exploration_request(
            'XREQ-NOT-POSSESSED',2,'EXP','RES','SURFACE',
            prerequisite_observation_id='OBS-NOT-POSSESSED')
        r=run_public_surface_prospector_policy(snapshot,request,'KEY')
        self.assertEqual(r.decision.outcome,ExplorationDecisionOutcome.DEFER)
        self.assertEqual(r.decision.reason_code,ExplorationReasonCode.DEFER_PREREQUISITE_OBSERVATION)

    def test_surface_unknown_cost_blocks_before_worker(self):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel()
        h={'model':model,'remote_cost':remote_cost,'surface_cost':surface_cost}
        self.remote_epoch(k,h)
        snapshot,request=surface_snapshot_and_request(
            k,surface_cost,h['remote_observation'].id,cost_known=False)
        r=run_public_surface_prospector_policy(snapshot,request,'KEY')
        self.assertEqual(r.decision.outcome,ExplorationDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('exploration.SURFACE_COST',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_surface_insufficient_budget_declines(self):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel(balance='30')
        h={'model':model,'remote_cost':remote_cost,'surface_cost':surface_cost}
        self.remote_epoch(k,h)
        snapshot,request=surface_snapshot_and_request(
            k,surface_cost,h['remote_observation'].id)
        r=run_public_surface_prospector_policy(snapshot,request,'KEY')
        self.assertEqual(snapshot.account_balance,D('20'))
        self.assertEqual(r.decision.outcome,ExplorationDecisionOutcome.DECLINE)
        self.assertEqual(r.decision.reason_code,ExplorationReasonCode.INSUFFICIENT_BUDGET)

    def test_missing_surface_capability_declines(self):
        k,model,remote_cost,surface_cost=surface_prospecting_kernel(surface_capability=False)
        h={'model':model,'remote_cost':remote_cost,'surface_cost':surface_cost}
        self.remote_epoch(k,h)
        snapshot,request=surface_snapshot_and_request(
            k,surface_cost,h['remote_observation'].id)
        r=run_public_surface_prospector_policy(snapshot,request,'KEY')
        self.assertEqual(r.decision.outcome,ExplorationDecisionOutcome.DECLINE)
        self.assertEqual(r.decision.reason_code,ExplorationReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_world_side_prerequisite_validation_rejects_wrong_channel_resource_or_possession(self):
        k,model,_,_=surface_prospecting_kernel()
        # No spending occurs because each case is rejected before exploration execution.
        k.observations['O-NOT-OWNED']=Observation('O-NOT-OWNED',1,'OTHER','RES','REMOTE','POSITIVE',False)
        with self.assertRaisesRegex(InvariantError,'not possessed'):
            k.surface_prospect_paid(2,'PUB','RES','EXP','earth_supplier',D('25'),'O-NOT-OWNED',model)

        k.observations['O-SURFACE']=Observation('O-SURFACE',1,'PUB','RES','SURFACE','POSITIVE',False)
        k.agents['PUB'].information.add('O-SURFACE')
        with self.assertRaisesRegex(InvariantError,'must be REMOTE'):
            k.surface_prospect_paid(2,'PUB','RES','EXP','earth_supplier',D('25'),'O-SURFACE',model)

        from offworld_kernel.mvp_state import ScenarioResource
        k.add_resource(ScenarioResource('OTHER','OFF:T1','RESOURCE_Y',D('1'),D('1'),D('1'),D('1')))
        k.observations['O-OTHER']=Observation('O-OTHER',1,'PUB','OTHER','REMOTE','POSITIVE',False)
        k.agents['PUB'].information.add('O-OTHER')
        with self.assertRaisesRegex(InvariantError,'resource mismatch'):
            k.surface_prospect_paid(2,'PUB','RES','EXP','earth_supplier',D('25'),'O-OTHER',model)

    def test_world_draw_and_world_likelihoods_do_not_enter_surface_snapshot(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        snap=h['surface_snapshot']
        self.assertFalse(hasattr(snap,'world_false_positive'))
        self.assertFalse(hasattr(snap,'world_false_negative'))
        self.assertFalse(hasattr(snap,'deterministic_draw'))
        probe,_=run_hostile_access_probe(snap)
        self.assertEqual({k:v for k,v in probe.items() if v=='LEAK'},{})

    def test_belief_update_uses_observation_not_hidden_resource(self):
        rk,rh=self.full_case('RICH_PUBLIC_3','20')
        # A positive SURFACE signal with the same prior/model produces the same posterior
        # even when evaluated on a separate NULL kernel; hidden truth is not an input.
        nk,model,_,_=surface_prospecting_kernel('NULL_PUBLIC_1','0')
        nk.observations['SAME-SIGNAL']=Observation(
            'SAME-SIGNAL',2,'PUB','RES','SURFACE','POSITIVE',False)
        nk.agents['PUB'].information.add('SAME-SIGNAL')
        nk.agents['PUB'].beliefs['RES']=D('0.50')
        rec=nk.update_agent_belief_from_observation(
            2,'PUB','SAME-SIGNAL','RES',
            model.agent_detection_rate,model.agent_false_positive_rate,
            model.model_id,model.source_ref)
        self.assertEqual(rec.posterior,rh['surface_belief_update'].posterior)
        self.assertEqual(rec.posterior,D('0.95'))

    def test_surface_expenditure_and_information_leave_physical_resource_unchanged_and_accounting_balanced(self):
        for uid,stock in (('RICH_PUBLIC_3','20'),('NULL_SURFACE_1','0')):
            k,h=self.full_case(uid,stock)
            self.assertEqual(k.resources['RES'].remaining,D(stock))
            self.assertEqual(
                tuple(sorted(h['surface_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))
            self.assertEqual(
                tuple(sorted(h['remote_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_surface_world_and_agent_records_keep_parameter_lineages_separate(self):
        k,h=self.full_case()
        world=h['surface_world_record']
        belief=h['surface_belief_update']
        self.assertEqual(world.world_model_id,h['model'].model_id)
        self.assertEqual(world.world_false_positive,D('0.05'))
        self.assertEqual(world.world_false_negative,D('0.05'))
        self.assertEqual(belief.detection_rate,D('0.95'))
        self.assertEqual(belief.false_positive_rate,D('0.05'))
        self.assertEqual(belief.model_id,h['model'].model_id)
        self.assertEqual(world.observation_id,belief.observation_id)
        self.assertNotIn(str(world.deterministic_draw),dict(h['surface_snapshot'].beliefs).keys())

    def test_surface_chain_replays_exactly(self):
        for uid,stock in (('RICH_PUBLIC_3','20'),('NULL_SURFACE_1','0')):
            ak,ah=self.full_case(uid,stock)
            bk,bh=self.full_case(uid,stock)
            self.assertEqual(tuple(ak.decision_epoch_records),tuple(bk.decision_epoch_records))
            self.assertEqual(ah['remote_policy'].decision,bh['remote_policy'].decision)
            self.assertEqual(ah['surface_policy'].decision,bh['surface_policy'].decision)
            self.assertEqual(ah['surface_world_record'],bh['surface_world_record'])
            self.assertEqual(ah['surface_belief_update'],bh['surface_belief_update'])
            self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
