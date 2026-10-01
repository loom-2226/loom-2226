"""Hybrid adapter for CIVPROP Resource Mass Balance V1.

This lane is evaluator-side physical accounting. It never exposes hidden physical
stock/grade to actor decision code and never mutates actor-visible knowledge.

GAP-008 currently supplies no economic consumption/export demand; those sinks can
be passed by later governed production/traffic layers without changing the mass
accounting contract.
"""
from __future__ import annotations

from engineering.civprop.contracts.resource_mass_balance_v1 import (
    ResourceMassBalanceRuntime,
)


class ResourceLaneV1:
    def __init__(self, bundle, recorder):
        package = bundle.scenario.resource_mass_balance_v1
        physical = bundle.truth.resource_physical_realization_v1
        if package is None:
            raise ValueError("ResourceLaneV1 requires Resource Mass Balance V1")
        if physical is None:
            raise ValueError(
                "ResourceLaneV1 requires evaluator physical realization"
            )
        self.runtime = ResourceMassBalanceRuntime(package, physical)
        self.recorder = recorder

    def step(self, *, year: int) -> None:
        states, flows = self.runtime.step(
            year=year,
            facilities=tuple(self.recorder.facilities),
        )
        self.recorder.resource_states.extend(states)
        self.recorder.resource_flows.extend(flows)


__all__ = ["ResourceLaneV1"]
