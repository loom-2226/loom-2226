"""Gate-C named lunar service qualification.

This contract admits only a named provider service whose payload, actor access,
provider capacity, launch qualification and destination are independently
evidenced. It is not a generic Blue Ghost performance model.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

CONTRACT_VERSION = "0.3.0"
SERVICE_ID = "NASA_LUSEE_NIGHT_BLUE_GHOST_2"
REQUIRED_ACTOR_CAPABILITY = "CLPS_NAMED_LUNAR_DELIVERY_ACCESS"

@dataclass(frozen=True)
class NamedServiceAssessment:
    service_id: str
    actor_id: str
    origin_location_id: str
    destination_location_id: str
    payload_id: str
    status: str
    cargo_mass_tonnes: float | None
    provider_surface_capacity_tonnes: float | None
    geometry_status: str
    actor_access_status: str
    vehicle_capability_status: str
    infrastructure_status: str
    limiting_constraints: tuple[str, ...]
    provenance_refs: tuple[str, ...]


def assess_named_service(*, actor_id: str, year: int,
                         actor_capabilities: Mapping[str, str],
                         evidence: Mapping[str, object]) -> NamedServiceAssessment:
    constraints: list[str] = []
    refs = tuple(str(x) for x in evidence.get("provenance_refs", ()))
    if not refs:
        constraints.append("PROVENANCE_MISSING")

    if evidence.get("service_id") != SERVICE_ID:
        constraints.append("NAMED_SERVICE_MISMATCH")
    if actor_id != "NASA":
        constraints.append("ACTOR_OUT_OF_SCOPE")

    access = actor_capabilities.get(REQUIRED_ACTOR_CAPABILITY, "UNKNOWN")
    if access not in {"ACCESS", "OPERATIONAL"}:
        constraints.append("ACTOR_ACCESS_UNKNOWN" if access == "UNKNOWN" else "ACTOR_ACCESS_NOT_USABLE")

    # Baseline chemical/cislunar capability: no Timeline frontier is used to
    # manufacture access. The service must instead exist in dated evidence.
    observed_from = int(evidence.get("observed_from_year", 9999))
    if year < observed_from:
        constraints.append("SERVICE_NOT_YET_EVIDENCED")

    geometry = evidence.get("geometry_status")
    if geometry != "QUALIFIED_EARTH_MOON_NAMED_ROUTE":
        constraints.append("GEOMETRY_NOT_QUALIFIED")

    payload = evidence.get("payload_mass_kg")
    capacity = evidence.get("provider_surface_capacity_kg")
    if payload is None or capacity is None:
        constraints.append("VEHICLE_ENVELOPE_UNKNOWN")
    else:
        payload = float(payload); capacity = float(capacity)
        if payload < 0 or capacity <= 0:
            constraints.append("INVALID_MASS_ENVELOPE")
        elif payload > capacity:
            constraints.append("PAYLOAD_EXCEEDS_PROVIDER_SURFACE_CAPACITY")

    if evidence.get("payload_manifest_status") != "NAMED_ON_PROVIDER_MISSION":
        constraints.append("PAYLOAD_NOT_MANIFESTED")
    if evidence.get("launch_qualification_status") != "STRUCTURAL_QUALIFICATION_COMPLETE_FOR_FALCON_9":
        constraints.append("LAUNCH_QUALIFICATION_UNKNOWN")
    if evidence.get("surface_service_status") != "CONTRACTED_NASA_CLPS_DELIVERY":
        constraints.append("SURFACE_SERVICE_NOT_CONTRACTED")

    if constraints:
        infeasible = {"PAYLOAD_EXCEEDS_PROVIDER_SURFACE_CAPACITY", "SERVICE_NOT_YET_EVIDENCED"}
        status = "INFEASIBLE" if any(x in infeasible for x in constraints) else "UNKNOWN"
    else:
        status = "FEASIBLE_NAMED_SERVICE"

    return NamedServiceAssessment(
        SERVICE_ID, actor_id, "EARTH_SURFACE", "LUNA_FAR_SIDE",
        str(evidence.get("payload_id", "UNKNOWN")), status,
        None if payload is None else payload / 1000.0,
        None if capacity is None else capacity / 1000.0,
        str(geometry or "UNKNOWN"), access,
        "QUALIFIED_NAMED_PROVIDER_ENVELOPE" if not any(x in constraints for x in (
            "VEHICLE_ENVELOPE_UNKNOWN","INVALID_MASS_ENVELOPE",
            "PAYLOAD_EXCEEDS_PROVIDER_SURFACE_CAPACITY","LAUNCH_QUALIFICATION_UNKNOWN")) else "UNKNOWN",
        "CONTRACTED_PROVIDER_SURFACE_DELIVERY" if evidence.get("surface_service_status") == "CONTRACTED_NASA_CLPS_DELIVERY" else "UNKNOWN",
        tuple(constraints), refs,
    )
