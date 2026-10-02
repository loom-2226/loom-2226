"""GAP-014 Demographic Depth V1 experimental contract.
NON_CANON / MACHINERY TEST. Demography is cohort accounting, not spontaneous
population. Unknown rates remain unknown and cannot be silently treated as zero.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DemographicRatesV1:
 birth_rate_per_person_year:float|None
 death_rate_per_person_year:float|None
 provenance_refs:tuple[str,...]
 authority_class:str="AUTHORED_DEMOGRAPHIC_MACHINERY_ASSUMPTION"

@dataclass(frozen=True)
class CohortStateV1:
 cohort_id:str
 location_id:str
 population:float
 year:int
 provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class DemographicTransitionV1:
 cohort_id:str
 location_id:str
 year:int
 opening_population:float
 births:float|None
 deaths:float|None
 net_migration:float
 closing_population:float|None
 status:str

def propagate_cohort(*,cohort:CohortStateV1,rates:DemographicRatesV1,
                     net_migration:float,year:int):
 if year<=cohort.year: raise ValueError("NON_FORWARD_DEMOGRAPHIC_TRANSITION")
 if cohort.population<0: raise ValueError("NEGATIVE_POPULATION")
 if not rates.provenance_refs: raise ValueError("MISSING_RATE_PROVENANCE")
 if rates.birth_rate_per_person_year is None or rates.death_rate_per_person_year is None:
  return DemographicTransitionV1(cohort.cohort_id,cohort.location_id,year,
   cohort.population,None,None,net_migration,None,"UNKNOWN_RATES")
 if rates.birth_rate_per_person_year<0 or rates.death_rate_per_person_year<0:
  raise ValueError("NEGATIVE_DEMOGRAPHIC_RATE")
 dt=year-cohort.year
 births=cohort.population*rates.birth_rate_per_person_year*dt
 deaths=cohort.population*rates.death_rate_per_person_year*dt
 closing=cohort.population+births-deaths+net_migration
 if closing<0: raise ValueError("NEGATIVE_CLOSING_POPULATION")
 return DemographicTransitionV1(cohort.cohort_id,cohort.location_id,year,
  cohort.population,births,deaths,net_migration,closing,"RESOLVED_MACHINERY_TEST")

def biological_viability_status(*,population,minimum_viable_population):
 if minimum_viable_population is None: return "UNKNOWN"
 if population is None: return "UNKNOWN"
 if minimum_viable_population<0: raise ValueError("INVALID_VIABILITY_THRESHOLD")
 return "MEETS_AUTHORED_THRESHOLD" if population>=minimum_viable_population else "BELOW_AUTHORED_THRESHOLD"
