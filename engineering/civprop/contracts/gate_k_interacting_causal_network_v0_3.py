from dataclasses import dataclass
import hashlib,json
from .gate_i_physical_capacity_feedback_v0_3 import project_capacity
from .gate_j_endogenous_opportunity_v0_3 import detect_capacity_opportunity
@dataclass(frozen=True)
class NetworkYear:
 year:int; capacity:float|None; opportunity_status:str; inventory:float; production:float; demand_served:float; shortage:float
@dataclass(frozen=True)
class GateKResult:
 years:tuple[NetworkYear,...]; final_inventory:float; canonical_sha256:str
def run_network(*,project,start_year,end_year,installed_capacity,failure_year,initial_inventory,annual_input,production_per_capacity,annual_demand):
 if min(initial_inventory,annual_input,production_per_capacity,annual_demand)<0: raise ValueError("negative network control")
 cs=project_capacity(project=project,years=tuple(range(start_year,end_year+1)),installed_capacity=installed_capacity,failure_year=failure_year)
 inventory=float(initial_inventory); out=[]
 for c in cs:
  opp=detect_capacity_opportunity(states=cs,year=c.year,required_capacity=1.0)
  inventory+=annual_input
  prod=0.0 if opp.status!="ELIGIBLE" else min(inventory,float(c.usable_capacity))*production_per_capacity
  used=0.0 if production_per_capacity==0 else prod/production_per_capacity
  inventory-=used; served=min(annual_demand,prod); shortage=annual_demand-served
  out.append(NetworkYear(c.year,c.usable_capacity,opp.status,inventory,prod,served,shortage))
 sha=hashlib.sha256(json.dumps([x.__dict__ for x in out],sort_keys=True,separators=(",",":")).encode()).hexdigest()
 return GateKResult(tuple(out),inventory,sha)
@dataclass(frozen=True)
class ConsumerAllocation:
 consumer_id:str; priority:float; demand:float; served:float; shortage:float
@dataclass(frozen=True)
class CompetingNetworkYear:
 year:int; production:float; allocations:tuple[ConsumerAllocation,...]; unallocated_output:float
def run_competing_network(*,project,start_year,end_year,installed_capacity,failure_year,annual_input,production_per_capacity,consumers):
 base=run_network(project=project,start_year=start_year,end_year=end_year,installed_capacity=installed_capacity,
  failure_year=failure_year,initial_inventory=0,annual_input=annual_input,production_per_capacity=production_per_capacity,annual_demand=10**30)
 out=[]
 for row in base.years:
  remaining=row.production; allocations=[]
  for c in sorted(consumers,key=lambda x:(-float(x["priority"]),str(x["consumer_id"]))):
   demand=float(c["demand"]); served=min(demand,remaining); remaining-=served
   allocations.append(ConsumerAllocation(str(c["consumer_id"]),float(c["priority"]),demand,served,demand-served))
  out.append(CompetingNetworkYear(row.year,row.production,tuple(allocations),remaining))
 return tuple(out)
