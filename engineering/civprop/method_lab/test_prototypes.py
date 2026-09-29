"""Common acceptance tests for the three Method Lab propagation prototypes."""
from __future__ import annotations

from dataclasses import asdict
import inspect
import json
from pathlib import Path
import unittest

from .contracts import PropagationEngine, canonical_json, load_bundle, validate_result
from .prototypes.actor_event import ActorEventEngine
from .prototypes.dynamic_recursive import DynamicRecursiveEngine
from .prototypes.system_dynamics import SystemDynamicsEngine
from .run_prototypes import run_all


HERE = Path(__file__).resolve().parent
ENGINE_TYPES = (DynamicRecursiveEngine, SystemDynamicsEngine, ActorEventEngine)


class PrototypeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(HERE)

    def engines(self):
        return [engine_type() for engine_type in ENGINE_TYPES]

    def test_committed_seed42_summary_reproduces(self):
        committed = json.loads((HERE / "prototype_seed42_summary_v1.json").read_text())
        self.assertEqual(committed, run_all(HERE, seed=42))

    def test_runner_uses_same_bundle_and_three_candidates(self):
        summary = run_all(HERE, seed=42)
        self.assertEqual(
            set(summary["engines"]),
            {"DYNAMIC_RECURSIVE", "SYSTEM_DYNAMICS_HEAVY", "ACTOR_DISCRETE_EVENT"},
        )
        self.assertEqual(summary["input_bundle_sha256"], self.bundle.bundle_sha256)
        for engine in summary["engines"].values():
            self.assertEqual(len(engine["result_sha256"]), 64)
            self.assertEqual(set(engine["final_locations"]), {x.location_id for x in self.bundle.scenario.locations})

    def test_all_candidates_implement_common_protocol(self):
        for engine in self.engines():
            self.assertIsInstance(engine, PropagationEngine)
            self.assertTrue(engine.engine_id)
            self.assertTrue(engine.engine_version)

    def test_all_candidates_emit_valid_common_result(self):
        for engine in self.engines():
            with self.subTest(engine=engine.engine_id):
                result = engine.run(self.bundle, seed=42)
                validate_result(result, self.bundle)
                self.assertEqual(result.metadata.engine_id, engine.engine_id)
                self.assertEqual(result.metadata.engine_version, engine.engine_version)
                self.assertEqual(result.metadata.input_bundle_sha256, self.bundle.bundle_sha256)
                self.assertEqual(result.metadata.seed, 42)

    def test_every_candidate_emits_every_location_every_year(self):
        expected = {
            (year, location.location_id)
            for year in range(self.bundle.scenario.start_year, self.bundle.scenario.end_year + 1)
            for location in self.bundle.scenario.locations
        }
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            observed = {(x.year, x.location_id) for x in result.annual_states}
            self.assertEqual(observed, expected, engine.engine_id)

    def test_same_seed_replays_identically(self):
        for engine in self.engines():
            a = engine.run(self.bundle, seed=42)
            b = engine.run(self.bundle, seed=42)
            self.assertEqual(canonical_json(a), canonical_json(b), engine.engine_id)

    def test_candidates_do_not_read_evaluator_truth(self):
        for engine_type in ENGINE_TYPES:
            module = __import__(engine_type.__module__, fromlist=["*"])
            source = inspect.getsource(module)
            self.assertNotIn(".truth", source, engine_type.engine_id)
            self.assertNotIn("TruthResource", source, engine_type.engine_id)

    def test_each_candidate_can_generate_offworld_infrastructure(self):
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            self.assertTrue(result.facilities, engine.engine_id)
            self.assertTrue(
                any(f.location_id != "EARTH_SURFACE" for f in result.facilities),
                engine.engine_id,
            )

    def test_construction_lag_is_observed(self):
        archetypes = {
            x.project_archetype_id: x for x in self.bundle.scenario.project_archetypes
        }
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            for facility in result.facilities:
                required = archetypes[facility.project_archetype_id].construction_lag_years
                self.assertGreaterEqual(
                    facility.commissioned_year - facility.committed_year,
                    required,
                    (engine.engine_id, facility.facility_id),
                )

    def test_population_is_conserved_by_migration_flows(self):
        initial_total = sum(x.biological_population for x in self.bundle.scenario.locations)
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            final_year = self.bundle.scenario.end_year
            final_total = sum(
                x.biological_population
                for x in result.annual_states
                if x.year == final_year
            )
            self.assertAlmostEqual(final_total, initial_total, places=8, msg=engine.engine_id)
            for flow in result.flows:
                if flow.flow_type == "MIGRATION":
                    self.assertIsNotNone(flow.origin_location_id)
                    self.assertIsNotNone(flow.destination_location_id)
                    self.assertGreaterEqual(flow.amount, 0)

    def test_population_never_exceeds_habitat_capacity(self):
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            for state in result.annual_states:
                self.assertLessEqual(
                    state.biological_population,
                    state.capacities.habitat + 1e-9,
                    (engine.engine_id, state.year, state.location_id),
                )

    def test_facilities_do_not_precede_technology_frontier_or_actor_access(self):
        frontiers = {x.tech_id: x.frontier_year for x in self.bundle.scenario.technology_frontier}
        capabilities = {
            (x.actor_id, x.tech_id): x for x in self.bundle.scenario.actor_capability
        }
        archetypes = {
            x.project_archetype_id: x for x in self.bundle.scenario.project_archetypes
        }
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            for facility in result.facilities:
                project = archetypes[facility.project_archetype_id]
                for tech in project.required_tech:
                    self.assertGreaterEqual(facility.committed_year, frontiers[tech])
                    capability = capabilities[(facility.owner_actor_id, tech)]
                    self.assertEqual(
                        capability.status,
                        "USABLE",
                        (engine.engine_id, facility.facility_id, tech),
                    )
                    self.assertGreaterEqual(facility.committed_year, capability.valid_from)
                    if capability.valid_to is not None:
                        self.assertLessEqual(facility.committed_year, capability.valid_to)

    def test_results_expose_causal_activity_not_only_snapshots(self):
        for engine in self.engines():
            result = engine.run(self.bundle, seed=42)
            self.assertTrue(result.decisions, engine.engine_id)
            self.assertTrue(result.events, engine.engine_id)
            event_types = {x.event_type for x in result.events}
            self.assertIn("RUN_STARTED", event_types, engine.engine_id)
            self.assertIn("RUN_COMPLETED", event_types, engine.engine_id)

    def test_candidate_histories_are_behaviorally_distinct(self):
        histories = {
            canonical_json(engine.run(self.bundle, seed=42))
            for engine in self.engines()
        }
        self.assertEqual(len(histories), 3)

    def test_three_candidates_are_not_aliases_of_one_implementation(self):
        ids = {engine.engine_id for engine in self.engines()}
        modules = {engine.__class__.__module__ for engine in self.engines()}
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(modules), 3)


if __name__ == "__main__":
    unittest.main()
