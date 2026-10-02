"""Check the lifetime and actor isolation of predecision opportunity caches."""
from pathlib import Path
from types import SimpleNamespace
import unittest

from engineering.civprop.contracts.demand_pressure_v1 import DemandObservation
from .contracts import load_bundle
from .prototypes.common import (
    initial_state, opportunities, opportunity_context, project_demand,
    resource_probability,
)


class OpportunityContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(Path(__file__).resolve().parent)

    def test_shared_actor_calls_preserve_order_and_values(self):
        states = initial_state(self.bundle)
        context = opportunity_context(self.bundle, states, 2030)
        for actor in self.bundle.scenario.actors:
            self.assertEqual(
                opportunities(self.bundle, states, actor.actor_id, 2030),
                opportunities(self.bundle, states, actor.actor_id, 2030, shared_context=context),
            )

    def test_new_knowledge_is_read_on_every_call_and_is_actor_scoped(self):
        states = initial_state(self.bundle)
        context = opportunity_context(self.bundle, states, 2030)
        actor = self.bundle.scenario.actors[0].actor_id
        knowledge = {
            (actor, "A", "LUNA_SURFACE"): SimpleNamespace(probability=0.01),
            (actor, "B", "LUNA_SURFACE"): SimpleNamespace(probability=0.02),
            ("OTHER", "C", "LUNA_SURFACE"): SimpleNamespace(probability=0.99),
        }
        for probability in (0.02, 0.8):
            knowledge[(actor, "B", "LUNA_SURFACE")].probability = probability
            rows = opportunities(
                self.bundle, states, actor, 2030, knowledge=knowledge, shared_context=context,
            )
            lunar = [row for row in rows if row.location_id == "LUNA_SURFACE"]
            self.assertTrue(lunar)
            self.assertEqual(resource_probability(
                self.bundle, "LUNA_SURFACE", actor_id=actor, knowledge=knowledge,
            ), probability)
            self.assertTrue(all(row.resource_probability == probability for row in lunar))

    def test_demand_index_preserves_last_observation_for_channel(self):
        states = initial_state(self.bundle)
        observations = tuple(
            DemandObservation(2030, "LUNA_SURFACE", "POWER", "test", amount, 0, amount, ())
            for amount in (2.0, 9.0)
        )
        context = opportunity_context(self.bundle, states, 2030, demand_observations=observations)
        self.assertIs(context.demand_by_location["LUNA_SURFACE"]["POWER"], observations[-1])
        for project in context.resolved_projects:
            self.assertEqual(
                project_demand(self.bundle, project, 2030, location_id="LUNA_SURFACE",
                               demand_observations=observations),
                project_demand(self.bundle, project, 2030, location_id="LUNA_SURFACE",
                               demand_observations=observations,
                               demand_by_location=context.demand_by_location),
            )

    def test_rebuilding_snapshot_refreshes_transport_origins_and_demand_cache(self):
        states = initial_state(self.bundle)
        states["LUNA_SURFACE"].transport = 0.0
        old = opportunity_context(self.bundle, states, 2030)
        old.project_demands[("test", "LUNA_SURFACE")] = 5.0
        states["LUNA_SURFACE"].transport = 1.0
        new = opportunity_context(self.bundle, states, 2031)
        self.assertNotIn("LUNA_SURFACE", old.available_origins)
        self.assertIn("LUNA_SURFACE", new.available_origins)
        self.assertEqual(new.project_demands, {})
