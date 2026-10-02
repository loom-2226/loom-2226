import tempfile
from pathlib import Path
import unittest
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.mission_lane_v1 import MissionLaneV1
from engineering.civprop.method_lab.prototypes.common import Recorder
class TestSolarCharacterizationDecisionPathV03(unittest.TestCase):
 def test_real_bundle_characterization_reaches_commit_gate(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); b=load_bundle(d); lane=MissionLaneV1(b,42,Recorder())
   mission=next(m for m in lane.package.missions if lane._question_by_id[m.target_question_id].question_kind=='UNRESOLVED_CHARACTERIZATION')
   actor=next(a.actor_id for a in b.scenario.actors)
   q=lane._question_by_id[mission.target_question_id]; k=lane.knowledge[(actor,q.subject_id,mission.destination_location_id)]
   cost,_,_,unit=lane._economics(mission.mission_archetype_id,2026)
   access=lane._access_status(actor_id=actor,mission_archetype_id=mission.mission_archetype_id,year=2026)
   capability=lane._capability_status(actor_id=actor,mission_archetype_id=mission.mission_archetype_id,year=2026)
   weight=lane._exploration_weight(actor,2026)
   decision=lane._evaluate_characterization(knowledge=k,mission=mission,year=2026,actor_id=actor,access_status=access,capability_status=capability,budget_status='KNOWN',budget_amount=10**9,budget_unit=unit,mission_cost=cost)
   self.assertEqual(access,'UNKNOWN'); self.assertEqual(capability,'UNKNOWN'); self.assertIn(weight,{0.25,0.5,0.75})
   self.assertEqual(decision.action,'WAIT'); self.assertIn('CAPABILITY_NOT_USABLE',decision.rationale_codes); self.assertIsNone(decision.expected_value_of_information)
if __name__=='__main__': unittest.main()
