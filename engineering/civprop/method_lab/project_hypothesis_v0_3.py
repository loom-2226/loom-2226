"""Actor-originated project hypotheses.

A hypothesis is a proposed course of action, not a fact. It may bind only fields
supported by actor knowledge/world authority and keeps unresolved requirements explicit.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Mapping,Sequence

class HypothesisStatus(str,Enum):
 DRAFT="DRAFT"; INVESTIGATING="INVESTIGATING"; ASSEMBLING="ASSEMBLING"
 FEASIBILITY_REVIEW="FEASIBILITY_REVIEW"; READY_TO_COMMIT="READY_TO_COMMIT"
 BLOCKED="BLOCKED"; DEFERRED="DEFERRED"; REJECTED="REJECTED"

@dataclass(frozen=True)
class ProjectHypothesisV03:
 hypothesis_id:str; origin_actor_id:str; objective:str; subject_id:str
 project_archetype_id:str|None; project_kind:str|None
 origin_location_id:str|None; destination_location_id:str|None
 target_year:int|None; scale_value:float|None; scale_unit:str|None
 required_technology_ids:tuple[str,...]; required_capacities:tuple[tuple[str,float],...]
 unresolved_requirements:tuple[str,...]; status:HypothesisStatus
 provenance_refs:tuple[str,...]
 semantics:str="ACTOR_PROPOSED_HYPOTHESIS_NOT_WORLD_FACT"

def from_observed_mission(*,actor_id:str,subject_id:str,objective:str,actor_state:Mapping[str,object],
                          accessibility:Mapping[str,object],project_archetype_id:str|None=None):
 """Form the narrowest hypothesis supported by observed actor/service records."""
 refs=set(); dest=None; origin=None; year=None; unresolved=[]
 access_records=actor_state.get("access_rights",{}).get("records",[])
 provider_records=actor_state.get("provider_service_access",{}).get("records",[])
 matching=[x for x in access_records+provider_records if x.get("subject_id") in (subject_id,subject_id+"_WITH_NASA_MNP")]
 for x in matching:
  refs.update(x.get("provenance_refs",()));year=year or x.get("target_landing_year")
 paths=[x for x in accessibility.get("service_paths",[]) if x.get("subject_id") in (subject_id,subject_id+"_WITH_NASA_MNP")]
 for p in paths:
  refs.update(p.get("provenance_refs",()));origin=p.get("origin_location_id");dest=p.get("destination_location_id");year=year or p.get("target_year")
  if p.get("status")!="FEASIBLE":unresolved.append("TRANSPORT_FEASIBILITY")
  unresolved.extend(str(x) for x in p.get("limiting_constraints",[]))
 if not paths:unresolved.append("TRANSPORT_SERVICE_PATH")
 if not dest:unresolved.append("DESTINATION")
 return ProjectHypothesisV03(
  f"HYP:{actor_id}:{subject_id}",actor_id,objective,subject_id,project_archetype_id,
  "MISSION" if project_archetype_id else None,origin,dest,year,None,None,(),(),
  tuple(sorted(set(unresolved))),HypothesisStatus.INVESTIGATING if unresolved else HypothesisStatus.FEASIBILITY_REVIEW,
  tuple(sorted(refs)))

def refine(h:ProjectHypothesisV03,*,resolved_requirements:Sequence[str]=(),new_provenance:Sequence[str]=()):
 remaining=tuple(x for x in h.unresolved_requirements if x not in set(resolved_requirements))
 status=HypothesisStatus.FEASIBILITY_REVIEW if not remaining else HypothesisStatus.INVESTIGATING
 return ProjectHypothesisV03(**{**h.__dict__,"unresolved_requirements":remaining,"status":status,
   "provenance_refs":tuple(sorted(set(h.provenance_refs+tuple(new_provenance))))})
