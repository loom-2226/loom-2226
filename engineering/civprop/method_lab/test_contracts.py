"""Method Lab V1 contract tests. No production DB/network writes."""
from dataclasses import replace
from pathlib import Path
import hashlib
import json
import unittest

from .contracts import (
    CapacityVector,
    DecisionRecord,
    EventRecord,
    FacilityRecord,
    LabResult,
    LocationState,
    PropagationEngine,
    RunMetadata,
    canonical_json,
    load_bundle,
    validate_result,
)


HERE = Path(__file__).resolve().parent


class MethodLabInputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(HERE)

    def test_manifest_and_payload_hashes_are_pinned(self):
        manifest = json.loads((HERE / "manifest_v1.json").read_text())
        for name, expected in manifest["sha256"].items():
            self.assertEqual(
                hashlib.sha256((HERE / name).read_bytes()).hexdigest(),
                expected,
            )
        self.assertEqual(self.bundle.manifest["format"], "CIVPROP_METHOD_LAB_BUNDLE_V1")

    def test_fixture_is_small_and_spatially_complete_for_lab(self):
        scenario = self.bundle.scenario
        self.assertEqual((scenario.start_year, scenario.end_year), (2026, 2036))
        self.assertEqual(len(scenario.actors), 2)
        self.assertEqual(
            {x.location_id for x in scenario.locations},
            {"EARTH_SURFACE", "EARTH_ORBIT", "LUNA_SURFACE", "CISLUNAR_FREE_SPACE"},
        )
        self.assertEqual(
            {x.placement for x in scenario.locations},
            {"SURFACE", "ORBITAL", "FREE_SPACE"},
        )

    def test_hidden_truth_is_not_in_actor_visible_scenario(self):
        visible = json.loads((HERE / "scenario_v1.json").read_text())
        flattened = canonical_json(visible).lower()
        self.assertNotIn('"present":', flattened)
        self.assertNotIn('"grade_index":', flattened)
        self.assertIn("moon_polar_water", flattened)
        self.assertEqual(self.bundle.truth.resources[0].resource_id, "MOON_POLAR_WATER")

    def test_timeline_frontier_is_separate_from_actor_access(self):
        scenario = self.bundle.scenario
        frontiers = {x.tech_id: x.frontier_year for x in scenario.technology_frontier}
        access = {(x.actor_id, x.tech_id): x for x in scenario.actor_capability}
        self.assertEqual(frontiers["LUNAR_SURFACE_OPERATIONS"], 2028)
        self.assertEqual(access[("LAB_PUBLIC", "LUNAR_SURFACE_OPERATIONS")].valid_from, 2029)
        self.assertEqual(access[("LAB_COMMERCIAL", "LUNAR_SURFACE_OPERATIONS")].status, "CONDITIONAL")

    def test_unknown_accessibility_survives_fixture(self):
        statuses = {
            point.status
            for profile in self.bundle.scenario.accessibility
            for point in profile.years
        }
        self.assertIn("UNKNOWN", statuses)
        self.assertIn("FEASIBLE", statuses)

    def test_project_archetypes_are_generic_not_preassigned_destinations(self):
        scenario = json.loads((HERE / "scenario_v1.json").read_text())
        for archetype in scenario["project_archetypes"]:
            self.assertNotIn("target_location_id", archetype)
            self.assertTrue(archetype["allowed_placements"])
            self.assertGreater(archetype["capital_cost"], 0)
            self.assertGreaterEqual(archetype["construction_lag_years"], 1)


class MethodLabOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(HERE)

    def result(self):
        return LabResult(
            metadata=RunMetadata(
                format="CIVPROP_METHOD_LAB_RESULT_V1",
                run_id="run-test",
                engine_id="dummy",
                engine_version="0",
                input_bundle_sha256=self.bundle.bundle_sha256,
                seed=42,
                start_year=2026,
                end_year=2036,
            ),
            annual_states=(
                LocationState(
                    year=2026,
                    location_id="EARTH_SURFACE",
                    biological_population=1_000_000,
                    transient_population=0,
                    workforce=500_000,
                    capital=100,
                    capacities=CapacityVector(power=100, industrial=100, transport=100, habitat=1_000_000),
                ),
                LocationState(
                    year=2036,
                    location_id="LUNA_SURFACE",
                    biological_population=0,
                    transient_population=0,
                    workforce=0,
                    capital=0,
                    capacities=CapacityVector(),
                ),
            ),
            facilities=(),
            decisions=(
                DecisionRecord(
                    decision_id="d1",
                    year=2026,
                    actor_id="LAB_PUBLIC",
                    action="WAIT",
                    target_location_id="LUNA_SURFACE",
                    project_archetype_id=None,
                    status="DECLINED",
                    rationale_codes=("NO_FEASIBLE_PROJECT",),
                ),
            ),
            events=(
                EventRecord(
                    event_id="e1",
                    year=2026,
                    event_type="RUN_STARTED",
                    actor_id=None,
                    location_id=None,
                    parent_event_ids=(),
                ),
            ),
            flows=(),
        )

    def test_minimal_result_validates_and_serializes_deterministically(self):
        result = self.result()
        validate_result(result, self.bundle)
        self.assertEqual(canonical_json(result), canonical_json(result))

    def test_negative_state_fails_closed(self):
        bad = replace(
            self.result(),
            annual_states=(
                replace(self.result().annual_states[0], biological_population=-1),
            ),
        )
        with self.assertRaises(ValueError):
            validate_result(bad, self.bundle)

    def test_unknown_references_fail_closed(self):
        bad = replace(
            self.result(),
            decisions=(
                replace(self.result().decisions[0], actor_id="NOT_AN_ACTOR"),
            ),
        )
        with self.assertRaises(ValueError):
            validate_result(bad, self.bundle)

    def test_facility_cannot_commission_before_construction_lag(self):
        facility = FacilityRecord(
            facility_id="f1",
            project_archetype_id="HABITAT",
            location_id="LUNA_SURFACE",
            owner_actor_id="LAB_PUBLIC",
            committed_year=2028,
            commissioned_year=2029,
            status="ACTIVE",
            capital=18,
            capacities=CapacityVector(habitat=100),
        )
        bad = replace(self.result(), facilities=(facility,))
        with self.assertRaises(ValueError):
            validate_result(bad, self.bundle)

    def test_facility_placement_must_match_archetype(self):
        facility = FacilityRecord(
            facility_id="f-placement",
            project_archetype_id="LOGISTICS_NODE",
            location_id="LUNA_SURFACE",
            owner_actor_id="LAB_PUBLIC",
            committed_year=2028,
            commissioned_year=2029,
            status="ACTIVE",
            capital=12,
            capacities=CapacityVector(transport=10),
        )
        bad = replace(self.result(), facilities=(facility,))
        with self.assertRaises(ValueError):
            validate_result(bad, self.bundle)

    def test_duplicate_ids_fail_closed(self):
        event = self.result().events[0]
        bad = replace(self.result(), events=(event, event))
        with self.assertRaises(ValueError):
            validate_result(bad, self.bundle)

    def test_engine_protocol_is_small(self):
        class Dummy:
            engine_id = "dummy"
            engine_version = "0"

            def run(self, bundle, seed):
                return self_outer.result()

        self_outer = self
        self.assertIsInstance(Dummy(), PropagationEngine)


if __name__ == "__main__":
    unittest.main()
