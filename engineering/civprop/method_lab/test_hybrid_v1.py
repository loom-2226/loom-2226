"""Acceptance tests for the selected CIVPROP Hybrid Engine V1 reference implementation."""
from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
import unittest

from engineering.civprop.contracts.demand_pressure_v1 import (
    load_demand_pressure_package,
)
from engineering.civprop.contracts.mission_knowledge_v1 import (
    MissionKnowledgeRuntime,
    load_mission_knowledge_package,
)
from .contracts import PropagationEngine, canonical_json, load_bundle, validate_result
from .mission_lane_v1 import MissionLaneV1
from .prototypes.common import resource_probability
from .prototypes.hybrid_v1 import HybridEngineV1


HERE = Path(__file__).resolve().parent


class HybridEngineV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(HERE)

    def run_seed(self, seed=42):
        return HybridEngineV1().run(self.bundle, seed)

    def mission_bundle(self, *, success_value=50.0, truth_present=None):
        raw = json.loads(
            (
                HERE.parent
                / "contracts"
                / "mission_knowledge_v1.json"
            ).read_text()
        )
        raw["capital_unit"] = self.bundle.scenario.units["capital"]
        raw["decision_models"][0]["success_value"] = {
            "status": "SCENARIO_ASSUMPTION",
            "value": float(success_value),
            "unit": self.bundle.scenario.units["capital"],
            "provenance_refs": ["test:mission-value"],
        }
        package = load_mission_knowledge_package(raw)
        scenario = replace(
            self.bundle.scenario,
            mission_knowledge_v1=package,
        )
        truth = self.bundle.truth
        if truth_present is not None:
            truth = replace(
                truth,
                resources=tuple(
                    replace(resource, present=bool(truth_present))
                    if resource.resource_id == "MOON_POLAR_WATER"
                    else resource
                    for resource in truth.resources
                ),
            )
        return replace(self.bundle, scenario=scenario, truth=truth)

    def causal_bundle(self, *, channel, strategic_requirements=(), locations=None):
        package = load_demand_pressure_package({
            "format": "CIVPROP_DEMAND_PRESSURE_V1",
            "contract_version": "1.0.0",
            "scope": "NON_EARTH_SURFACE",
            "excluded_location_ids": ["EARTH_SURFACE"],
            "parameter_status": "UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1",
            "channels": [channel],
            "strategic_requirements": list(strategic_requirements),
        })
        scenario = replace(
            self.bundle.scenario,
            demand_pressure_v1=package,
            demand_signals=(),
            locations=tuple(locations or self.bundle.scenario.locations),
        )
        return replace(self.bundle, scenario=scenario)

    def test_implements_common_engine_protocol(self):
        engine = HybridEngineV1()
        self.assertIsInstance(engine, PropagationEngine)
        self.assertEqual(engine.engine_id, "HYBRID_V1")

    def test_result_validates_and_covers_all_years_locations(self):
        result = self.run_seed()
        validate_result(result, self.bundle)
        expected = {
            (year, location.location_id)
            for year in range(self.bundle.scenario.start_year, self.bundle.scenario.end_year + 1)
            for location in self.bundle.scenario.locations
        }
        self.assertEqual({(x.year, x.location_id) for x in result.annual_states}, expected)

    def test_same_seed_is_bitwise_reproducible(self):
        self.assertEqual(canonical_json(self.run_seed(42)), canonical_json(self.run_seed(42)))

    def test_engine_does_not_read_evaluator_truth(self):
        import engineering.civprop.method_lab.prototypes.hybrid_v1 as module
        source = inspect.getsource(module)
        self.assertNotIn(".truth", source)
        self.assertNotIn("TruthResource", source)

        self.assertNotIn(
            "hidden",
            inspect.getsource(MissionKnowledgeRuntime.evaluate).lower(),
        )
        self.assertNotIn(
            ".truth",
            inspect.getsource(MissionLaneV1.evaluate_and_commit),
        )
        execution_source = inspect.getsource(MissionLaneV1.execute_due)
        self.assertIn(".truth", execution_source)

    def test_three_selected_mechanisms_are_observable(self):
        result = self.run_seed()
        event_types = {x.event_type for x in result.events}
        # dynamic-recursive skeleton
        self.assertIn("YEAR_STARTED", event_types)
        self.assertIn("YEAR_COMPLETED", event_types)
        # system-dynamics pressure
        self.assertIn("OPPORTUNITY_PRESSURE_QUALIFIED", event_types)
        # actor/event commitment
        self.assertIn("PROJECT_COMMITTED", event_types)
        self.assertTrue(any(d.action == "COMMIT_PROJECT" for d in result.decisions))

    def test_pressure_is_not_an_immortal_bucket(self):
        engine = HybridEngineV1()
        self.assertGreater(engine.pressure_decay, 0.0)
        self.assertLess(engine.pressure_decay, 1.0)

    def test_major_commitments_require_qualified_pressure(self):
        result = self.run_seed()
        qualified = {
            (e.year, e.actor_id, e.location_id)
            for e in result.events
            if e.event_type == "OPPORTUNITY_PRESSURE_QUALIFIED"
        }
        for decision in result.decisions:
            if decision.action != "COMMIT_PROJECT":
                continue
            self.assertIn(
                (decision.year, decision.actor_id, decision.target_location_id),
                qualified,
            )

    def test_population_conservation_and_habitat_constraint(self):
        result = self.run_seed()
        initial_total = sum(x.biological_population for x in self.bundle.scenario.locations)
        end_year = self.bundle.scenario.end_year
        final = [x for x in result.annual_states if x.year == end_year]
        self.assertAlmostEqual(sum(x.biological_population for x in final), initial_total, places=8)
        for state in result.annual_states:
            self.assertLessEqual(state.biological_population, state.capacities.habitat + 1e-9)

    def test_facilities_obey_lag_and_access(self):
        result = self.run_seed()
        projects = {x.project_archetype_id: x for x in self.bundle.scenario.project_archetypes}
        frontiers = {x.tech_id: x.frontier_year for x in self.bundle.scenario.technology_frontier}
        caps = {(x.actor_id, x.tech_id): x for x in self.bundle.scenario.actor_capability}
        for facility in result.facilities:
            project = projects[facility.project_archetype_id]
            self.assertGreaterEqual(
                facility.commissioned_year - facility.committed_year,
                project.construction_lag_years,
            )
            for tech in project.required_tech:
                self.assertGreaterEqual(facility.committed_year, frontiers[tech])
                self.assertEqual(caps[(facility.owner_actor_id, tech)].status, "USABLE")

    def test_engine_generates_a_nontrivial_offworld_history(self):
        result = self.run_seed()
        self.assertGreater(len(result.facilities), 0)
        self.assertTrue(any(f.location_id != "EARTH_SURFACE" for f in result.facilities))
        self.assertGreater(len(result.decisions), 0)
        self.assertGreater(len(result.events), 0)

    def test_causal_no_demand_produces_no_pressure_qualified_projects(self):
        locations = [
            replace(
                location,
                transient_population=0.0,
            )
            if location.location_id == "EARTH_ORBIT"
            else location
            for location in self.bundle.scenario.locations
        ]
        bundle = self.causal_bundle(
            channel={
                "channel_id": "HABITAT",
                "unit": "person",
                "available_field": "habitat",
                "decay": 0.60,
                "gain": 1.0,
                "drivers": [
                    {"field": "biological_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                    {"field": "transient_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                ],
            },
            locations=locations,
        )
        result = HybridEngineV1().run(bundle, 42)
        self.assertEqual(result.metadata.engine_version, "method-reference-v2")
        self.assertFalse(
            any(e.event_type == "OPPORTUNITY_PRESSURE_QUALIFIED" for e in result.events)
        )
        self.assertFalse(any(d.action == "COMMIT_PROJECT" for d in result.decisions))

    def test_causal_habitat_shortage_accumulates_and_qualifies_habitat(self):
        bundle = self.causal_bundle(
            channel={
                "channel_id": "HABITAT",
                "unit": "person",
                "available_field": "habitat",
                "decay": 0.60,
                "gain": 1.0,
                "drivers": [
                    {"field": "biological_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                    {"field": "transient_population", "coefficient": 1.0,
                     "coefficient_unit": "person/person"},
                ],
            },
        )
        result = HybridEngineV1().run(bundle, 42)
        habitat_commits = [
            d for d in result.decisions
            if d.action == "COMMIT_PROJECT"
            and d.project_archetype_id == "HABITAT"
            and d.target_location_id == "EARTH_ORBIT"
        ]
        self.assertTrue(habitat_commits)
        self.assertGreaterEqual(habitat_commits[0].year, 2027)

    def test_declared_strategic_requirement_can_qualify_logistics_without_population(self):
        bundle = self.causal_bundle(
            channel={
                "channel_id": "TRANSPORT",
                "unit": "scenario_capacity_unit",
                "available_field": "transport",
                "decay": 0.60,
                "gain": 1.0,
                "drivers": [],
            },
            strategic_requirements=[{
                "requirement_id": "DECLARED_ORBIT_LOGISTICS",
                "actor_id": "LAB_PUBLIC",
                "location_id": "EARTH_ORBIT",
                "channel_id": "TRANSPORT",
                "amount": 20.0,
                "unit": "scenario_capacity_unit",
                "valid_from_year": 2026,
                "valid_to_year": 2026,
                "provenance_refs": ["test:declared"],
            }],
        )
        result = HybridEngineV1().run(bundle, 42)
        commits = [
            d for d in result.decisions
            if d.action == "COMMIT_PROJECT"
            and d.project_archetype_id == "LOGISTICS_NODE"
            and d.target_location_id == "EARTH_ORBIT"
        ]
        self.assertTrue(commits)
        self.assertEqual(commits[0].year, 2026)

    def test_mission_lane_executes_observes_and_updates_knowledge(self):
        bundle = self.mission_bundle()
        result = HybridEngineV1().run(bundle, 42)
        validate_result(result, bundle)
        self.assertEqual(result.metadata.engine_version, "method-reference-v4")
        self.assertEqual(len(result.missions), 1)
        mission = result.missions[0]
        self.assertEqual(mission.actor_id, "LAB_PUBLIC")
        self.assertEqual(mission.committed_year, 2029)
        self.assertEqual(mission.execution_year, 2030)
        self.assertEqual(mission.status, "EXECUTED")
        self.assertEqual(len(result.observations), 1)
        self.assertEqual(result.observations[0].mission_id, mission.mission_id)
        updated = [
            x
            for x in result.knowledge_states
            if x.actor_id == "LAB_PUBLIC" and x.observation_ids
        ]
        self.assertEqual(len(updated), 1)
        self.assertGreater(updated[0].probability, 0.45)
        event_types = {x.event_type for x in result.events}
        for required in (
            "MISSION_COMMITTED",
            "MISSION_EXECUTED",
            "OBSERVATION_PRODUCED",
            "OBSERVATION_RECEIVED",
            "KNOWLEDGE_UPDATED",
        ):
            self.assertIn(required, event_types)

    def test_adverse_observation_lowers_posterior(self):
        bundle = self.mission_bundle()
        result = HybridEngineV1().run(bundle, 5)
        observation = result.observations[0]
        self.assertFalse(observation.detected)
        updated = next(
            x
            for x in result.knowledge_states
            if x.actor_id == "LAB_PUBLIC" and x.observation_ids
        )
        self.assertLess(updated.probability, 0.45)

    def test_pre_observation_mission_choice_is_independent_of_hidden_truth(self):
        present = HybridEngineV1().run(
            self.mission_bundle(truth_present=True),
            42,
        )
        absent = HybridEngineV1().run(
            self.mission_bundle(truth_present=False),
            42,
        )
        present_pre = [
            x
            for x in present.mission_decisions
            if x.year <= 2029 and x.actor_id == "LAB_PUBLIC"
        ]
        absent_pre = [
            x
            for x in absent.mission_decisions
            if x.year <= 2029 and x.actor_id == "LAB_PUBLIC"
        ]
        self.assertEqual(present_pre, absent_pre)
        self.assertEqual(present_pre[-1].action, "COMMIT_MISSION")

    def test_updated_knowledge_is_the_resource_probability_seen_by_project_scoring(self):
        bundle = self.mission_bundle()
        result = HybridEngineV1().run(bundle, 42)
        latest = {}
        for state in result.knowledge_states:
            latest[(state.actor_id, state.subject_id, state.location_id)] = state
        posterior = latest[
            ("LAB_PUBLIC", "MOON_POLAR_WATER", "LUNA_SURFACE")
        ].probability
        consumed = resource_probability(
            bundle,
            "LUNA_SURFACE",
            actor_id="LAB_PUBLIC",
            knowledge=latest,
        )
        self.assertAlmostEqual(consumed, posterior, places=12)
        self.assertNotAlmostEqual(consumed, 0.45, places=12)
        hybrid_source = inspect.getsource(HybridEngineV1.run)
        self.assertIn("mission_lane.knowledge", hybrid_source)


if __name__ == "__main__":
    unittest.main()
