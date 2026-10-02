"""Semantic firewall for PostgreSQL Earth variables consumed by GAP-014."""
from dataclasses import dataclass

@dataclass(frozen=True)
class VariableSemanticV1:
 key:str; unit:str; grain:str; population_basis:str; epistemic_status:str
 valid_from_year:int; valid_to_year:int; coverage_scope:str; misuse_warning:str

def semantic_for(*,rows,variable_key,year):
 matches=[r for r in rows if r["variable_key"]==variable_key]
 if len(matches)!=1: raise ValueError("VARIABLE_SEMANTIC_NOT_UNIQUE")
 r=matches[0]
 if not int(r["valid_from_year"])<=year<=int(r["valid_to_year"]): return None
 return VariableSemanticV1(variable_key,r["unit"],r["grain"],r["population_accounting_basis"],
  r["epistemic_status"],int(r["valid_from_year"]),int(r["valid_to_year"]),
  r["coverage_scope"],r.get("misuse_warning") or "")

def require_compatible(*,left,right,require_same_unit=False,require_same_basis=False):
 if left is None or right is None: raise ValueError("VARIABLE_SEMANTIC_UNAVAILABLE")
 if require_same_unit and left.unit!=right.unit: raise ValueError("VARIABLE_UNIT_MISMATCH")
 if require_same_basis and left.population_basis!=right.population_basis:
  raise ValueError("POPULATION_ACCOUNTING_BASIS_MISMATCH")
 return True

def may_use_as_person_count(*,semantic):
 if semantic is None: return False
 return semantic.unit=="persons" and semantic.population_basis not in (
  "non-person automation","production labor input","biological labor input",
  "synthetic-person labor input",
 )
