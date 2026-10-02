import unittest
from engineering.civprop.contracts.ceres_causal_vertical_slice_v0_3 import run_ceres_machinery_slice
from engineering.civprop.contracts.mission_knowledge_v1 import KnowledgeQuestion

class CeresCausalVerticalSliceTests(unittest.TestCase):
 def q(self):
  return KnowledgeQuestion("SOLAR_RESOURCE::CERES::WATER","UNRESOLVED_CHARACTERIZATION","CERES::WATER","CERES",None,"NOT_AUTHORIZED","PRIVATE",("M4B",),"UNKNOWN_AFTER_SEARCH")
 def test_qualified_claim_changes_decision_without_inventing_resource_truth(self):
  b,k,c,q,a=run_ceres_machinery_slice(question=self.q(),actor_id="PROSPECTOR_TEST",certifier_id="CERT_TEST",financier_id="CAPITAL_TEST",observation_id="OBS_CERES_1",year=2030,qualified_person=True,chain_of_custody=True,auditable_data=True,sampling_sufficient=True)
  self.assertEqual(b.action,"WAIT"); self.assertEqual(q.status,"QUALIFIED"); self.assertEqual(a.action,"ADVANCE_DUE_DILIGENCE")
  self.assertEqual(c.claim_kind,"CHARACTERIZATION_RESULT")
  for forbidden in ("abundance","recoverability","economic_value","probability"):
   self.assertFalse(hasattr(c,forbidden))
 def test_certifier_can_decline_and_blocks_decision_change(self):
  b,k,c,q,a=run_ceres_machinery_slice(question=self.q(),actor_id="PROSPECTOR_TEST",certifier_id="CERT_TEST",financier_id="CAPITAL_TEST",observation_id="OBS_CERES_2",year=2030,qualified_person=True,chain_of_custody=False,auditable_data=True,sampling_sufficient=True)
  self.assertEqual(q.status,"DECLINED"); self.assertIn("NO_CHAIN_OF_CUSTODY",q.rationale_codes); self.assertEqual(a.action,"WAIT")
 def test_insufficient_sampling_declines(self):
  *_,q,a=run_ceres_machinery_slice(question=self.q(),actor_id="P",certifier_id="C",financier_id="F",observation_id="O",year=2030,qualified_person=True,chain_of_custody=True,auditable_data=True,sampling_sufficient=False)
  self.assertIn("INSUFFICIENT_SAMPLING",q.rationale_codes); self.assertEqual(a.action,"WAIT")
 def test_wrong_body_rejected(self):
  q=self.q(); q=KnowledgeQuestion(q.question_id,q.question_kind,q.subject_id,"VESTA",q.prior_probability,q.prior_status,q.visibility,q.provenance_refs,q.evidence_disposition)
  with self.assertRaisesRegex(ValueError,"Ceres-only"):
   run_ceres_machinery_slice(question=q,actor_id="P",certifier_id="C",financier_id="F",observation_id="O",year=2030,qualified_person=True,chain_of_custody=True,auditable_data=True,sampling_sufficient=True)
if __name__=='__main__': unittest.main()
