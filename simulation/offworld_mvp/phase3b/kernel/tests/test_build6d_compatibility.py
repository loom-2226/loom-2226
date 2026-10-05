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


from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.policy import PolicyContext
from hashlib import sha256
class CompatibilityTests(unittest.TestCase):
    def test_B01_legacy_random_key_exact(self):
        rid=RunIdentity('LEGACY','v1','SNAP','LEGACY_CONTRACT',());k=MethodologyHardenedBuild4Kernel(rid)
        n=int.from_bytes(sha256(b'LEGACY|v1|a|b').digest()[:8],'big');self.assertEqual(k.keyed_draw('a','b'),D(n)/D(2**64))
        self.assertNotIn('boundary_manifest',k._methodology_payload());self.assertNotIn('causal_trace_root',k._methodology_payload())
    def test_B02_strict_missing_manifest_blocks(self):
        with self.assertRaises(InvariantError):MethodologyHardenedBuild4Kernel(RunIdentity('RICH','v1','SNAP',CONTRACT,()))
    def test_B03_history_is_explicitly_incomplete(self):
        view=legacy_event_view(('ORIGINAL_EVENT',));self.assertEqual(view['status'],'LEGACY_TRACE_INCOMPLETE');self.assertIn('consumption_receipts',view['missing'])
    def test_B04_wrong_source_commit_rejected(self):
        from offworld_kernel.provenance import verify_commit_code_linkage
        with self.assertRaises(InvariantError):verify_commit_code_linkage('c4074be751deaea9e9b1eb5b9b686e65aa170afa','0'*64)
    def test_B05_schema_closes_five_records(self):
        from offworld_kernel.schema_registry import canonical_registry_payload
        reg=canonical_registry_payload();self.assertEqual(reg['registry_version'],'ODD_SCHEMA_REGISTRY_0_20')
        for name in ('ContextValue','ConsumptionRequest','AdmissionReceipt','BoundaryManifest','CausalEnvelope'):self.assertIn(name,reg['types'])
