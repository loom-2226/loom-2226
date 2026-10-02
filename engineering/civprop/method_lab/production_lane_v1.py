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
    def __init__(self, bundle, recorder, current_index=None):
        package = bundle.scenario.production_accounting_v1
        if package is None:
            raise ValueError(
                "ProductionLaneV1 requires Production Accounting V1"
            )
        self.bundle = bundle
        self.recorder = recorder
        self.current_index = current_index
        self.runtime = ProductionAccountingRuntime(package)
        self.location_to_body = {
            x.location_id: x.parent_body_id
            for x in bundle.scenario.locations
        }
        # Historical recorder lists remain append-only provenance.  Production only
        # needs the newly appended current-year physical states, so cursors prevent
        # O(total-history) rescans every year.
        self._power_cursor = 0
        self._traffic_cursor = 0
        self._resource_cursor = 0

    def step(self, *, year: int) -> None:
        if self.current_index is not None:
            self.current_index.sync_facilities(self.recorder.facilities, year=year)
            self.current_index.sync_physical_states(self.recorder)
            active_facilities = self.current_index.active_facilities()
        else:
            active_facilities = tuple(
                facility for facility in self.recorder.facilities
                if facility.status == "ACTIVE" and facility.commissioned_year <= year
            )
        new_power = self.recorder.power_states[self._power_cursor:]
        new_traffic = self.recorder.location_traffic_states[self._traffic_cursor:]
        new_resources = self.recorder.resource_states[self._resource_cursor:]
        self._power_cursor = len(self.recorder.power_states)
        self._traffic_cursor = len(self.recorder.location_traffic_states)
        self._resource_cursor = len(self.recorder.resource_states)
        current_power = tuple(x for x in new_power if x.year == year)
        current_traffic = tuple(x for x in new_traffic if x.year == year)
        current_resources = tuple(x for x in new_resources if x.year == year)
        power_by_location = ({k:v for k,v in self.current_index.latest_power_by_location.items() if v.year == year}
                             if self.current_index is not None else {x.location_id:x for x in current_power})
        traffic_by_location = ({k:v for k,v in self.current_index.latest_traffic_by_location.items() if v.year == year}
                               if self.current_index is not None else {x.location_id:x for x in current_traffic})
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
            traffic_state = traffic_by_location.get(
                facility.location_id
            )
            if traffic_state is not None:
                if traffic_state.transport_service_ratio is None:
                    transport_status = "UNKNOWN"
                    transport_ratio = None
                else:
                    transport_status = "KNOWN"
                    transport_ratio = (
                        traffic_state.transport_service_ratio
                    )
                constraint_observations["TRANSPORT"] = (
                    ConstraintObservationV1(
                        constraint_id="TRANSPORT",
                        status=transport_status,
                        utilization_ratio=transport_ratio,
                        provenance_refs=(
                            "CIVPROP_TRAFFIC_FLEET_V1",
                            traffic_state.location_traffic_state_id,
                        ),
                    )
                )
            rows.append(
                self.runtime.evaluate_facility(
                    year=year,
                    facility=facility,
                    constraint_observations=constraint_observations,
                    resource_states=current_resources,
                    peer_facilities=active_facilities,
                    power_states=current_power,
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
