"""GAP-014 annual runtime integration.

Earth authority is an exogenous no-offworld baseline. CIVPROP applies only its own
conserved migration delta on top; it never rewrites the promoted trajectory.
"""
from engineering.civprop.contracts.demographic_migration_bridge_v1 import (
 MigrationDemandV1,authorize_migration,apply_conserved_migration,
)

class DemographicRuntimeV1:
 def __init__(self,authority,migration_demand):
  self.authority=authority
  self.migration_demand=migration_demand or {"rows":[]}
  self.earth_migration_delta=0.0
  rows=authority.get("earth_biological_population_by_year",[])
  self.bio={int(x["year"]):float(x["biological_population"]) for x in rows}
  if not self.bio: raise ValueError("DEMOGRAPHIC_AUTHORITY_EMPTY")
  self.provenance=tuple(authority.get("provenance_refs",()))
  if not self.provenance: raise ValueError("DEMOGRAPHIC_AUTHORITY_PROVENANCE_MISSING")

 def apply_earth_baseline(self,*,year,states):
  if year not in self.bio: raise ValueError("EARTH_DEMOGRAPHIC_YEAR_MISSING")
  earth=states["EARTH_SURFACE"]
  value=self.bio[year]+self.earth_migration_delta
  if value<0: raise ValueError("EARTH_POPULATION_NEGATIVE_AFTER_MIGRATION")
  earth.biological_population=value

 def migrate(self,*,year,states,route_traffic_states,recorder):
  rows=[x for x in self.migration_demand.get("rows",[]) if int(x["year"])==year]
  for x in rows:
   origin=x["origin_location_id"]; dest=x["destination_location_id"]
   routes=[r for r in route_traffic_states if r.year==year and
    r.origin_location_id==origin and r.destination_location_id==dest]
   if len(routes)!=1: continue
   d=MigrationDemandV1(year,origin,dest,x.get("requested_persons"),
      tuple(x.get("provenance_refs",())))
   a=authorize_migration(demand=d,route_traffic_state=routes[0],
      origin_population=states[origin].biological_population)
   if a.status!="AUTHORIZED" or not a.authorized_migrants: continue
   pops={k:v.biological_population for k,v in states.items()}
   out=apply_conserved_migration(populations=pops,authorization=a)
   amount=a.authorized_migrants
   for k,v in out.items(): states[k].biological_population=v
   if origin=="EARTH_SURFACE": self.earth_migration_delta-=amount
   if dest=="EARTH_SURFACE": self.earth_migration_delta+=amount
   recorder.migration(year,origin,dest,amount)
