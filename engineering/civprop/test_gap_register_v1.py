"""Contract tests for the CIVPROP gap register and post-gap handoff plan."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from .run_civprop_v1 import _base_gaps, build_output, default_paths


HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "gap_register_v1.json"
POST_GAP_DOC = HERE.parents[1] / "docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md"


class CivpropGapRegisterV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text())
        cls.input_dir, cls.catalog_path = default_paths()
        cls.current_output = build_output(
            input_dir=cls.input_dir,
            infrastructure_catalog_path=cls.catalog_path,
            seed=42,
        )

    def test_registry_has_all_15_gaps_once(self):
        gaps = self.registry["gaps"]
        self.assertEqual(len(gaps), 15)
        self.assertEqual(
            [g["gap_id"] for g in gaps],
            [f"GAP-{i:03d}" for i in range(1, 16)],
        )

    def test_names_and_meanings_match_locked_runner(self):
        expected = {
            g["gap_id"]: (g["name"], g["meaning"])
            for g in _base_gaps()
        }
        observed = {
            g["gap_id"]: (g["name"], g["meaning"])
            for g in self.registry["gaps"]
        }
        self.assertEqual(observed, expected)

    def test_current_status_matches_default_executable_output(self):
        expected = {
            g["gap_id"]: g["status"]
            for g in self.current_output["known_gaps"]
        }
        observed = {
            g["gap_id"]: g["current_status"]
            for g in self.registry["gaps"]
        }
        self.assertEqual(observed, expected)
        self.assertEqual(observed["GAP-001"], "CLOSED")
        self.assertEqual(observed["GAP-002"], "CLOSED")
        self.assertEqual(observed["GAP-003"], "CLOSED")
        self.assertEqual(observed["GAP-004"], "CLOSED")
        self.assertEqual(observed["GAP-005"], "CLOSED")
        self.assertEqual(observed["GAP-006"], "CLOSED")
        self.assertEqual(observed["GAP-007"], "CLOSED")
        self.assertEqual(observed["GAP-008"], "CLOSED")
        self.assertEqual(observed["GAP-009"], "CLOSED")
        self.assertEqual(observed["GAP-010"], "CLOSED")
        self.assertEqual(observed["GAP-011"], "CLOSED")
        self.assertTrue(all(observed[f"GAP-{i:03d}"] == "OPEN" for i in range(12, 16)))

    def test_every_gap_has_exit_criteria_and_handoff(self):
        for gap in self.registry["gaps"]:
            self.assertTrue(gap["exit_criteria"], gap["gap_id"])
            self.assertTrue(gap["current_evidence"], gap["gap_id"])
            self.assertTrue(gap["next_action"], gap["gap_id"])
            self.assertTrue(gap["output_or_contract_affected"], gap["gap_id"])
            self.assertIn(gap["current_status"], {"OPEN", "CLOSED", "BLOCKED"})

    def test_gap1_closure_references_promoted_artifacts(self):
        gap1 = self.registry["gaps"][0]
        self.assertEqual(gap1["current_status"], "CLOSED")
        refs = set(gap1["current_evidence"])
        self.assertIn("engineering/civprop/compile_inputs_v1.py", refs)
        self.assertIn(
            "engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/compiler_manifest_v1.json",
            refs,
        )
        self.assertIn("docs/civprop/CIVPROP_INPUT_COMPILER_V1.md", refs)

    def test_gap2_closure_references_promoted_artifacts(self):
        gap2 = self.registry["gaps"][1]
        self.assertEqual(gap2["current_status"], "CLOSED")
        refs = set(gap2["current_evidence"])
        self.assertIn("engineering/civprop/contracts/actor_state_v1.py", refs)
        self.assertIn("engineering/civprop/compile_inputs_v1.py", refs)
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP2_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn("docs/civprop/CIVPROP_ACTOR_STATE_AND_BUDGETS_V1.md", refs)

    def test_gap3_closure_references_transport_accessibility_artifacts(self):
        gap3 = self.registry["gaps"][2]
        self.assertEqual(gap3["current_status"], "CLOSED")
        refs = set(gap3["current_evidence"])
        self.assertIn("engineering/civprop/contracts/accessibility_v1.py", refs)
        self.assertIn(
            "engineering/civprop/civprop0/runs/roover_transport_mid2030_v1.json",
            refs,
        )
        self.assertIn("engineering/civprop/compile_inputs_v1.py", refs)
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP3_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn("docs/civprop/CIVPROP_TRANSPORT_ACCESSIBILITY_V1.md", refs)

    def test_gap4_closure_references_demand_pressure_artifacts(self):
        gap4 = self.registry["gaps"][3]
        self.assertEqual(gap4["current_status"], "CLOSED")
        refs = set(gap4["current_evidence"])
        self.assertIn("engineering/civprop/contracts/demand_pressure_v1.py", refs)
        self.assertIn(
            "engineering/civprop/contracts/test_demand_pressure_v1.py",
            refs,
        )
        self.assertIn("engineering/civprop/compile_inputs_v1.py", refs)
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP4_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn("docs/civprop/CIVPROP_DEMAND_PRESSURE_V1.md", refs)

    def test_gap5_closure_references_project_economics_artifacts(self):
        gap5 = self.registry["gaps"][4]
        self.assertEqual(gap5["current_status"], "CLOSED")
        refs = set(gap5["current_evidence"])
        self.assertIn("engineering/civprop/contracts/project_economics_v1.py", refs)
        self.assertIn("engineering/civprop/contracts/project_economics_v1.json", refs)
        self.assertIn(
            "engineering/civprop/contracts/test_project_economics_v1.py",
            refs,
        )
        self.assertIn("engineering/civprop/compile_inputs_v1.py", refs)
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP5_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn("docs/civprop/CIVPROP_PROJECT_ECONOMICS_V1.md", refs)

    def test_gap6_closure_references_mission_knowledge_artifacts(self):
        gap6 = self.registry["gaps"][5]
        self.assertEqual(gap6["current_status"], "CLOSED")
        refs = set(gap6["current_evidence"])
        self.assertIn("engineering/civprop/contracts/mission_knowledge_v1.py", refs)
        self.assertIn("engineering/civprop/contracts/mission_knowledge_v1.json", refs)
        self.assertIn(
            "engineering/civprop/contracts/test_mission_knowledge_v1.py",
            refs,
        )
        self.assertIn("engineering/civprop/method_lab/mission_lane_v1.py", refs)
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP6_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn(
            "docs/civprop/CIVPROP_MISSIONS_AND_KNOWLEDGE_V1.md",
            refs,
        )

    def test_gap7_closure_references_pressure_observability_artifacts(self):
        gap7 = self.registry["gaps"][6]
        self.assertEqual(gap7["current_status"], "CLOSED")
        refs = set(gap7["current_evidence"])
        self.assertIn(
            "engineering/civprop/contracts/pressure_observability_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/contracts/test_pressure_observability_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/method_lab/pressure_lane_v1.py",
            refs,
        )
        self.assertIn("engineering/civprop/run_civprop_v1.py", refs)
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP7_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn(
            "docs/civprop/CIVPROP_PRESSURE_OBSERVABILITY_V1.md",
            refs,
        )

    def test_gap8_closure_references_resource_mass_balance_artifacts(self):
        gap8 = self.registry["gaps"][7]
        self.assertEqual(gap8["current_status"], "CLOSED")
        refs = set(gap8["current_evidence"])
        self.assertIn(
            "engineering/civprop/contracts/resource_mass_balance_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/contracts/test_resource_mass_balance_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/method_lab/resource_lane_v1.py",
            refs,
        )
        self.assertIn(
            "dev/solar_civprop_resource_contract/RESOURCE_STATE_CONTRACT_V1.sql",
            refs,
        )
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP8_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn(
            "docs/civprop/CIVPROP_RESOURCE_MASS_BALANCE_V1.md",
            refs,
        )

    def test_gap9_closure_references_production_accounting_artifacts(self):
        gap9 = self.registry["gaps"][8]
        self.assertEqual(gap9["current_status"], "CLOSED")
        refs = set(gap9["current_evidence"])
        self.assertIn(
            "engineering/civprop/contracts/production_accounting_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/contracts/test_production_accounting_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/method_lab/production_lane_v1.py",
            refs,
        )
        self.assertIn(
            "data/postgres/migrations/004_earth_temporal_authority.sql",
            refs,
        )
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP9_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn(
            "docs/civprop/CIVPROP_PRODUCTION_ACCOUNTING_V1.md",
            refs,
        )

    def test_gap10_closure_references_power_balance_artifacts(self):
        gap10 = self.registry["gaps"][9]
        self.assertEqual(gap10["current_status"], "CLOSED")
        refs = set(gap10["current_evidence"])
        self.assertIn(
            "engineering/civprop/contracts/power_balance_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/contracts/test_power_balance_v1.py",
            refs,
        )
        self.assertIn(
            "engineering/civprop/method_lab/power_lane_v1.py",
            refs,
        )
        self.assertIn(
            "docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md",
            refs,
        )
        self.assertIn(
            "data/postgres/evidence/LOOM_CERES_MVP_A_FIELD_QUALIFICATION_v0.1.json",
            refs,
        )
        self.assertIn(
            "engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP10_BASELINE_MANIFEST.json",
            refs,
        )
        self.assertIn(
            "docs/civprop/CIVPROP_POWER_BALANCE_V1.md",
            refs,
        )

    def test_gap11_closure_references_traffic_fleet_artifacts(self):
        gap11 = self.registry["gaps"][10]
        self.assertEqual(gap11["current_status"], "CLOSED")
        refs = set(gap11["current_evidence"])
        self.assertIn("engineering/civprop/contracts/traffic_fleet_v1.py", refs)
        self.assertIn("engineering/civprop/contracts/test_traffic_fleet_v1.py", refs)
        self.assertIn("engineering/civprop/method_lab/traffic_lane_v1.py", refs)
        self.assertIn("engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP11_BASELINE_MANIFEST.json", refs)
        self.assertIn("docs/civprop/CIVPROP_TRAFFIC_FLEET_V1.md", refs)

    def test_post_gap_plan_has_ordered_gates(self):
        plan = self.registry["post_gap_plan"]
        self.assertEqual(
            [x["gate_id"] for x in plan],
            [
                "POST-01",
                "POST-02",
                "POST-03",
                "POST-04",
                "POST-05",
                "POST-06",
                "POST-07",
            ],
        )
        for gate in plan:
            self.assertTrue(gate["name"])
            self.assertTrue(gate["purpose"])
            self.assertTrue(gate["exit_criteria"])

    def test_post_gap_plan_preserves_engine_replaceability(self):
        final = self.registry["post_gap_plan"][-1]
        self.assertEqual(final["gate_id"], "POST-07")
        self.assertIn("alternative propagation engines", final["purpose"].lower())
        self.assertIn("same input/output contracts", final["purpose"].lower())

    def test_reference_run_is_not_automatically_canon(self):
        post = {x["gate_id"]: x for x in self.registry["post_gap_plan"]}
        self.assertIn("not canon", post["POST-03"]["purpose"].lower())
        self.assertIn("comparator", post["POST-05"]["purpose"].lower())

    def test_document_exists_and_names_authoritative_registry(self):
        text = POST_GAP_DOC.read_text()
        self.assertIn("engineering/civprop/gap_register_v1.json", text)
        self.assertIn("GAP-001", text)
        self.assertIn("POST-01", text)
        self.assertIn("POST-07", text)
        self.assertIn(self.registry["as_of_main_commit"], text)


if __name__ == "__main__":
    unittest.main()
