import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal as D

from offworld_kernel.build3 import RunIdentity
from offworld_kernel.kernel import InvariantError
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AgentKind, AgentState, RuntimeObjectClass, ScenarioResource, SystemState
from offworld_kernel.policy import FactState, PolicyContext, SnapshotFact, build_decision_snapshot
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent

class PolicyFirewallTests(unittest.TestCase):
    def fixture(self):
        rid=RunIdentity('RICH-HIDDEN','v9','SYNTH_POLICY','BUILD4_MVP_METHODOLOGY_R1',())
        k=MethodologyHardenedBuild4Kernel(rid)
        k.add_node('EARTH:X',NodeKind.EARTH)
        k.add_node('OFF:T1',NodeKind.OFFWORLD)
        k.add_account('agent_cash','SPN','EARTH:X',AccountKind.FUNDS,D('125'))
        a=AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','agent_cash',
                     capabilities={'EXPLORE','REQUEST_FINANCE'},objectives=('RETURN',))
        a.information.add('OBS_PUBLIC_001')
        a.beliefs['resource_exists']=D('0.65')
        a.asset_refs.add('LICENSE-1')
        a.claim_holdings['VEH-1']=D('0.20')
        k.add_agent(a)
        # Hidden world state is deliberately much richer than the policy snapshot.
        k.add_resource(ScenarioResource('RES-HIDDEN','OFF:T1','METALS',D('999'),D('900'),D('800'),D('777')))
        k.add_system(SystemState('DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
        k.scheduler.register_coupling(CouplingSpec(
            'DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))

        facts=(
            SnapshotFact('market_price',FactState.KNOWN,'42','AUTHORED:PRICE_TABLE_TEST'),
            SnapshotFact('surface_grade',FactState.UNKNOWN,None,'OBSERVATION:NOT_AVAILABLE'),
        )
        snap=build_decision_snapshot(k,'SPN','1',D('1.5'),facts)
        snap_ref=k.scheduler.open_decision_window('1',snap.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'decide-spn-1',D('1.5'),Phase.DECISION_WINDOW,0,'SPN','DECISION_ORCHESTRATOR',
            snapshot_ref=snap_ref))
        return k,snap,snap_ref

    def test_snapshot_is_deeply_value_copied_and_contains_no_hidden_world_state(self):
        k,snap,snap_ref=self.fixture()
        self.assertEqual(snap.account_balance,D('125'))
        self.assertEqual(snap.capabilities,('EXPLORE','REQUEST_FINANCE'))
        self.assertEqual(dict(snap.beliefs)['resource_exists'],D('0.65'))
        self.assertEqual(snap.resource_holdings,())
        rendered=repr(snap)
        self.assertNotIn('777',rendered)
        self.assertNotIn('999',rendered)
        self.assertNotIn('RICH-HIDDEN',rendered)
        self.assertNotIn('v9',rendered)
        self.assertNotIn('RES-HIDDEN',rendered)
        self.assertTrue(snap_ref.endswith(snap.fingerprint()))

        # Mutating the live agent after snapshot creation does not mutate the snapshot.
        k.agents['SPN'].beliefs['resource_exists']=D('0.01')
        k.state.accounts['agent_cash'].balance=D('1')
        self.assertEqual(dict(snap.beliefs)['resource_exists'],D('0.65'))
        self.assertEqual(snap.account_balance,D('125'))

    def test_snapshot_and_context_are_immutable_value_objects(self):
        k,snap,snap_ref=self.fixture()
        ctx=PolicyContext(snap,snap_ref,'POLICY-KEY-1')
        with self.assertRaises(FrozenInstanceError):
            snap.account_balance=D('0')
        with self.assertRaises(FrozenInstanceError):
            ctx.decision_key='OTHER'
        with self.assertRaises(AttributeError):
            _=ctx.__dict__
        with self.assertRaises(AttributeError):
            _=snap.__dict__

    def test_decision_window_rejects_kernel_bearing_generic_handler(self):
        k,snap,snap_ref=self.fixture()
        rt=ScheduledSimulationRuntime(k)
        with self.assertRaisesRegex(InvariantError,'kernel-bearing handler forbidden'):
            rt.register_handler('DECISION_ORCHESTRATOR',lambda kernel,event:'ILLEGAL')

    def test_hostile_policy_cannot_reach_kernel_world_seed_or_hidden_state(self):
        k,snap,snap_ref=self.fixture()
        attempts={}

        def hostile(ctx):
            # This policy is intentionally nosy. It receives only PolicyContext.
            for name in ('kernel','world','world_module','seed','master_seed','hidden_state',
                         'resources','run_identity','universe_id','universe_version','scheduler','state'):
                try:
                    getattr(ctx,name)
                    attempts[name]='LEAK'
                except AttributeError:
                    attempts[name]='BLOCKED'

            for name in ('kernel','world','seed','hidden_state','resources','run_identity',
                         'universe_id','universe_version'):
                try:
                    getattr(ctx.snapshot,name)
                    attempts['snapshot.'+name]='LEAK'
                except AttributeError:
                    attempts['snapshot.'+name]='BLOCKED'

            # UNKNOWN is present as UNKNOWN, never converted to zero/value.
            fact={f.key:f for f in ctx.snapshot.admitted_facts}['surface_grade']
            attempts['unknown_state']=fact.state.value
            attempts['unknown_value']=fact.value

            # Deterministic policy randomness is derived only from the admitted context/key.
            attempts['draw']=str(ctx.deterministic_draw('underwrite'))
            return 'HOSTILE_PROBE_COMPLETE'

        rt=ScheduledSimulationRuntime(k)
        rt.register_policy_handler('decide-spn-1','SPN',snap,'POLICY-KEY-1',hostile)
        rt.seal()
        result=rt.run()

        self.assertEqual(result.event_results,(('decide-spn-1','HOSTILE_PROBE_COMPLETE'),))
        leaks={k:v for k,v in attempts.items() if v=='LEAK'}
        self.assertEqual(leaks,{})
        self.assertEqual(attempts['unknown_state'],'UNKNOWN')
        self.assertIsNone(attempts['unknown_value'])
        self.assertEqual(result.validation_status,'NOT_EMPIRICALLY_VALIDATED')

    def test_policy_snapshot_must_match_current_agent_visible_state_at_registration(self):
        k,snap,snap_ref=self.fixture()
        k.agents['SPN'].beliefs['resource_exists']=D('0.99')
        rt=ScheduledSimulationRuntime(k)
        with self.assertRaisesRegex(InvariantError,'does not match current admitted agent-visible state'):
            rt.register_policy_handler('decide-spn-1','SPN',snap,'POLICY-KEY-1',lambda ctx:'NO')

    def test_decision_key_draw_replays_without_world_seed(self):
        _,snap,ref=self.fixture()
        a=PolicyContext(snap,ref,'K')
        b=PolicyContext(snap,ref,'K')
        self.assertEqual(a.deterministic_draw('x'),b.deterministic_draw('x'))
        self.assertNotEqual(a.deterministic_draw('x'),a.deterministic_draw('y'))

if __name__=='__main__': unittest.main()
