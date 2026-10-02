"""Gate-C adapter from a qualified named physical service into Traffic/Fleet states.

This is a qualification realization, not an assertion that the future mission
has already flown. It deliberately does not create a reusable fleet asset.
"""
from __future__ import annotations
from dataclasses import dataclass
from .gate_c_named_lunar_service_v0_3 import NamedServiceAssessment
from .traffic_fleet_v1 import VoyageStateV1, LocationTrafficStateV1

ADAPTER_VERSION="0.3.0"

@dataclass(frozen=True)
class NamedServiceTrafficRealization:
    realization_class: str
    service_id: str
    year: int
    voyage: VoyageStateV1
    location_states: tuple[LocationTrafficStateV1,...]
    provenance_refs: tuple[str,...]


def realize_named_service(*, assessment: NamedServiceAssessment, year: int,
                          vehicle_id: str="BLUE_GHOST_2_NAMED_SERVICE") -> NamedServiceTrafficRealization:
    if assessment.status != "FEASIBLE_NAMED_SERVICE":
        raise ValueError("only FEASIBLE_NAMED_SERVICE may enter Traffic/Fleet realization")
    if assessment.cargo_mass_tonnes is None or assessment.provider_surface_capacity_tonnes is None:
        raise ValueError("named service requires known bounded cargo and provider capacity")
    if assessment.cargo_mass_tonnes > assessment.provider_surface_capacity_tonnes:
        raise ValueError("cargo exceeds provider surface envelope")

    v=VoyageStateV1(
        voyage_id=f"gatec-{assessment.service_id}-{year}",
        year=int(year), service_id=assessment.service_id, vehicle_id=vehicle_id,
        voyage_ordinal=1, origin_location_id=assessment.origin_location_id,
        destination_location_id=assessment.destination_location_id,
        cargo_tonnes=assessment.cargo_mass_tonnes, passenger_movements=0.0,
        departure_calls=1, arrival_calls=1,
    )
    earth=LocationTrafficStateV1(
        location_traffic_state_id=f"gatec-earth-{year}", year=int(year),
        location_id=assessment.origin_location_id, cargo_inbound_tonnes=0.0,
        cargo_outbound_tonnes=v.cargo_tonnes, cargo_throughput_tonnes_year=v.cargo_tonnes,
        passenger_inbound_movements=0.0, passenger_outbound_movements=0.0,
        passenger_movements_year=0.0, arrival_calls=0, departure_calls=1,
        ship_calls_year=1, transport_service_ratio=None,
        metric_scope="GATE_C_NAMED_SERVICE_QUALIFICATION_REALIZATION",
    )
    moon=LocationTrafficStateV1(
        location_traffic_state_id=f"gatec-moon-{year}", year=int(year),
        location_id=assessment.destination_location_id, cargo_inbound_tonnes=v.cargo_tonnes,
        cargo_outbound_tonnes=0.0, cargo_throughput_tonnes_year=v.cargo_tonnes,
        passenger_inbound_movements=0.0, passenger_outbound_movements=0.0,
        passenger_movements_year=0.0, arrival_calls=1, departure_calls=0,
        ship_calls_year=1, transport_service_ratio=None,
        metric_scope="GATE_C_NAMED_SERVICE_QUALIFICATION_REALIZATION",
    )
    return NamedServiceTrafficRealization(
        "QUALIFICATION_CONTROL_NOT_HISTORICAL_COMPLETION_OR_LAUNCH_FORECAST",
        assessment.service_id,int(year),v,(earth,moon),assessment.provenance_refs)
