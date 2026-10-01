"""Production Accounting V1 adapter for Hybrid.

The lane is accounting/output only at GAP-009 closure. It does not mutate location
state, facility capacity, actor knowledge, pressure, budgets, decisions, or RNG.

Later governed gaps may supply explicit constraint observations. Until then missing
required power/labor/material/transport constraints remain UNKNOWN.
"""
from __future__ import annotations

from engineering.civprop.contracts.production_accounting_v1 import (
    ProductionAccountingRuntime,
)


class ProductionLaneV1:
    def __init__(self, bundle, recorder):
        package = bundle.scenario.production_accounting_v1
        if package is None:
            raise ValueError(
                "ProductionLaneV1 requires Production Accounting V1"
            )
        self.bundle = bundle
        self.recorder = recorder
        self.runtime = ProductionAccountingRuntime(package)
        self.location_to_body = {
            x.location_id: x.parent_body_id
            for x in bundle.scenario.locations
        }

    def step(self, *, year: int) -> None:
        active_facilities = tuple(
            facility
            for facility in self.recorder.facilities
            if facility.status == "ACTIVE"
            and facility.commissioned_year <= year
        )
        rows = []
        for facility in sorted(
            active_facilities,
            key=lambda x: x.facility_id,
        ):
            rows.append(
                self.runtime.evaluate_facility(
                    year=year,
                    facility=facility,
                    constraint_observations={},
                    resource_states=tuple(self.recorder.resource_states),
                    peer_facilities=active_facilities,
                )
            )

        sectors, locations, bodies = self.runtime.aggregate(
            year=year,
            facility_states=tuple(rows),
            location_to_body=self.location_to_body,
        )
        self.recorder.facility_production_states.extend(rows)
        self.recorder.sector_production_states.extend(sectors)
        self.recorder.location_production_states.extend(locations)
        self.recorder.body_production_states.extend(bodies)


__all__ = ["ProductionLaneV1"]
