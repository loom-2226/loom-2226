import unittest
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'build6/qualification'))
from build6d_fixture import make_kernel,policy_inputs,system_epoch,run_case
from offworld_kernel.boundary import *
from offworld_kernel.causal_trace import *
from offworld_kernel.kernel import InvariantError
from offworld_kernel.policy import build_decision_snapshot,SnapshotFact


class ContextAdmissionTests(unittest.TestCase):
    def setUp(self):self.k,self.h=make_kernel()
    def request(self,actor='PUB',concept='agent.BELIEF',time='1'):
        return policy_inputs(self.k,actor,time,())[1].consumption_request
    def test_C01_complete_declaration(self):
        q=self.request()
        for field in ('request_id','use','scope','time_basis','perspective','required_unit','required_role'):
            with self.subTest(field=field),self.assertRaises(InvariantError):replace(q,**{field:''})
    def test_C02_real_unknown_never_scenario_truth(self):
        q=ConsumptionRequest('real','GENESIS','QUALIFICATION','RES','R_RECOVERABLE','SITE:OFF:T1','SIM_TIME','1','1','REAL','','GOVERNANCE','','ADMITTED','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
        v,_=admit_for_use(self.k,q);self.assertEqual(v.value_state,FactState.UNKNOWN);self.assertIsNone(v.value)
    def test_C03_distinct_resource_views(self):
        self.k.resources['RES'].in_situ=D(30);self.k.resources['RES'].accessible=D(25)
        values=[]
        for concept in RESOURCE_CONCEPTS:
            q=ConsumptionRequest(concept,'AUDIT','QUALIFICATION','RES',concept,'SITE:OFF:T1','SIM_TIME','1','1','REALIZED',self.k.boundary_manifest.run_id,'WORLD_SIM','','ADMITTED','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
            values.append(admit_for_use(self.k,q)[0])
        self.assertEqual([x.value for x in values],['30','25','20',None]);self.assertEqual(values[-1].value_state,FactState.UNKNOWN)
    def test_C04_raw_fact_laundering(self):
        receipts=policy_inputs(self.k,'PUB','1',())
        with self.assertRaisesRegex(InvariantError,'LINEAGE'):build_decision_snapshot(self.k,'PUB','1',1,(SnapshotFact('resource.truth',FactState.KNOWN,'20','FORGED'),),admission_receipts=receipts)
    def test_C05_receipt_forgery(self):
        receipt=policy_inputs(self.k,'PUB','1',())[0]
        with self.assertRaisesRegex(InvariantError,'LINEAGE'):replace(receipt,resolved_value_hash='0'*64)
    def test_C06_quarantined_source(self):
        m=self.k.boundary_manifest;assertions=tuple(replace(a,admission_state='QUARANTINED') if a.assertion_id=='PUB:exploration.REMOTE_COST' else a for a in m.assertions)
        self.k.boundary_manifest=replace(m,assertions=assertions)
        with self.assertRaisesRegex(InvariantError,'ADMISSION'):snapshot_facts(self.k,policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',)))
    def test_C08_absence_is_unknown(self):
        self.k.agents['PUB'].beliefs.clear();v,_=admit_for_use(self.k,self.request())
        self.assertEqual((v.value_state,v.value),(FactState.UNKNOWN,None))
    def test_C09_scope_widening(self):
        q=self.request()
        with self.assertRaisesRegex(InvariantError,'SCOPE'):admit_for_use(self.k,replace(q,scope='ALL_WORLD'))
    def test_C10_future_cutoff(self):
        with self.assertRaisesRegex(InvariantError,'TIME'):replace(self.request(),knowledge_cutoff='2')
    def test_C11_private_observation_possession(self):
        from offworld_kernel.mvp_state import Observation
        self.k.observations['SECRET']=Observation('SECRET',1,'PUB','RES','REMOTE','POSITIVE',False)
        self.k.agents['PUB'].information.add('SECRET')
        r=policy_inputs(self.k,'FIN','1',('observation.SIGNAL',),{'observation.SIGNAL':'SECRET'})[-1]
        self.assertEqual(r.state,FactState.BLOCKED);self.assertEqual(r.reason_code,'BLOCKED_POSSESSION')
    def test_C12_permission_without_possession(self):
        from offworld_kernel.mvp_state import Observation
        self.k.observations['PUBLIC']=Observation('PUBLIC',1,'PUB','RES','REMOTE','POSITIVE',True)
        r=policy_inputs(self.k,'FIN','1',('observation.SIGNAL',),{'observation.SIGNAL':'PUBLIC'})[-1]
        self.assertEqual(r.state,FactState.BLOCKED)
    def test_C13_conflicting_admitted_sources(self):
        m=self.k.boundary_manifest;a=next(a for a in m.assertions if a.assertion_id=='PUB:exploration.REMOTE_COST')
        self.k.boundary_manifest=replace(m,assertions=(*m.assertions,replace(a,assertion_id='CONFLICT',value='11')))
        r=policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',))[-1]
        self.assertEqual((r.state,r.reason_code),(FactState.BLOCKED,'CONFLICT_REVIEW_REQUIRED'))
    def test_C14_implicit_context_crossing(self):
        q=self.request()
        for kw in ({'context_id':'OTHER_RUN'},{'world_context':'SCENARIO','context_id':'OTHER_SCENARIO'},{'consumer_id':'FIN','perspective_actor_id':'FIN'}):
            with self.subTest(kw=kw),self.assertRaises(InvariantError):admit_for_use(self.k,replace(q,**kw))
    def test_C14_unit_role_mismatch(self):
        for kw in ({'required_unit':'PERSON'},{'required_role':'PHYSICAL_TRUTH'}):
            with self.subTest(kw=kw),self.assertRaises(InvariantError):admit_for_use(self.k,replace(self.request(),**kw))
    def test_U02_missing_prior_has_no_half_fallback(self):
        self.k.agents['PUB'].priors.clear();r=policy_inputs(self.k,'PUB','1',())[2];self.assertEqual(r.state,FactState.UNKNOWN)
    def test_U03_unknown_cost_blocks_worker(self):
        from offworld_kernel.policy_runner import run_public_explorer_policy
        from offworld_kernel.exploration_protocol import build_exploration_request
        m=self.k.boundary_manifest;self.k.boundary_manifest=replace(m,assertions=tuple(replace(a,value=None,value_state=FactState.UNKNOWN) if a.assertion_id=='PUB:exploration.REMOTE_COST' else a for a in m.assertions))
        r=policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',));snap=build_decision_snapshot(self.k,'PUB','1',1,snapshot_facts(self.k,r),admission_receipts=r)
        out=run_public_explorer_policy(snap,build_exploration_request('U02',1,'EXP','RES'),'U02')
        self.assertEqual(out.decision.outcome.value,'BLOCKED_UNKNOWN');self.assertEqual(out.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
    def test_U04_known_zero_distinct_unknown(self):
        self.k.agents['PUB'].beliefs['RES']=D(0);v,_=admit_for_use(self.k,self.request());self.assertEqual((v.value_state,v.value),(FactState.KNOWN,'0'))
        with self.assertRaises(InvariantError):replace(v,value_state=FactState.UNKNOWN)
    def test_U05_missing_colony_blocked(self):
        self.k.colonies.clear();r=policy_inputs(self.k,'PUB','12',('settlement.STAGE',))[-1];self.assertEqual(r.state,FactState.BLOCKED)
    def test_U05_missing_parameter_blocked(self):
        with self.assertRaisesRegex(InvariantError,'PARAMETER'):self.k.boundary_manifest.parameter('UNDECLARED')
    def test_U09_no_undeclared_fact(self):
        with self.assertRaises(InvariantError):build_decision_snapshot(self.k,'PUB','1',1,())

    def test_C07_recorded_excluded_is_blocked(self):
        m=self.k.boundary_manifest;a=next(x for x in m.assertions if x.assertion_id=='PUB:exploration.REMOTE_COST')
        self.k.boundary_manifest=replace(m,assertions=tuple(replace(x,admission_state='REJECTED') if x==a else x for x in m.assertions))
        q=policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',))[-1].consumption_request
        for assertion_set in ('ADMITTED','ALL_RECORDED'):
            v,_=admit_for_use(self.k,replace(q,assertion_set=assertion_set))
            self.assertEqual(v.value_state,FactState.BLOCKED);self.assertIn('REJECTED',v.reason_code);self.assertIsNone(v.value)
    def test_U01_missing_belief_and_prior_blocks_Bayes_atomically(self):
        from offworld_kernel.mvp_state import Observation
        from types import SimpleNamespace
        k=self.k;k.observations['O']=Observation('O',1,'PUB','RES','REMOTE','POSITIVE',False);k.agents['PUB'].information.add('O')
        k.agents['PUB'].beliefs.clear();k.agents['PUB'].priors.clear();prior=canonical((k.agents,k.events))
        k._boundary_event_context=(SimpleNamespace(process_id='SYS:update_agent_belief_from_observation',effective_time=D(1)),(),())
        from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
        with self.assertRaisesRegex(InvariantError,'UNKNOWN'):
            MethodologyHardenedBuild4Kernel.update_agent_belief_from_observation(k,1,'PUB','O','RES',D('.8'),D('.2'),'MODEL','SOURCE')
        self.assertEqual(canonical((k.agents,k.events)),prior)
    def test_U02_missing_required_sponsor_prior_blocks_without_default(self):
        from offworld_kernel.sponsor_protocol import build_sponsor_project_request
        from offworld_kernel.policy_runner import run_sponsor_operator_policy
        self.k.agents['SPN'].priors.clear()
        receipts=policy_inputs(self.k,'SPN','3',('project.STATUS','project.CASH_BALANCE','underwriting.DEVELOPMENT_CAPEX'))
        snap=build_decision_snapshot(self.k,'SPN','U02',3,snapshot_facts(self.k,receipts),admission_receipts=receipts)
        result=run_sponsor_operator_policy(snap,build_sponsor_project_request('U02',3,'P','RES','O'),'U02')
        self.assertEqual(result.decision.outcome.value,'BLOCKED_UNKNOWN');self.assertFalse(self.k.state.transactions)
    def test_U09_missing_numerical_manifest_blocks_genesis(self):
        from offworld_kernel.boundary import validate_opening
        for key in ('remote_fp','surface_fn','lambda','S','capacity','financier_hurdle_rate'):
            k,_=make_kernel();m=k.boundary_manifest;parameters=tuple(x for x in m.parameters if x[0]!=key)
            k.boundary_manifest=replace(m,parameters=parameters);k.run_identity=replace(k.run_identity,parameters=parameters)
            k.boundary_manifest=replace(k.boundary_manifest,opening_state_hash=content_hash(k._boundary_projection()))
            with self.subTest(key=key),self.assertRaisesRegex(InvariantError,'PARAMETER'):validate_opening(k)
    def test_F15_cash_reserve_cannot_be_resource_reserve(self):
        q=ConsumptionRequest('RESERVE','AUDIT','QUALIFICATION','RES','R_RESERVE','SITE:OFF:T1','SIM_TIME','1','1','REALIZED',self.k.boundary_manifest.run_id,'WORLD_SIM','','ADMITTED','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
        v,_=admit_for_use(self.k,q);self.assertEqual((v.value_state,v.value),(FactState.UNKNOWN,None))
        with self.assertRaisesRegex(InvariantError,'SCOPE'):admit_for_use(self.k,replace(q,required_unit='MODEL_CURRENCY',required_role='FINANCIAL_STATE'))
    def test_C03_depleted_realized_non_equal_hierarchy(self):
        from offworld_kernel.boundary import query_context
        k=self.k;k.resources['RES'].in_situ=D(30);k.resources['RES'].accessible=D(25);k.resources['RES'].remaining=D(15)
        m=k.boundary_manifest;start={'R_IN_SITU':'30','R_ACCESSIBLE':'25','R_RECOVERABLE':'20'}
        k.boundary_manifest=replace(m,assertions=tuple(replace(a,value=start[a.concept]) if a.world_context=='SCENARIO' and a.concept in start else a for a in m.assertions))
        expected={'R_IN_SITU':'25','R_ACCESSIBLE':'20','R_RECOVERABLE':'15'}
        for concept in start:
            q=ConsumptionRequest(concept,'AUDIT','QUALIFICATION','RES',concept,'SITE:OFF:T1','SIM_TIME','14','14','SCENARIO',m.scenario_id,'WORLD_SIM','','ADMITTED','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
            self.assertEqual(query_context(k,q).value,start[concept]);self.assertEqual(query_context(k,replace(q,world_context='REALIZED',context_id=m.run_id)).value,expected[concept])

    def test_C03_stipulated_truth_and_uncertainty_standing_separate(self):
        for value in self.k.boundary_manifest.assertions:
            if value.world_context=='SCENARIO' and value.concept in RESOURCE_CONCEPTS:
                self.assertEqual(value.proposition_kind,'SCENARIO_STIPULATION');self.assertEqual(value.epistemic_mode,'SCENARIO_STIPULATION')
            if value.world_context=='SCENARIO':self.assertEqual(value.uncertainty_state,'UNCHARACTERIZED')
