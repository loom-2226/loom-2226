"""Solar transfer opportunity × propulsion regime × actor capability V0.3.

This is a screening boundary, not a vehicle-performance model.  Lambert geometry
supports impulsive-transfer screening only.  Low-thrust, torch and metric regimes
remain solver-gated until their own qualified transport models exist. Timeline
dates are consideration anchors and never grant actor capability.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .solar_transport_opportunity_v0_3 import TransferOpportunity

BRIDGE_VERSION="0.3.0"
ACTOR_USABLE={"OPERATIONAL","ACCESS"}
ACTOR_NOT_YET={"DEVELOPMENT"}
ACTOR_UNKNOWN={"UNKNOWN"}

PROPULSION_REGIMES={
 "CHEMICAL_IMPULSIVE":{
   "authority_class":"BASELINE_SCREENING_METHOD",
   "geometry_solver":"LAMBERT_UNIVERSAL_ZERO_REV_PROGRADE",
   "frontier_milestone_id":None,
   "required_actor_capabilities":("ORBITAL_LAUNCH","SPACECRAFT_OPS","DEEP_SPACE"),
   "performance_model_status":"GEOMETRY_ONLY_NO_PAYLOAD_OR_MASS_RATIO",
 },
 "NUCLEAR_ELECTRIC":{
   "authority_class":"AUTHOR_SCENARIO_MODERATE",
   "geometry_solver":"LOW_THRUST_SOLVER_REQUIRED",
   "frontier_milestone_id":"TRN-MOD-NEP",
   "required_actor_capabilities":("SPACECRAFT_OPS","DEEP_SPACE","NUCLEAR_ELECTRIC_SPACECRAFT"),
   "performance_model_status":"NOT_IMPLEMENTED",
 },
 "FUSION_TORCH":{
   "authority_class":"SPECULATIVE_FICTION",
   "geometry_solver":"TORCH_SOLVER_REQUIRED",
   "frontier_milestone_id":"SPEC-MOD-TORCH",
   "required_actor_capabilities":("SPACECRAFT_OPS","DEEP_SPACE","FUSION_TORCH_SPACECRAFT"),
   "performance_model_status":"NOT_IMPLEMENTED",
 },
 "METRIC_VESSEL":{
   "authority_class":"SPECULATIVE_FICTION",
   "geometry_solver":"METRIC_SOLVER_REQUIRED",
   "frontier_milestone_id":"SPEC-MOD-METRIC-SHIP",
   "required_actor_capabilities":("SPACECRAFT_OPS","DEEP_SPACE","METRIC_VESSEL"),
   "performance_model_status":"NOT_IMPLEMENTED",
 },
}

@dataclass(frozen=True)
class ActorTransportAssessment:
 actor_id:str
 propulsion_regime:str
 origin_body_id:str
 destination_body_id:str
 departure_epoch_utc:str
 status:str
 geometry_status:str
 technology_frontier_status:str
 actor_capability_status:str
 limiting_constraints:tuple[str,...]
 provenance_refs:tuple[str,...]

def _frontier(regime, year:int, timeline_by_milestone:Mapping[str,Mapping]):
 mid=regime["frontier_milestone_id"]
 if mid is None: return "BASELINE_METHOD"
 row=timeline_by_milestone.get(mid)
 if row is None: return "UNKNOWN"
 return "BEFORE_CONSIDERATION_ANCHOR" if year<int(row["frontier_year"]) else "CONSIDERATION_ANCHOR_REACHED_NOT_ACHIEVEMENT"

def assess_actor_transport(opportunity:TransferOpportunity, propulsion_regime:str,
                           actor_id:str, actor_capabilities:Mapping[str,str],
                           timeline_by_milestone:Mapping[str,Mapping]):
 if propulsion_regime not in PROPULSION_REGIMES: raise ValueError("unknown propulsion regime")
 r=PROPULSION_REGIMES[propulsion_regime]
 year=int(opportunity.departure_epoch_utc[:4]); frontier=_frontier(r,year,timeline_by_milestone)
 constraints=[]
 if opportunity.status!="GEOMETRY_OPPORTUNITY_ONLY": constraints.append("GEOMETRY_NOT_QUALIFIED_AS_OPPORTUNITY")
 vals=[actor_capabilities.get(x,"UNKNOWN") for x in r["required_actor_capabilities"]]
 if any(x=="UNKNOWN" for x in vals): actor="UNKNOWN"; constraints.append("ACTOR_CAPABILITY_UNKNOWN")
 elif any(x=="DEVELOPMENT" for x in vals): actor="CONDITIONAL"; constraints.append("ACTOR_CAPABILITY_DEVELOPMENT")
 else: actor="USABLE"
 if frontier=="BEFORE_CONSIDERATION_ANCHOR": constraints.append("TECHNOLOGY_BEFORE_CONSIDERATION_ANCHOR")
 if frontier=="UNKNOWN": constraints.append("TECHNOLOGY_FRONTIER_UNKNOWN")
 if r["performance_model_status"]=="NOT_IMPLEMENTED": constraints.append("PROPULSION_PERFORMANCE_SOLVER_NOT_IMPLEMENTED")
 # A reached timeline anchor cannot turn a missing actor capability or solver into FEASIBLE.
 if constraints:
  status="INFEASIBLE" if "TECHNOLOGY_BEFORE_CONSIDERATION_ANCHOR" in constraints else "UNKNOWN"
 else:
  status="SCREENABLE_GEOMETRY_AND_ACTOR_ACCESS"
 prov=tuple(dict.fromkeys((*opportunity.provenance_refs,
   f"PROPULSION_REGIME:{propulsion_regime}",
   *(tuple([r["frontier_milestone_id"]]) if r["frontier_milestone_id"] else ()))))
 return ActorTransportAssessment(actor_id,propulsion_regime,opportunity.origin_body_id,
  opportunity.destination_body_id,opportunity.departure_epoch_utc,status,
  opportunity.status,frontier,actor,tuple(constraints),prov)
