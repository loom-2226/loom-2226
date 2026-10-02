"""Coverage-aware read boundary for live Earth PostgreSQL authority.

Prevents accidental summation across unlike geographic coverage universes.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorityCoverageV1:
 fact_family:str
 variable_key:str
 coverage_scope:str
 valid_from_year:int
 valid_to_year:int
 geographic_coverage:str
 epistemic_status:str
 unavailable_intervals:object

def coverage_for(*,coverage_rows,fact_family,year):
 rows=[r for r in coverage_rows if r["fact_family"]==fact_family]
 if len(rows)!=1: raise ValueError("AUTHORITY_COVERAGE_NOT_UNIQUE")
 r=rows[0]
 if year<int(r["valid_from_year"]) or year>int(r["valid_to_year"]):
  return None
 return AuthorityCoverageV1(r["fact_family"],r.get("variable_key") or "",
  r["coverage_scope"],int(r["valid_from_year"]),int(r["valid_to_year"]),
  r["geographic_coverage"],r["epistemic_status"],r.get("unavailable_intervals"))

def require_same_coverage(*,left,right):
 if left is None or right is None: raise ValueError("AUTHORITY_COVERAGE_UNAVAILABLE")
 if left.geographic_coverage!=right.geographic_coverage:
  raise ValueError("AUTHORITY_COVERAGE_MISMATCH")
 return True

def can_treat_as_global(*,coverage):
 return coverage is not None and coverage.geographic_coverage=="237_WPP_COUNTRY_AREA"
