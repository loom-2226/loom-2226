"""Production Accounting V1 adapter for Hybrid.

The lane is accounting/output only at GAP-009 closure. It does not mutate location
state, facility capacity, actor knowledge, pressure, budgets, decisions, or RNG.

Later governed gaps may supply explicit constraint observations. Until then missing
required power/labor/material/transport constraints remain UNKNOWN.
"""
from __future__ import annotations

from engineering.civprop.contracts.production_accounting_v1 import (
    ConstraintObservationV1,
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
        power_by_location = {
            x.location_id: x
            for x in self.recorder.power_states
            if x.year == year
        }
        rows = []
        for facility in sorted(
            active_facilities,
            key=lambda x: x.facility_id,
        ):
            constraint_observations = {}
            power_state = power_by_location.get(facility.location_id)
            if power_state is not None:
                if power_state.power_service_ratio is None:
                    power_status = "UNKNOWN"
                    power_ratio = None
                else:
                    power_status = "KNOWN"
                    power_ratio = power_state.power_service_ratio
                constraint_observations["POWER"] = (
                    ConstraintObservationV1(
                        constraint_id="POWER",
                        status=power_status,
                        utilization_ratio=power_ratio,
                        provenance_refs=(
                            "CIVPROP_POWER_BALANCE_V1",
                            power_state.power_state_id,
                        ),
                    )
                )
            rows.append(
                self.runtime.evaluate_facility(
                    year=year,
                    facility=facility,
                    constraint_observations=constraint_observations,
                    resource_states=tuple(self.recorder.resource_states),
                    peer_facilities=active_facilities,
                    power_states=tuple(self.recorder.power_states),
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
