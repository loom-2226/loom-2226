"""GAP-014 synthetic-person realization layer.
NON_CANON / MACHINERY TEST. Persons realize an already-authorized integer
population. They do not generate or modify demographic totals.
"""
from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class SyntheticPersonV1:
 person_id:str
 cohort_id:str
 location_id:str
 realization_year:int
 ordinal:int
 authority_class:str="SYNTHETIC_PERSON_NON_EMPIRICAL"

@dataclass(frozen=True)
class SyntheticPopulationV1:
 cohort_id:str
 location_id:str
 year:int
 authorized_population:int
 persons:tuple[SyntheticPersonV1,...]
 provenance_refs:tuple[str,...]
 authority_class:str="SYNTHETIC_POPULATION_REALIZATION_NON_EMPIRICAL"

def realize_synthetic_population(*,cohort_id,location_id,year,
                                 authorized_population,provenance_refs,
                                 realization_key):
 if isinstance(authorized_population,bool) or not isinstance(authorized_population,int):
  raise TypeError("SYNTHETIC_REALIZATION_REQUIRES_INTEGER_POPULATION")
 if authorized_population<0: raise ValueError("NEGATIVE_AUTHORIZED_POPULATION")
 if not provenance_refs: raise ValueError("MISSING_POPULATION_PROVENANCE")
 if not realization_key: raise ValueError("MISSING_REALIZATION_KEY")
 persons=[]
 for ordinal in range(authorized_population):
  token=f"{realization_key}|{cohort_id}|{location_id}|{year}|{ordinal}".encode()
  pid="syn:"+hashlib.sha256(token).hexdigest()[:24]
  persons.append(SyntheticPersonV1(pid,cohort_id,location_id,year,ordinal))
 return SyntheticPopulationV1(cohort_id,location_id,year,authorized_population,
  tuple(persons),tuple(provenance_refs))

def reconcile_synthetic_population(realization):
 ids=[p.person_id for p in realization.persons]
 if len(ids)!=len(set(ids)): raise ValueError("DUPLICATE_SYNTHETIC_PERSON_ID")
 if len(ids)!=realization.authorized_population:
  raise ValueError("SYNTHETIC_POPULATION_COUNT_MISMATCH")
 if any(p.cohort_id!=realization.cohort_id or
        p.location_id!=realization.location_id or
        p.realization_year!=realization.year
        for p in realization.persons):
  raise ValueError("SYNTHETIC_PERSON_SCOPE_MISMATCH")
 return True
