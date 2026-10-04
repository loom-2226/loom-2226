import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_project_lifecycle_fixture import project_lifecycle_kernel
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import AssetKind
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.project_lifecycle import (
    DevelopmentResolutionOutcome,
    DevelopmentStageOutcome,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from tests.test_build5_sponsor_operator import Build5SponsorOperatorTests


class Build5ProjectLifecycleTests(unittest.TestCase):
    def reach_development(self,universe_id='RICH_PUBLIC_3',stock='20',
                          year7_earth_ceiling='100'):
        k,h=project_lifecycle_kernel(
            universe_id,stock,year7_earth_ceiling=year7_earth_ceiling)
        helper=Build5SponsorOperatorTests()
        helper.publication_epoch(k,h,chain_id='CHAIN-LIFECYCLE-006A')
        helper.sponsor_epoch(
            k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-006A-FINANCE',3)
        helper.finance_epoch(k,h)
        helper.sponsor_epoch(
            k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-006A-DEVELOP',5)
        self.assertEqual(k.state.projects['P'].status,'DEVELOPMENT')
        return k,h

    def lifecycle_epoch(self,k,h,epoch_id='EPOCH-5-CONSTRUCTION'):
        plan=h['development_plan']
        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            'CONSTRUCTION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','wip','fcf','earth_impact','resource_constraints','events'),
            ('project_state','development_plan','accounts','resource_constraints'),
            ('accounts','transactions','wip','fcf','earth_impact','resource_constraints','events'),
            'DECLARED_STAGE',Phase.OPERATIONS))
        k.scheduler.register_coupling(CouplingSpec(
            'DEVELOPMENT_RESOLUTION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('project_state','wip','assets','events'),
            ('development_plan','development_stage_records','wip'),
            ('project_state','wip','assets','events'),
            'DECLARED_COMPLETION',Phase.OPERATIONS))

        for year in (6,7):
            k.scheduler.schedule(ScheduledEvent(
                f'construct-y{year}',D(year),Phase.OPERATIONS,0,
                f'construct-y{year}','CONSTRUCTION_SYSTEM',
                payload=(('plan_id',plan.id),)))
        k.scheduler.schedule(ScheduledEvent(
            'development-resolution-y8',D('8'),Phase.OPERATIONS,0,
            'development-resolution-y8','DEVELOPMENT_RESOLUTION_SYSTEM',
            payload=(('plan_id',plan.id),),
            parent_ids=('construct-y6','construct-y7')))

        plan_manifest=(
            'DEVELOPMENT_PLAN:'+plan.id+':'+plan.plan_version+':'+plan.source_ref)
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(plan_manifest,),policy_manifest_ids=('NO_POLICY_THIS_EPOCH',))
        rt=ScheduledSimulationRuntime(k,prov)
        h['stage_records']=[]

        def construct(kernel,event):
            r=kernel.execute_development_stage(
                int(event.effective_time),dict(event.payload)['plan_id'])
            h['stage_records'].append(r)
            return '|'.join((
                r.plan_id,str(r.year),r.outcome.value,str(r.planned_amount),
                r.reason,r.transaction_id))

        def resolve(kernel,event):
            r=kernel.resolve_development_plan(
                int(event.effective_time),dict(event.payload)['plan_id'])
            h['resolution']=r
            return '|'.join((
                r.plan_id,r.outcome.value,str(r.accumulated_cost),
                str(r.commissioned),str(r.written_off),r.asset_id,r.reason))

        rt.register_handler('CONSTRUCTION_SYSTEM',construct)
        rt.register_handler('DEVELOPMENT_RESOLUTION_SYSTEM',resolve)
        before=AccountingPeriodSnapshot.capture(k,6)
        rt.seal()
        result=rt.run()
        h['lifecycle_result']=result
        h['lifecycle_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def success_chain(self,universe_id='RICH_PUBLIC_3',stock='20'):
        k,h=self.reach_development(universe_id,stock,'100')
        self.lifecycle_epoch(k,h)
        return k,h

    def failure_chain(self):
        # Year-7 Earth ceiling is 20, below the declared indivisible stage of 30.
        k,h=self.reach_development('RICH_PUBLIC_3','20','20')
        self.lifecycle_epoch(k,h)
        return k,h

    def test_successful_staged_construction_reaches_operating(self):
        k,h=self.success_chain()
        self.assertEqual(
            [r.outcome for r in h['stage_records']],
            [DevelopmentStageOutcome.SPENT,DevelopmentStageOutcome.SPENT])
        self.assertEqual([r.planned_amount for r in h['stage_records']],[D('30'),D('30')])
        w=k.wip['WIP-P']
        self.assertEqual(w.accumulated_cost,D('60'))
        self.assertEqual(w.commissioned,D('60'))
        self.assertEqual(w.written_off,D('0'))
        self.assertEqual(w.remaining_wip,D('0'))
        self.assertEqual(h['resolution'].outcome,DevelopmentResolutionOutcome.OPERATING)
        self.assertEqual(k.state.projects['P'].status,'OPERATING')
        a=k.state.assets['MINE-P']
        self.assertEqual(a.kind,AssetKind.PRODUCTIVE)
        self.assertEqual(a.book_value,D('60'))
        self.assertEqual(a.capacity,D('10'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(len(k.decision_epoch_records),5)

    def test_failed_incomplete_construction_writes_off_wip(self):
        k,h=self.failure_chain()
        self.assertEqual(h['stage_records'][0].outcome,DevelopmentStageOutcome.SPENT)
        self.assertEqual(h['stage_records'][1].outcome,DevelopmentStageOutcome.BLOCKED_SUPPLY)
        self.assertEqual(h['stage_records'][1].reason,'EARTH_RESOURCE_ALLOCATION_CAPACITY')
        w=k.wip['WIP-P']
        self.assertEqual(w.accumulated_cost,D('30'))
        self.assertEqual(w.commissioned,D('0'))
        self.assertEqual(w.written_off,D('30'))
        self.assertEqual(w.remaining_wip,D('0'))
        self.assertEqual(h['resolution'].outcome,DevelopmentResolutionOutcome.FAILED)
        self.assertEqual(k.state.projects['P'].status,'FAILED')
        self.assertNotIn('MINE-P',k.state.assets)
        self.assertEqual(k.state.accounts['project_cash'].balance,D('30'))
        self.assertEqual(len(k.decision_epoch_records),5)

    def test_successful_construction_uses_actual_earth_financing_origin(self):
        k,h=self.success_chain()
        fcf=[e for e in k.state.fcf_events if e.project_id=='P' and e.asset_id=='WIP-P']
        self.assertEqual(len(fcf),2)
        self.assertEqual([e.amount for e in fcf],[D('30'),D('30')])
        self.assertEqual([e.year for e in fcf],[6,7])
        self.assertTrue(all(e.financing_origin_nodes==('EARTH:X',) for e in fcf))
        self.assertTrue(all(e.supplier_node=='EARTH:X' for e in fcf))
        self.assertTrue(all(e.asset_node=='OFF:T1' for e in fcf))

    def test_stage_and_resolution_lineage_reaches_sponsor_develop_decision(self):
        k,h=self.success_chain()
        sponsor_decision=h['EPOCH-4-SPONSOR-DEVELOP_policy'].decision.id
        develop_event=next(
            e for e in k.events
            if e.action.value=='DEVELOP' and e.result=='DEVELOPMENT' and 'P' in e.inputs)
        self.assertIn(sponsor_decision,develop_event.parent_ids)
        stage_events=[e for e in k.events if e.action.value=='CONSTRUCT' and e.result=='SPENT']
        self.assertEqual(len(stage_events),2)
        self.assertTrue(all(develop_event.id in e.parent_ids for e in stage_events))
        resolution_event=next(
            e for e in k.events
            if e.actor=='DEVELOPMENT_RESOLUTION_SYSTEM' and e.result=='OPERATING')
        self.assertTrue(all(r.event_id in resolution_event.parent_ids for r in h['stage_records']))

    def test_construction_does_not_query_hidden_resource_truth(self):
        rk,rh=self.success_chain('RICH_PUBLIC_3','20')
        nk,nh=self.success_chain('NULL_FP_1','0')
        self.assertEqual(rh['obs'].signal,'POSITIVE')
        self.assertEqual(nh['obs'].signal,'POSITIVE')
        self.assertEqual(rh['stage_records'],nh['stage_records'])
        self.assertEqual(rh['resolution'],nh['resolution'])
        self.assertEqual(rk.state.projects['P'].status,'OPERATING')
        self.assertEqual(nk.state.projects['P'].status,'OPERATING')
        self.assertEqual(rk.resources['RES'].remaining,D('20'))
        self.assertEqual(nk.resources['RES'].remaining,D('0'))
        self.assertEqual(rk.state.assets['MINE-P'].book_value,nk.state.assets['MINE-P'].book_value)

    def test_operating_requires_full_declared_cost_not_merely_some_wip(self):
        k,h=self.failure_chain()
        self.assertEqual(k.wip['WIP-P'].accumulated_cost,D('30'))
        self.assertEqual(k.state.projects['P'].status,'FAILED')
        self.assertNotIn('MINE-P',k.state.assets)

    def test_stage_is_indivisible_and_never_overspends_supply_ceiling(self):
        k,h=self.failure_chain()
        c=k.resource_constraints[('EARTH:X',7)]
        self.assertEqual(c.ceiling,D('20'))
        self.assertEqual(c.reserved,D('0'))
        self.assertEqual(c.spent,D('0'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('30'))

    def test_all_lifecycle_accounting_identities_pass(self):
        for builder in (self.success_chain,self.failure_chain):
            k,h=builder()
            self.assertEqual(
                tuple(sorted(h['lifecycle_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_wip_writeoff_is_value_loss_not_reverse_cash(self):
        k,h=self.failure_chain()
        capex=[t for t in k.state.transactions if t.purpose.value=='CAPEX']
        self.assertEqual(sum((t.amount for t in capex),D('0')),D('30'))
        self.assertFalse(any(
            t.source_account=='earth_supplier' and t.destination_account=='project_cash'
            for t in k.state.transactions))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('40'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('30'))

    def test_direct_lifecycle_mutation_between_epochs_is_blocked(self):
        k,h=self.reach_development()
        with self.assertRaisesRegex(InvariantError,'decision-epoch chain'):
            k.execute_development_stage(6,h['development_plan'].id)

    def test_raw_plan_or_wip_tamper_is_detected(self):
        k,h=self.reach_development()
        plan=h['development_plan']
        # Replacing a frozen plan object behind the governance layer is raw tampering.
        from dataclasses import replace
        k.development_plans[plan.id]=replace(plan,required_cost=D('61'))
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-PLAN')

        k,h=self.success_chain()
        # Completed chains are also guarded. Raw WIP edits invalidate the boundary.
        k.wip['WIP-P'].written_off=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-WIP')

    def test_success_and_failure_chains_replay_exactly(self):
        for builder in (self.success_chain,self.failure_chain):
            ak,ah=builder()
            bk,bh=builder()
            self.assertEqual(tuple(ak.decision_epoch_records),tuple(bk.decision_epoch_records))
            self.assertEqual(ah['stage_records'],bh['stage_records'])
            self.assertEqual(ah['resolution'],bh['resolution'])
            self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
