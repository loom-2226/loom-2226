"""Functional 2026 actor baseline derived from candidate evidence + governed Earth authority.

Values are initialization estimates, not historical financial claims. Every
numeric estimate carries method/status and is bounded by a governed 2026
sector aggregate. Named-actor allocations are model estimates only.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from hashlib import sha256
import json,re

BASELINE_ID="ACTOR_BASELINE_2026_V0_3"
EARTH_SNAPSHOT="earth-v0-1-9934d0ac-20260925"

CATEGORY_SECTOR={
"CAPITAL":"SERVICES","OFFTAKER":"BULK_MATERIALS","INSURER":"SERVICES",
"CARRIER":"SHIPS_AEROSPACE","REGISTRY":"CERTIFICATION_METROLOGY","STATE":"SERVICES",
"SETTLEMENT_LABOR":"SERVICES","INFORMATION":"COMPUTE","PROSPECTOR":"SHIPS_AEROSPACE",
"INCUMBENT_INDUSTRY":"BULK_MATERIALS","SUPPLIER_PRIME":"SHIPS_AEROSPACE",
"INFRASTRUCTURE":"TRANSPORT_LOGISTICS","SOFT_POWER":"SERVICES","CERTIFICATION":"CERTIFICATION_METROLOGY"}

# Fraction of relevant sector annual investment represented by one "scale point".
# These are explicit initialization model parameters, deliberately conservative.
CATEGORY_INVESTMENT_UNIT_SHARE={
"CAPITAL":0.0010,"OFFTAKER":0.0004,"INSURER":0.0005,"CARRIER":0.0040,
"REGISTRY":0.00001,"STATE":0.0001,"SETTLEMENT_LABOR":0.00001,"INFORMATION":0.0002,
"PROSPECTOR":0.0008,"INCUMBENT_INDUSTRY":0.0010,"SUPPLIER_PRIME":0.0020,
"INFRASTRUCTURE":0.0005,"SOFT_POWER":0.000005,"CERTIFICATION":0.00002}

@dataclass(frozen=True)
class SectorAuthority2026:
    sector:str; gross_output:float; investment:float; capital:float; employment:float
@dataclass(frozen=True)
class ActorBaseline2026:
    actor_id:str; name:str; category:str; lifecycle_status:str
    functional_2026:bool; scale_class:str; scale_score:float
    economic_sector:str; financial_capacity_estimate:float
    financial_capacity_low:float; financial_capacity_high:float
    capacity_semantics:str; operating_capacity_index:float
    evidence_status:str; estimate_method:str; confidence:str
    source_refs:tuple[str,...]

def _lifecycle(a):
    s=str(a.get("status_2026","")).upper(); seed=str(a.get("seed_as","")).upper()
    text=(a.get("basis_2026","")+" "+a.get("name","")).lower()
    if "HISTORICAL" in s or "HISTORICAL" in seed or any(x in text for x in ("defunct","wound down","acquired by","absorbed into")):
        return "HISTORICAL"
    if "PROPOSAL" in s or "proposed" in text or "planned successor" in text:
        return "PROPOSAL_OR_PENDING"
    return "ACTIVE_OR_OPERATING"

def _scale(a):
    t=(a.get("basis_2026","")+" "+a.get("name","")).lower()
    if any(x in t for x in ("one of the largest","very large","largest ","dominant ","major reinsurer","global union federation","world's largest","state-directed")):
        return "XL",8.0
    if any(x in t for x in ("large ","major ","national ","state corporation","government pension","sovereign fund","global ","primary us","leading ")):
        return "L",3.0
    if any(x in t for x in ("startup","small ","junior ","single-module","trade newsletter","nonprofit","learned society","proposal","working group")):
        return "S",0.1
    return "M",1.0

def _semantics(cat):
    return {"CAPITAL":"deployable_financing_capacity","OFFTAKER":"procurement_capacity",
    "INSURER":"underwriting_capacity","CARRIER":"fleet_and_service_investment_capacity",
    "REGISTRY":"institutional_operating_capacity","STATE":"policy_and_program_capacity",
    "SETTLEMENT_LABOR":"community_and_welfare_operating_capacity","INFORMATION":"collection_and_analytics_capacity",
    "PROSPECTOR":"venture_and_project_development_capacity","INCUMBENT_INDUSTRY":"corporate_investment_capacity",
    "SUPPLIER_PRIME":"company_capital_and_independent_rd_capacity","INFRASTRUCTURE":"network_and_facility_investment_capacity",
    "SOFT_POWER":"institutional_operating_and_grant_capacity","CERTIFICATION":"certification_and_assurance_operating_capacity"}[cat]

def build_actor_baseline_2026(seed,sector_authority):
    by_sector={x.sector:x for x in sector_authority}; out=[]
    for a in sorted(seed["actors"],key=lambda x:x["id"]):
        life=_lifecycle(a); cls,score=_scale(a); cat=a["category"]; sec=CATEGORY_SECTOR[cat]; auth=by_sector[sec]
        functional=life=="ACTIVE_OR_OPERATING"
        if functional:
            center=auth.investment*CATEGORY_INVESTMENT_UNIT_SHARE[cat]*score
            # Wide interval honestly represents crude named-actor allocation.
            low=center*0.25; high=center*4.0
            op=min(100.0,score*20.0)
            status="DERIVED_ESTIMATED"
            method=f"2026_{sec}_INVESTMENT_X_CATEGORY_SHARE_X_TEXT_SCALE"
        else:
            center=low=high=op=0.0
            status="DIRECT_STATUS_DERIVED_ZERO_CURRENT_FUNCTION"
            method="SEED_LIFECYCLE_STATUS"
        refs=(f"candidate_seed:{a['id']}",f"postgres:{EARTH_SNAPSHOT}:earth_sector_year:{sec}:2026")
        out.append(ActorBaseline2026(a["id"],a["name"],cat,life,functional,cls,score,sec,
            center,low,high,_semantics(cat),op,status,method,a.get("conf","UNKNOWN"),refs))
    return tuple(out)

def baseline_digest(rows):
    payload=json.dumps([asdict(x) for x in rows],sort_keys=True,separators=(",",":"))
    return sha256(payload.encode()).hexdigest()

__all__=["BASELINE_ID","EARTH_SNAPSHOT","SectorAuthority2026","ActorBaseline2026",
         "build_actor_baseline_2026","baseline_digest","CATEGORY_SECTOR","CATEGORY_INVESTMENT_UNIT_SHARE"]
