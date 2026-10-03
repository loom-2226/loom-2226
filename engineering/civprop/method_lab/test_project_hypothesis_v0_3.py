import json,unittest
from pathlib import Path
from .project_hypothesis_v0_3 import *
ROOT=Path(__file__).resolve().parents[3]
SC=ROOT/'engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json'
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.x=json.loads(SC.read_text());cls.a=cls.x['actor_state_v1']['actors'][0]
 def test_roover_forms_real_scoped_hypothesis_but_transport_remains_unknown(self):
  h=from_observed_mission(actor_id='AUS',subject_id='ROO_VER',objective='Execute observed Australian lunar rover mission',
      actor_state=self.a,accessibility=self.x['accessibility_v1'])
  self.assertEqual(h.destination_location_id,'LUNA_SURFACE');self.assertEqual(h.target_year,2030)
  self.assertIn('TRANSPORT_FEASIBILITY',h.unresolved_requirements)
  self.assertEqual(h.status,HypothesisStatus.INVESTIGATING);self.assertTrue(h.provenance_refs)
 def test_hypothesis_can_refine_without_rewriting_original(self):
  h=from_observed_mission(actor_id='AUS',subject_id='ROO_VER',objective='Execute observed Australian lunar rover mission',
      actor_state=self.a,accessibility=self.x['accessibility_v1'])
  r=refine(h,resolved_requirements=h.unresolved_requirements,new_provenance=('QUALIFIED_POSITIVE_CONTROL',))
  self.assertEqual(r.status,HypothesisStatus.FEASIBILITY_REVIEW);self.assertNotEqual(h.status,r.status)
 def test_no_service_path_does_not_invent_destination(self):
  h=from_observed_mission(actor_id='AUS',subject_id='X',objective='X',actor_state=self.a,accessibility={'service_paths':[]})
  self.assertIsNone(h.destination_location_id);self.assertIn('DESTINATION',h.unresolved_requirements)
if __name__=='__main__':unittest.main()
