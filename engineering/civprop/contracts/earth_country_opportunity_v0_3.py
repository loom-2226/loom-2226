"""Country/sector opportunity surface derived only from governed LOOM Earth state.

Opportunity != actor capability, funding, project commitment, or physical feasibility.
Scores are dimensionless relative diagnostics; raw authority values remain attached.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,math

SECTORS=("BULK_MATERIALS","CERTIFICATION_METROLOGY","COMPUTE","ENERGY","HABITATS_CONSTRUCTION",
"MEDICINE","PRECISION_MATERIALS","SERVICES","SHIPS_AEROSPACE","TRANSPORT_LOGISTICS")

@dataclass(frozen=True)
class CountrySectorStateV03:
 iso3:str; name:str; year:int; sector:str
 value_added:float; gross_output:float; investment:float; capital:float; employment:float
 biological_population:float; births:float; deaths:float; median_age:float
 age_under_20:float; age_20_64:float; age_65_plus:float
 legacy_labor_force:float; legacy_employment:float
 machinery_capital:float; structures_capital:float; transport_equipment_capital:float; other_assets_capital:float
 effective_labor:float|None=None; synthetic_effective_labor:float|None=None; machine_task_capacity:float|None=None
@dataclass(frozen=True)
class CountryOpportunityV03:
 iso3:str; name:str; year:int; sector:str
 scale_share:float; investment_intensity:float; capital_intensity:float; employment_share:float
 replacement_pressure:float|None; expansion_signal:float|None
 labor_depth:float; demographic_support:float
 opportunity_signal:float
 productive_asset_share:float; transport_asset_share:float
 authority_fields:tuple[str,...]; unavailable_fields:tuple[str,...]
 semantics:str="OPPORTUNITY_CONTEXT_NOT_ACTOR_AUTHORITY"

def derive(states):
 if not states:return ()
 bysec={}
 for s in states: bysec.setdefault(s.sector,[]).append(s)
 out=[]
 for s in states:
  peers=bysec[s.sector]
  go=sum(x.gross_output for x in peers); inv=sum(x.investment for x in peers); emp=sum(x.employment for x in peers)
  scale=s.gross_output/go if go else 0.0
  ii=s.investment/s.gross_output if s.gross_output else 0.0
  ci=s.capital/s.gross_output if s.gross_output else 0.0
  es=s.employment/emp if emp else 0.0
  ld=s.employment/s.legacy_labor_force if s.legacy_labor_force else 0.0
  working=s.age_20_64/s.biological_population if s.biological_population else 0.0
  # Opportunity is deliberately broad: scale + current investment effort + sector labor + demographic support.
  # log investment intensity prevents pathological ratios dominating tiny economies.
  # Scalar is retained only as a browse/diagnostic index. Runtime decisions must consume
  # named dimensions appropriate to the trigger, never this index as capability.
  sig=0.40*scale + 0.25*min(1.0,ii) + 0.20*es + 0.15*working
  assets=s.machinery_capital+s.structures_capital+s.transport_equipment_capital+s.other_assets_capital
  productive=(s.machinery_capital+s.structures_capital)/assets if assets else 0.0
  transport=s.transport_equipment_capital/assets if assets else 0.0
  unavailable=[]
  if s.effective_labor is None:unavailable.append("effective_labor")
  if s.synthetic_effective_labor is None:unavailable.append("synthetic_effective_labor")
  if s.machine_task_capacity is None:unavailable.append("machine_task_capacity")
  unavailable.extend(("asset_investment","replacement_need","replacement_funded","expansion_investment"))
  out.append(CountryOpportunityV03(s.iso3,s.name,s.year,s.sector,scale,ii,ci,es,None,None,ld,working,sig,productive,transport,
   ("sector_value_added","sector_gross_output","sector_investment","sector_capital","sector_employment",
    "biological_population","births","deaths","median_age","age_bands","legacy_labor_force","legacy_employment",
    "asset_class_capital"),tuple(unavailable)))
 return tuple(sorted(out,key=lambda x:(x.year,x.iso3,x.sector)))

def digest(rows):
 return sha256(json.dumps([asdict(x) for x in rows],sort_keys=True,separators=(",",":")).encode()).hexdigest()
