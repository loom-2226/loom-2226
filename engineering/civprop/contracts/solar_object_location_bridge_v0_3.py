"""Deterministic Solar authority -> CIVPROP candidate-location bridge V0.3.

This bridge expands the *candidate universe* only.  It does not assert transport
accessibility, actor capability, economic attractiveness, settlement, or surface
operations.  Those remain downstream contracts.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any

BRIDGE_VERSION = "0.3.0"
NON_DESTINATION_CLASSES = {"BARYCENTER", "SPACECRAFT", "STAR"}
SURFACE_CAPABLE_CLASSES = {
    "PLANET", "DWARF_PLANET", "NATURAL_SATELLITE", "ASTEROID",
    "NEAR_EARTH_ASTEROID", "TROJAN_ASTEROID", "TRANS_NEPTUNIAN_OBJECT",
    "BINARY_ASTEROID_PRIMARY", "CENTAUR", "COMET",
}

@dataclass(frozen=True)
class SolarCandidateLocation:
    location_id: str
    body_id: str
    canonical_name: str
    body_class: str
    placement: str
    nav0_status: str
    nav1_status: str
    candidate_status: str
    provenance_refs: tuple[str, ...]


def _candidate_status(row: dict[str, Any]) -> str:
    if row["body_class"] in NON_DESTINATION_CLASSES:
        return "NON_DESTINATION_CLASS"
    if row["nav0"] != "SUPPORTED":
        return "IDENTITY_NOT_NAV0_SUPPORTED"
    if row["nav1"] != "SUPPORTED":
        return "NAV1_NOT_SUPPORTED_AT_ASSESSMENT_EPOCH"
    return "NAV1_CANDIDATE"


def build_solar_candidate_locations(nav_readiness_path: Path) -> dict[str, Any]:
    nav = json.loads(nav_readiness_path.read_text())
    rows: list[SolarCandidateLocation] = []
    for body in sorted(nav["bodies"], key=lambda x: x["body_id"]):
        status = _candidate_status(body)
        # Every natural/material destination gets an ORBITAL/PROXIMITY candidate lane.
        # SURFACE is a separate candidate location, not authority that landing is feasible.
        if body["body_class"] in NON_DESTINATION_CLASSES:
            continue
        placements = ("ORBITAL", "SURFACE") if body["body_class"] in SURFACE_CAPABLE_CLASSES else ("ORBITAL",)
        for placement in placements:
            rows.append(SolarCandidateLocation(
                location_id=f"{body['body_id']}_{placement}", body_id=body["body_id"],
                canonical_name=body["canonical_name"], body_class=body["body_class"],
                placement=placement, nav0_status=body["nav0"], nav1_status=body["nav1"],
                candidate_status=status,
                provenance_refs=("NAV_READINESS_V1", "SOLAR_OBJECT_LOCATION_BRIDGE_V0_3"),
            ))
    return {
        "format": "CIVPROP_SOLAR_OBJECT_LOCATION_BRIDGE_V0_3",
        "bridge_version": BRIDGE_VERSION,
        "assessment_epoch_utc": nav["assessment_epoch_utc"],
        "semantics": {
            "candidate_is_not_accessible": True,
            "surface_location_is_not_surface_access_authority": True,
            "nav1_failure_preserves_body": True,
            "transport_and_actor_access_are_downstream": True,
        },
        "locations": [asdict(x) for x in rows],
    }
