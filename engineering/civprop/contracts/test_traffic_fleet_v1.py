"""Hostile tests for CIVPROP Traffic/Fleet V1."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from .accessibility_v1 import load_accessibility_package
from .demand_pressure_v1 import load_demand_pressure_package
from .traffic_fleet_v1 import (
    TrafficFleetRuntime,
    load_traffic_fleet_package,
)


HERE = Path(__file__).resolve().parent
PARAMETERS = HERE / "traffic_fleet_v1.json"
SCENARIO = HERE.parent / "compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json"


def _state(*, transient=0.0, transport=0.0):
    return SimpleNamespace(
        biological_population=0.0,
        transient_population=float(transient),
        workforce=0.0,
        capital=0.0,
        power=0.0,
        resource=0.0,
        industrial=0.0,
        habitat=0.0,
        shipyard=0.0,
        transport=float(transport),
    )


def _accessibility(status="FEASIBLE"):
    return load_accessibility_package(
        {
            "format": "CIVPROP_ACCESSIBILITY_V1",
            "contract_version": "1.0.0",
            "epoch_policy": "ANNUAL_REFERENCE_EPOCH_JULY_01_UTC",
            "location_bindings": [
                {"location_id": "EARTH_SURFACE", "body_id": "EARTH"},
                {"location_id": "LUNA_SURFACE", "body_id": "MOON"},
            ],
            "geometry_samples": [],
            "service_paths": [
                {
                    "service_id": "SYNTH_LUNA_FREIGHT",
                    "actor_id": "AUS",
                    "provider_id": "SYNTH_PROVIDER",
                    "subject_id": None,
                    "origin_location_id": "EARTH_SURFACE",
                    "destination_location_id": "LUNA_SURFACE",
                    "mission_class": "GENERIC_FREIGHT",
                    "service_class": "SYNTH_FREIGHT",
                    "valid_from_year": 2026,
                    "valid_to_year": None,
                    "target_year": None,
                    "status": status,
                    "limiting_constraints": [],
                    "provenance_refs": ["test:accessibility"],
                    "cost_components": [
                        {
                            "component_id": "SERVICE_PRICE",
                            "status": "KNOWN",
                            "value": 1.0,
                            "unit": "test/service-unit",
                            "uncertainty": None,
                        }
                    ],
                    "generalized_cost": {
                        "status": "KNOWN",
                        "value": 1.0,
                        "unit": "test/service-unit",
                        "uncertainty": None,
                    },
                    "required_technology_ids": [],
                }
            ],
        }
    )


def _synthetic_package(*, passenger_demand=0.0, availability=1.0):
    raw = json.loads(PARAMETERS.read_text())
    raw["service_bindings"] = [
        {
            "service_id": "SYNTH_LUNA_FREIGHT",
            "generic_demand_eligible": True,
            "traffic_role": "GENERIC_CARGO_PASSENGER",
            "provenance_refs": ["test:binding"],
        }
    ]
    raw["vehicle_classes"] = [
        {
            "vehicle_class_id": "SYNTH_20T",
            "compatible_service_ids": ["SYNTH_LUNA_FREIGHT"],
            "cargo_capacity_tonnes": {
                "status": "KNOWN",
                "value": 20.0,
                "unit": "tonne",
                "provenance_refs": ["test:cargo"],
            },
            "passenger_capacity_persons": {
                "status": "KNOWN",
                "value": 4.0,
                "unit": "person",
                "provenance_refs": ["test:pax"],
            },
            "mission_duration_days": {
                "status": "KNOWN",
                "value": 60.0,
                "unit": "day",
                "provenance_refs": ["test:mission"],
            },
            "turnaround_days": {
                "status": "KNOWN",
                "value": 31.0,
                "unit": "day",
                "provenance_refs": ["test:turnaround"],
            },
            "provenance_refs": ["test:class"],
        }
    ]
    raw["fleet_assets"] = [
        {
            "vehicle_id": "SHIP-1",
            "vehicle_class_id": "SYNTH_20T",
            "owner_actor_id": "SYNTH_PROVIDER",
            "service_id": "SYNTH_LUNA_FREIGHT",
            "commissioned_year": 2026,
            "retired_year": None,
            "availability_fraction": {
                "status": "KNOWN",
                "value": availability,
                "unit": "fraction",
                "provenance_refs": ["test:availability"],
            },
            "provenance_refs": ["test:ship1"],
        },
        {
            "vehicle_id": "SHIP-2",
            "vehicle_class_id": "SYNTH_20T",
            "owner_actor_id": "SYNTH_PROVIDER",
            "service_id": "SYNTH_LUNA_FREIGHT",
            "commissioned_year": 2026,
            "retired_year": None,
            "availability_fraction": {
                "status": "KNOWN",
                "value": availability,
                "unit": "fraction",
                "provenance_refs": ["test:availability"],
            },
            "provenance_refs": ["test:ship2"],
        },
    ]
    raw["demand_allocations"] = [
        {
            "allocation_id": "EARTH_TO_LUNA_GENERIC",
            "actor_id": "AUS",
            "origin_location_id": "EARTH_SURFACE",
            "destination_location_id": "LUNA_SURFACE",
            "service_id": "SYNTH_LUNA_FREIGHT",
            "cargo_fraction_of_transport_requirement": 1.0,
            "passenger_demand_persons_year": {
                "status": "KNOWN",
                "value": passenger_demand,
                "unit": "person/year",
                "provenance_refs": ["test:pax-demand"],
            },
            "valid_from_year": 2026,
            "valid_to_year": None,
            "provenance_refs": ["test:allocation"],
        }
    ]
    return load_traffic_fleet_package(raw)


class TrafficFleetV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scenario = json.loads(SCENARIO.read_text())
        cls.demand = load_demand_pressure_package(
            scenario["demand_pressure_v1"]
        )
        cls.default_accessibility = load_accessibility_package(
            scenario["accessibility_v1"]
        )

    def test_default_boundary_does_not_auto_spawn_fleet(self):
        package = load_traffic_fleet_package(
            json.loads(PARAMETERS.read_text())
        )
        self.assertFalse(package.timeline_context.auto_spawn_fleet)
        self.assertEqual(
            package.timeline_context.heavy_service_milestone_id,
            "TRN-MOD-HEAVY",
        )
        self.assertEqual(
            package.timeline_context.heavy_service_threshold_year,
            2040,
        )
        self.assertEqual(package.fleet_assets, ())
        self.assertEqual(package.vehicle_classes, ())
        self.assertEqual(package.demand_allocations, ())
        self.assertFalse(package.service_bindings[0].generic_demand_eligible)

    def test_default_demand_remains_unassigned_od(self):
        runtime = TrafficFleetRuntime(
            load_traffic_fleet_package(json.loads(PARAMETERS.read_text())),
            self.default_accessibility,
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=10000),
            "EARTH_ORBIT": _state(transient=200, transport=800),
            "LUNA_SURFACE": _state(),
            "CISLUNAR_FREE_SPACE": _state(),
        }
        demand, services, fleets, voyages, routes, metrics, overrides = (
            runtime.step_year(year=2026, states=states)
        )
        orbit = next(x for x in demand if x.location_id == "EARTH_ORBIT")
        self.assertEqual(
            orbit.local_transport_requirement_tonnes_year,
            800.0,
        )
        self.assertEqual(orbit.assignment_status, "UNASSIGNED_OD")
        self.assertEqual(orbit.assigned_cargo_demand_tonnes_year, 0.0)
        self.assertEqual(orbit.unassigned_cargo_demand_tonnes_year, 800.0)
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].active_fleet_count, 0)
        self.assertEqual(fleets, ())
        self.assertEqual(voyages, ())
        self.assertEqual(routes, ())
        self.assertEqual(overrides, ())
        self.assertEqual(
            next(x for x in metrics if x.location_id == "EARTH_ORBIT").ship_calls_year,
            0,
        )

    def test_named_payload_service_cannot_receive_generic_demand(self):
        raw = json.loads(PARAMETERS.read_text())
        raw["demand_allocations"] = [
            {
                "allocation_id": "BAD",
                "actor_id": "AUS",
                "origin_location_id": "EARTH_SURFACE",
                "destination_location_id": "LUNA_SURFACE",
                "service_id": "AUS_ROOVER_CLPS_CT4_IM5",
                "cargo_fraction_of_transport_requirement": 1.0,
                "passenger_demand_persons_year": {
                    "status": "KNOWN",
                    "value": 0,
                    "unit": "person/year",
                    "provenance_refs": ["test"],
                },
                "valid_from_year": 2026,
                "valid_to_year": None,
                "provenance_refs": ["test"],
            }
        ]
        with self.assertRaises(ValueError):
            load_traffic_fleet_package(raw)

    def test_two_vehicle_capacity_bounds_realized_cargo(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(),
            _accessibility(),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=50, transport=1000),
        }
        demand, services, fleets, voyages, routes, metrics, overrides = (
            runtime.step_year(year=2026, states=states)
        )
        route = routes[0]
        # 4 trips/vehicle/year * 2 vehicles * 20 t = 160 t/year.
        self.assertEqual(services[0].available_trips, 8)
        self.assertEqual(services[0].cargo_capacity_tonnes_year, 160.0)
        self.assertEqual(route.new_cargo_demand_tonnes, 200.0)
        self.assertEqual(route.realized_cargo_tonnes, 160.0)
        self.assertEqual(route.closing_cargo_backlog_tonnes, 40.0)
        self.assertEqual(route.realized_trips, 8)
        self.assertEqual(len(voyages), 8)
        self.assertTrue(all(x.utilization_ratio == 1.0 for x in fleets))
        self.assertAlmostEqual(route.transport_service_ratio, 0.8)
        self.assertEqual(overrides[0].required_transport_tonnes_year, 200.0)
        self.assertEqual(overrides[0].available_transport_tonnes_year, 160.0)

    def test_backlog_carries_forward_and_feeds_pressure_requirement(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(),
            _accessibility(),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=50, transport=1000),
        }
        runtime.step_year(year=2026, states=states)
        _, _, _, _, routes, _, overrides = runtime.step_year(
            year=2027,
            states=states,
        )
        route = routes[0]
        self.assertEqual(route.opening_cargo_backlog_tonnes, 40.0)
        self.assertEqual(route.total_cargo_demand_tonnes, 240.0)
        self.assertEqual(route.realized_cargo_tonnes, 160.0)
        self.assertEqual(route.closing_cargo_backlog_tonnes, 80.0)
        self.assertAlmostEqual(route.transport_service_ratio, 160 / 240)
        self.assertEqual(
            overrides[0].required_transport_tonnes_year,
            240.0,
        )

    def test_origin_destination_and_node_incidence_reconcile(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(),
            _accessibility(),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=50, transport=1000),
        }
        _, _, _, voyages, routes, metrics, _ = runtime.step_year(
            year=2026,
            states=states,
        )
        earth = next(x for x in metrics if x.location_id == "EARTH_SURFACE")
        luna = next(x for x in metrics if x.location_id == "LUNA_SURFACE")
        self.assertEqual(earth.cargo_outbound_tonnes, 160.0)
        self.assertEqual(earth.cargo_inbound_tonnes, 0.0)
        self.assertEqual(luna.cargo_inbound_tonnes, 160.0)
        self.assertEqual(luna.cargo_outbound_tonnes, 0.0)
        self.assertEqual(earth.cargo_throughput_tonnes_year, 160.0)
        self.assertEqual(luna.cargo_throughput_tonnes_year, 160.0)
        self.assertEqual(earth.ship_calls_year, 8)
        self.assertEqual(luna.ship_calls_year, 8)
        self.assertEqual(sum(x.cargo_tonnes for x in voyages), 160.0)
        self.assertEqual(routes[0].departure_calls, 8)
        self.assertEqual(routes[0].arrival_calls, 8)

    def test_passenger_movements_are_explicit_not_inferred_from_cargo(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(passenger_demand=10),
            _accessibility(),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=10, transport=1000),
        }
        _, _, _, _, routes, metrics, _ = runtime.step_year(
            year=2026,
            states=states,
        )
        route = routes[0]
        self.assertEqual(route.realized_passenger_movements, 10.0)
        luna = next(x for x in metrics if x.location_id == "LUNA_SURFACE")
        self.assertEqual(luna.passenger_movements_year, 10.0)

    def test_unknown_accessibility_does_not_claim_realized_movement(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(),
            _accessibility(status="UNKNOWN"),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=50, transport=1000),
        }
        _, _, _, voyages, routes, _, overrides = runtime.step_year(
            year=2026,
            states=states,
        )
        self.assertEqual(routes[0].traffic_status, "UNKNOWN")
        self.assertIsNone(routes[0].realized_cargo_tonnes)
        self.assertEqual(voyages, ())
        self.assertEqual(overrides, ())

    def test_local_handling_capacity_can_constrain_fleet_service(self):
        runtime = TrafficFleetRuntime(
            _synthetic_package(),
            _accessibility(),
            self.demand,
        )
        states = {
            "EARTH_SURFACE": _state(transport=1000),
            "LUNA_SURFACE": _state(transient=50, transport=100),
        }
        _, _, _, voyages, routes, _, overrides = runtime.step_year(
            year=2026,
            states=states,
        )
        self.assertEqual(routes[0].cargo_service_capacity_tonnes_year, 100.0)
        self.assertEqual(routes[0].realized_cargo_tonnes, 100.0)
        self.assertEqual(len(voyages), 5)
        self.assertEqual(overrides[0].available_transport_tonnes_year, 100.0)

    def test_duplicate_or_overallocated_services_fail_closed(self):
        raw = json.loads(PARAMETERS.read_text())
        synth = json.loads(json.dumps(_package_to_raw(_synthetic_package())))
        # Contract already forbids more than one allocation per service.
        synth["demand_allocations"].append(
            copy.deepcopy(synth["demand_allocations"][0])
        )
        synth["demand_allocations"][-1]["allocation_id"] = "DUP2"
        with self.assertRaises(ValueError):
            load_traffic_fleet_package(synth)


def _package_to_raw(package):
    # Only used to make a hostile mutation from the tested synthetic package.
    from dataclasses import asdict
    return asdict(package)


if __name__ == "__main__":
    unittest.main()
