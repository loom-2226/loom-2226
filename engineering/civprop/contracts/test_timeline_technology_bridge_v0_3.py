import unittest
from pathlib import Path
from engineering.civprop.contracts.timeline_technology_bridge_v0_3 import build_timeline_technology_bridge
ROOT=Path(__file__).resolve().parents[3]
REG=ROOT/"docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md"
SNAP="timeline-v0-1-0232bf23494f-20260925"
class TimelineTechnologyBridgeV03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pkg=build_timeline_technology_bridge(REG,SNAP)
  cls.by={x["source_milestone_id"]:x for x in cls.pkg["technology_frontier"]}
 def test_all_selected_anchors_present(self): self.assertEqual(len(self.pkg["technology_frontier"]),23)
 def test_transport_anchors(self):
  self.assertEqual(self.by["TRN-MOD-HEAVY"]["frontier_year"],2040)
  self.assertEqual(self.by["TRN-MOD-NEP"]["frontier_year"],2050)
 def test_speculative_transport_is_explicit(self):
  self.assertEqual(self.by["SPEC-MOD-TORCH"]["frontier_year"],2120)
  self.assertEqual(self.by["SPEC-MOD-METRIC-SHIP"]["authority_class"],"SPECULATIVE_FICTION")
 def test_date_never_grants_actor_capability(self):
  self.assertTrue(self.pkg["semantics"]["date_does_not_unlock"])
  self.assertTrue(all(x["actor_capability_effect"]=="NONE_WITHOUT_SEPARATE_ACTOR_STATE_EVENT" for x in self.by.values()))
 def test_canon_comparator_not_promoted(self):
  self.assertNotIn("TRN-2140-TORCH-MATURE",self.by)
  self.assertNotIn("TRN-2223-LOOM-CREW",self.by)
 def test_site_specific_and_unknown_preserved(self):
  self.assertTrue(self.pkg["semantics"]["site_specific"])
  self.assertTrue(self.pkg["semantics"]["unknown_not_zero"])
if __name__=="__main__": unittest.main()
