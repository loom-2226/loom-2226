"""Contract tests for GAP-001: real CIVPROP input compiler V1."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from .compile_inputs_v1 import (
    AUTHORITY_CAPTURE_FORMAT,
    COMPILED_AUTHORITY,
    COMPILED_FIXTURE_ID,
    compile_from_capture,
    default_capture_path,
    default_output_dir,
)
from .method_lab.contracts import load_bundle
from .run_civprop_v1 import build_output, default_paths as runner_default_paths


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]


class CivpropRealInputCompilerV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture_path = default_capture_path()
        cls.capture = json.loads(cls.capture_path.read_text())
        cls.output_dir = default_output_dir()
        cls.bundle = load_bundle(cls.output_dir)
        cls.scenario = json.loads((cls.output_dir / "scenario_v1.json").read_text())
        cls.compiler_manifest = json.loads(
            (cls.output_dir / "compiler_manifest_v1.json").read_text()
        )

    def test_authority_capture_is_real_and_pinned(self):
        c = self.capture
        self.assertEqual(c["format"], AUTHORITY_CAPTURE_FORMAT)
        self.assertEqual(c["earth"]["snapshot"]["snapshot_id"], "earth-v0-1-9934d0ac-20260925")
        self.assertEqual(c["earth"]["snapshot"]["state"], "VALIDATED")
        self.assertEqual(c["timeline"]["snapshot"]["snapshot_id"], "timeline-v0-1-0232bf23494f-20260925")
        self.assertEqual(c["timeline"]["snapshot"]["state"], "VALIDATED")
        self.assertEqual(c["solar"]["ephemeris_source"]["ephemeris_source_id"], "DE440")
        self.assertEqual(c["solar"]["ephemeris_source"]["status"], "QUALIFIED")
        self.assertTrue(c["solar"]["ephemeris_source"]["navigation_grade"])
        self.assertEqual(c["resource"]["assertion"]["key"], "MOON_POLAR_WATER_ICE")
        self.assertEqual(c["actor"]["earth_area"]["iso3"], "AUS")
        self.assertEqual(c["actor"]["roover_service"]["actor_id"], "AUS")

    def test_compiled_package_uses_locked_compatibility_envelope(self):
        self.assertEqual(self.bundle.scenario.format, "CIVPROP_METHOD_LAB_SCENARIO_V1")
        self.assertEqual(self.bundle.scenario.fixture_id, COMPILED_FIXTURE_ID)
        self.assertEqual(self.bundle.manifest["authority"], COMPILED_AUTHORITY)
        self.assertEqual(
            self.scenario["classification"],
            "COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1",
        )

    def test_real_earth_boundary_is_mapped_where_semantics_align(self):
        earth = next(
            x for x in self.scenario["locations"] if x["location_id"] == "EARTH_SURFACE"
        )
        self.assertEqual(
            earth["initial_state"]["biological_population"],
            self.capture["earth"]["global_2026"]["biological_population"],
        )
        self.assertEqual(
            earth["initial_state"]["workforce"],
            self.capture["earth"]["global_2026"]["legacy_employment"],
        )
        self.assertEqual(
            earth["initial_state"]["capacities"]["habitat"],
            self.capture["earth"]["global_2026"]["biological_population"],
        )

    def test_earth_long_run_authority_is_preserved_not_squeezed_into_wrong_fields(self):
        context = self.scenario["authority_context"]["earth"]
        self.assertEqual(len(context["aus_demographic_2026_2036"]), 11)
        self.assertEqual(len(context["aus_economic_2026_2036"]), 11)
        self.assertEqual(context["aus_demographic_2026_2036"][0]["year"], 2026)
        self.assertEqual(context["aus_economic_2026_2036"][-1]["year"], 2036)
        # Real USD-like national capital is evidence context, not scenario_credit.
        earth = next(
            x for x in self.scenario["locations"] if x["location_id"] == "EARTH_SURFACE"
        )
        self.assertNotEqual(
            earth["initial_state"]["capital"],
            self.capture["earth"]["global_2026"]["economic_capital"],
        )

    def test_gap2_actor_state_replaces_budget_and_generic_capability_placeholders(self):
        actors = self.scenario["actors"]
        self.assertEqual(actors, [{"actor_id": "AUS", "actor_type": "STATE"}])
        self.assertNotIn("starting_capital", actors[0])
        self.assertNotIn("annual_capital_inflow", actors[0])

        actor_state = self.scenario["actor_state_v1"]
        self.assertEqual(actor_state["format"], "CIVPROP_ACTOR_STATE_V1")
        aus = actor_state["actors"][0]
        spendable = aus["budget"]["spendable_allocation"]
        self.assertEqual(spendable["status"], "UNKNOWN")
        self.assertIsNone(spendable["amount"])
        self.assertIsNone(spendable["unit"])

        commitments = aus["budget"]["committed_funds"]
        self.assertEqual(commitments[0]["amount"], 42000000)
        self.assertEqual(commitments[0]["unit"], "AUD")
        self.assertIn("ROO_VER", commitments[0]["scope"])

        self.assertEqual(self.scenario["actor_capability"], [])
        assumptions = {x["assumption_id"] for x in self.scenario["assumption_register"]}
        self.assertNotIn("ASSUME-GAP002-AUS-BUDGET", assumptions)
        self.assertNotIn("ASSUME-GAP002-AUS-CAPABILITIES", assumptions)

    def test_gap3_replaces_synthetic_accessibility_with_versioned_service(self):
        self.assertNotIn("accessibility", self.scenario)
        package = self.scenario["accessibility_v1"]
        self.assertEqual(package["format"], "CIVPROP_ACCESSIBILITY_V1")
        self.assertEqual(package["contract_version"], "1.0.0")
        self.assertEqual(package["epoch_policy"], "ANNUAL_REFERENCE_EPOCH_JULY_01_UTC")
        sample = package["geometry_samples"][0]
        self.assertEqual(sample["epoch_utc"], "2030-07-01T00:00:00Z")
        self.assertEqual(sample["reference_frame"], "J2000/ECLIPTIC")
        self.assertTrue(sample["navigation_grade"])
        self.assertGreater(sample["straight_line_separation_km"], 0)
        service = package["service_paths"][0]
        self.assertEqual(service["actor_id"], "AUS")
        self.assertEqual(service["subject_id"], "ROO_VER_WITH_NASA_MNP")
        self.assertEqual(service["status"], "UNKNOWN")
        self.assertEqual(service["generalized_cost"]["status"], "UNKNOWN")
        self.assertIsNone(service["generalized_cost"]["value"])
        assumptions = {x["assumption_id"] for x in self.scenario["assumption_register"]}
        self.assertNotIn("ASSUME-GAP003-ACCESSIBILITY", assumptions)

    def test_gap4_replaces_exogenous_demand_series_with_causal_stock_flow_model(self):
        self.assertNotIn("demand_signals", self.scenario)
        package = self.scenario["demand_pressure_v1"]
        self.assertEqual(package["format"], "CIVPROP_DEMAND_PRESSURE_V1")
        self.assertEqual(package["contract_version"], "1.0.0")
        self.assertEqual(
            package["parameter_status"],
            "UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1",
        )
        channels = {x["channel_id"]: x for x in package["channels"]}
        self.assertEqual(
            set(channels),
            {"HABITAT", "TRANSPORT", "INDUSTRIAL", "RESOURCE", "POWER"},
        )
        self.assertEqual(channels["HABITAT"]["unit"], "person")
        self.assertEqual(channels["POWER"]["unit"], "MW")
        self.assertEqual(channels["TRANSPORT"]["unit"], "tonnes/year")
        self.assertEqual(channels["INDUSTRIAL"]["unit"], "tonnes/year")
        self.assertEqual(channels["RESOURCE"]["unit"], "tonnes/year")
        assumptions = {x["assumption_id"] for x in self.scenario["assumption_register"]}
        self.assertNotIn("ASSUME-GAP004-DEMAND", assumptions)

    def test_gap5_replaces_method_lab_project_economics_with_typed_parameter_set(self):
        package = self.scenario["project_economics_v1"]
        self.assertEqual(package["format"], "CIVPROP_PROJECT_ECONOMICS_V1")
        self.assertEqual(package["contract_version"], "1.0.0")
        self.assertEqual(package["capital_unit"], "USD_2026_billion")
        serialized = json.dumps(package, sort_keys=True)
        self.assertNotIn("METHOD_LAB_SYNTHETIC_V1", serialized)
        self.assertNotIn("scenario_credit", serialized)
        self.assertNotIn("scenario_capacity_unit", serialized)
        self.assertEqual(
            self.scenario["units"]["project_capital"],
            "USD_2026_billion",
        )
        self.assertEqual(self.scenario["units"]["transport"], "tonnes/year")
        self.assertEqual(self.scenario["units"]["industrial"], "tonnes/year")
        self.assertEqual(self.scenario["units"]["resource"], "tonnes/year")
        assumptions = {x["assumption_id"] for x in self.scenario["assumption_register"]}
        self.assertNotIn("ASSUME-GAP005-PROJECT-ECONOMICS", assumptions)

    def test_other_unresolved_engine_inputs_are_not_disguised_as_authority(self):
        assumptions = self.scenario["assumption_register"]
        gaps = {x["gap_id"] for x in assumptions}
        self.assertNotIn("GAP-002", gaps)
        self.assertNotIn("GAP-003", gaps)
        self.assertNotIn("GAP-004", gaps)
        self.assertNotIn("GAP-005", gaps)
        self.assertIn("GAP-006", gaps)
        for row in assumptions:
            self.assertIn(row["status"], {"EXPLICIT_PLACEHOLDER", "COMPATIBILITY_BOUNDARY"})
            self.assertTrue(row["semantics"])

    def test_real_timeline_rules_and_milestones_are_frozen_in_context(self):
        timeline = self.scenario["authority_context"]["timeline"]
        rules = {x["rule_key"] for x in timeline["interpretation_rules"]}
        self.assertIn("DATE_DOES_NOT_UNLOCK", rules)
        self.assertIn("UNKNOWN_NOT_ZERO", rules)
        milestones = {x["milestone_id"] for x in timeline["milestones_2026_2036"]}
        self.assertIn("TRN-2031-LOOK", milestones)
        self.assertIn("COM-MOD-LUNAR", milestones)

    def test_real_solar_and_resource_authority_are_frozen_in_context(self):
        solar = self.scenario["authority_context"]["solar"]
        self.assertEqual({x["body_id"] for x in solar["bodies"]}, {"EARTH", "MOON"})
        self.assertEqual(solar["ephemeris_source"]["ephemeris_source_id"], "DE440")
        resource = self.scenario["authority_context"]["resource"]
        self.assertEqual(resource["assertion"]["body_id"], "MOON")
        self.assertEqual(resource["assertion"]["abundance_semantics"], "PRESENT_UNQUANTIFIED")
        # Numeric prior remains explicitly an assumption because evidence does not provide one.
        belief = self.scenario["resource_beliefs"][0]
        self.assertEqual(belief["evidence_status"], "EMPIRICAL_PRESENCE_PLUS_SCENARIO_PRIOR")
        self.assertEqual(belief["prior_probability"], 0.45)

    def test_actor_authority_preserves_scope_instead_of_granting_generic_access(self):
        actor_ctx = self.scenario["authority_context"]["actor"]
        self.assertEqual(actor_ctx["earth_area"]["iso3"], "AUS")
        self.assertEqual(actor_ctx["roover_service"]["destination_scope"], "LUNAR_SOUTH_POLE_REGION")
        self.assertIsNone(actor_ctx["roover_service"]["delivery_capacity_kg"])
        self.assertIn("Fleet SPIDER", actor_ctx["fleet_access"]["case"]["scope"])
        government = actor_ctx["aus_government_access"]["case"]
        self.assertEqual(government["actor_id"], "AUS")
        self.assertEqual(government["payload"], "ROO_VER_WITH_NASA_MNP")
        self.assertIn("not sovereign lunar transport", government["limitations"][0])
        access = self.scenario["actor_state_v1"]["actors"][0]["access_rights"]["records"][0]
        self.assertEqual(access["subject_id"], "ROO_VER")
        self.assertNotEqual(access["subject_id"], "FLEET_SPACE_TECHNOLOGIES")

    def test_compiler_manifest_closes_gap1_through_gap5(self):
        manifest = self.compiler_manifest
        self.assertEqual(manifest["format"], "CIVPROP_INPUT_COMPILER_MANIFEST_V1")
        self.assertEqual(len(manifest["compiler_source_sha256"]), 64)
        int(manifest["compiler_source_sha256"], 16)
        self.assertEqual(manifest["gap_resolution"]["GAP-001"], "CLOSED")
        self.assertEqual(manifest["gap_resolution"]["GAP-002"], "CLOSED")
        self.assertEqual(manifest["gap_resolution"]["GAP-003"], "CLOSED")
        self.assertEqual(manifest["gap_resolution"]["GAP-004"], "CLOSED")
        self.assertEqual(manifest["gap_resolution"]["GAP-005"], "CLOSED")
        self.assertEqual(manifest["gap_resolution"]["GAP-006"], "OPEN")
        self.assertEqual(manifest["runtime_input"]["fixture_id"], COMPILED_FIXTURE_ID)

    def test_compiler_is_deterministic_from_frozen_capture(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "compiled"
            compile_from_capture(self.capture_path, out)
            for name in (
                "scenario_v1.json",
                "truth_v1.json",
                "manifest_v1.json",
                "compiler_manifest_v1.json",
            ):
                self.assertEqual(
                    (out / name).read_bytes(),
                    (self.output_dir / name).read_bytes(),
                    name,
                )

    def test_compiler_output_does_not_depend_on_capture_filesystem_location(self):
        with tempfile.TemporaryDirectory() as td:
            external_capture = Path(td) / "authority.json"
            external_capture.write_bytes(self.capture_path.read_bytes())
            out = Path(td) / "compiled"
            compile_from_capture(external_capture, out)
            for name in (
                "scenario_v1.json",
                "truth_v1.json",
                "manifest_v1.json",
                "compiler_manifest_v1.json",
            ):
                self.assertEqual(
                    (out / name).read_bytes(),
                    (self.output_dir / name).read_bytes(),
                    name,
                )

    def test_runner_default_switches_to_compiled_gap1_package(self):
        input_dir, _ = runner_default_paths()
        self.assertEqual(input_dir.resolve(), self.output_dir.resolve())

    def test_locked_runner_accepts_compiled_package(self):
        catalog = HERE / "contracts" / "infrastructure_archetypes_v1.json"
        output = build_output(
            input_dir=self.output_dir,
            infrastructure_catalog_path=catalog,
            seed=42,
        )
        self.assertEqual(
            output["metadata"]["inputs"]["fixture_id"],
            COMPILED_FIXTURE_ID,
        )
        self.assertEqual(
            output["metadata"]["inputs"]["input_authority"],
            COMPILED_AUTHORITY,
        )
        gap1 = next(x for x in output["known_gaps"] if x["gap_id"] == "GAP-001")
        gap2 = next(x for x in output["known_gaps"] if x["gap_id"] == "GAP-002")
        gap3 = next(x for x in output["known_gaps"] if x["gap_id"] == "GAP-003")
        gap4 = next(x for x in output["known_gaps"] if x["gap_id"] == "GAP-004")
        gap5 = next(x for x in output["known_gaps"] if x["gap_id"] == "GAP-005")
        self.assertEqual(gap1["status"], "CLOSED")
        self.assertEqual(gap2["status"], "CLOSED")
        self.assertEqual(gap3["status"], "CLOSED")
        self.assertEqual(gap4["status"], "CLOSED")
        self.assertEqual(gap5["status"], "CLOSED")
        self.assertTrue(output["actor_states"])
        self.assertTrue(output["annual_states"])
        self.assertTrue(output["events"])


if __name__ == "__main__":
    unittest.main()
