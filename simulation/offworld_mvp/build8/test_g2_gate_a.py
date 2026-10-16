"""Offline G2 Gate A acceptance. All experimental alternatives are authored."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from .genesis_g1 import load_scenario
from .g2_gate_a import HERE, run, verify_extension
from offworld_kernel.kernel import InvariantError


def identity(doc):
    return hashlib.sha256((json.dumps(doc, indent=2, sort_keys=True) + "\n").encode()).hexdigest()


class PrivateGateATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.digest = load_scenario(HERE / "g2_gate_a_scenario.json")
        cls.base = run(cls.doc, cls.digest)

    def test_strict_acceptance_and_originals(self):
        r = self.base
        self.assertEqual(r["outcome"], "AUTHORIZE")
        self.assertEqual(r["reason"], "APPROVED_PRIVATE_REMOTE_EXPLORATION")
        self.assertEqual(r["request_originals"], 1)
        self.assertEqual(r["decision_originals"], 1)
        self.assertEqual(r["receipt_count"], 4)
        self.assertEqual(len(r["rule_refs"]), 1)
        self.assertEqual(r["causal_trace"], "PASS")
        self.assertTrue(r["no_observations"] and r["no_payments"])
        self.assertEqual(r["scenario"], self.doc)
        self.assertEqual(r["source_digests"], self.doc["sources"])

    def test_five_authored_mutations_change_typed_outcome(self):
        paths = {
            "cash": ("actors", 0, "opening_cash"),
            "cost": ("observation_offer", "cost"),
            "prior": ("actors", 0, "prior"),
            "policy": ("actors", 0, "policy_ref"),
            "horizon": ("time", "end_year"),
        }
        self.assertEqual(set(paths), set(self.doc["g2_test_alternatives"]))
        for kind, path in paths.items():
            with self.subTest(kind=kind):
                doc = copy.deepcopy(self.doc)
                pointer = doc
                for part in path[:-1]:
                    pointer = pointer[part]
                pointer[path[-1]] = doc["g2_test_alternatives"][kind]
                result = run(doc, identity(doc))
                self.assertNotEqual(result["run_id"], self.base["run_id"])
                self.assertNotEqual(result["outcome"], self.base["outcome"])
                self.assertTrue(result["no_payments"] and result["no_observations"])
                self.assertEqual(result["causal_trace"], "PASS")

    def test_repeat_same_run_and_worker_determinism(self):
        self.assertEqual(run(self.doc, self.digest), self.base)

    def test_worker_isolation_and_no_world_in_wire(self):
        probe = run(self.doc, self.digest, probe=True)
        self.assertTrue(probe)
        self.assertTrue(all(v == "BLOCKED" for v in probe.values()), probe)

    def test_pin_tamper_fails_closed(self):
        doc = copy.deepcopy(self.doc)
        name = "simulation/offworld_mvp/build8/g2_private_policy.py"
        doc["sources"][name] = "0" * len(doc["sources"][name])
        with self.assertRaisesRegex(ValueError, "G2_EXTENSION_SOURCE_MISMATCH"):
            verify_extension(doc)
        original = Path.read_bytes
        def modified(path):
            b = original(path)
            return b + b"x" if str(path).endswith("g2_private_worker.py") else b
        with patch.object(Path, "read_bytes", modified):
            with self.assertRaisesRegex(ValueError, "G2_EXTENSION_SOURCE_MISMATCH"):
                verify_extension(self.doc)

    def test_reject_bad_policy_version(self):
        with self.assertRaisesRegex(InvariantError, "typed policy result/version"):
            run(self.doc, self.digest, tamper_version=True)

    def test_reject_bad_decision_lineage(self):
        with self.assertRaisesRegex((InvariantError, ValueError),
                                    "PRIVATE_DECISION_LINEAGE"):
            run(self.doc, self.digest, tamper_decision=True)


if __name__ == "__main__":
    unittest.main()
