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
        k,_=make_kernel();a=k.keyed_draw('x');b=k.keyed_draw('y');self.assertEqual((a,b),(k.keyed_draw('x'),k.keyed_draw('y')))
    def test_R06_key_framing(self):
        k,_=make_kernel();self.assertNotEqual(k.keyed_draw('a|b','c'),k.keyed_draw('a','b|c'))
    def test_R07_worker_has_no_world_access(self):
        from offworld_kernel.policy_runner import run_hostile_access_probe
        k,_=make_kernel();r=policy_inputs(k,'PUB','1',());s=build_decision_snapshot(k,'PUB','1',1,(),admission_receipts=r)
        out,_=run_hostile_access_probe(s);self.assertTrue(all(v=='BLOCKED' for v in out.values()));self.assertFalse(hasattr(s,'run_identity'))
    def test_R08_comparison_metadata_required(self):
        k,_=make_kernel()
        with self.assertRaises(InvariantError):replace(k.boundary_manifest,comparison_parameters=())
    def test_R10_versioned_algorithm_blocks_unregistered(self):
        k,_=make_kernel();c=dict(k.boundary_manifest.comparison_parameters);c['algorithm']='UNDECLARED';k.boundary_manifest=replace(k.boundary_manifest,comparison_parameters=tuple(c.items()))
        with self.assertRaises(InvariantError):k.keyed_draw('x')
