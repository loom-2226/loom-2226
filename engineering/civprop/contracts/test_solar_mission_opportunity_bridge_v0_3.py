import unittest
from pathlib import Path
from engineering.civprop.contracts.solar_mission_opportunity_bridge_v0_3 import build_solar_mission_opportunity_catalog
ROOT=Path(__file__).resolve().parents[3]
NAV=ROOT/"reports/solar_civprop/NAV_READINESS_V1.json"
M4B=ROOT/"dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv"
class SolarMissionOpportunityV03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=build_solar_mission_opportunity_catalog(NAV,M4B)
  cls.m={(x["destination_body_id"],x["resource_family"]):x for x in cls.p["mission_opportunities"]}
  cls.q={(x["body_id"],x["resource_family"]):x for x in cls.p["questions"]}
 def test_all_m4b_lanes_become_questions_not_resource_claims(self):
  self.assertEqual(len(self.p["questions"]),380); self.assertEqual(len(self.p["mission_opportunities"]),380)
 def test_unknown_after_search_remains_unresolved_not_zero(self):
  q=self.q[("AMUN","VOLATILES")]
  self.assertEqual(q["knowledge_state"],"UNRESOLVED_AFTER_SEARCH"); self.assertIsNone(q["prior_probability"])
 def test_presence_does_not_become_abundance_or_economic_resource(self):
  m=self.m[("CERES","VOLATILES")]
  self.assertEqual(m["economic_claim_status"],"NONE")
  self.assertEqual(m["resource_inventory_status"],"UNKNOWN_UNLESS_SEPARATELY_QUANTIFIED_AND_SCOPED")
 def test_inferred_is_not_promoted_to_measured(self):
  self.assertEqual(self.q[("ENCELADUS","SILICATES_ROCK")]["knowledge_state"],"INFERRED_OR_MODELLED_SCOPE_LIMITED")
 def test_mission_never_materializes_facility(self):
  self.assertTrue(all(x["action_kind"]=="MISSION" and x["facility_materialization"]=="FORBIDDEN" for x in self.p["mission_opportunities"]))
 def test_nav_lien_blocks_mission_not_body_existence(self):
  # DACTYL is in the 110-body NAV catalog but lacks NAV-1 at the representative epoch.
  for fam in ("VOLATILES","METALS","SILICATES_ROCK","CARBONACEOUS_ORGANICS"):
   self.assertEqual(self.m[("DACTYL",fam)]["status"],"BLOCKED_OR_UNKNOWN")
   self.assertIn("NAV1_UNSUPPORTED_AT_ASSESSMENT_EPOCH",self.m[("DACTYL",fam)]["limiting_constraints"])
 def test_no_generic_solar_probability_is_invented(self):
  self.assertTrue(all(x["prior_probability"] is None for x in self.p["questions"]))
if __name__=="__main__": unittest.main()
