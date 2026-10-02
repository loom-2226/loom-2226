import csv
from pathlib import Path
import unittest
from .solar_reconnaissance_knowledge_v0_3 import state_from_coverage_row,reconnaissance_eligibility,evaluate_characterization,complete_characterization
ROOT=Path(__file__).resolve().parents[3]
class TestSolarReconnaissanceKnowledgeV03(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with (ROOT/'dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv').open(newline='') as f:
   cls.rows=list(csv.DictReader(f))
 def row(self,body,family): return next(r for r in self.rows if r['body_id']==body and r['resource_family']==family)
 def test_unknown_is_eligible_without_becoming_zero_or_probability(self):
  s=state_from_coverage_row(self.row('CERES','METALS'))
  self.assertEqual(s.evidence_disposition,'UNKNOWN_AFTER_SEARCH'); self.assertIsNone(s.prior_probability)
  self.assertTrue(reconnaissance_eligibility(s,nav1_candidate=True).eligible)
 def test_supported_evidence_can_still_need_characterization(self):
  s=state_from_coverage_row(self.row('MARS','VOLATILES'))
  self.assertIsNone(s.prior_probability); self.assertTrue(reconnaissance_eligibility(s,nav1_candidate=True).eligible)
 def test_nav_lien_blocks_eligibility(self):
  s=state_from_coverage_row(self.row('NIX','VOLATILES'))
  x=reconnaissance_eligibility(s,nav1_candidate=False)
  self.assertFalse(x.eligible); self.assertIn('NAV1_NOT_AVAILABLE',x.rationale_codes)
 def test_numeric_prior_is_hostile(self):
  from dataclasses import replace
  s=replace(state_from_coverage_row(self.row('CERES','METALS')),prior_probability=.5)
  x=reconnaissance_eligibility(s,nav1_candidate=True)
  self.assertFalse(x.eligible); self.assertIn('UNAUTHORIZED_NUMERIC_PRIOR',x.rationale_codes)
 def test_characterization_uses_authored_actor_priority_not_resource_value(self):
  s=state_from_coverage_row(self.row('CERES','METALS'))
  d=evaluate_characterization(s,nav1_candidate=True,capability_usable=True,budget_known=True,affordable=True,exploration_weight=.75)
  self.assertEqual(d.action,'COMMIT_MISSION'); self.assertIn('AUTHORED_EXPLORATION_PRIORITY',d.rationale_codes)
 def test_completion_does_not_invent_resource_truth(self):
  s=state_from_coverage_row(self.row('CERES','METALS'))
  o=complete_characterization(s)
  self.assertEqual(o.characterization_status,'CHARACTERIZATION_COMPLETED')
  self.assertEqual(o.resource_result_status,'UNRESOLVED_WITHOUT_AUTHORIZED_OBSERVATION_RESULT')
 def test_affordability_and_capability_fail_closed(self):
  s=state_from_coverage_row(self.row('MARS','VOLATILES'))
  self.assertEqual(evaluate_characterization(s,nav1_candidate=True,capability_usable=False,budget_known=True,affordable=True,exploration_weight=.75).action,'WAIT')
  self.assertEqual(evaluate_characterization(s,nav1_candidate=True,capability_usable=True,budget_known=True,affordable=False,exploration_weight=.75).action,'WAIT')
if __name__=='__main__': unittest.main()
