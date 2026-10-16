"""Build 8 G1 local-only checks. Every experimental value comes from scenario data."""
import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

from .genesis_g1 import (ROOT, DEFAULT_SCENARIO_PATH, build_opening,
                         load_scenario, validate_scenario)

def digest_for(data):
    return hashlib.sha256(
        (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()


class GenesisG1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario, cls.digest = load_scenario()
        cls.kernel, cls.baseline = build_opening(
            cls.scenario, scenario_sha256=cls.digest)

    def test_01_truthful_opening_and_exact_sources(self):
        self.assertEqual(self.baseline["strict_opening"], "PASS")
        self.assertEqual(self.baseline["frozen_provenance"], "PASS")
        self.assertEqual(self.baseline["scenario"], self.scenario)
        self.assertEqual(self.baseline["source_digests"], self.scenario["sources"])
        self.assertEqual(self.digest, digest_for(self.scenario))
        self.assertEqual(len(self.kernel.observations), 0)
        self.assertEqual(len(self.kernel.state.transactions), 0)
        self.assertEqual(len(self.kernel.events), 0)
        self.assertEqual(len(self.kernel._boundary_genesis_inputs), 1)
        self.assertIsNone(self.scenario["world_binding"])
        self.assertEqual(self.baseline["standing"],
                         "UNQUALIFIED_G1_OPENING_NO_OBSERVATION")

    def test_02_six_independent_mutations_change_effect_and_identity(self):
        # Base and alternative values are ALL loaded from the authored file.
        # Independent mutation must affect the behaviorally relevant output,
        # not merely change serialized or echoed input text.
        s = self.scenario
        paths = {
            "cash": (("actors", 0, "opening_cash"), "agent_cash"),
            "capability": (("actors", 0, "capabilities"), "agent_capabilities"),
            "prior": (("actors", 0, "prior"), "agent_prior"),
            "cost": (("observation_offer", "cost"), "potentially_affordable_looks"),
            "horizon": (("time", "end_year"), "calendar_year_slots"),
            "policy": (("actors", 0, "policy_ref"), "could_consider_exploration"),
        }
        self.assertEqual(set(paths), set(s["test_alternatives"]))
        for kind, (path, observable) in paths.items():
            with self.subTest(field_type=kind):
                changed = copy.deepcopy(s)
                pointer = changed
                for part in path[:-1]:
                    pointer = pointer[part]
                pointer[path[-1]] = copy.deepcopy(s["test_alternatives"][kind])
                k, report = build_opening(changed,
                                          scenario_sha256=digest_for(changed))
                self.assertNotEqual(report["run_id"], self.baseline["run_id"])
                self.assertNotEqual(report["opening_result"][observable],
                                    self.baseline["opening_result"][observable],
                                    "DEAD_INPUT: " + kind)
                self.assertEqual(report["strict_opening"], "PASS")
                self.assertEqual(report["frozen_provenance"], "PASS")
                if kind in ("cash", "capability", "prior", "policy"):
                    self.assertNotEqual(
                        report["opening_result"]["constructed_opening_fingerprint"],
                        self.baseline["opening_result"]["constructed_opening_fingerprint"])
                self.assertNotEqual(report["scenario_sha256"], self.digest)

    def test_03_deterministic_reopen(self):
        k, replay = build_opening(self.scenario, scenario_sha256=self.digest)
        self.assertEqual(self.baseline, replay)
        self.assertEqual(self.kernel.boundary_manifest.fingerprint(),
                         k.boundary_manifest.fingerprint())
        self.assertEqual(self.kernel.decision_epoch_state_fingerprint(),
                         k.decision_epoch_state_fingerprint())

    def test_04_tampered_declared_hash_rejected(self):
        changed = copy.deepcopy(self.scenario)
        name = next(iter(changed["sources"]))
        changed["sources"][name] = "0" * len(changed["sources"][name])
        with self.assertRaisesRegex(ValueError, "SOURCE_DIGEST_MISMATCH"):
            build_opening(changed, scenario_sha256=digest_for(changed))
        with self.assertRaisesRegex(ValueError, "SCENARIO_BYTE_DIGEST_MISMATCH"):
            build_opening(self.scenario, scenario_sha256=digest_for(changed))

    def test_05_missing_input_rejected(self):
        changed = copy.deepcopy(self.scenario)
        del changed["actors"][0]["opening_cash"]
        with self.assertRaises((ValueError, KeyError)):
            validate_scenario(changed)

    def test_06_no_automatic_2035_cost_extension(self):
        changed = copy.deepcopy(self.scenario)
        changed["time"]["end_year"] = self.scenario["test_alternatives"]["horizon"]
        _, report = build_opening(changed, scenario_sha256=digest_for(changed))
        self.assertFalse(report["scenario"]["mission_cost_future"]["hold_2026_cost"])
        self.assertEqual(report["scenario"]["mission_cost_future"]["post_boundary"],
                         "UNAVAILABLE_NO_MISSIONS_IN_G1")
        self.assertEqual(len(report["scenario"]["projects"]), 0)

    def test_07_advisory_static_literal_scan(self):
        # Intentionally secondary: rejects only obvious top-level assignments.
        # Cannot detect indirect hardcoding, dead inputs, conditional bypasses,
        # missing behavioral effects, or fabricated admissions.
        module = ast.parse(
            Path(__file__).with_name("genesis_g1.py").read_text()
        )
        experiment_names = {"POOL", "COST", "HORIZON", "PRIOR",
                            "PROFILES", "OPENING_CASH", "SUCCESS_VALUE",
                            "DETECTION", "FALSE_POSITIVE"}
        offenders = []
        for stmt in module.body:
            if isinstance(stmt, ast.Assign):
                for lhs in stmt.targets:
                    if isinstance(lhs, ast.Name) and lhs.id in experiment_names:
                        offenders.append(lhs.id)
        self.assertFalse(offenders, "experiment literal in module: " + str(offenders))

    def test_08_frozen_sources_are_byte_identical(self):
        for path, digest in self.scenario["sources"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                                 digest)
        self.assertEqual(load_scenario(DEFAULT_SCENARIO_PATH)[1], self.digest)


if __name__ == "__main__":
    unittest.main()
