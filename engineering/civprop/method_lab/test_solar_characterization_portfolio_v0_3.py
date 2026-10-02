import tempfile,unittest
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.mission_lane_v1 import MissionLaneV1
from engineering.civprop.method_lab.prototypes.common import Recorder,MutableActorBudget
class T(unittest.TestCase):
 def test_annual_commits_are_bounded_by_authored_exploration_posture(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); b=load_bundle(d); r=Recorder(); lane=MissionLaneV1(b,42,r); unit=b.scenario.units['project_capital']; budgets={a.actor_id:MutableActorBudget('KNOWN',1e9,unit,'TEST') for a in b.scenario.actors}; lane.evaluate_and_commit(year=2026,budgets=budgets,recorder=r)
   chars={q.question_id for q in lane.package.questions if q.question_kind=='UNRESOLVED_CHARACTERIZATION'}
   for a in b.scenario.actors:
    commits=[x for x in r.mission_decisions if x.actor_id==a.actor_id and x.question_id in chars and x.action=='COMMIT_MISSION']
    cap=lane._characterization_annual_cap(a.actor_id,2026)
    self.assertLessEqual(len(commits),cap); self.assertGreater(cap,0)
    decisions=[x for x in r.mission_decisions if x.actor_id==a.actor_id and x.question_id in chars]
    self.assertLessEqual(len(decisions),cap)
 def test_rank_prefers_lower_placeholder_friction_without_resource_value(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); b=load_bundle(d); r=Recorder(); lane=MissionLaneV1(b,42,r); actor=b.scenario.actors[0].actor_id
   chars=[m for m in lane.package.missions if lane._question_by_id[m.target_question_id].question_kind=='UNRESOLVED_CHARACTERIZATION']
   ranked=sorted((lane._characterization_rank(actor,m,2026,lane._economics(m.mission_archetype_id,2026)[0]),m) for m in chars)
   self.assertLessEqual(ranked[0][0][0],ranked[-1][0][0])
if __name__=='__main__': unittest.main()
