import unittest
from engineering.civprop.contracts.demographic_depth_v1 import *
class DemographicDepthTests(unittest.TestCase):
 def test_unknown_rates_do_not_become_zero(self):
  c=CohortStateV1("C","MARS",100,2100,("OBS",))
  r=propagate_cohort(cohort=c,rates=DemographicRatesV1(None,None,("UNKNOWN",)),
   net_migration=0,year=2101)
  self.assertEqual(r.status,"UNKNOWN_RATES"); self.assertIsNone(r.closing_population)
 def test_birth_death_migration_accounting(self):
  c=CohortStateV1("C","MARS",100,2100,("OBS",))
  r=propagate_cohort(cohort=c,rates=DemographicRatesV1(.02,.01,("TEST",)),
   net_migration=5,year=2101)
  self.assertEqual((r.births,r.deaths,r.closing_population),(2,1,106))
 def test_habitat_does_not_create_people(self):
  c=CohortStateV1("EMPTY","CERES",0,2100,("EMPTY",))
  r=propagate_cohort(cohort=c,rates=DemographicRatesV1(.02,.01,("TEST",)),
   net_migration=0,year=2101)
  self.assertEqual(r.closing_population,0)
 def test_migration_is_explicit(self):
  c=CohortStateV1("C","LUNA",10,2100,("OBS",))
  r=propagate_cohort(cohort=c,rates=DemographicRatesV1(0,0,("TEST",)),
   net_migration=7,year=2101)
  self.assertEqual(r.closing_population,17)
 def test_viability_unknown_without_threshold(self):
  self.assertEqual(biological_viability_status(population=100,minimum_viable_population=None),"UNKNOWN")
 def test_viability_threshold_is_authored_not_inferred(self):
  self.assertEqual(biological_viability_status(population=99,minimum_viable_population=100),"BELOW_AUTHORED_THRESHOLD")
  self.assertEqual(biological_viability_status(population=100,minimum_viable_population=100),"MEETS_AUTHORED_THRESHOLD")
if __name__=="__main__": unittest.main()
