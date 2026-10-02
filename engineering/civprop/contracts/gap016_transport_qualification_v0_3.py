"""GAP-016 scoped transport qualification state for causal-runtime migration.

NON-CANON / UNPROMOTED.  A named contracted service may be physically usable
without reconstructing provider-internal propulsion, while generic vehicle
performance remains solver-gated.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .gate_c_named_lunar_service_v0_3 import assess_named_service

@dataclass(frozen=True)
class Gap016QualificationV03:
 status:str
 qualified_scope:tuple[str,...]
 open_scope:tuple[str,...]
 service_status:str
 generic_chemical_status:str
 nuclear_electric_status:str
 fusion_torch_status:str
 metric_vessel_status:str
 controlling_principles:tuple[str,...]
 provenance_refs:tuple[str,...]

def qualify_gap016(*,year:int,actor_id:str,actor_capabilities:Mapping[str,str],
                   named_service_evidence:Mapping[str,object])->Gap016QualificationV03:
 a=assess_named_service(actor_id=actor_id,year=year,
     actor_capabilities=actor_capabilities,evidence=named_service_evidence)
 qualified=()
 if a.status=="FEASIBLE_NAMED_SERVICE":
  qualified=("NASA_LUSEE_NIGHT_BLUE_GHOST_2_NAMED_PROVIDER_SERVICE",)
 return Gap016QualificationV03(
  "PARTIAL_CLOSURE_NAMED_SERVICE_ONLY" if qualified else "OPEN",
  qualified,
  ("GENERIC_CHEMICAL_INTERBODY_VEHICLE_PERFORMANCE",
   "NUCLEAR_ELECTRIC_LOW_THRUST_PERFORMANCE",
   "FUSION_TORCH_TRANSPORT_PERFORMANCE",
   "METRIC_VESSEL_TRANSPORT_PERFORMANCE"),
  a.status,
  "EVIDENCE_FED_ROCKET_EQUATION_AVAILABLE_BUT_GENERIC_MANEUVER_AND_VEHICLE_AUTHORITY_MISSING",
  "PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED",
  "PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED",
  "PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED",
  ("NAMED_CONTRACTED_SERVICE_MAY_ABSTRACT_PROVIDER_INTERNAL_PROPULSION",
   "NAMED_SERVICE_DOES_NOT_GENERALIZE_TO_ARBITRARY_PAYLOAD_ACTOR_DATE_OR_SITE",
   "TIMELINE_FRONTIER_DOES_NOT_CREATE_ACTOR_CAPABILITY",
   "GEOMETRY_OPPORTUNITY_DOES_NOT_IMPLY_VEHICLE_FEASIBILITY"),
  tuple(a.provenance_refs))
