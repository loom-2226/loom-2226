import unittest
from engineering.civprop.contracts.gap014_postgres_authority_v1 import *

class Gap014PostgresTests(unittest.TestCase):
 def test_full_surface_ready(self):
  self.assertEqual(postgres_surface_status(available_relations=EARTH_GAP014_REQUIRED_RELATIONS)["status"],"READY")
 def test_missing_cohort_detected(self):
  r=postgres_surface_status(available_relations=("earth_demographic_year","earth_labor_composition_year","earth_derivation"))
  self.assertEqual(r["missing"],("earth_biological_cohort_year",))
 def test_queries_are_snapshot_and_year_scoped(self):
  q=gap014_postgres_queries(snapshot_id="S",year=2226)
  for name in ("demographic","cohorts","labor"):
   self.assertIn("snapshot_id='S'",q[name]); self.assertIn("year=2226",q[name])
 def test_derivation_query_is_snapshot_scoped(self):
  self.assertIn("earth_derivation",gap014_postgres_queries(snapshot_id="S",year=2226)["derivations"])
 def test_no_legacy_profile_surface(self):
  all_rel=EARTH_GAP014_REQUIRED_RELATIONS+EARTH_GAP014_SUPPORTING_RELATIONS
  self.assertNotIn("entity_demographic_profiles",all_rel)
if __name__=="__main__": unittest.main()
