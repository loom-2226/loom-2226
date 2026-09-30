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
GOLDEN = HERE / "baselines" / "CIVPROP_ENGINE_V1_SYNTHETIC_SEED42.json"
BASELINE_MANIFEST = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_EXECUTABLE_BASELINE_MANIFEST.json"
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
        for key in ("annual_states", "facilities", "decisions", "events", "flows"):
            self.assertIn(key, output)
        self.assertTrue(output["annual_states"])
        self.assertTrue(output["facilities"])
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
                for key in ("annual_states", "facilities", "decisions", "events", "flows")
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
        self.assertEqual(manifest["baseline_id"], "CIVPROP_ENGINE_V1_EXECUTABLE_BASELINE_2026_09_30")
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
