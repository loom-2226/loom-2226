"""Integration tests for ProductionLaneV1."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
import unittest

from engineering.civprop.contracts.production_accounting_v1 import (
    load_production_accounting_package,
)
from engineering.civprop.contracts.traffic_fleet_v1 import (
    LocationTrafficStateV1,
)
from .contracts import CapacityVector, FacilityRecord, load_bundle
from .production_lane_v1 import ProductionLaneV1
from .prototypes.common import Recorder


HERE = Path(__file__).resolve().parent


class ProductionLaneV1Tests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_bundle(HERE)
        raw = json.loads(
            (
                HERE.parent
                / "contracts"
                / "production_accounting_v1.json"
            ).read_text()
        )
        package = load_production_accounting_package(raw)
        self.bundle = replace(
            self.bundle,
            scenario=replace(
                self.bundle.scenario,
                production_accounting_v1=package,
            ),
        )
        self.recorder = Recorder()
        self.recorder.facilities.append(
            FacilityRecord(
                facility_id="fac-production-lane-test",
                project_archetype_id="INDUSTRIAL_WORKSHOP",
                location_id="LUNA_SURFACE",
                owner_actor_id="AUS",
                committed_year=2026,
                commissioned_year=2030,
                status="ACTIVE",
                capital=1.5,
                capacities=CapacityVector(industrial=100.0),
            )
        )

    def test_lane_emits_facility_and_reconciled_aggregates(self):
        lane = ProductionLaneV1(self.bundle, self.recorder)
        lane.step(year=2030)

        self.assertEqual(len(self.recorder.facility_production_states), 1)
        self.assertEqual(len(self.recorder.sector_production_states), 1)
        self.assertEqual(len(self.recorder.location_production_states), 1)
        self.assertEqual(len(self.recorder.body_production_states), 1)

        state = self.recorder.facility_production_states[0]
        self.assertEqual(state.facility_id, "fac-production-lane-test")
        self.assertEqual(state.sector_id, "INDUSTRY")
        self.assertEqual(state.utilization_status, "UNKNOWN")
        self.assertIsNone(state.realized_utilization)
        self.assertEqual(state.physical_output_status, "UNKNOWN")
        self.assertIsNone(state.physical_output_quantity)
        self.assertEqual(state.valuation_status, "UNKNOWN")
        self.assertIsNone(state.gross_output)
        self.assertIsNone(state.value_added)
        self.assertEqual(state.commissioned_investment, 1.5)
        self.assertEqual(state.closing_gross_productive_capital, 1.5)

        sector = self.recorder.sector_production_states[0]
        location = self.recorder.location_production_states[0]
        body = self.recorder.body_production_states[0]
        self.assertEqual(sector.facility_count, 1)
        self.assertEqual(location.facility_count, 1)
        self.assertEqual(body.facility_count, 1)
        self.assertEqual(body.body_id, "MOON")
        self.assertEqual(sector.commissioned_investment, 1.5)
        self.assertEqual(location.commissioned_investment, 1.5)
        self.assertEqual(body.commissioned_investment, 1.5)

    def test_lane_consumes_known_transport_service_ratio(self):
        self.recorder.location_traffic_states.append(
            LocationTrafficStateV1(
                location_traffic_state_id="lt-test",
                year=2030,
                location_id="LUNA_SURFACE",
                cargo_inbound_tonnes=80.0,
                cargo_outbound_tonnes=0.0,
                cargo_throughput_tonnes_year=80.0,
                passenger_inbound_movements=0.0,
                passenger_outbound_movements=0.0,
                passenger_movements_year=0.0,
                arrival_calls=4,
                departure_calls=0,
                ship_calls_year=4,
                transport_service_ratio=0.8,
                metric_scope="MODELED_GENERIC_TRAFFIC_ONLY",
            )
        )
        lane = ProductionLaneV1(self.bundle, self.recorder)
        lane.step(year=2030)
        state = self.recorder.facility_production_states[0]
        constraints = {
            x.constraint_id: x
            for x in state.constraint_observations
        }
        self.assertIn("TRANSPORT", constraints)
        self.assertEqual(constraints["TRANSPORT"].status, "KNOWN")
        self.assertEqual(
            constraints["TRANSPORT"].utilization_ratio,
            0.8,
        )
        self.assertIn(
            "CIVPROP_TRAFFIC_FLEET_V1",
            constraints["TRANSPORT"].provenance_refs,
        )
        self.assertEqual(state.utilization_status, "UNKNOWN")

    def test_lane_does_not_mutate_facility_or_emit_events(self):
        before = tuple(self.recorder.facilities)
        lane = ProductionLaneV1(self.bundle, self.recorder)
        lane.step(year=2030)
        self.assertEqual(tuple(self.recorder.facilities), before)
        self.assertEqual(self.recorder.events, [])
        self.assertEqual(self.recorder.decisions, [])
        self.assertEqual(self.recorder.flows, [])


if __name__ == "__main__":
    unittest.main()
