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


from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.scheduler import CouplingSpec,ScheduledEvent,Phase
from offworld_kernel.mvp_state import RuntimeObjectClass,Observation
from build6d_fixture import OWNERS
class CausalTraceTests(unittest.TestCase):
    def test_L01_domain_neutral_type_preserving_projection(self):
        self.assertNotEqual(canonical(D('1')),canonical('1'));self.assertNotEqual(canonical(('1',)),canonical(['1']))
        a=(('OTHER_DOMAIN','input',canonical('old')),);b=(('OTHER_DOMAIN','input',canonical('new')),)
        self.assertEqual(state_delta(a,b)[0][:2],('OTHER_DOMAIN','input'))
        from dataclasses import fields
        self.assertFalse(any(x.name in ('project_id','price','account_id','market_id') for x in fields(CausalEnvelope)))
    def test_L02_missing_parent_and_artifact(self):
        k,h=make_kernel();k.begin_decision_epoch('L02','L02');e=k.causal_envelopes[0]
        for malformed in (replace(e,parent_envelope_refs=('MISSING',)).finalized(),replace(e,lineage_refs=('MISSING',)).finalized()):
            with self.assertRaises(InvariantError):validate_trace((malformed,),k.causal_artifacts)
    def test_L03_omitted_delta_hash_chain_detected(self):
        k,h=make_kernel();k.begin_decision_epoch('L03','L03');e=k.causal_envelopes[0]
        with self.assertRaises(InvariantError):validate_trace((replace(e,post_domain_hash='0'*64),),k.causal_artifacts)
    def test_L04_raw_handler_write_invalidates(self):
        k,h=make_kernel();k.begin_decision_epoch('RAW','RAW');sid='SYS:add_commitment';owned=OWNERS['add_commitment']
        k.scheduler.register_coupling(CouplingSpec(sid,'v1',RuntimeObjectClass.SYSTEM,owned,(),owned,'EVENT',Phase.OPERATIONS));k.scheduler.schedule(ScheduledEvent('RAW',D(1),Phase.OPERATIONS,0,sid,sid))
        q=ConsumptionRequest('RAW',sid,'SYSTEM_TRANSITION',sid,'transition.RULE','PROCESS:'+sid,'SIM_TIME','1','1','SCENARIO',k.boundary_manifest.scenario_id,'WORLD_SIM','','ADMITTED','TYPED_RULE','TRANSITION_RULE');receipt=admit_for_use(k,q)[1]
        rt=ScheduledSimulationRuntime(k,ReplayProvenance.from_kernel(k))
        def hostile(kernel,event):kernel.state.accounts['public_funds'].balance+=D(1);return 'pretend no change'
        rt.register_handler(sid,hostile,admission_receipts=(receipt,),transition_methods=('add_commitment',));rt.seal()
        with self.assertRaisesRegex(InvariantError,'INVALID_RUN'):rt.run()
    def test_L06_wrong_chain_and_cycle(self):
        k,h=make_kernel();k.begin_decision_epoch('L06','L06');e=k.causal_envelopes[0]
        with self.assertRaises(InvariantError):validate_trace((replace(e,previous_trace_hash='WRONG').finalized(),),k.causal_artifacts)
        with self.assertRaises(InvariantError):validate_trace((replace(e,parent_envelope_refs=(e.envelope_id,)).finalized(),),k.causal_artifacts)
    def test_L07_agent_audit_clipped(self):
        k,h=make_kernel();k.begin_decision_epoch('L07','L07');out=reconstruct(k.causal_envelopes,k.causal_artifacts,k.causal_envelopes[0].envelope_id,perspective='AGENT',actor_id='PUB')
        self.assertEqual(out['status'],'BLOCKED_PERSPECTIVE');self.assertEqual(out['artifacts'],())
    def test_U06_degenerate_update_is_atomic(self):
        k,h=make_kernel();k.observations['O']=Observation('O',1,'PUB','RES','REMOTE','POSITIVE',False);k.agents['PUB'].information.add('O');k.agents['PUB'].beliefs['RES']=D(0)
        # Declared fixture successor for this hostile opening; no activity is
        # promoted as valid genesis. Direct preflight tests before the executor.
        from types import SimpleNamespace
        event=SimpleNamespace(process_id='SYS:publish_observation')
        k._boundary_event_context=(event,(),());prior=canonical(k.agents)
        with self.assertRaises(InvariantError):k._boundary_preflight('publish_observation',k.publish_observation,(1,'PUB','O','PUBLIC',(('PUB','RES',D(1),D(0)),)),{})
        self.assertEqual(canonical(k.agents),prior)
    def test_U07_all_recipient_preflight_is_atomic(self):
        k,h=make_kernel();k.observations['O']=Observation('O',1,'PUB','RES','REMOTE','POSITIVE',False);k.agents['PUB'].information.add('O');k.agents['SPN'].priors.clear();k.agents['SPN'].beliefs.clear()
        from types import SimpleNamespace
        k._boundary_event_context=(SimpleNamespace(process_id='SYS:publish_observation'),(),());prior=canonical(k.agents)
        with self.assertRaises(InvariantError):k._boundary_preflight('publish_observation',k.publish_observation,(1,'PUB','O','PUBLIC',(('FIN','resource_exists',D('.8'),D('.2')),('SPN','resource_exists',D('.8'),D('.2')))),{})
        self.assertEqual(canonical(k.agents),prior)
    def test_U08_legacy_transition_not_authorized(self):
        k,h=make_kernel();k.begin_decision_epoch('U08','U08')
        with self.assertRaises(InvariantError):k.observe(1,'PUB','RES','REMOTE')
    def test_F10_genesis_truth_tamper(self):
        k,h=make_kernel();k.resources['RES'].remaining=D(19)
        with self.assertRaisesRegex(InvariantError,'GENESIS'):k.begin_decision_epoch('TAMPER','TAMPER')
    def test_F11_direct_mint_guard(self):
        k,h=make_kernel();k.begin_decision_epoch('GUARD','GUARD')
        with self.assertRaises(InvariantError):k.add_account('MINT','PUB','EARTH:USA',__import__('offworld_kernel.model',fromlist=['AccountKind']).AccountKind.FUNDS,D(100))

    def test_L05_untyped_lying_policy_result_rejected(self):
        from build6d_fixture import policy_epoch
        from offworld_kernel.exploration_protocol import build_exploration_request
        from offworld_kernel.policy_runner import public_explorer_policy_version
        k,h=make_kernel();q=build_exploration_request('L05',1,'EXP','RES')
        with self.assertRaisesRegex(InvariantError,'LINEAGE'):policy_epoch(k,h,'L05','PUB','1',q,('exploration.REMOTE_COST',),lambda *args:'invented decision',public_explorer_policy_version())
        self.assertFalse(k.state.transactions)
    def test_L09_partial_executor_failure_is_invalid(self):
        from offworld_kernel.policy_runner import run_public_explorer_policy,public_explorer_policy_version
        from offworld_kernel.exploration_protocol import build_exploration_request
        from build6d_fixture import policy_epoch
        k,h=make_kernel();d,ref=policy_epoch(k,h,'L09','PUB','1',build_exploration_request('L09',1,'EXP','RES'),('exploration.REMOTE_COST',),run_public_explorer_policy,public_explorer_policy_version())
        event=ScheduledEvent('PARTIAL',D(1),Phase.OPERATIONS,0,'PUB','SYS:add_commitment');k._boundary_event_context=(event,(),(ref,))
        def broken(cid,financier_id,project_id,amount):k.state.accounts['public_funds'].balance-=D(1);raise RuntimeError('partial executor failure')
        with self.assertRaises(RuntimeError):k._boundary_mutation('add_commitment',broken,('BROKEN','PUB','EXP',D(10)),{})
        self.assertTrue(k._boundary_invalid);self.assertEqual(k.causal_envelopes[-1].reason_code,'INVALID_RUN')
