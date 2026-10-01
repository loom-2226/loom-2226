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
GOLDEN = HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP12_MATERIALIZATION_SEED42.json"
BASELINE_MANIFEST = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP12_BASELINE_MANIFEST.json"
)
GAP11_GOLDEN = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP11_TRAFFIC_FLEET_SEED42.json"
)
PREVIOUS_GOLDEN = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP7_PRESSURE_OBSERVABILITY_SEED42.json"
)
GAP8_GOLDEN = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP8_RESOURCE_MASS_BALANCE_SEED42.json"
)
GAP9_GOLDEN = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP9_PRODUCTION_ACCOUNTING_SEED42.json"
)
GAP10_GOLDEN = (
    HERE / "baselines" / "CIVPROP_ENGINE_V1_GAP10_POWER_BALANCE_SEED42.json"
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
        self.assertEqual(output["metadata"]["engine"]["version"], "method-reference-v9")
        for key in (
            "actor_state_boundary",
            "accessibility_boundary",
            "demand_pressure_boundary",
            "project_economics_boundary",
            "mission_knowledge_boundary",
            "pressure_observability_boundary",
            "resource_mass_balance_boundary",
            "production_accounting_boundary",
            "power_balance_boundary",
            "traffic_fleet_boundary",
            "facility_site_materialization_boundary",
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "resource_states",
            "resource_flows",
            "facility_production_states",
            "sector_production_states",
            "location_production_states",
            "body_production_states",
            "power_states",
            "power_flows",
            "atlas_power_metrics",
            "traffic_demand_states",
            "traffic_service_states",
            "fleet_states",
            "voyage_states",
            "route_traffic_states",
            "location_traffic_states",
            "traffic_pressure_overrides",
            "atlas_traffic_metrics",
            "materialization_compatibility_states",
            "materialized_modules",
            "sites",
            "materialized_facilities",
            "orbitals",
            "settlements",
            "atlas_facilities",
            "events",
            "flows",
        ):
            self.assertIn(key, output)
        self.assertTrue(output["actor_states"])
        self.assertTrue(output["annual_states"])
        self.assertTrue(output["decisions"])
        self.assertTrue(output["mission_decisions"])
        self.assertTrue(output["knowledge_states"])
        self.assertEqual(output["missions"], [])
        self.assertEqual(output["observations"], [])
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

    def test_evaluator_truth_access_is_bounded_to_mission_and_resource_lanes(self):
        truth = self.input_dir / "truth_v1.json"
        expected = hashlib.sha256(truth.read_bytes()).hexdigest()
        inputs = self.output["metadata"]["inputs"]
        self.assertEqual(inputs["evaluator_truth_sha256"], expected)
        self.assertFalse(inputs["mission_observation_truth_consumed"])
        self.assertTrue(inputs["resource_physical_realization_consumed"])
        self.assertTrue(inputs["evaluator_truth_consumed_by_engine"])
        self.assertEqual(
            inputs["evaluator_truth_access_policy"],
            "OBSERVATION_RUNTIME_AND_RESOURCE_MASS_BALANCE_LANE_ONLY_NOT_ACTOR_INPUT",
        )
        payload = json.dumps(
            {
                key: self.output[key]
                for key in (
                    "actor_states",
                    "actor_transactions",
                    "annual_states",
                    "facilities",
                    "decisions",
                    "mission_decisions",
                    "missions",
                    "observations",
                    "knowledge_states",
                    "events",
                    "flows",
                )
            },
            sort_keys=True,
        )
        self.assertNotIn("grade_index", payload)
        self.assertNotIn('"present":', payload)
        self.assertIn("MOON_POLAR_WATER", payload)

    def test_infrastructure_semantics_are_pinned(self):
        infra = self.output["metadata"]["infrastructure"]
        self.assertEqual(
            infra["catalog_id"],
            "CIVPROP_INFRASTRUCTURE_ARCHETYPES_V1",
        )
        self.assertEqual(
            infra["parameter_set_id"],
            "EARTH_LUNA_PROJECT_ECONOMICS_V1_2026_2036",
        )
        self.assertEqual(
            infra["parameter_status"],
            "PROJECT_ECONOMICS_V1_MIXED_STATUS",
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

    def test_gap1_through_gap12_are_closed_in_default_output(self):
        statuses = {x["gap_id"]: x["status"] for x in self.output["known_gaps"]}
        self.assertEqual(statuses["GAP-001"], "CLOSED")
        self.assertEqual(statuses["GAP-002"], "CLOSED")
        self.assertEqual(statuses["GAP-003"], "CLOSED")
        self.assertEqual(statuses["GAP-004"], "CLOSED")
        self.assertEqual(statuses["GAP-005"], "CLOSED")
        self.assertEqual(statuses["GAP-006"], "CLOSED")
        self.assertEqual(statuses["GAP-007"], "CLOSED")
        self.assertEqual(statuses["GAP-008"], "CLOSED")
        self.assertEqual(statuses["GAP-009"], "CLOSED")
        self.assertEqual(statuses["GAP-010"], "CLOSED")
        self.assertEqual(statuses["GAP-011"], "CLOSED")
        self.assertEqual(statuses["GAP-012"], "CLOSED")
        self.assertEqual(statuses["GAP-013"], "OPEN")

    def test_default_input_has_compiler_provenance(self):
        compiler = self.output["metadata"]["inputs"]["compiler"]
        self.assertEqual(compiler["compiler_id"], "CIVPROP_INPUT_COMPILER_V1")
        self.assertEqual(compiler["compiler_version"], "1.11.0")
        self.assertEqual(compiler["gap_resolution"]["GAP-001"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-002"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-003"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-004"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-005"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-006"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-007"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-008"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-009"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-010"], "CLOSED")
        self.assertEqual(compiler["gap_resolution"]["GAP-011"], "CLOSED")
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
            "VERSIONED_IMMUTABLE_ANNUAL_LEDGER_WITH_RECONSTRUCTABLE_TRANSITIONS",
        )
        self.assertEqual(
            semantics["runtime_reasoning"],
            "EXPLICIT_CODE_RULES_AND_KEYED_STOCHASTICITY_NO_LLM_AUTHORITY",
        )
        self.assertEqual(
            semantics["atlas_role"],
            "ENGINE_STATE_PLUS_DETERMINISTIC_GAP012_MATERIALIZATION_DERIVED_STRATEGIC_METRICS_REMAIN_GAP015",
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
            "VERSIONED_IMMUTABLE_ANNUAL_LEDGER_WITH_RECONSTRUCTABLE_TRANSITIONS",
        )
        self.assertEqual(
            semantics["mission_knowledge"],
            "GENERAL_MISSION_ACTION_CONTRACT_WITH_BINARY_RESOURCE_OBSERVATION_V1",
        )
        self.assertEqual(
            semantics["resource_truth"],
            "EVALUATOR_ONLY_HIDDEN_REALIZATION_BOUNDED_RUNTIME_LANES_ONLY",
        )
        self.assertEqual(
            semantics["knowledge_update"],
            "DETERMINISTIC_BAYESIAN_UPDATE_WITH_DUPLICATE_SCOPE_AND_CHRONOLOGY_GUARDS",
        )

    def test_gap6_default_lane_preserves_private_prior_and_waits_without_invented_value(self):
        boundary = self.output["mission_knowledge_boundary"]
        self.assertEqual(boundary["format"], "CIVPROP_MISSION_KNOWLEDGE_V1")
        self.assertEqual(
            boundary["package_status"],
            "GENERAL_CONTRACT_BINARY_RESOURCE_IMPLEMENTATION_V1",
        )
        self.assertEqual(
            boundary["decision_models"][0]["success_value"]["status"],
            "UNKNOWN",
        )
        self.assertEqual(len(self.output["knowledge_states"]), 1)
        knowledge = self.output["knowledge_states"][0]
        self.assertEqual(knowledge["actor_id"], "AUS")
        self.assertEqual(knowledge["visibility"], "PRIVATE")
        self.assertEqual(knowledge["probability"], 0.45)
        self.assertEqual(self.output["missions"], [])
        self.assertEqual(self.output["observations"], [])
        self.assertEqual(len(self.output["mission_decisions"]), 11)
        self.assertTrue(
            all(x["action"] == "WAIT" for x in self.output["mission_decisions"])
        )
        self.assertTrue(
            all(
                "FOLLOW_ON_VALUE_UNKNOWN" in x["rationale_codes"]
                for x in self.output["mission_decisions"]
            )
        )

    def test_gap7_pressure_ledger_is_reconstructable(self):
        boundary = self.output["pressure_observability_boundary"]
        self.assertEqual(
            boundary["format"],
            "CIVPROP_PRESSURE_OBSERVABILITY_V1",
        )
        self.assertEqual(boundary["contract_version"], "1.0.0")
        self.assertTrue(boundary["emit_contributions"])
        self.assertTrue(boundary["emit_all_qualifications"])
        self.assertTrue(boundary["record_legacy_discharge"])

        self.assertEqual(len(self.output["pressure_states"]), 165)
        self.assertEqual(len(self.output["pressure_contributions"]), 99)
        self.assertEqual(self.output["pressure_qualifications"], [])
        self.assertTrue(
            all(
                x["semantics"] == "CAUSAL_DEMAND_CHANNEL_PRESSURE"
                for x in self.output["pressure_states"]
            )
        )
        self.assertTrue(
            all(x["discharge"] == 0.0 for x in self.output["pressure_states"])
        )

        states = {
            (x["year"], x["location_id"], x["channel_id"]): x
            for x in self.output["pressure_states"]
        }
        first = states[(2026, "EARTH_ORBIT", "HABITAT")]
        self.assertEqual(first["unit"], "person")
        self.assertEqual(first["opening_pressure"], 0.0)
        self.assertEqual(first["required"], 200.0)
        self.assertEqual(first["available"], 50.0)
        self.assertEqual(first["unmet_demand"], 150.0)
        self.assertEqual(first["decay"], 0.60)
        self.assertEqual(first["gain"], 0.24)
        self.assertEqual(first["decayed_pressure"], 0.0)
        self.assertEqual(first["added_pressure"], 36.0)
        self.assertEqual(first["closing_pressure"], 36.0)

        second = states[(2027, "EARTH_ORBIT", "HABITAT")]
        self.assertEqual(second["opening_pressure"], first["closing_pressure"])
        self.assertAlmostEqual(second["decayed_pressure"], 21.6, places=12)
        self.assertAlmostEqual(second["added_pressure"], 36.0, places=12)
        self.assertAlmostEqual(second["closing_pressure"], 57.6, places=12)

        contributions = [
            x
            for x in self.output["pressure_contributions"]
            if x["pressure_state_id"] == first["pressure_state_id"]
        ]
        self.assertEqual(
            {
                (x["component_type"], x["source_id"], x["quantity"], x["sign"])
                for x in contributions
            },
            {
                ("STATE_DRIVER", "state:transient_population", 200.0, 1),
                ("INSTALLED_CAPACITY", "state:habitat", 50.0, -1),
            },
        )

    def test_gap7_observability_does_not_change_gap6_behavior(self):
        previous = json.loads(PREVIOUS_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-007 changed behavioral surface {key}",
            )

    def test_gap8_resource_mass_balance_preserves_unknown_abundance(self):
        boundary = self.output["resource_mass_balance_boundary"]
        self.assertEqual(
            boundary["format"],
            "CIVPROP_RESOURCE_MASS_BALANCE_V1",
        )
        self.assertEqual(boundary["contract_version"], "1.0.0")
        self.assertEqual(
            boundary["resources"][0]["evidence_state"],
            "PRESENT_UNQUANTIFIED",
        )
        process = boundary["process_models"][0]
        self.assertEqual(
            process["extraction_feed_capacity_per_facility"]["status"],
            "UNKNOWN",
        )
        self.assertEqual(
            process["recovery_fraction"]["status"],
            "UNKNOWN",
        )

        self.assertEqual(len(self.output["resource_states"]), 11)
        self.assertEqual(self.output["resource_flows"], [])
        for state in self.output["resource_states"]:
            self.assertEqual(
                state["authority_class"],
                "EVALUATOR_PHYSICAL_STATE",
            )
            self.assertFalse(state["actor_visible"])
            self.assertEqual(
                state["production_status"],
                "NO_ACTIVE_PROCESS_CAPACITY",
            )
            self.assertIsNone(state["opening_stock_tonnes"])
            self.assertIsNone(state["grade_mass_fraction"])
            self.assertEqual(state["extracted_feed_tonnes"], 0.0)
            self.assertEqual(state["recovered_product_tonnes"], 0.0)
            self.assertIsNone(state["closing_stock_tonnes"])
            self.assertIsNone(state["opening_inventory_tonnes"])
            self.assertIsNone(state["closing_inventory_tonnes"])

    def test_gap8_mass_balance_does_not_change_gap7_behavior(self):
        previous = json.loads(PREVIOUS_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-008 changed behavioral surface {key}",
            )

    def test_gap9_production_accounting_preserves_physical_economic_separation(self):
        boundary = self.output["production_accounting_boundary"]
        self.assertEqual(
            boundary["format"],
            "CIVPROP_PRODUCTION_ACCOUNTING_V1",
        )
        self.assertEqual(boundary["contract_version"], "1.2.0")
        self.assertEqual(
            boundary["monetary_stock_unit"],
            "USD_2026_billion",
        )
        self.assertEqual(
            boundary["monetary_flow_unit"],
            "USD_2026_billion/year",
        )
        models = {
            x["project_archetype_id"]: x
            for x in boundary["facility_models"]
        }
        self.assertEqual(
            set(models),
            {
                "LOGISTICS_NODE",
                "POWER_PLANT",
                "HABITAT",
                "RESOURCE_PLANT",
                "INDUSTRIAL_WORKSHOP",
            },
        )
        self.assertEqual(
            models["POWER_PLANT"]["output_source"],
            "POWER_GENERATION",
        )
        self.assertIsNone(models["POWER_PLANT"]["downstream_gap"])
        self.assertEqual(
            models["POWER_PLANT"]["output_unit"],
            "MWh/year",
        )
        self.assertEqual(
            models["LOGISTICS_NODE"]["downstream_gap"],
            "GAP-015",
        )
        self.assertEqual(
            models["HABITAT"]["downstream_gap"],
            "GAP-014",
        )
        for model in models.values():
            self.assertTrue(
                all(
                    model["valuation"][name]["status"] == "UNKNOWN"
                    and model["valuation"][name]["value"] is None
                    for name in (
                        "unit_output_value",
                        "intermediate_consumption_per_output",
                        "operating_cost_per_output",
                    )
                )
            )
        self.assertEqual(self.output["facility_production_states"], [])
        self.assertEqual(self.output["sector_production_states"], [])
        self.assertEqual(self.output["location_production_states"], [])
        self.assertEqual(self.output["body_production_states"], [])
        self.assertEqual(self.output["facilities"], [])

        semantics = self.output["semantics"]
        self.assertEqual(
            semantics["value_added"],
            "GROSS_OUTPUT_MINUS_INTERMEDIATE_CONSUMPTION_OPERATING_COST_IS_DISTINCT",
        )
        self.assertEqual(
            semantics["productive_capital"],
            "GROSS_COMMISSIONED_PROJECT_CAPITAL_NO_DEPRECIATION_BEFORE_GAP013",
        )

    def test_gap9_accounting_does_not_change_gap8_behavior(self):
        previous = json.loads(GAP8_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "resource_states",
            "resource_flows",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-009 changed behavioral surface {key}",
            )

    def test_gap10_power_balance_separates_capacity_load_and_energy(self):
        boundary = self.output["power_balance_boundary"]
        self.assertEqual(boundary["format"], "CIVPROP_POWER_BALANCE_V1")
        self.assertEqual(boundary["contract_version"], "1.0.0")
        self.assertEqual(boundary["scope"], "NON_EARTH_SURFACE")
        self.assertFalse(boundary["timeline_context"]["auto_unlock"])
        self.assertEqual(
            boundary["timeline_context"]["industrial_milestone_id"],
            "ENE-MOD-INDUSTRIAL",
        )
        self.assertEqual(
            boundary["storage_model_status"],
            "NOT_MODELED_V1",
        )
        self.assertEqual(boundary["storage_power_capacity_mw"], 0.0)
        self.assertEqual(boundary["storage_energy_capacity_mwh"], 0.0)

        self.assertEqual(len(self.output["power_states"]), 33)
        self.assertEqual(self.output["power_flows"], [])
        self.assertEqual(len(self.output["atlas_power_metrics"]), 33)
        self.assertFalse(
            any(
                x["location_id"] == "EARTH_SURFACE"
                for x in self.output["power_states"]
            )
        )

        states = {
            (x["year"], x["location_id"]): x
            for x in self.output["power_states"]
        }
        orbit = states[(2026, "EARTH_ORBIT")]
        self.assertEqual(orbit["installed_generation_capacity_mw"], 5.0)
        self.assertEqual(orbit["population_peak_load_mw"], 5.0)
        self.assertEqual(orbit["facility_peak_load_mw"], 0.0)
        self.assertEqual(orbit["peak_demand_mw"], 5.0)
        self.assertIsNone(orbit["average_generation_mw"])
        self.assertIsNone(orbit["firm_generation_capacity_mw"])
        self.assertIsNone(orbit["average_demand_mw"])
        self.assertIsNone(orbit["generated_energy_mwh"])
        self.assertIsNone(orbit["consumed_energy_mwh"])
        self.assertEqual(orbit["energy_balance_status"], "UNKNOWN")
        self.assertIsNone(orbit["power_service_ratio"])
        self.assertEqual(orbit["storage_model_status"], "NOT_MODELED_V1")
        self.assertIsNone(orbit["atlas_power_average_mw"])
        self.assertEqual(orbit["atlas_power_peak_mw"], 5.0)

        luna = states[(2026, "LUNA_SURFACE")]
        self.assertEqual(luna["installed_generation_capacity_mw"], 0.0)
        self.assertEqual(luna["peak_demand_mw"], 0.0)
        self.assertEqual(luna["average_demand_mw"], 0.0)
        self.assertEqual(luna["average_generation_mw"], 0.0)
        self.assertEqual(luna["generated_energy_mwh"], 0.0)
        self.assertEqual(luna["consumed_energy_mwh"], 0.0)
        self.assertEqual(luna["energy_balance_status"], "CLOSED")
        self.assertEqual(luna["power_service_ratio"], 1.0)

        metrics = {
            (x["year"], x["location_id"]): x
            for x in self.output["atlas_power_metrics"]
        }
        for key, state in states.items():
            metric = metrics[key]
            self.assertEqual(
                metric["power_state_id"],
                state["power_state_id"],
            )
            self.assertEqual(
                metric["power_average_mw"],
                state["atlas_power_average_mw"],
            )
            self.assertEqual(
                metric["power_peak_mw"],
                state["atlas_power_peak_mw"],
            )
            self.assertEqual(
                metric["measurement_basis"],
                "ANNUAL_AVERAGE_AND_PEAK_ELECTRICAL_LOAD_DEMAND",
            )

    def test_gap10_power_balance_does_not_change_gap9_behavior(self):
        previous = json.loads(GAP9_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "resource_states",
            "resource_flows",
            "facility_production_states",
            "sector_production_states",
            "location_production_states",
            "body_production_states",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-010 changed pre-existing surface {key}",
            )

    def test_gap11_traffic_fleet_preserves_unassigned_od_and_no_auto_spawn(self):
        boundary = self.output["traffic_fleet_boundary"]
        self.assertEqual(boundary["format"], "CIVPROP_TRAFFIC_FLEET_V1")
        self.assertEqual(boundary["contract_version"], "1.0.0")
        self.assertEqual(
            boundary["demand_assignment_policy"],
            "EXPLICIT_OD_ONLY",
        )
        self.assertFalse(
            boundary["timeline_context"]["auto_spawn_fleet"]
        )
        self.assertEqual(boundary["vehicle_classes"], [])
        self.assertEqual(boundary["fleet_assets"], [])
        self.assertEqual(boundary["demand_allocations"], [])
        self.assertEqual(len(boundary["service_bindings"]), 1)
        self.assertFalse(
            boundary["service_bindings"][0]["generic_demand_eligible"]
        )

        self.assertEqual(len(self.output["traffic_demand_states"]), 33)
        self.assertEqual(len(self.output["traffic_service_states"]), 11)
        self.assertEqual(self.output["fleet_states"], [])
        self.assertEqual(self.output["voyage_states"], [])
        self.assertEqual(self.output["route_traffic_states"], [])
        self.assertEqual(len(self.output["location_traffic_states"]), 33)
        self.assertEqual(self.output["traffic_pressure_overrides"], [])
        self.assertEqual(len(self.output["atlas_traffic_metrics"]), 33)

        orbit = next(
            x
            for x in self.output["traffic_demand_states"]
            if x["year"] == 2026
            and x["location_id"] == "EARTH_ORBIT"
        )
        self.assertEqual(
            orbit["local_transport_requirement_tonnes_year"],
            800.0,
        )
        self.assertEqual(
            orbit["assigned_cargo_demand_tonnes_year"],
            0.0,
        )
        self.assertEqual(
            orbit["unassigned_cargo_demand_tonnes_year"],
            800.0,
        )
        self.assertEqual(orbit["assignment_status"], "UNASSIGNED_OD")
        self.assertEqual(orbit["passenger_demand_status"], "UNKNOWN")

        service = self.output["traffic_service_states"][0]
        self.assertEqual(
            service["service_id"],
            "AUS_ROOVER_CLPS_CT4_IM5",
        )
        self.assertEqual(service["accessibility_status"], "UNKNOWN")
        self.assertFalse(service["generic_demand_eligible"])
        self.assertEqual(service["active_fleet_count"], 0)
        self.assertEqual(service["available_trips"], 0)
        self.assertEqual(service["cargo_capacity_tonnes_year"], 0.0)
        self.assertEqual(
            service["passenger_capacity_persons_year"],
            0.0,
        )

        metrics = {
            (x["year"], x["location_id"]): x
            for x in self.output["atlas_traffic_metrics"]
        }
        states = {
            (x["year"], x["location_id"]): x
            for x in self.output["location_traffic_states"]
        }
        self.assertEqual(set(metrics), set(states))
        for key, state in states.items():
            metric = metrics[key]
            self.assertEqual(
                state["metric_scope"],
                "MODELED_GENERIC_TRAFFIC_ONLY",
            )
            self.assertEqual(state["cargo_throughput_tonnes_year"], 0)
            self.assertEqual(state["passenger_movements_year"], 0)
            self.assertEqual(state["ship_calls_year"], 0)
            self.assertIsNone(state["transport_service_ratio"])
            self.assertEqual(
                metric["cargo_throughput_tonnes_year"],
                state["cargo_throughput_tonnes_year"],
            )
            self.assertEqual(
                metric["passenger_movements_year"],
                state["passenger_movements_year"],
            )
            self.assertEqual(
                metric["ship_calls_year"],
                state["ship_calls_year"],
            )
            self.assertEqual(
                metric["measurement_basis"],
                "ANNUAL_MODELED_NODE_TRAFFIC_INCIDENCE",
            )

    def test_gap12_materialization_is_post_engine_and_conservative(self):
        boundary = self.output["facility_site_materialization_boundary"]
        self.assertEqual(
            boundary["format"],
            "CIVPROP_FACILITY_SITE_MATERIALIZATION_V1",
        )
        self.assertEqual(boundary["contract_version"], "1.0.0")
        self.assertEqual(boundary["colocation_policy"], "EXPLICIT_ONLY")
        self.assertEqual(boundary["naming_policy"], "PRESENTATION_ONLY")
        self.assertEqual(boundary["site_bindings"], [])
        self.assertEqual(boundary["presentation_names"], [])
        self.assertEqual(
            boundary["initial_state_policy"]["status"],
            "UNQUALIFIED_COMPATIBILITY",
        )
        self.assertEqual(
            boundary["initial_state_policy"]["materialization_policy"],
            "NEVER_MATERIALIZE_WITHOUT_MODULE_PROVENANCE",
        )
        self.assertNotIn(
            "STRATEGIC_PORT",
            boundary["atlas_type_rules"]["allowed_outputs"],
        )

        compatibility = {
            x["location_id"]: x
            for x in self.output["materialization_compatibility_states"]
        }
        self.assertEqual(
            set(compatibility),
            {
                "EARTH_ORBIT",
                "LUNA_SURFACE",
                "CISLUNAR_FREE_SPACE",
            },
        )
        self.assertEqual(
            compatibility["EARTH_ORBIT"]["capacities"]["power"],
            5.0,
        )
        self.assertEqual(
            compatibility["EARTH_ORBIT"]["capacities"]["transport"],
            800.0,
        )
        self.assertTrue(
            all(
                x["status"] == "UNQUALIFIED_COMPATIBILITY"
                for x in compatibility.values()
            )
        )
        self.assertEqual(self.output["materialized_modules"], [])
        self.assertEqual(self.output["sites"], [])
        self.assertEqual(self.output["materialized_facilities"], [])
        self.assertEqual(self.output["orbitals"], [])
        self.assertEqual(self.output["settlements"], [])
        self.assertEqual(self.output["atlas_facilities"], [])
        self.assertEqual(
            self.output["metadata"]["engine"]["version"],
            "method-reference-v9",
        )

    def test_gap12_materialization_does_not_change_gap11_behavior(self):
        previous = json.loads(GAP11_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "resource_states",
            "resource_flows",
            "facility_production_states",
            "sector_production_states",
            "location_production_states",
            "body_production_states",
            "power_states",
            "power_flows",
            "atlas_power_metrics",
            "traffic_demand_states",
            "traffic_service_states",
            "fleet_states",
            "voyage_states",
            "route_traffic_states",
            "location_traffic_states",
            "traffic_pressure_overrides",
            "atlas_traffic_metrics",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-012 changed pre-existing surface {key}",
            )

    def test_gap11_traffic_does_not_change_gap10_behavior(self):
        previous = json.loads(GAP10_GOLDEN.read_text())
        for key in (
            "actor_states",
            "actor_transactions",
            "actor_state_events",
            "annual_states",
            "facilities",
            "decisions",
            "mission_decisions",
            "missions",
            "observations",
            "knowledge_states",
            "pressure_states",
            "pressure_contributions",
            "pressure_qualifications",
            "resource_states",
            "resource_flows",
            "facility_production_states",
            "sector_production_states",
            "location_production_states",
            "body_production_states",
            "power_states",
            "power_flows",
            "atlas_power_metrics",
            "events",
            "flows",
        ):
            self.assertEqual(
                self.output[key],
                previous[key],
                f"GAP-011 changed pre-existing surface {key}",
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
                "project_economics_contract_sha256",
                "project_economics_parameter_set_sha256",
                "mission_knowledge_contract_sha256",
                "mission_knowledge_parameter_set_sha256",
                "mission_lane_sha256",
                "pressure_observability_contract_sha256",
                "pressure_observability_parameter_set_sha256",
                "pressure_lane_sha256",
                "resource_mass_balance_contract_sha256",
                "resource_mass_balance_parameter_set_sha256",
                "resource_lane_sha256",
                "production_accounting_contract_sha256",
                "production_accounting_parameter_set_sha256",
                "production_lane_sha256",
                "power_balance_contract_sha256",
                "power_balance_parameter_set_sha256",
                "power_lane_sha256",
                "traffic_fleet_contract_sha256",
                "traffic_fleet_parameter_set_sha256",
                "traffic_lane_sha256",
                "facility_site_materialization_contract_sha256",
                "facility_site_materialization_parameter_set_sha256",
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
        self.assertEqual(manifest["baseline_id"], "CIVPROP_ENGINE_V1_GAP12_MATERIALIZATION_BASELINE_2026_10_02")
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
