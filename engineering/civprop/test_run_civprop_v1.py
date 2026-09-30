"""End-to-end tests for the locked CIVPROP Engine V1 executable baseline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from .run_civprop_v1 import (
    OUTPUT_CONTRACT_VERSION,
    OUTPUT_FORMAT,
    RUNNER_ID,
    RUNNER_VERSION,
    build_output,
    default_paths,
)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
GOLDEN = HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP4_DEMAND_PRESSURE_SEED42.json"
BASELINE_MANIFEST = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP4_BASELINE_MANIFEST.json"
)


class CivpropEngineV1ExecutableBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_dir, cls.catalog_path = default_paths()
        cls.output = build_output(
            input_dir=cls.input_dir,
            infrastructure_catalog_path=cls.catalog_path,
            seed=42,
        )

    def test_one_entrypoint_produces_full_locked_output(self):
        output = self.output
        self.assertEqual(output["format"], OUTPUT_FORMAT)
        self.assertEqual(output["metadata"]["runner"]["id"], RUNNER_ID)
        self.assertEqual(output["metadata"]["runner"]["version"], RUNNER_VERSION)
        self.assertEqual(output["metadata"]["engine"]["id"], "HYBRID_V1")
        self.assertEqual(output["metadata"]["engine"]["version"], "method-reference-v2")
        for key in (
            "actor_state_boundary",
            "accessibility_boundary",
            "demand_pressure_boundary",
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "events",
            "flows",
        ):
            self.assertIn(key, output)
        self.assertTrue(output["actor_states"])
        self.assertTrue(output["annual_states"])
        self.assertTrue(output["decisions"])
        self.assertTrue(output["events"])

    def test_runtime_input_hash_is_actor_visible_scenario_only(self):
        scenario = self.input_dir / "scenario_v1.json"
        expected = hashlib.sha256(scenario.read_bytes()).hexdigest()
        self.assertEqual(
            self.output["metadata"]["inputs"]["actor_visible_scenario_sha256"],
            expected,
        )
        self.assertEqual(
            self.output["metadata"]["inputs"]["runtime_input_sha256"],
            expected,
        )

    def test_evaluator_truth_is_declared_but_not_runtime_input_or_output_state(self):
        truth = self.input_dir / "truth_v1.json"
        expected = hashlib.sha256(truth.read_bytes()).hexdigest()
        inputs = self.output["metadata"]["inputs"]
        self.assertEqual(inputs["evaluator_truth_sha256"], expected)
        self.assertFalse(inputs["evaluator_truth_consumed_by_engine"])
        payload = json.dumps(
            {
                key: self.output[key]
                for key in (
                    "actor_states",
                    "actor_transactions",
                    "annual_states",
                    "facilities",
                    "decisions",
                    "events",
                    "flows",
                )
            },
            sort_keys=True,
        )
        self.assertNotIn("grade_index", payload)
        self.assertNotIn("MOON_POLAR_WATER", payload)

    def test_infrastructure_semantics_are_pinned(self):
        infra = self.output["metadata"]["infrastructure"]
        self.assertEqual(
            infra["catalog_id"],
            "CIVPROP_INFRASTRUCTURE_ARCHETYPES_V1",
        )
        self.assertEqual(
            infra["parameter_set_id"],
            "METHOD_LAB_SYNTHETIC_V1",
        )
        self.assertEqual(
            infra["parameter_status"],
            "SYNTHETIC_METHOD_FIXTURE",
        )
        self.assertEqual(
            set(infra["parameterized_archetypes"]),
            {
                "LOGISTICS_NODE",
                "POWER_PLANT",
                "HABITAT",
                "RESOURCE_PLANT",
                "INDUSTRIAL_WORKSHOP",
            },
        )

    def test_gap1_through_gap4_are_closed_in_default_output(self):
        statuses = {x["gap_id"]: x["status"] for x in self.output["known_gaps"]}
        self.assertEqual(statuses["GAP-001"], "CLOSED")
        self.assertEqual(statuses["GAP-002"], "CLOSED")
        self.assertEqual(statuses["GAP-003"], "CLOSED")
        self.assertEqual(statuses["GAP-004"], "CLOSED")
        self.assertEqual(statuses["GAP-005"], "OPEN")

    def test_default_input_has_compiler_provenance(self):
        compiler = self.output["metadata"]["inputs"]["compiler"]
        self.assertEqual(compiler["compiler_id"], "CIVPROP_INPUT_COMPILER_V1")
        self.assertEqual(compiler["compiler_version"], "1.3.0")
        self.assertEqual(compiler["gap_resolution"]["GAP-001"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-002"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-003"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-004"], "CLOSED")
        self.assertEqual(len(compiler["manifest_sha256"]), 64)

    def test_semantics_are_explicit_not_implied(self):
        semantics = self.output["semantics"]
        self.assertEqual(
            semantics["annual_snapshot_timing"],
            "END_OF_YEAR_AFTER_DUE_COMMISSIONING_DECISIONS_AND_MIGRATION",
        )
        self.assertEqual(
            semantics["facility_records"],
            "COMMISSIONED_FACILITIES_ONLY",
        )
        self.assertEqual(
            semantics["pressure_state"],
            "INTERNAL_NOT_EMITTED_ONLY_QUALIFICATION_EVENTS_VISIBLE",
        )
        self.assertEqual(
            semantics["runtime_reasoning"],
            "EXPLICIT_CODE_RULES_AND_KEYED_STOCHASTICITY_NO_LLM_AUTHORITY",
        )
        self.assertEqual(
            semantics["atlas_role"],
            "ENGINE_STATE_NOT_FINAL_ATLAS_MATERIALIZATION",
        )
        self.assertEqual(
            semantics["actor_budget_output"],
            "ANNUAL_ACTOR_STATE_WITH_REPLAYABLE_TRANSACTIONS",
        )
        self.assertEqual(
            semantics["accessibility"],
            "VERSIONED_PHYSICS_SERVICE_TRI_STATE_WITH_DECOMPOSED_COSTS",
        )
        self.assertEqual(
            semantics["demand_pressure"],
            "STATE_DERIVED_REQUIREMENT_MINUS_CAPACITY_WITH_UNIT_PRESERVING_MEMORY",
        )
        self.assertEqual(
            semantics["pressure_state"],
            "INTERNAL_NOT_EMITTED_ONLY_QUALIFICATION_EVENTS_VISIBLE",
        )

    def test_gap2_actor_state_preserves_unknown_and_no_generic_capability_unlock(self):
        states = [x for x in self.output["actor_states"] if x["actor_id"] == "AUS"]
        self.assertEqual(len(states), 11)
        self.assertTrue(all(x["spendable_allocation"]["status"] == "UNKNOWN" for x in states))
        self.assertTrue(all(x["spendable_allocation"]["amount"] is None for x in states))
        boundary = self.output["actor_state_boundary"]["actors"][0]
        self.assertEqual(
            boundary["budget"]["spendable_allocation"]["status"], "UNKNOWN"
        )
        self.assertEqual(
            boundary["budget"]["committed_funds"][0]["amount"], 42000000.0
        )
        self.assertEqual(
            boundary["budget"]["committed_funds"][0]["unit"], "AUD"
        )
        self.assertEqual(boundary["ownership"]["status"], "UNKNOWN")
        self.assertEqual(boundary["access_rights"]["status"], "KNOWN_RECORDS")
        self.assertEqual(boundary["installed_capability"]["status"], "UNKNOWN")
        self.assertEqual(self.output["actor_state_events"], [])
        self.assertEqual(self.output["actor_transactions"], [])
        self.assertEqual(self.output["facilities"], [])
        self.assertTrue(all(x["action"] == "WAIT" for x in self.output["decisions"]))
        self.assertTrue(
            all("SPENDABLE_ALLOCATION_UNKNOWN" in x["rationale_codes"] for x in self.output["decisions"])
        )

    def test_implementation_fingerprint_pins_code(self):
        impl = self.output["metadata"]["implementation"]
        self.assertEqual(
            set(impl),
            {
                "runner_sha256",
                "hybrid_engine_sha256",
                "common_helpers_sha256",
                "method_lab_contracts_sha256",
                "infrastructure_contract_sha256",
                "actor_state_contract_sha256",
                "accessibility_contract_sha256",
                "demand_pressure_contract_sha256",
            },
        )
        for value in impl.values():
            self.assertEqual(len(value), 64)
            int(value, 16)

    def test_same_seed_reproduces_byte_identical_payload(self):
        again = build_output(
            input_dir=self.input_dir,
            infrastructure_catalog_path=self.catalog_path,
            seed=42,
        )
        self.assertEqual(
            json.dumps(self.output, sort_keys=True, separators=(",", ":")),
            json.dumps(again, sort_keys=True, separators=(",", ":")),
        )

    def test_cli_roundtrip_matches_library_entrypoint(self):
        with tempfile.TemporaryDirectory() as td:
            output_path = Path(td) / "run.json"
            subprocess.run(
                [
                    "python3",
                    str(HERE / "run_civprop_v1.py"),
                    "--input-dir",
                    str(self.input_dir),
                    "--infrastructure-catalog",
                    str(self.catalog_path),
                    "--seed",
                    "42",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            observed = json.loads(output_path.read_text())
            self.assertEqual(observed, self.output)

    def test_baseline_manifest_pins_golden_output_and_runtime_contract(self):
        manifest = json.loads(BASELINE_MANIFEST.read_text())
        self.assertEqual(manifest["format"], "CIVPROP_ENGINE_V1_EXECUTABLE_BASELINE_MANIFEST")
        self.assertEqual(manifest["baseline_id"], "CIVPROP_ENGINE_V1_GAP4_DEMAND_PRESSURE_BASELINE_2026_09_30")
        self.assertEqual(manifest["runner"]["version"], RUNNER_VERSION)
        self.assertEqual(manifest["output_contract_version"], OUTPUT_CONTRACT_VERSION)
        self.assertEqual(
            manifest["golden_output"]["sha256"],
            hashlib.sha256(GOLDEN.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            manifest["runtime_input"]["sha256"],
            self.output["metadata"]["inputs"]["runtime_input_sha256"],
        )
        self.assertEqual(
            manifest["implementation"],
            self.output["metadata"]["implementation"],
        )

    def test_committed_seed42_golden_output_reproduces(self):
        committed = json.loads(GOLDEN.read_text())
        self.assertEqual(committed, self.output)


if __name__ == "__main__":
    unittest.main()
