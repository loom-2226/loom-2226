"""Convert governed Earth country-sector context into neutral actor relevance triggers."""
from dataclasses import dataclass
SECTOR_ROLES={
"BULK_MATERIALS":("OFFTAKER","INCUMBENT_INDUSTRY","PROSPECTOR"),
"CERTIFICATION_METROLOGY":("CERTIFICATION","REGISTRY"),
"COMPUTE":("INFORMATION","SUPPLIER_PRIME","INFRASTRUCTURE"),
"ENERGY":("INCUMBENT_INDUSTRY","OFFTAKER","INFRASTRUCTURE"),
"HABITATS_CONSTRUCTION":("INFRASTRUCTURE","SUPPLIER_PRIME","SETTLEMENT_LABOR"),
"MEDICINE":("OFFTAKER","SUPPLIER_PRIME","SETTLEMENT_LABOR"),
"PRECISION_MATERIALS":("SUPPLIER_PRIME","INCUMBENT_INDUSTRY","OFFTAKER"),
"SERVICES":("CAPITAL","INSURER","INFORMATION","SOFT_POWER"),
"SHIPS_AEROSPACE":("CARRIER","PROSPECTOR","SUPPLIER_PRIME","INFRASTRUCTURE"),
"TRANSPORT_LOGISTICS":("CARRIER","INFRASTRUCTURE","OFFTAKER"),
}
@dataclass(frozen=True)
class EarthOpportunityTriggerV03:
 context_id:str; year:int; iso3:str; sector:str; relevant_categories:tuple[str,...]
 provenance_refs:tuple[str,...]; semantics:str="RELEVANCE_CONTEXT_ONLY_NO_ACTION_AUTHORITY"

def triggers(rows):
 return tuple(EarthOpportunityTriggerV03(
  f"EARTH:{r['year']}:{r['iso3']}:{r['sector']}",int(r["year"]),r["iso3"],r["sector"],SECTOR_ROLES[r["sector"]],
  (f"postgres:earth-v0-1-9934d0ac-20260925:earth_sector_year:{r['iso3']}:{r['sector']}:{r['year']}",))
  for r in rows)
