"""Adapter tests for TrafficLaneV1 pressure handoff."""
from __future__ import annotations

from types import SimpleNamespace
import unittest

from engineering.civprop.contracts.demand_pressure_v1 import (
    DemandComponent,
    DemandObservation,
)
from engineering.civprop.contracts.traffic_fleet_v1 import (
    TrafficPressureOverrideV1,
)
from .traffic_lane_v1 import TrafficLaneV1


class TrafficLaneV1Tests(unittest.TestCase):
    def test_pressure_override_replaces_available_service_and_adds_backlog(self):
        lane = object.__new__(TrafficLaneV1)
        lane.recorder = SimpleNamespace(
            traffic_pressure_overrides=[
                TrafficPressureOverrideV1(
                    year=2030,
                    location_id="LUNA_SURFACE",
                    required_transport_tonnes_year=240.0,
                    available_transport_tonnes_year=160.0,
                    opening_backlog_clearance_tonnes_year=40.0,
                    allocation_coverage_fraction=1.0,
                )
            ]
        )
        observation = DemandObservation(
            year=2030,
            location_id="LUNA_SURFACE",
            channel_id="TRANSPORT",
            unit="tonnes/year",
            required=200.0,
            available=1000.0,
            unmet=0.0,
            driver_components=("state:transient_population",),
            quantified_components=(
                DemandComponent(
                    component_type="STATE_DRIVER",
                    source_id="state:transient_population",
                    quantity=200.0,
                    unit="tonnes/year",
                ),
            ),
        )
        (observed,) = lane.apply_pressure_overrides(
            year=2030,
            observations=(observation,),
        )
        self.assertEqual(observed.required, 240.0)
        self.assertEqual(observed.available, 160.0)
        self.assertEqual(observed.unmet, 80.0)
        self.assertEqual(
            observed.available_component_type,
            "TRAFFIC_SERVICE_CAPACITY",
        )
        self.assertEqual(
            observed.available_source_id,
            "traffic:service_capacity:2030:LUNA_SURFACE",
        )
        backlog = [
            x
            for x in observed.quantified_components
            if x.component_type == "TRAFFIC_BACKLOG_CLEARANCE"
        ]
        self.assertEqual(len(backlog), 1)
        self.assertEqual(backlog[0].quantity, 40.0)

    def test_no_override_preserves_original_observation_identity(self):
        lane = object.__new__(TrafficLaneV1)
        lane.recorder = SimpleNamespace(
            traffic_pressure_overrides=[]
        )
        observation = DemandObservation(
            year=2030,
            location_id="LUNA_SURFACE",
            channel_id="TRANSPORT",
            unit="tonnes/year",
            required=200.0,
            available=1000.0,
            unmet=0.0,
            driver_components=(),
        )
        (observed,) = lane.apply_pressure_overrides(
            year=2030,
            observations=(observation,),
        )
        self.assertIs(observed, observation)


if __name__ == "__main__":
    unittest.main()
