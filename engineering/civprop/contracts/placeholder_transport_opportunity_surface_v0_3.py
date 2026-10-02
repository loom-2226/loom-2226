"""Authored non-physical Solar transport-friction placeholder for V0.3.

Purpose: let Solar geography matter during propagation while GAP-016 remains OPEN.
Values are dimensionless scenario assumptions, deliberately NOT distance, delta-v,
C3, flight time, payload, price, probability, or empirical accessibility.
"""
from __future__ import annotations
from dataclasses import dataclass

CONTRACT_VERSION="0.3.1"

# Earth-origin generalized friction bands.  Strongly nonlinear by design.
# These are propagation-test assumptions, not measurements.
BODY_FRICTION={
 "MOON":1.5,
 "MERCURY":8.0,"VENUS":4.0,"MARS":6.0,
 "CERES":18.0,"VESTA":18.0,"PSYCHE":20.0,
 "JUPITER":55.0,"SATURN":100.0,"URANUS":220.0,"NEPTUNE":320.0,
 "PLUTO":500.0,"CHARON":500.0,
 "ERIS":650.0,"MAKEMAKE":575.0,"HAUMEA":550.0,"SEDNA":900.0,
 "QUAOAR":525.0,"ORCUS":500.0,"SALACIA":525.0,"GONGGONG":650.0,
 "ARROKOTH":650.0,"IXION":525.0,"MS4":575.0,"VARUNA":525.0,
}
CLASS_FRICTION={
 "NEAR_EARTH_ASTEROID":7.0,
 "ASTEROID":20.0,
 "BINARY_ASTEROID_PRIMARY":20.0,
 "COMET":25.0,
 "CENTAUR":140.0,
 "TROJAN_ASTEROID":55.0,
 "TRANS_NEPTUNIAN_OBJECT":600.0,
 "INTERSTELLAR_OBJECT":1000.0,
}
PARENT_SYSTEM_FRICTION={
 # satellites inherit the coarse burden of reaching their planetary system.
 "MARS":6.0,"JUPITER":55.0,"SATURN":100.0,"URANUS":220.0,"NEPTUNE":320.0,"PLUTO":500.0,
}
SATELLITE_PARENT={
 "PHOBOS":"MARS","DEIMOS":"MARS",
 "IO":"JUPITER","EUROPA":"JUPITER","GANYMEDE":"JUPITER","CALLISTO":"JUPITER",
 "MIMAS":"SATURN","ENCELADUS":"SATURN","TETHYS":"SATURN","DIONE":"SATURN","RHEA":"SATURN","TITAN":"SATURN","HYPERION":"SATURN","IAPETUS":"SATURN","PHOEBE":"SATURN",
 "MIRANDA":"URANUS","ARIEL":"URANUS","UMBRIEL":"URANUS","TITANIA":"URANUS","OBERON":"URANUS",
 "TRITON":"NEPTUNE","NEREID":"NEPTUNE","PROTEUS":"NEPTUNE",
 "CHARON":"PLUTO","NIX":"PLUTO","HYDRA":"PLUTO","KERBEROS":"PLUTO","STYX":"PLUTO",
}

@dataclass(frozen=True)
class PlaceholderTransportOpportunity:
 origin_location_id:str
 destination_location_id:str
 year:int
 value:float
 unit:str="DIMENSIONLESS_GENERALIZED_FRICTION_PLACEHOLDER"
 status:str="EXPLICIT_AUTHORED_PLACEHOLDER"
 gap_owner:str="GAP-016"
 provenance_ref:str="NON_PHYSICAL_SOLAR_V03_PROPAGATION_PLACEHOLDER"

def friction_for_body(body_id:str,body_class:str)->float:
 b=str(body_id).upper()
 if b=="EARTH": return 1.0
 if b in BODY_FRICTION: return BODY_FRICTION[b]
 if b in SATELLITE_PARENT: return PARENT_SYSTEM_FRICTION[SATELLITE_PARENT[b]]
 if body_class in CLASS_FRICTION: return CLASS_FRICTION[body_class]
 if body_class=="NATURAL_SATELLITE": return 40.0 # explicit fallback, not inferred physics
 if body_class=="PLANET": return 40.0
 if body_class=="DWARF_PLANET": return 300.0
 raise ValueError(f"no authored placeholder friction for {body_id}/{body_class}")

def evaluate(origin_location_id:str,destination_location_id:str,year:int,*,destination_body_id:str,destination_body_class:str)->PlaceholderTransportOpportunity:
 if not (2026 <= int(year) <= 2226): raise ValueError("V0.3 placeholder is scoped only to 2026..2226")
 return PlaceholderTransportOpportunity(origin_location_id,destination_location_id,int(year),friction_for_body(destination_body_id,destination_body_class))

def semantics():
 return {
  "physical_claim":False,"constant_over_time":True,"constant_across_destinations":False,
  "earth_reference_friction":1.0,"higher_value_means_more_friction":True,
  "actor_access_claim":False,"economic_claim":False,"production_eligible":False,
  "replacement_gap":"GAP-016",
  "design_intent":"COARSE_NONLINEAR_SOLAR_GEOGRAPHY_FOR_PROPAGATION_TESTING",
  "forbidden_interpretations":["DISTANCE","DELTA_V","C3","FLIGHT_TIME","PAYLOAD","PRICE","PROBABILITY","EMPIRICAL_ACCESSIBILITY"],
 }
