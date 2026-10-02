"""Explicit non-physical transport-opportunity placeholder for Solar V0.3.

Purpose: exercise full-Solar propagation plumbing while GAP-016 remains OPEN.
This value has NO physical units and MUST NOT be interpreted as distance, delta-v,
C3, flight time, payload, price, probability, or empirical accessibility.
"""
from __future__ import annotations
from dataclasses import dataclass

CONTRACT_VERSION="0.3.0"
PLACEHOLDER_TRANSPORT_OPPORTUNITY=1.0

@dataclass(frozen=True)
class PlaceholderTransportOpportunity:
    origin_location_id:str
    destination_location_id:str
    year:int
    value:float=PLACEHOLDER_TRANSPORT_OPPORTUNITY
    unit:str="DIMENSIONLESS_PLACEHOLDER"
    status:str="EXPLICIT_PLACEHOLDER"
    gap_owner:str="GAP-016"
    provenance_ref:str="NON_PHYSICAL_SOLAR_V03_PROPAGATION_PLACEHOLDER"

def evaluate(origin_location_id:str,destination_location_id:str,year:int)->PlaceholderTransportOpportunity:
    if not (2026 <= int(year) <= 2226):
        raise ValueError("V0.3 placeholder is scoped only to 2026..2226")
    return PlaceholderTransportOpportunity(origin_location_id,destination_location_id,int(year))

def semantics():
    return {
      "physical_claim":False,
      "constant_over_time":True,
      "constant_across_destinations":True,
      "actor_access_claim":False,
      "economic_claim":False,
      "production_eligible":False,
      "replacement_gap":"GAP-016",
      "forbidden_interpretations":["DISTANCE","DELTA_V","C3","FLIGHT_TIME","PAYLOAD","PRICE","PROBABILITY","EMPIRICAL_ACCESSIBILITY"],
    }
