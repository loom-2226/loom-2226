import json,tempfile,unittest
from pathlib import Path
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.contracts.gate_b_causal_spine_v0_3 import (
 apply_gate_b_qualification,timeline_frontier_from_capture,CONTROL_TECH,CAPTURE_SHA)
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.prototypes.common import actor_tech_status
from engineering.civprop.method_lab.mission_lane_v1 import MissionLaneV1

CAP=Path('/tmp/LOOM_GATE_A_AUTHORITY_CAPTURE_V03_COMPLETE')
class R:
 def __init__(self): self.knowledge_states=[]; self.mission_decisions=[]; self.missions=[]; self.events=[]; self.mission_opportunity_dispositions=[]
 def event(self,*a): self.events.append(a)

def bundle(positive=False):
 td=tempfile.TemporaryDirectory(); p=build_bundle_dir(Path(td.name))
 sp=p/'scenario_v1.json'; s=json.loads(sp.read_text()); s=apply_gate_b_qualification(s,CAP,positive_control=positive); sp.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
 # Qualification loader: update bundle hashes after explicit derived scenario.
 mp=p/'manifest_v1.json'; m=json.loads(mp.read_text()); import hashlib
 m['sha256'][m['scenario_file']]=hashlib.sha256(sp.read_bytes()).hexdigest()
 tb=(p/m['truth_file']).read_bytes(); m['bundle_sha256']=hashlib.sha256(sp.read_bytes()+b'\n'+tb).hexdigest(); mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
 return td,load_bundle(p)

class GateB(unittest.TestCase):
 def test_timeline_is_from_frozen_gate_a(self):
  f=timeline_frontier_from_capture(CAP); self.assertEqual(len(f),24)
  by={x['source_milestone_id']:x for x in f}
  self.assertEqual(by['TRN-MOD-HEAVY']['frontier_year'],2040)
  self.assertEqual(by['TRN-MOD-NEP']['frontier_year'],2050)
  self.assertEqual(by['SPEC-MOD-TORCH']['frontier_year'],2120)
  self.assertNotIn('TRN-2140-TORCH-MATURE',by)
 def test_timeline_alone_does_not_grant_actor_access(self):
  td,b=bundle(False)
  try:
   self.assertEqual(actor_tech_status(b,'NASA',CONTROL_TECH,2026),'UNKNOWN')
   self.assertEqual(actor_tech_status(b,'NASA','TRN_MOD_NEP',2050),'UNKNOWN')
  finally: td.cleanup()
 def test_positive_control_explicitly_grants_only_control_capability(self):
  td,b=bundle(True)
  try:
   self.assertEqual(actor_tech_status(b,'NASA',CONTROL_TECH,2026),'USABLE')
   self.assertEqual(actor_tech_status(b,'NASA','TRN_MOD_NEP',2050),'UNKNOWN')
   self.assertEqual(actor_tech_status(b,'CNSA',CONTROL_TECH,2026),'UNKNOWN')
  finally: td.cleanup()
 def test_normal_arm_accounts_all_nasa_candidates_as_gate_exclusions(self):
  td,b=bundle(False)
  try:
   r=R(); lane=MissionLaneV1(b,42,r)
   from engineering.civprop.contracts.actor_state_v1 import actor_state_runtime
   ar=actor_state_runtime(b.scenario.actor_state_v1)
   budgets={a.actor_id: ar.budget(a.actor_id,2026).amount for a in b.scenario.actors}
   lane.evaluate_and_commit(year=2026,budgets=budgets,recorder=r)
   disp=[x for x in r.mission_opportunity_dispositions if x['actor_id']=='NASA']
   self.assertEqual(len(disp),344)
   self.assertEqual(sum(x['disposition']=='EXCLUDED_GATE' for x in disp),344)
   self.assertEqual(sum(x['disposition']=='DECISION_EMITTED' for x in disp),0)
   self.assertTrue(all('ACCESS_UNKNOWN' in x['reason_codes'] for x in disp))
  finally: td.cleanup()
 def test_positive_control_makes_solar_decisions_reappear(self):
  td,b=bundle(True)
  try:
   r=R(); lane=MissionLaneV1(b,42,r)
   from engineering.civprop.contracts.actor_state_v1 import actor_state_runtime
   ar=actor_state_runtime(b.scenario.actor_state_v1)
   budgets={a.actor_id: ar.budget(a.actor_id,2026).amount for a in b.scenario.actors}
   # Mutable budget semantics are exercised by full Hybrid later; for this lane
   # positive control, numeric budget is sufficient and uses scenario capital unit.
   lane.evaluate_and_commit(year=2026,budgets=budgets,recorder=r)
   solar=[d for d in r.mission_decisions if d.mission_archetype_id.startswith('SOLAR_RECON::')]
   self.assertGreater(len(solar),0)
   self.assertTrue(any(d.actor_id=='NASA' for d in solar))
   disp=[x for x in r.mission_opportunity_dispositions if x['actor_id']=='NASA']
   self.assertEqual(len(disp),344)
   self.assertEqual(sum(x['disposition']=='DECISION_EMITTED' for x in disp),3)
   self.assertEqual(sum(x['disposition']=='EXCLUDED_ANNUAL_PORTFOLIO_CAP' for x in disp),341)
  finally: td.cleanup()
if __name__=='__main__': unittest.main()
