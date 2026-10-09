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


from offworld_kernel.policy import PolicyContext
class ComparisonRandomTests(unittest.TestCase):
    def test_R01_pre_observation_information_identical(self):
        snapshots=[]
        for world in ('NULL','SPARSE','RICH'):
            k,_=make_kernel(world);r=policy_inputs(k,'PUB','1',('exploration.REMOTE_COST',));snapshots.append(build_decision_snapshot(k,'PUB','REMOTE',1,snapshot_facts(k,r),admission_receipts=r))
        self.assertEqual(snapshots[0],snapshots[1]);self.assertEqual(snapshots[1],snapshots[2])
    def test_R02_matched_world_stream(self):
        draws=[]
        for world in ('NULL','SPARSE','RICH'):
            k,_=make_kernel(world);draws.append((k.keyed_draw('OBS',1,'PUB','RES','REMOTE'),k.keyed_draw('OBS',2,'PUB','RES','SURFACE')))
        self.assertEqual(draws[0],draws[1]);self.assertEqual(draws[1],draws[2]);self.assertLess(draws[0][0],D('.2'));self.assertGreater(draws[0][1],D('.05'))
    def test_R03_policy_seed_independent_of_world_and_snapshot(self):
        k,_=make_kernel();r=policy_inputs(k,'PUB','1',());snap=build_decision_snapshot(k,'PUB','SAME',1,(),admission_receipts=r)
        from offworld_kernel.policy import comparison_decision_key
        a=PolicyContext(snap,'REF',comparison_decision_key(k.boundary_manifest.comparison_parameters,'PUB','SAME','KEY'))
        self.assertFalse(hasattr(a,'draw_contract'))
        b=replace(a,snapshot=replace(snap,account_balance=D(99)),snapshot_ref='OTHER')
        self.assertEqual(a.deterministic_draw('choice'),b.deterministic_draw('choice'))
    def test_R04_unrelated_actor_does_not_advance_stream(self):
        k,_=make_kernel();before=k.keyed_draw('OBS',1,'PUB','RES','REMOTE');k.keyed_draw('OBS',1,'UNRELATED','RES','REMOTE');self.assertEqual(before,k.keyed_draw('OBS',1,'PUB','RES','REMOTE'))
    def test_R05_reorder_stability(self):
        k,_=make_kernel();a=k.keyed_draw('OBS',1,'PUB','RES','REMOTE');b=k.keyed_draw('OBS',1,'PUB','RES','SURFACE');self.assertEqual((a,b),(k.keyed_draw('OBS',1,'PUB','RES','REMOTE'),k.keyed_draw('OBS',1,'PUB','RES','SURFACE')))
    def test_R06_key_framing(self):
        k,_=make_kernel();self.assertNotEqual(k.keyed_draw('OBS',1,'a|b','c','REMOTE'),k.keyed_draw('OBS',1,'a','b|c','REMOTE'))
    def test_R07_worker_has_no_world_access(self):
        from offworld_kernel.policy_runner import run_hostile_access_probe
        k,_=make_kernel();r=policy_inputs(k,'PUB','1',());s=build_decision_snapshot(k,'PUB','1',1,(),admission_receipts=r)
        out,_=run_hostile_access_probe(s);self.assertTrue(all(v=='BLOCKED' for v in out.values()));self.assertFalse(hasattr(s,'run_identity'))
    def test_R08_comparison_metadata_required(self):
        k,_=make_kernel()
        with self.assertRaises(InvariantError):replace(k.boundary_manifest,comparison_parameters=())
    def test_R10_versioned_algorithm_blocks_unregistered(self):
        k,_=make_kernel();c=dict(k.boundary_manifest.comparison_parameters);c['algorithm']='UNDECLARED';k.boundary_manifest=replace(k.boundary_manifest,comparison_parameters=tuple(c.items()))
        with self.assertRaises(InvariantError):k.keyed_draw('OBS',1,'PUB','RES','REMOTE')

    def test_R04_actor_registry_and_POLICY_independence(self):
        from offworld_kernel.policy import comparison_decision_key
        k,_=make_kernel();q=policy_inputs(k,'PUB','1',());s=build_decision_snapshot(k,'PUB','R04',1,(),admission_receipts=q)
        before=k.keyed_draw('OBS',1,'PUB','RES','REMOTE');c=k.boundary_manifest.comparison_parameters
        policy=PolicyContext(s,'R04',comparison_decision_key(c,'PUB','R04','SLOT')).deterministic_draw('choice')
        k.agents.pop('FIN');k.agents['UNRELATED']=replace(k.agents['PUB'],id='UNRELATED')
        comparison_decision_key(c,'UNRELATED','R04','SLOT')
        self.assertEqual(before,k.keyed_draw('OBS',1,'PUB','RES','REMOTE'))
        self.assertEqual(policy,PolicyContext(s,'R04',comparison_decision_key(c,'PUB','R04','SLOT')).deterministic_draw('choice'))
    def test_R05_scheduler_insertion_order_and_map_iteration(self):
        from offworld_kernel.scheduler import DeterministicScheduler,CouplingSpec,ScheduledEvent,Phase
        from offworld_kernel.mvp_state import RuntimeObjectClass
        logs=[]
        for order in (('a','b'),('b','a')):
            scheduler=DeterministicScheduler();scheduler.register_coupling(CouplingSpec('S','V',RuntimeObjectClass.SYSTEM,(),(),(),'EVENT',Phase.OPERATIONS))
            for key in order:scheduler.schedule(ScheduledEvent(key,D(1),Phase.OPERATIONS,0,key,'S'))
            logs.append(tuple(e.event_id for e in scheduler.ordered_events()))
        self.assertEqual(*logs)
        k,_=make_kernel();q=policy_inputs(k,'PUB','1',());first=build_decision_snapshot(k,'PUB','MAP',1,(),admission_receipts=q)
        k.agents=dict(reversed(tuple(k.agents.items())));k.state.accounts=dict(reversed(tuple(k.state.accounts.items())))
        self.assertEqual(first,build_decision_snapshot(k,'PUB','MAP',1,(),admission_receipts=q))
    def test_R08_after_seal_random_configuration_drift_rejected(self):
        from build6d_fixture import strict_provenance
        from offworld_kernel.runtime import ScheduledSimulationRuntime
        k,_=make_kernel();k.begin_decision_epoch('R08','R08');rt=ScheduledSimulationRuntime(k,strict_provenance(k));rt.seal()
        c=dict(k.boundary_manifest.comparison_parameters);c['world_seed']='20261006';k.boundary_manifest=replace(k.boundary_manifest,comparison_parameters=tuple(sorted(c.items())))
        with self.assertRaisesRegex(InvariantError,'sealed'):rt.run()
    def test_R10_valid_seed_change_creates_new_identity_and_draw(self):
        k,_=make_kernel();m=k.boundary_manifest;before=m.fingerprint();draw=k.keyed_draw('OBS',1,'PUB','RES','REMOTE')
        c=dict(m.comparison_parameters);c['world_seed']='20261006';k.boundary_manifest=replace(m,comparison_parameters=tuple(sorted(c.items())))
        self.assertNotEqual(before,k.boundary_manifest.fingerprint());self.assertNotEqual(draw,k.keyed_draw('OBS',1,'PUB','RES','REMOTE'));self.assertEqual(m.fingerprint(),before)
    def test_R06_undeclared_family_rejected(self):
        k,_=make_kernel()
        for keys in (('UNKNOWN',1,'PUB','RES','REMOTE'),('OBS',1,'PUB','RES','UNKNOWN'),('OBS',)):
            with self.subTest(keys=keys),self.assertRaisesRegex(InvariantError,'key family'):k.keyed_draw(*keys)
