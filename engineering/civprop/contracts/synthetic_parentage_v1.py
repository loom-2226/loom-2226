"""GAP-014 governed parentage and family-formation boundary.
NON_CANON / MACHINERY TEST. Parentage is an explicit realized relationship,
never inferred from household co-membership, age, sex/gender, or identity.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ParentageAssignmentV1:
 child_id:str
 parent_ids:tuple[str,...]
 assignment_kind:str
 provenance_refs:tuple[str,...]
 authority_class:str="SYNTHETIC_PARENTAGE_REALIZATION_NON_EMPIRICAL"

_ALLOWED=frozenset({"BIOLOGICAL","GESTATIONAL","GENETIC","LEGAL","SOCIAL","ARTIFICIAL_GESTATION"})

def assign_parentage(*,child_id,parent_ids,assignment_kind,provenance_refs,
                     known_person_ids):
 if assignment_kind not in _ALLOWED: raise ValueError("UNSUPPORTED_PARENTAGE_KIND")
 if not provenance_refs: raise ValueError("MISSING_PARENTAGE_PROVENANCE")
 parents=tuple(parent_ids)
 if len(parents)!=len(set(parents)): raise ValueError("DUPLICATE_PARENT")
 if child_id in parents: raise ValueError("SELF_PARENTAGE")
 known=set(known_person_ids)
 if child_id not in known or any(p not in known for p in parents):
  raise ValueError("UNKNOWN_PERSON_IN_PARENTAGE")
 # Zero parents is valid when lineage is unresolved; do not fabricate ancestry.
 return ParentageAssignmentV1(child_id,parents,assignment_kind,tuple(provenance_refs))

def validate_parentage_set(*,assignments,birth_person_ids):
 births=set(birth_person_ids)
 seen=set()
 for a in assignments:
  if a.child_id not in births: raise ValueError("PARENTAGE_CHILD_NOT_AUTHORIZED_BIRTH")
  if a.child_id in seen: raise ValueError("DUPLICATE_CHILD_PARENTAGE_ASSIGNMENT")
  seen.add(a.child_id)
 if seen!=births: raise ValueError("PARENTAGE_BIRTH_SET_MISMATCH")
 return True

@dataclass(frozen=True)
class FamilyFormationEventV1:
 event_id:str
 event_kind:str
 participant_ids:tuple[str,...]
 year:int
 provenance_refs:tuple[str,...]
 authority_class:str="SYNTHETIC_FAMILY_EVENT_NON_EMPIRICAL"

def family_event(*,event_id,event_kind,participant_ids,year,provenance_refs,
                 known_person_ids):
 if event_kind not in {"HOUSEHOLD_FORMATION","HOUSEHOLD_DISSOLUTION","LEGAL_PARTNERSHIP",
                       "LEGAL_SEPARATION","GUARDIANSHIP"}:
  raise ValueError("UNSUPPORTED_FAMILY_EVENT")
 if not provenance_refs: raise ValueError("MISSING_FAMILY_EVENT_PROVENANCE")
 people=tuple(participant_ids)
 if len(people)!=len(set(people)): raise ValueError("DUPLICATE_FAMILY_PARTICIPANT")
 if any(p not in set(known_person_ids) for p in people): raise ValueError("UNKNOWN_FAMILY_PARTICIPANT")
 return FamilyFormationEventV1(event_id,event_kind,people,year,tuple(provenance_refs))
