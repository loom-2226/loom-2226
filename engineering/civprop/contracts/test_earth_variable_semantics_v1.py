import unittest
from engineering.civprop.contracts.earth_variable_semantics_v1 import *
def row(k,u,b,lo=2100,hi=2226):
 return {"variable_key":k,"unit":u,"grain":"economic-area-year","population_accounting_basis":b,
 "epistemic_status":"SELECTED_MODEL","valid_from_year":lo,"valid_to_year":hi,
 "coverage_scope":"economic 80","misuse_warning":"warning"}
class SemanticTests(unittest.TestCase):
 def test_synthetic_headcount_is_person_count(self):
  s=semantic_for(rows=[row("DEM.SYNTH_POP","persons","recognized synthetic persons")],variable_key="DEM.SYNTH_POP",year=2226)
  self.assertTrue(may_use_as_person_count(semantic=s))
 def test_machine_capacity_not_person_count(self):
  s=semantic_for(rows=[row("WORK.MACHINE_TASK_CAPACITY","effective-labor equivalents","non-person automation")],variable_key="WORK.MACHINE_TASK_CAPACITY",year=2226)
  self.assertFalse(may_use_as_person_count(semantic=s))
 def test_effective_labor_not_person_count(self):
  s=semantic_for(rows=[row("WORK.BIO_EFFECTIVE_LABOR","effective-labor equivalents","biological labor input")],variable_key="WORK.BIO_EFFECTIVE_LABOR",year=2226)
  self.assertFalse(may_use_as_person_count(semantic=s))
 def test_preboundary_is_unavailable(self):
  self.assertIsNone(semantic_for(rows=[row("DEM.SYNTH_POP","persons","recognized synthetic persons")],variable_key="DEM.SYNTH_POP",year=2099))
 def test_basis_mismatch_rejected(self):
  a=semantic_for(rows=[row("A","persons","biological humans")],variable_key="A",year=2226)
  b=semantic_for(rows=[row("B","persons","recognized synthetic persons")],variable_key="B",year=2226)
  with self.assertRaisesRegex(ValueError,"BASIS_MISMATCH"):
   require_compatible(left=a,right=b,require_same_basis=True)
if __name__=="__main__": unittest.main()
