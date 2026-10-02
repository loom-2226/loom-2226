"""Power Balance V1 adapter for Hybrid.

Runs after commissioning/resource accounting and before Production Accounting V1.
It emits annual location-level power state and energy flows only; it does not mutate
civilization state, budgets, decisions, pressure, knowledge, or RNG.
"""
from __future__ import annotations

from engineering.civprop.contracts.power_balance_v1 import (
    PowerBalanceRuntime,
)


class PowerLaneV1:
    def __init__(self, bundle, recorder, current_index=None):
        package = bundle.scenario.power_balance_v1
        demand = bundle.scenario.demand_pressure_v1
        if package is None or demand is None:
            raise ValueError(
                "PowerLaneV1 requires Power Balance V1 and Demand/Pressure V1"
            )
        self.bundle = bundle
        self.recorder = recorder
        self.current_index = current_index
        self.runtime = PowerBalanceRuntime(package, demand)

    def step(self, *, year: int, states) -> None:
        if self.current_index is not None:
            self.current_index.sync_facilities(self.recorder.facilities, year=year)
            facilities_by_location = self.current_index.active_facilities_by_location
        else:
            facilities_by_location = {}
            for facility in self.recorder.facilities:
                if facility.status == "ACTIVE" and facility.commissioned_year <= year:
                    facilities_by_location.setdefault(facility.location_id, []).append(facility)
        for location_id in sorted(states):
            if self.runtime.is_excluded(location_id):
                continue
            state, flows = self.runtime.step_location(
                year=year,
                location_id=location_id,
                state=states[location_id],
                facilities=tuple(facilities_by_location.get(location_id, ())),
            )
            self.recorder.power_states.append(state)
            self.recorder.power_flows.extend(flows)


__all__ = ["PowerLaneV1"]
