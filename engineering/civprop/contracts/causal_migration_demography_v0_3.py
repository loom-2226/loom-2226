"""Step-6 causal movement -> migration -> demographic continuation.

NON-CANON / UNPROMOTED. Passenger movement is not residence change. Migration
requires separately provenance-bearing demand and matching realized transport.
Off-Earth natural increase remains UNKNOWN until rates are authorized.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .demographic_migration_bridge_v1 import MigrationDemandV1,authorize_migration,apply_conserved_migration
from .demographic_depth_v1 import CohortStateV1,DemographicRatesV1,propagate_cohort

@dataclass(frozen=True)
class MigrationRealizationV03:
 year:int; origin_location_id:str; destination_location_id:str
 passenger_movements:float|None; requested_migrants:float|None
 realized_migrants:float|None; status:str; provenance_refs:tuple[str,...]

def realize_migration(*,year:int,origin_location_id:str,destination_location_id:str,
                      requested_migrants:float|None,demand_provenance_refs:tuple[str,...],
                      route_traffic_state,origin_population:float):
 d=MigrationDemandV1(year,origin_location_id,destination_location_id,requested_migrants,demand_provenance_refs)
 a=authorize_migration(demand=d,route_traffic_state=route_traffic_state,origin_population=origin_population)
 return MigrationRealizationV03(year,origin_location_id,destination_location_id,
  a.realized_passenger_movements,requested_migrants,a.authorized_migrants,a.status,
  tuple(demand_provenance_refs))

def apply_migration_and_create_cohort(*,populations:Mapping[str,float],
                                      realization:MigrationRealizationV03):
 if realization.status!='AUTHORIZED' or realization.realized_migrants is None:
  return dict(populations),None
 # Recreate the narrow authorization object through the governed bridge rather
 # than duplicating its conservation equation.
 from .demographic_migration_bridge_v1 import AuthorizedMigrationV1
 a=AuthorizedMigrationV1(realization.year,realization.origin_location_id,
   realization.destination_location_id,realization.requested_migrants,
   realization.passenger_movements,realization.realized_migrants,'AUTHORIZED',
   realization.provenance_refs)
 out=apply_conserved_migration(populations=populations,authorization=a)
 cohort=CohortStateV1(
  f"MIGRANT_COHORT_{realization.destination_location_id}_{realization.year}",
  realization.destination_location_id,realization.realized_migrants,
  realization.year,realization.provenance_refs)
 return out,cohort

def continue_offworld_cohort(*,cohort:CohortStateV1,year:int,
                             rates:DemographicRatesV1):
 return propagate_cohort(cohort=cohort,rates=rates,net_migration=0.0,year=year)
