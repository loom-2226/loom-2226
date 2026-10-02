"""GAP-014 synthetic life-course transition contract.
NON_CANON / MACHINERY TEST. Life events reconcile to authorized demographic
events; persons do not independently invent births, deaths, or migration.
"""
from dataclasses import dataclass
import hashlib
from .synthetic_person_v1 import SyntheticPersonV1

@dataclass(frozen=True)
class SyntheticLifeEventV1:
 event_id:str
 event_kind:str
 person_id:str
 cohort_id:str
 origin_location_id:str
 destination_location_id:str|None
 year:int
 authority_class:str="SYNTHETIC_LIFE_EVENT_NON_EMPIRICAL"

@dataclass(frozen=True)
class LifeCourseRealizationV1:
 opening_person_ids:tuple[str,...]
 birth_person_ids:tuple[str,...]
 death_person_ids:tuple[str,...]
 migrant_person_ids:tuple[str,...]
 closing_person_ids:tuple[str,...]
 events:tuple[SyntheticLifeEventV1,...]
 authority_class:str="SYNTHETIC_LIFE_COURSE_REALIZATION_NON_EMPIRICAL"

def _id(key,*parts):
 return hashlib.sha256(("|".join((key,)+tuple(map(str,parts)))).encode()).hexdigest()[:24]

def realize_life_course(*,opening_persons,cohort_id,location_id,year,
                        authorized_births,authorized_deaths,
                        outbound_migrant_ids=(),realization_key=""):
 for n in (authorized_births,authorized_deaths):
  if isinstance(n,bool) or not isinstance(n,int) or n<0:
   raise ValueError("AUTHORIZED_EVENT_COUNT_MUST_BE_NONNEGATIVE_INTEGER")
 if not realization_key: raise ValueError("MISSING_REALIZATION_KEY")
 opening=tuple(opening_persons)
 if any(p.cohort_id!=cohort_id or p.location_id!=location_id for p in opening):
  raise ValueError("OPENING_PERSON_SCOPE_MISMATCH")
 ids=[p.person_id for p in opening]
 if len(ids)!=len(set(ids)): raise ValueError("DUPLICATE_OPENING_PERSON_ID")
 if authorized_deaths>len(ids): raise ValueError("DEATHS_EXCEED_OPENING_POPULATION")
 migrants=tuple(outbound_migrant_ids)
 if len(migrants)!=len(set(migrants)) or any(x not in ids for x in migrants):
  raise ValueError("INVALID_OUTBOUND_MIGRANT")
 death_pool=[x for x in ids if x not in migrants]
 if authorized_deaths>len(death_pool): raise ValueError("DEATH_MIGRATION_OVERLAP_EXHAUSTS_POPULATION")
 deaths=tuple(sorted(death_pool,key=lambda x:_id(realization_key,"death",x,year))[:authorized_deaths])
 births=tuple("syn:"+_id(realization_key,"birth",cohort_id,location_id,year,i)
              for i in range(authorized_births))
 survivors=tuple(x for x in ids if x not in deaths and x not in migrants)
 closing=survivors+births
 events=[]
 for x in deaths:
  events.append(SyntheticLifeEventV1("evt:"+_id(realization_key,"death-event",x,year),
   "DEATH",x,cohort_id,location_id,None,year))
 for x in migrants:
  events.append(SyntheticLifeEventV1("evt:"+_id(realization_key,"migration-event",x,year),
   "OUT_MIGRATION",x,cohort_id,location_id,None,year))
 for x in births:
  events.append(SyntheticLifeEventV1("evt:"+_id(realization_key,"birth-event",x,year),
   "BIRTH",x,cohort_id,location_id,location_id,year))
 return LifeCourseRealizationV1(tuple(ids),births,deaths,migrants,closing,tuple(events))

def reconcile_life_course(*,realization,authorized_opening,authorized_births,
                          authorized_deaths,authorized_out_migration):
 if len(realization.opening_person_ids)!=authorized_opening: raise ValueError("OPENING_COUNT_MISMATCH")
 if len(realization.birth_person_ids)!=authorized_births: raise ValueError("BIRTH_COUNT_MISMATCH")
 if len(realization.death_person_ids)!=authorized_deaths: raise ValueError("DEATH_COUNT_MISMATCH")
 if len(realization.migrant_person_ids)!=authorized_out_migration: raise ValueError("MIGRATION_COUNT_MISMATCH")
 expected=authorized_opening+authorized_births-authorized_deaths-authorized_out_migration
 if len(realization.closing_person_ids)!=expected: raise ValueError("CLOSING_COUNT_MISMATCH")
 if len(realization.closing_person_ids)!=len(set(realization.closing_person_ids)):
  raise ValueError("DUPLICATE_CLOSING_PERSON_ID")
 return True
