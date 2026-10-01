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
    def __init__(self, bundle, recorder):
        package = bundle.scenario.power_balance_v1
        demand = bundle.scenario.demand_pressure_v1
        if package is None or demand is None:
            raise ValueError(
                "PowerLaneV1 requires Power Balance V1 and Demand/Pressure V1"
            )
        self.bundle = bundle
        self.recorder = recorder
        self.runtime = PowerBalanceRuntime(package, demand)

    def step(self, *, year: int, states) -> None:
        facilities = tuple(self.recorder.facilities)
        for location_id in sorted(states):
            if self.runtime.is_excluded(location_id):
                continue
            state, flows = self.runtime.step_location(
                year=year,
                location_id=location_id,
                state=states[location_id],
                facilities=facilities,
            )
            self.recorder.power_states.append(state)
            self.recorder.power_flows.extend(flows)


__all__ = ["PowerLaneV1"]
