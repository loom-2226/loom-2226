import unittest
from engineering.civprop.contracts.demographic_technology_bridge_v1 import *
class DemographicTechnologyBridgeTests(unittest.TestCase):
 def exp(self,exists=True,access=True,received=True,tech="MED_X"):
  return DemographicTechnologyExposureV1("C","MARS",tech,2120,exists,access,received,("fixture",))
 def mod(self,m=.5,tech="MED_X",kind="MORTALITY"):
  return DemographicModifierV1(tech,kind,m,("fixture-effect",))
 def test_exists_is_not_access(self):
  self.assertEqual(exposure_gate(self.exp(access=False)),"NO_ACTOR_ACCESS")
 def test_access_is_not_intervention(self):
  self.assertEqual(exposure_gate(self.exp(received=False)),"INTERVENTION_NOT_RECEIVED")
 def test_threshold_row_never_is_effect(self):
  self.assertFalse(timeline_row_is_demographic_effect({"frontier_year":2070,"family":"MED"}))
 def test_unexposed_does_not_modify(self):
  self.assertEqual(apply_demographic_modifier(baseline_rate=.02,
   exposure=self.exp(access=False),modifier=self.mod()),.02)
 def test_explicit_effect_can_modify(self):
  self.assertEqual(apply_demographic_modifier(baseline_rate=.02,
   exposure=self.exp(),modifier=self.mod()),.01)
 def test_unknown_effect_stays_unknown(self):
  self.assertIsNone(apply_demographic_modifier(baseline_rate=.02,
   exposure=self.exp(),modifier=self.mod(m=None)))
 def test_unknown_baseline_stays_unknown(self):
  self.assertIsNone(apply_demographic_modifier(baseline_rate=None,
   exposure=self.exp(),modifier=self.mod()))
 def test_wrong_technology_rejected(self):
  with self.assertRaisesRegex(ValueError,"MISMATCH"):
   apply_demographic_modifier(baseline_rate=.02,exposure=self.exp(),modifier=self.mod(tech="GEN_X"))
 def test_med_generations_anchor_does_not_create_births(self):
  row={"source_milestone_id":"MED-MOD-GENERATIONS","frontier_year":2120,
       "frontier_semantics":"CONSIDERATION_ANCHOR_NOT_ACHIEVEMENT"}
  self.assertFalse(timeline_row_is_demographic_effect(row))
 def test_cybernetic_effect_requires_supported_demographic_kind(self):
  with self.assertRaisesRegex(ValueError,"UNSUPPORTED"):
   apply_demographic_modifier(baseline_rate=.02,exposure=self.exp(tech="CYBER_X"),
    modifier=self.mod(tech="CYBER_X",kind="PERSONHOOD"))
if __name__=="__main__": unittest.main()
