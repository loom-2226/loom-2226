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
    def test_C07_absence_is_unknown(self):
        self.k.agents['PUB'].beliefs.clear();v,_=admit_for_use(self.k,self.request())
        self.assertEqual((v.value_state,v.value),(FactState.UNKNOWN,None))
    def test_C08_scope_widening(self):
        q=self.request()
        with self.assertRaisesRegex(InvariantError,'SCOPE'):admit_for_use(self.k,replace(q,scope='ALL_WORLD'))
    def test_C09_future_cutoff(self):
        with self.assertRaisesRegex(InvariantError,'TIME'):replace(self.request(),knowledge_cutoff='2')
    def test_C10_private_observation_possession(self):
        from offworld_kernel.mvp_state import Observation
        self.k.observations['SECRET']=Observation('SECRET',1,'PUB','RES','REMOTE','POSITIVE',False)
        self.k.agents['PUB'].information.add('SECRET')
        r=policy_inputs(self.k,'FIN','1',('observation.SIGNAL',),{'observation.SIGNAL':'SECRET'})[-1]
        self.assertEqual(r.state,FactState.BLOCKED);self.assertEqual(r.reason_code,'BLOCKED_POSSESSION')
    def test_C11_permission_without_possession(self):
        from offworld_kernel.mvp_state import Observation
        self.k.observations['PUBLIC']=Observation('PUBLIC',1,'PUB','RES','REMOTE','POSITIVE',True)
        r=policy_inputs(self.k,'FIN','1',('observation.SIGNAL',),{'observation.SIGNAL':'PUBLIC'})[-1]
        self.assertEqual(r.state,FactState.BLOCKED)
    def test_C12_conflicting_admitted_sources(self):
        m=self.k.boundary_manifest;a=next(a for a in m.assertions if a.assertion_id=='PUB:exploration.REMOTE_COST')
        self.k.boundary_manifest=replace(m,assertions=(*m.assertions,replace(a,assertion_id='CONFLICT',value='11')))
        r=policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',))[-1]
        self.assertEqual((r.state,r.reason_code),(FactState.BLOCKED,'CONFLICT_REVIEW_REQUIRED'))
    def test_C13_implicit_context_crossing(self):
        q=self.request()
        for kw in ({'context_id':'OTHER_RUN'},{'world_context':'SCENARIO','context_id':'OTHER_SCENARIO'},{'consumer_id':'FIN','perspective_actor_id':'FIN'}):
            with self.subTest(kw=kw),self.assertRaises(InvariantError):admit_for_use(self.k,replace(q,**kw))
    def test_C14_unit_role_mismatch(self):
        for kw in ({'required_unit':'PERSON'},{'required_role':'PHYSICAL_TRUTH'}):
            with self.subTest(kw=kw),self.assertRaises(InvariantError):admit_for_use(self.k,replace(self.request(),**kw))
    def test_U01_missing_prior_has_no_half_fallback(self):
        self.k.agents['PUB'].priors.clear();r=policy_inputs(self.k,'PUB','1',())[2];self.assertEqual(r.state,FactState.UNKNOWN)
    def test_U02_unknown_cost_blocks_worker(self):
        from offworld_kernel.policy_runner import run_public_explorer_policy
        from offworld_kernel.exploration_protocol import build_exploration_request
        m=self.k.boundary_manifest;self.k.boundary_manifest=replace(m,assertions=tuple(replace(a,value=None,value_state=FactState.UNKNOWN) if a.assertion_id=='PUB:exploration.REMOTE_COST' else a for a in m.assertions))
        r=policy_inputs(self.k,'PUB','1',('exploration.REMOTE_COST',));snap=build_decision_snapshot(self.k,'PUB','1',1,snapshot_facts(self.k,r),admission_receipts=r)
        out=run_public_explorer_policy(snap,build_exploration_request('U02',1,'EXP','RES'),'U02')
        self.assertEqual(out.decision.outcome.value,'BLOCKED_UNKNOWN');self.assertEqual(out.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
    def test_U03_known_zero_distinct_unknown(self):
        self.k.agents['PUB'].beliefs['RES']=D(0);v,_=admit_for_use(self.k,self.request());self.assertEqual((v.value_state,v.value),(FactState.KNOWN,'0'))
        with self.assertRaises(InvariantError):replace(v,value_state=FactState.UNKNOWN)
    def test_U04_missing_colony_blocked(self):
        self.k.colonies.clear();r=policy_inputs(self.k,'PUB','12',('settlement.STAGE',))[-1];self.assertEqual(r.state,FactState.BLOCKED)
    def test_U05_missing_parameter_blocked(self):
        with self.assertRaisesRegex(InvariantError,'PARAMETER'):self.k.boundary_manifest.parameter('UNDECLARED')
    def test_U09_no_undeclared_fact(self):
        with self.assertRaises(InvariantError):build_decision_snapshot(self.k,'PUB','1',1,())
