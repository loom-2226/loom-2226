"""Step-7 causal economic feedback boundary.

NON-CANON / UNPROMOTED. Converts observed physical demand/capacity shortfalls
into explicit pressure and opportunity signals without inventing prices, GDP,
actor budgets, labor headcounts, or investment multipliers.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class EconomicConstraintV03:
 year:int; location_id:str; channel_id:str; required:float|None; available:float|None
 unmet:float|None; service_ratio:float|None; status:str; provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class EconomicPressureV03:
 year:int; location_id:str; channel_id:str; pressure:float|None; status:str
 reason_codes:tuple[str,...]; provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class EconomicOpportunityV03:
 opportunity_id:str; year:int; location_id:str; channel_id:str; status:str
 reason_codes:tuple[str,...]; observed_pressure:float|None; threshold:float|None
 provenance_refs:tuple[str,...]

def observe_constraint(*,year:int,location_id:str,channel_id:str,required,available,
                       provenance_refs:tuple[str,...]):
 if not provenance_refs: raise ValueError("ECONOMIC_CONSTRAINT_PROVENANCE_MISSING")
 if required is None or available is None:
  return EconomicConstraintV03(year,location_id,channel_id,required,available,None,None,"UNKNOWN",provenance_refs)
 r=float(required); a=float(available)
 if r<0 or a<0: raise ValueError("NEGATIVE_ECONOMIC_QUANTITY")
 unmet=max(0.0,r-a); ratio=1.0 if r==0 else min(1.0,a/r)
 return EconomicConstraintV03(year,location_id,channel_id,r,a,unmet,ratio,"RESOLVED_PHYSICAL_BALANCE",provenance_refs)

def advance_pressure(*,constraint:EconomicConstraintV03,previous_pressure:float|None,
                     decay:float,gain:float):
 if not 0<=decay<1 or gain<=0: raise ValueError("INVALID_PRESSURE_PARAMETER")
 refs=constraint.provenance_refs+("STEP7_CAUSAL_PRESSURE_DERIVATION",)
 if constraint.unmet is None or previous_pressure is None:
  return EconomicPressureV03(constraint.year,constraint.location_id,constraint.channel_id,None,"UNKNOWN",("UNRESOLVED_INPUT",),refs)
 if previous_pressure<0: raise ValueError("NEGATIVE_PREVIOUS_PRESSURE")
 value=float(previous_pressure)*decay+float(constraint.unmet)*gain
 return EconomicPressureV03(constraint.year,constraint.location_id,constraint.channel_id,value,"RESOLVED",(),refs)

def opportunity_from_pressure(*,pressure:EconomicPressureV03,threshold:float|None):
 oid=f"ECON-{pressure.location_id}-{pressure.channel_id}-{pressure.year}"
 refs=pressure.provenance_refs+("STEP7_ENDOGENOUS_OPPORTUNITY_DERIVATION",)
 if pressure.pressure is None or threshold is None:
  return EconomicOpportunityV03(oid,pressure.year,pressure.location_id,pressure.channel_id,"BLOCKED",("PRESSURE_OR_THRESHOLD_UNKNOWN",),pressure.pressure,threshold,refs)
 if threshold<=0: raise ValueError("INVALID_OPPORTUNITY_THRESHOLD")
 if pressure.pressure<threshold:
  return EconomicOpportunityV03(oid,pressure.year,pressure.location_id,pressure.channel_id,"BLOCKED",("PRESSURE_BELOW_THRESHOLD",),pressure.pressure,threshold,refs)
 return EconomicOpportunityV03(oid,pressure.year,pressure.location_id,pressure.channel_id,"ELIGIBLE",(),pressure.pressure,threshold,refs)

def assert_no_budget_inference(*,opportunity:EconomicOpportunityV03):
 # Deliberately returns no money. Economic need is not actor spendable allocation.
 return None
