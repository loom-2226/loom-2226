from dataclasses import dataclass
from .asset_lifecycle_v1 import AssetLifecycleRuntimeV1,LifecyclePolicyV1,LifecycleEventV1
@dataclass(frozen=True)
class QFacility:
 facility_id:str; project_archetype_id:str; commissioned_year:int; capital:float
@dataclass(frozen=True)
class CapacityState:
 year:int; facility_id:str; status:str; installed_capacity:float; usable_capacity:float|None; provenance_refs:tuple[str,...]
def project_capacity(*,project,years,installed_capacity,failure_year=None):
 if project.get("status")!="ACTIVE":
  return tuple(CapacityState(y,project.get("project_id","UNKNOWN"),"NOT_COMMISSIONED",0,0,("GATE_I_PROJECT_NOT_ACTIVE",)) for y in years)
 if installed_capacity<0: raise ValueError("negative capacity")
 fid="FACILITY_"+project["project_id"]; f=QFacility(fid,"GATE_I_SERVICE",min(years),float(project.get("capital",1.0)))
 events=() if failure_year is None else (LifecycleEventV1(failure_year,fid,"FAILURE"),)
 rt=AssetLifecycleRuntimeV1((LifecyclePolicyV1("GATE_I_SERVICE",annual_depreciation_rate=0.0,service_life_years=100),),events)
 life={(x.year,x.facility_id):x for x in rt.project((f,),min(years),max(years))}
 return tuple(CapacityState(y,fid,life[(y,fid)].status,installed_capacity,None if life[(y,fid)].usable_capacity_fraction is None else installed_capacity*life[(y,fid)].usable_capacity_fraction,("GATE_H_ACTIVE_PROJECT","ASSET_LIFECYCLE_V1","AUTHORED_GATE_I_CAPACITY_CONTROL")) for y in years)
