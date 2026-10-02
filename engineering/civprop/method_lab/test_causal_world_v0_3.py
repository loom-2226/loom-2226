import ast,hashlib,inspect,json,tempfile,unittest
from pathlib import Path

from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.compile_inputs_v1 import capture_live_authority
from engineering.civprop.contracts.gap014_scenario_bridge_v1 import inject_demographic_authority
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.method_lab.causal_world_v0_3 import run_causal_world
from engineering.civprop.contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03,commit_winning_branches
from engineering.civprop.contracts.gate_h_closed_loop_causality_v0_3 import run_closed_loop


class CausalWorldV03Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.td=tempfile.TemporaryDirectory(); p=Path(cls.td.name)
  build_bundle_dir(p)
  capture=capture_live_authority(p/'gap014.json',database='loom_dev')
  sp=p/'scenario_v1.json'; scenario=json.loads(sp.read_text())
  sp.write_text(json.dumps(inject_demographic_authority(scenario=scenario,capture=capture),indent=2,sort_keys=True)+'\n')
  mp=p/'manifest_v1.json'; manifest=json.loads(mp.read_text()); sb=sp.read_bytes(); tb=(p/manifest['truth_file']).read_bytes()
  manifest['sha256'][manifest['scenario_file']]=hashlib.sha256(sb).hexdigest(); manifest['bundle_sha256']=hashlib.sha256(sb+b'\n'+tb).hexdigest()
  mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
  cls.bundle=load_bundle(p)

 @classmethod
 def tearDownClass(cls): cls.td.cleanup()

 def test_runtime_has_no_hybrid_dependency(self):
  import engineering.civprop.method_lab.causal_world_v0_3 as m
  src=Path(m.__file__).read_text(); tree=ast.parse(src)
  imported=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Import): imported.extend(a.name for a in n.names)
   elif isinstance(n,ast.ImportFrom): imported.append(n.module or '')
  self.assertFalse(any('hybrid_v1' in x.lower() for x in imported))

 def test_bounded_real_solar_bundle_runs_without_hybrid(self):
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2036,
   causal_facility_commissions=({"facility_id":"CAUSAL_CONTROL_POWER","project_archetype_id":"POWER_PLANT","location_id":"LUNA_SURFACE","owner_actor_id":"NASA","committed_year":2026,"commissioned_year":2027,"project_status":"ACTIVE","provenance_refs":["GATE_G_TRANSACTION","GATE_H_ACTIVE_PROJECT"]},))
  self.assertEqual(r.annual_lane_invocations['WORLD_ANNUAL_ACCOUNTING'],11)
  self.assertEqual(len(r.annual_states),11*len(self.bundle.scenario.locations))
  self.assertGreater(len(r.resource_states),0)
  self.assertGreater(len(r.power_states),0)
  self.assertGreater(len(r.traffic_demand_states),0)
  self.assertGreater(len(r.facility_production_states),0)
  represented=(len(r.mission_opportunity_dispositions)+sum(x["opportunity_count"] for x in r.mission_opportunity_disposition_summaries))
  self.assertGreater(represented,0)
  self.assertTrue(all(x["opportunity_count"]>0 and len(x["member_sha256"])==64 for x in r.mission_opportunity_disposition_summaries))

 def test_gate_g_h_active_project_can_feed_real_world_facility(self):
  state={"budgets":{"NASA":100.0},"provider_capacity":{"FIREFLY_AEROSPACE":1.0},"reservations":{},"projects":{},"future_events":[],"provenance_ledger":[],"committed_transaction_ids":[]}
  req=TransactionRequestV03("TX_WORLD","O_WORLD","NASA","FIREFLY_AEROSPACE",10,1,"P_WORLD",2027,"PROJECT_REVIEW",("STEP4_CONTROL",))
  committed,tx=commit_winning_branches(state=state,branches=({"opportunity_id":"O_WORLD","action":"COMMIT"},),request_by_opportunity={"O_WORLD":req})
  self.assertEqual(tx[0].status,"COMMITTED")
  closed=run_closed_loop(committed_state=committed,start_year=2026,end_year=2028,review_to_activation_lag_years=1)
  project=closed.final_state["projects"]["P_WORLD"]; self.assertEqual(project["status"],"ACTIVE")
  r=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2028,
   causal_facility_commissions=({"facility_id":"FAC_P_WORLD","project_archetype_id":"POWER_PLANT","location_id":"LUNA_SURFACE","owner_actor_id":"NASA","committed_year":2026,"commissioned_year":2028,"project_status":project["status"],"provenance_refs":["TX_WORLD","P_WORLD"]},))
  self.assertTrue(any(f.facility_id=="FAC_P_WORLD" for f in r.facilities))
  self.assertTrue(any(x.facility_id=="FAC_P_WORLD" for x in r.facility_production_states))

 def test_deterministic_bounded_replay(self):
  a=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2028)
  b=run_causal_world(bundle=self.bundle,seed=42,start_year=2026,end_year=2028)
  self.assertEqual(a.final_state_digest,b.final_state_digest)
  self.assertEqual(a.conductor_sha256,b.conductor_sha256)


if __name__=='__main__': unittest.main()
