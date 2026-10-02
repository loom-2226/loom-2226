"""GAP-014 age/cohort and household realization.
NON_CANON / MACHINERY TEST. Attributes require explicit authored assignments;
no demographic distribution, relationship, sex/gender, fertility or household
behavior is inferred from identity.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class PersonDemographicProfileV1:
 person_id:str
 birth_year:int|None
 age_years:int|None
 assignment_provenance:tuple[str,...]
 authority_class:str="SYNTHETIC_DEMOGRAPHIC_PROFILE_NON_EMPIRICAL"

@dataclass(frozen=True)
class HouseholdV1:
 household_id:str
 location_id:str
 member_ids:tuple[str,...]
 relationship_edges:tuple[tuple[str,str,str],...]
 provenance_refs:tuple[str,...]
 authority_class:str="SYNTHETIC_HOUSEHOLD_NON_EMPIRICAL"

def assign_age(*,person_id,observation_year,birth_year,provenance_refs):
 if birth_year is None:
  return PersonDemographicProfileV1(person_id,None,None,tuple(provenance_refs))
 if not provenance_refs: raise ValueError("MISSING_AGE_PROVENANCE")
 if birth_year>observation_year: raise ValueError("BIRTH_AFTER_OBSERVATION")
 return PersonDemographicProfileV1(person_id,birth_year,observation_year-birth_year,
  tuple(provenance_refs))

def form_household(*,household_id,location_id,member_ids,relationship_edges,
                   provenance_refs):
 members=tuple(member_ids)
 if not provenance_refs: raise ValueError("MISSING_HOUSEHOLD_PROVENANCE")
 if len(members)!=len(set(members)): raise ValueError("DUPLICATE_HOUSEHOLD_MEMBER")
 if not members: raise ValueError("EMPTY_HOUSEHOLD")
 edges=tuple(tuple(x) for x in relationship_edges)
 for src,rel,dst in edges:
  if src not in members or dst not in members: raise ValueError("RELATIONSHIP_ENDPOINT_OUTSIDE_HOUSEHOLD")
  if src==dst: raise ValueError("SELF_RELATIONSHIP")
  if not rel: raise ValueError("EMPTY_RELATIONSHIP_TYPE")
 return HouseholdV1(household_id,location_id,members,edges,tuple(provenance_refs))

def validate_household_partition(*,person_ids,households):
 people=tuple(person_ids)
 assigned=[]
 for h in households: assigned.extend(h.member_ids)
 if len(assigned)!=len(set(assigned)): raise ValueError("PERSON_IN_MULTIPLE_HOUSEHOLDS")
 if set(assigned)!=set(people): raise ValueError("HOUSEHOLD_PARTITION_MISMATCH")
 return True
