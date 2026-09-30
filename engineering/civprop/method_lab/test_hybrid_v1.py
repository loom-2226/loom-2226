"""Acceptance tests for the selected CIVPROP Hybrid Engine V1 reference implementation."""
from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from .contracts import PropagationEngine, canonical_json, load_bundle, validate_result
from .prototypes.hybrid_v1 import HybridEngineV1


HERE = Path(__file__).resolve().parent


class HybridEngineV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(HERE)

    def run_seed(self, seed=42):
        return HybridEngineV1().run(self.bundle, seed)

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


if __name__ == "__main__":
    unittest.main()
