import unittest
from engineering.civprop.contracts.generated_realization_v0_3 import *

class GeneratedRealizationTests(unittest.TestCase):
 def test_unknown_model_stays_unresolved(self):
  r=generate_realization(question_id='Q',location_id='CERES',material_family='WATER',seed=42,prevalence=None,provenance_refs=('AUTHORED_TEST',))
  self.assertEqual(r.state,'UNRESOLVED'); self.assertFalse(r.actor_visible); self.assertEqual(r.authority_class,'GENERATED_REALIZATION_NON_EMPIRICAL')
 def test_seeded_generation_is_deterministic(self):
  kw=dict(question_id='Q',location_id='CERES',material_family='WATER',seed=42,prevalence=.5,provenance_refs=('AUTHORED_TEST_PREVALENCE',))
  self.assertEqual(generate_realization(**kw),generate_realization(**kw))
 def test_generated_truth_cannot_be_read_by_actor(self):
  r=generate_realization(question_id='Q',location_id='CERES',material_family='WATER',seed=1,prevalence=1,provenance_refs=('AUTHORED_TEST',))
  with self.assertRaisesRegex(PermissionError,'EVALUATOR_ONLY'): actor_view(r)
 def test_observation_requires_authorized_transform(self):
  r=generate_realization(question_id='Q',location_id='CERES',material_family='WATER',seed=1,prevalence=1,provenance_refs=('AUTHORED_TEST',))
  with self.assertRaises(PermissionError): observe_generated_realization(realization=r,observation_id='O',year=2030,authorized=False)
  o=observe_generated_realization(realization=r,observation_id='O',year=2030,authorized=True)
  self.assertEqual(o.observed_status,'OBSERVED_PRESENT'); self.assertNotEqual(o.authority_class,r.authority_class)
 def test_no_abundance_recoverability_or_value_generated(self):
  r=generate_realization(question_id='Q',location_id='CERES',material_family='WATER',seed=1,prevalence=1,provenance_refs=('AUTHORED_TEST',))
  for x in ('abundance','stock_tonnes','grade','recoverability','economic_value','price'):
   self.assertFalse(hasattr(r,x))
 def test_extreme_prevalence(self):
  base=dict(question_id='Q',location_id='CERES',material_family='WATER',seed=99,provenance_refs=('AUTHORED_TEST',))
  self.assertEqual(generate_realization(prevalence=0,**base).state,'ABSENT')
  self.assertEqual(generate_realization(prevalence=1,**base).state,'PRESENT')
if __name__=='__main__': unittest.main()
