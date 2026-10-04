import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_operating_extraction_fixture import (
    operating_extraction_kernel,
    operating_request,
    operating_snapshot,
)
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.kernel import InvariantError
from offworld_kernel.mvp_state import (
    FinancingDecisionOutcome,
    OperatingCycleDecision,
    OperatingCycleDecisionOutcome,
    OperatingCycleReasonCode,
    RuntimeObjectClass,
)
from offworld_kernel.policy import build_decision_snapshot
from offworld_kernel.model import Asset, AssetKind
from offworld_kernel.policy_runner import (
    run_financier_policy,
    run_hostile_access_probe,
    run_sponsor_operating_policy,
    sponsor_operating_contract_hash,
    sponsor_operating_policy_version,
)
from offworld_kernel.policies.manifest import policy_source_bytes
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.underwriting import underwriting_snapshot_facts
from tests import test_build5_sponsor_operator as sponsor_tests
from tests import test_build5_project_lifecycle as lifecycle_tests


class Build5OperatingExtractionTests(unittest.TestCase):
    def synthetic_operate_decision(self,request,quantity='5',opex='20'):
        return OperatingCycleDecision(
            'ODEC-SYNTHETIC-HOSTILE',request.id,'SPN',
            OperatingCycleDecisionOutcome.OPERATE,D('0'),D(quantity),D(opex),
            'hostile boundary fixture',OperatingCycleReasonCode.OPERATING_CYCLE_AUTHORIZED,
            (), 'decision-snapshot:HOSTILE:fixture','HOSTILE_POLICY_V1'
        ).validate_protocol(request)

    def reach_operating(self,universe_id='RICH_PUBLIC_3',stock='20',
                        sponsor_capabilities=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT')):
        k,h=operating_extraction_kernel(
            universe_id,stock,sponsor_capabilities=sponsor_capabilities)
        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-OPERATING-008A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-008A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-008A-DEVELOP',5)
        l=lifecycle_tests.Build5ProjectLifecycleTests()
        l.lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')
        self.assertEqual(k.state.projects['P'].status,'OPERATING')
        self.assertEqual(k.state.assets['MINE-P'].capacity,D('5'))
        return k,h

    def operating_request_epoch(self,k,h,opex_unknown=False,
                                epoch_id='EPOCH-6-OPERATING-FINANCE-REQUEST'):
        snapshot=operating_snapshot(
            k,h['operating_table'],epoch_id,'9',opex_unknown=opex_unknown)
        request=operating_request(h['obs'].id,'OPREQ-008A-FINANCE',9)
        h['operating_request_snapshot']=snapshot
        h['operating_request']=request

        k.begin_decision_epoch(epoch_id)
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_ACTION_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('financing_requests','events'),('operating_decision',),
            ('financing_requests','events'),'EVENT',Phase.ACTION_VALIDATION))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'operating-e6-decision',D('9'),Phase.DECISION_WINDOW,0,'SPN',
            'OPERATING_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'operating-e6-action',D('9'),Phase.ACTION_VALIDATION,0,'SPN-OPERATING',
            'OPERATING_ACTION_EXECUTOR',parent_ids=('operating-e6-decision',)))

        policy_id=(
            'POLICY:'+sponsor_operating_policy_version()
            +':CONTRACT:'+sponsor_operating_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_operating_policy(ctx.snapshot,request,ctx.decision_key)
            h['operating_request_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.requested_financing),str(d.planned_quantity),str(d.authorized_opex)))

        def action(kernel,event):
            d=h['operating_request_policy'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.REQUEST_FINANCE:
                return 'NO_OPERATING_FINANCE_REQUEST:'+d.outcome.value
            q=build_financing_request(
                'FINREQ-008A-OPERATING',9,'SPN','P',d.requested_financing,
                'OPERATING',(request.observation_id,))
            kernel.submit_financing_request(q,parent_ids=(d.id,))
            h['operating_financing_request']=q
            return 'OPERATING_FINANCE_REQUESTED:'+str(q.amount)

        rt.register_policy_handler(
            'operating-e6-decision','SPN',snapshot,'OPERATING-REQUEST-KEY-008A',policy)
        rt.register_handler('OPERATING_ACTION_EXECUTOR',action)
        before=AccountingPeriodSnapshot.capture(k,9)
        rt.seal()
        result=rt.run()
        h['operating_request_result']=result
        h['operating_request_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def operating_finance_epoch(self,k,h):
        q=h['operating_financing_request']
        facts=underwriting_snapshot_facts(
            h['operating_table'],'GENERIC_RESOURCE_PROJECT_MVP',9)
        snapshot=build_decision_snapshot(k,'FIN','OPERATING-FINANCE-9',D('9'),facts)
        h['operating_financier_snapshot']=snapshot

        k.begin_decision_epoch('EPOCH-7-OPERATING-FINANCE')
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_FINANCE_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'OPERATING_FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
            ('accounts','commitments'),('financing_decision',),
            ('accounts','commitments'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'operating-e7-finance-decision',D('9'),Phase.DECISION_WINDOW,0,'FIN',
            'OPERATING_FINANCE_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'operating-e7-finance-execute',D('9'),Phase.COMMITMENT_DISBURSEMENT,0,'FINANCE',
            'OPERATING_FINANCE_EXECUTOR',parent_ids=('operating-e7-finance-decision',)))

        policy_id=(
            'POLICY:'+h['manifest'].policy_version_hash(policy_source_bytes())
            +':PARAMS:'+h['manifest'].parameter_manifest_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_financier_policy(
                ctx.snapshot,q,h['manifest'],ctx.decision_key,
                allow_test_fixture=True)
            h['operating_financier_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,str(d.amount)))

        def execute(kernel,event):
            d=h['operating_financier_policy'].decision
            if d.outcome!=FinancingDecisionOutcome.APPROVE:
                return 'NO_OPERATING_FUNDING:'+d.outcome.value
            kernel.add_commitment('C-OPERATING-008A','FIN','P',d.amount)
            kernel.disburse(9,'C-OPERATING-008A','fin_funds',d.amount)
            return 'OPERATING_FUNDED:'+str(d.amount)

        rt.register_policy_handler(
            'operating-e7-finance-decision','FIN',snapshot,'OPERATING-FINANCE-KEY-008A',policy)
        rt.register_handler('OPERATING_FINANCE_EXECUTOR',execute)
        before=AccountingPeriodSnapshot.capture(k,9)
        rt.seal()
        result=rt.run()
        h['operating_finance_result']=result
        h['operating_finance_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def operate_epoch(self,k,h):
        snapshot=operating_snapshot(k,h['operating_table'],'OPERATE-9','9')
        request=operating_request(h['obs'].id,'OPREQ-008A-RUN',9)
        h['operate_snapshot']=snapshot
        h['operate_request']=request

        k.begin_decision_epoch('EPOCH-8-OPERATE-EXTRACT')
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
        k.scheduler.schedule(ScheduledEvent(
            'operating-e8-decision',D('9'),Phase.DECISION_WINDOW,0,'SPN',
            'OPERATING_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'operating-e8-opex',D('9'),Phase.OPERATIONS,0,'OPEX',
            'OPERATING_COST_SYSTEM',parent_ids=('operating-e8-decision',)))
        k.scheduler.schedule(ScheduledEvent(
            'operating-e8-extract',D('9'),Phase.OPERATIONS,1,'EXTRACT',
            'EXTRACTION_RESOLUTION_SYSTEM',
            parent_ids=('operating-e8-decision','operating-e8-opex')))

        policy_id=(
            'POLICY:'+sponsor_operating_policy_version()
            +':CONTRACT:'+sponsor_operating_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('OPERATING_TABLE:'+h['operating_table'].fingerprint(),),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_sponsor_operating_policy(ctx.snapshot,request,ctx.decision_key)
            h['operate_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.planned_quantity),str(d.authorized_opex)))

        def opex(kernel,event):
            d=h['operate_policy'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.OPERATE:
                return 'NO_OPERATING_COST:'+d.outcome.value
            unit=h['operating_table'].get(
                'GENERIC_RESOURCE_PROJECT_MVP',
                __import__('offworld_kernel.underwriting',fromlist=['UnderwritingInputKind']).UnderwritingInputKind.OPERATING_COST
            ).value
            rec=kernel.spend_operating_cycle(
                9,'SPN',request,d,'earth_supplier',unit)
            h['operating_cost_record']=rec
            return '|'.join(('OPEX_SPENT',rec.transaction_id,str(rec.total_opex)))

        def extract(kernel,event):
            d=h['operate_policy'].decision
            if d.outcome!=OperatingCycleDecisionOutcome.OPERATE:
                return 'NO_EXTRACTION:'+d.outcome.value
            rec=kernel.resolve_operating_extraction(
                9,'SPN',request,d,h['operating_cost_record'])
            h['extraction_record']=rec
            return '|'.join((
                'EXTRACTION_RESOLVED',str(rec.planned_quantity),
                str(rec.actual_extracted),rec.extraction_event_id))

        rt.register_policy_handler(
            'operating-e8-decision','SPN',snapshot,'OPERATE-KEY-008A',policy)
        rt.register_handler('OPERATING_COST_SYSTEM',opex)
        rt.register_handler('EXTRACTION_RESOLUTION_SYSTEM',extract)
        before=AccountingPeriodSnapshot.capture(k,9)
        rt.seal()
        result=rt.run()
        h['operate_result']=result
        h['operate_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',
                  sponsor_capabilities=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT')):
        k,h=self.reach_operating(universe_id,stock,sponsor_capabilities)
        self.operating_request_epoch(k,h)
        self.operating_finance_epoch(k,h)
        self.operate_epoch(k,h)
        return k,h

    def test_rich_full_output(self):
        k,h=self.full_case('RICH_PUBLIC_3','20')
        self.assertEqual(h['operating_request_policy'].decision.outcome,
                         OperatingCycleDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(h['operating_request_policy'].decision.requested_financing,D('20'))
        self.assertEqual(h['operating_financier_policy'].decision.outcome,
                         FinancingDecisionOutcome.APPROVE)
        self.assertEqual(h['operate_policy'].decision.outcome,
                         OperatingCycleDecisionOutcome.OPERATE)
        self.assertEqual(h['operate_policy'].decision.planned_quantity,D('5'))
        self.assertEqual(h['operate_policy'].decision.authorized_opex,D('20'))
        r=h['extraction_record']
        self.assertEqual(r.actual_extracted,D('5'))
        self.assertEqual(r.resource_before,D('20'))
        self.assertEqual(r.resource_after,D('15'))
        self.assertEqual(r.inventory_before,D('0'))
        self.assertEqual(r.inventory_after,D('5'))
        self.assertEqual(k.resources['RES'].remaining,D('15'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('5'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('20'))
        self.assertEqual(len(k.decision_epoch_records),8)

    def test_sparse_underproduction_is_bounded_by_actual_resource(self):
        k,h=self.full_case('SPARSE_PUBLIC_1','3')
        r=h['extraction_record']
        self.assertEqual(h['operate_policy'].decision.planned_quantity,D('5'))
        self.assertEqual(r.actual_extracted,D('3'))
        self.assertEqual(r.resource_after,D('0'))
        self.assertEqual(r.inventory_after,D('3'))
        event=next(e for e in k.events if e.id==r.extraction_event_id)
        self.assertEqual(event.result,'PARTIAL_OUTPUT')

    def test_null_false_positive_spends_opex_and_recovers_zero(self):
        k,h=self.full_case('NULL_FP_1','0')
        r=h['extraction_record']
        self.assertEqual(h['operate_policy'].decision.outcome,
                         OperatingCycleDecisionOutcome.OPERATE)
        self.assertEqual(h['operating_cost_record'].total_opex,D('20'))
        self.assertEqual(r.actual_extracted,D('0'))
        self.assertEqual(r.resource_after,D('0'))
        self.assertEqual(r.inventory_after,D('0'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('90'))
        event=next(e for e in k.events if e.id==r.extraction_event_id)
        self.assertEqual(event.result,'ZERO_OUTPUT')

    def test_hidden_worlds_share_operating_and_finance_decisions_before_extraction(self):
        cases=[
            self.full_case('RICH_PUBLIC_3','20'),
            self.full_case('SPARSE_PUBLIC_1','3'),
            self.full_case('NULL_FP_1','0'),
        ]
        first=cases[0][1]
        for _,h in cases[1:]:
            self.assertEqual(first['operating_request_snapshot'],h['operating_request_snapshot'])
            self.assertEqual(first['operating_request_policy'].decision,h['operating_request_policy'].decision)
            self.assertEqual(first['operating_financing_request'],h['operating_financing_request'])
            self.assertEqual(first['operating_financier_snapshot'],h['operating_financier_snapshot'])
            self.assertEqual(first['operating_financier_policy'].decision,h['operating_financier_policy'].decision)
            self.assertEqual(first['operate_snapshot'],h['operate_snapshot'])
            self.assertEqual(first['operate_policy'].decision,h['operate_policy'].decision)
        self.assertEqual([h['extraction_record'].actual_extracted for _,h in cases],
                         [D('5'),D('3'),D('0')])

    def test_non_operating_project_cannot_execute_cycle(self):
        k,h=operating_extraction_kernel(
            'RICH_PUBLIC_3','20',
            sponsor_capabilities=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT'))
        req=operating_request(h['obs'].id,'OPREQ-HOSTILE-NONOPERATING',9)
        d=self.synthetic_operate_decision(req)
        with self.assertRaisesRegex(InvariantError,'requires OPERATING project'):
            k.spend_operating_cycle(9,'SPN',req,d,'earth_supplier',D('4'))
        self.assertEqual(k.state.projects['P'].status,'PROPOSED')
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))

    def test_wrong_productive_asset_is_rejected_before_spend(self):
        k,h=operating_extraction_kernel(
            'RICH_PUBLIC_3','20',
            sponsor_capabilities=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT'))
        k.state.projects['P'].status='OPERATING'
        k.state.accounts['project_cash'].balance=D('20')
        k.state.assets['MINE-P']=Asset(
            'MINE-P','WRONG-PROJECT','OFF:T1',AssetKind.PRODUCTIVE,D('60'),D('5'))
        req=operating_request(h['obs'].id,'OPREQ-HOSTILE-ASSET',9)
        d=self.synthetic_operate_decision(req)
        with self.assertRaisesRegex(InvariantError,'operating asset/project mismatch'):
            k.spend_operating_cycle(9,'SPN',req,d,'earth_supplier',D('4'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('20'))

    def test_forged_plan_above_productive_capacity_is_rejected(self):
        k,h=operating_extraction_kernel(
            'RICH_PUBLIC_3','20',
            sponsor_capabilities=('REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT'))
        k.state.projects['P'].status='OPERATING'
        k.state.accounts['project_cash'].balance=D('24')
        k.state.assets['MINE-P']=Asset(
            'MINE-P','P','OFF:T1',AssetKind.PRODUCTIVE,D('60'),D('5'))
        req=operating_request(h['obs'].id,'OPREQ-HOSTILE-CAPACITY',9)
        d=self.synthetic_operate_decision(req,quantity='6',opex='24')
        with self.assertRaisesRegex(InvariantError,'exceeds productive capacity'):
            k.spend_operating_cycle(9,'SPN',req,d,'earth_supplier',D('4'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('24'))

    def test_operating_policy_decision_alone_does_not_mutate_world(self):
        k,h=self.reach_operating()
        snap=operating_snapshot(k,h['operating_table'],'NO-MUTATE','9')
        req=operating_request(h['obs'].id,'OPREQ-NOMUTATE',9)
        cash=k.state.accounts['project_cash'].balance
        remaining=k.resources['RES'].remaining
        result=run_sponsor_operating_policy(snap,req,'NO-MUTATE')
        self.assertEqual(result.decision.outcome,OperatingCycleDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(k.state.accounts['project_cash'].balance,cash)
        self.assertEqual(k.resources['RES'].remaining,remaining)
        self.assertNotIn('FINREQ-008A-OPERATING',k.financing_requests)

    def test_unknown_operating_cost_blocks_before_worker(self):
        k,h=self.reach_operating()
        snap=operating_snapshot(k,h['operating_table'],'UNKNOWN-OPEX','9',opex_unknown=True)
        req=operating_request(h['obs'].id,'OPREQ-UNKNOWN',9)
        result=run_sponsor_operating_policy(snap,req,'UNKNOWN')
        self.assertEqual(result.decision.outcome,OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(result.decision.reason_code,
                         OperatingCycleReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN)
        self.assertEqual(result.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
        self.assertEqual(result.decision.unknown_input_keys,('underwriting.OPERATING_COST',))

    def test_missing_operating_capabilities_prevents_operation(self):
        k,h=self.reach_operating(
            sponsor_capabilities=('REQUEST_FINANCE','DEVELOP'))
        # Give project enough operating cash without entering another epoch.
        # This occurs before any operating decision epoch starts.
        k.state.accounts['project_cash'].balance=D('20')
        snap=operating_snapshot(k,h['operating_table'],'NO-CAP','9')
        req=operating_request(h['obs'].id,'OPREQ-NOCAP',9)
        result=run_sponsor_operating_policy(snap,req,'NO-CAP')
        self.assertEqual(result.decision.outcome,OperatingCycleDecisionOutcome.DEFER)
        self.assertEqual(result.decision.reason_code,
                         OperatingCycleReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_nonpositive_belief_defers_operation(self):
        k,h=self.reach_operating()
        k.agents['SPN'].beliefs['resource_exists']=k.agents['SPN'].priors['resource_exists']
        snap=operating_snapshot(k,h['operating_table'],'NO-EVIDENCE','9')
        req=operating_request(h['obs'].id,'OPREQ-NOEVIDENCE',9)
        result=run_sponsor_operating_policy(snap,req,'NO-EVIDENCE')
        self.assertEqual(result.decision.outcome,OperatingCycleDecisionOutcome.DEFER)
        self.assertEqual(result.decision.reason_code,
                         OperatingCycleReasonCode.NONPOSITIVE_EVIDENCE)

    def test_policy_hostile_probe_has_no_hidden_world_access(self):
        k,h=self.reach_operating()
        snap=operating_snapshot(k,h['operating_table'],'HOSTILE','9')
        result,_=run_hostile_access_probe(snap)
        self.assertEqual({k:v for k,v in result.items() if v=='LEAK'},{})

    def test_opex_is_double_sided_and_extraction_creates_no_revenue(self):
        k,h=self.full_case()
        rec=h['operating_cost_record']
        tx=next(t for t in k.state.transactions if t.id==rec.transaction_id)
        self.assertEqual(tx.purpose.value,'OPEX')
        self.assertEqual(tx.source_account,'project_cash')
        self.assertEqual(tx.destination_account,'earth_supplier')
        self.assertEqual(tx.amount,D('20'))
        post_operating_revenue=[
            t for t in k.state.transactions
            if t.purpose.value=='REVENUE' and t.year==9
        ]
        self.assertEqual(post_operating_revenue,[])

    def test_all_operating_epochs_preserve_A1_A9(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),('SPARSE_PUBLIC_1','3'),('NULL_FP_1','0')):
            _,h=self.full_case(uid,stock)
            for key in ('operating_request_checks','operating_finance_checks','operate_checks'):
                self.assertEqual(
                    tuple(sorted(h[key])),
                    ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_productive_capacity_raw_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.state.assets['MINE-P'].capacity+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-CAPACITY')

    def test_inventory_raw_tamper_is_detected_between_epochs(self):
        k,h=self.full_case()
        k.colonies['OFF:T1'].resource_inventory+=D('1')
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-INVENTORY')

    def test_operating_chain_replays_exactly(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),('SPARSE_PUBLIC_1','3'),('NULL_FP_1','0')):
            ak,ah=self.full_case(uid,stock)
            bk,bh=self.full_case(uid,stock)
            self.assertEqual(tuple(ak.decision_epoch_records),tuple(bk.decision_epoch_records))
            self.assertEqual(ah['operating_request_policy'].decision,
                             bh['operating_request_policy'].decision)
            self.assertEqual(ah['operating_financier_policy'].decision,
                             bh['operating_financier_policy'].decision)
            self.assertEqual(ah['operate_policy'].decision,bh['operate_policy'].decision)
            self.assertEqual(ah['operating_cost_record'],bh['operating_cost_record'])
            self.assertEqual(ah['extraction_record'],bh['extraction_record'])
            self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
