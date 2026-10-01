"""Traffic/Fleet V1 adapter for Hybrid.

The lane derives annual OD traffic from explicit allocations, Accessibility V1 and
versioned fleet assets. It does not auto-create routes or vehicles from timeline
dates. Backlog persists inside this lane across annual steps.
"""
from __future__ import annotations

from dataclasses import replace

from engineering.civprop.contracts.demand_pressure_v1 import DemandComponent
from engineering.civprop.contracts.traffic_fleet_v1 import TrafficFleetRuntime


class TrafficLaneV1:
    def __init__(self, bundle, recorder):
        package = bundle.scenario.traffic_fleet_v1
        accessibility = bundle.scenario.accessibility_v1
        demand = bundle.scenario.demand_pressure_v1
        if package is None or accessibility is None or demand is None:
            raise ValueError(
                "TrafficLaneV1 requires Traffic/Fleet, Accessibility and Demand/Pressure V1"
            )
        self.bundle = bundle
        self.recorder = recorder
        self.runtime = TrafficFleetRuntime(
            package,
            accessibility,
            demand,
        )

    def step(
        self,
        *,
        year: int,
        states,
        additional_requirements=None,
    ) -> None:
        (
            demand_states,
            service_states,
            fleet_states,
            voyages,
            route_states,
            location_states,
            overrides,
        ) = self.runtime.step_year(
            year=year,
            states=states,
            additional_requirements=additional_requirements,
        )
        self.recorder.traffic_demand_states.extend(demand_states)
        self.recorder.traffic_service_states.extend(service_states)
        self.recorder.fleet_states.extend(fleet_states)
        self.recorder.voyage_states.extend(voyages)
        self.recorder.route_traffic_states.extend(route_states)
        self.recorder.location_traffic_states.extend(location_states)
        self.recorder.traffic_pressure_overrides.extend(overrides)

    def apply_pressure_overrides(self, *, year: int, observations):
        overrides = {
            x.location_id: x
            for x in self.recorder.traffic_pressure_overrides
            if x.year == year
        }
        rows = []
        for observation in observations:
            if observation.channel_id != "TRANSPORT":
                rows.append(observation)
                continue
            override = overrides.get(observation.location_id)
            if override is None:
                rows.append(observation)
                continue

            quantified = list(observation.quantified_components)
            drivers = list(observation.driver_components)
            if override.opening_backlog_clearance_tonnes_year:
                source_id = "traffic:opening_backlog_clearance"
                quantified.append(
                    DemandComponent(
                        component_type="TRAFFIC_BACKLOG_CLEARANCE",
                        source_id=source_id,
                        quantity=override.opening_backlog_clearance_tonnes_year,
                        unit="tonnes/year",
                    )
                )
                drivers.append(source_id)

            required = override.required_transport_tonnes_year
            available = override.available_transport_tonnes_year
            rows.append(
                replace(
                    observation,
                    required=required,
                    available=available,
                    unmet=max(0.0, required - available),
                    driver_components=tuple(drivers),
                    quantified_components=tuple(quantified),
                    available_component_type="TRAFFIC_SERVICE_CAPACITY",
                    available_source_id=(
                        f"traffic:service_capacity:{year}:"
                        f"{observation.location_id}"
                    ),
                )
            )
        return tuple(rows)


__all__ = ["TrafficLaneV1"]
