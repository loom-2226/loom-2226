import unittest
from engineering.civprop.contracts.earth_authority_coverage_v1 import *
D={"fact_family":"demography","variable_key":"DEM.BIO_POP","coverage_scope":"237_WPP_COUNTRY_AREA","valid_from_year":2026,"valid_to_year":2226,"geographic_coverage":"237_WPP_COUNTRY_AREA","epistemic_status":"SELECTED_AUTHORITY","unavailable_intervals":[]}
L={"fact_family":"biosynthetic_labor","variable_key":"WORK.TOTAL_EFFECTIVE_LABOR","coverage_scope":"80_QUALIFIED_ECONOMIES","valid_from_year":2100,"valid_to_year":2226,"geographic_coverage":"80_QUALIFIED_ECONOMIES","epistemic_status":"SELECTED_MODEL","unavailable_intervals":[[2026,2099,"NOT_MODELED_BY_THIS_AUTHORITY"]]}
class CoverageTests(unittest.TestCase):
 def test_demography_is_global_coverage(self):
  self.assertTrue(can_treat_as_global(coverage=coverage_for(coverage_rows=[D],fact_family="demography",year=2226)))
 def test_labor_is_not_global_coverage(self):
  self.assertFalse(can_treat_as_global(coverage=coverage_for(coverage_rows=[L],fact_family="biosynthetic_labor",year=2226)))
 def test_mismatched_geographies_rejected(self):
  with self.assertRaisesRegex(ValueError,"COVERAGE_MISMATCH"):
   require_same_coverage(left=coverage_for(coverage_rows=[D],fact_family="demography",year=2226),right=coverage_for(coverage_rows=[L],fact_family="biosynthetic_labor",year=2226))
 def test_labor_before_2100_unavailable(self):
  self.assertIsNone(coverage_for(coverage_rows=[L],fact_family="biosynthetic_labor",year=2099))
 def test_nonunique_rejected(self):
  with self.assertRaisesRegex(ValueError,"NOT_UNIQUE"):
   coverage_for(coverage_rows=[D,D],fact_family="demography",year=2100)
if __name__=="__main__": unittest.main()
