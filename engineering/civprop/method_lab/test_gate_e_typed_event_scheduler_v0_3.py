import copy,json,unittest
from pathlib import Path
from engineering.civprop.contracts.gate_e_typed_event_scheduler_v0_3 import run_typed_scheduler
E=Path(__file__).resolve().parents[1]/"contracts/gate_c_blue_ghost_2_evidence_v0_3.json"
UNIVERSE=("NASA","FIREFLY_AEROSPACE","AUS","CNSA","ESA","SPACEX","JAXA")
CAP={"NASA":{"CLPS_NAMED_LUNAR_DELIVERY_ACCESS":"ACCESS"}}

class GateE(unittest.TestCase):
 def setUp(self): self.e=json.loads(E.read_text())
 def seeds(self):
  return [
   {"year":2027,"event_type":"NAMED_SERVICE_OPPORTUNITY","family":"TRANSPORT",
    "location_ids":["EARTH_SURFACE","LUNA_FAR_SIDE"],"payload":{"service_key":"bg2"}},
   {"year":2050,"event_type":"TECHNOLOGY_FRONTIER_REACHED","family":"TECHNOLOGY",
    "payload":{"tech_id":"TRN_MOD_NEP"},"provenance_refs":["TIMELINE_CONTROL"]}]
 def execute(self,seeds=None,cap=CAP,e=None,end=2051):
  return run_typed_scheduler(start_year=2026,end_year=end,seed_events=self.seeds() if seeds is None else seeds,
   actor_universe=UNIVERSE,actor_capabilities=cap,service_evidence={"bg2":self.e if e is None else e})
 def test_jumps_only_to_causal_years(self):
  r=self.execute(); self.assertEqual(r.processed_years,(2027,2029,2050)); self.assertEqual(r.annual_heartbeat_count,0)
 def test_multiple_typed_families_share_one_queue(self):
  r=self.execute(); self.assertEqual({x.family for x in r.events},{"TRANSPORT","TECHNOLOGY"})
 def test_future_child_event_created(self):
  r=self.execute(); review=[x for x in r.events if x.event_type=="POST_DELIVERY_REVIEW"][0]
  self.assertEqual(review.year,2029); self.assertEqual(len(review.parent_event_ids),1)
 def test_frontier_does_not_grant_capability(self):
  r=self.execute(); f=[x for x in r.events if x.event_type=="TECHNOLOGY_FRONTIER_REACHED"][0]
  self.assertEqual(f.status,"CONSIDERATION_ANCHOR"); self.assertEqual(f.actor_ids,())
 def test_same_time_dependency_order(self):
  r=self.execute(); kinds=[x.event_type for x in r.events if x.year==2027]
  self.assertEqual(kinds,["NAMED_SERVICE_OPPORTUNITY","NAMED_SERVICE_ASSESSMENT",
   "NAMED_SERVICE_REALIZATION","TRANSPORT_CONSEQUENCE","BRANCH_DEMOTION"])
 def test_failure_does_not_poison_independent_frontier_branch(self):
  r=self.execute(cap={"NASA":{}})
  self.assertEqual(r.consequences,())
  self.assertTrue(any(x.event_type=="TECHNOLOGY_FRONTIER_REACHED" and x.year==2050 for x in r.events))
 def test_unknown_vehicle_stops_only_transport_branch(self):
  e=copy.deepcopy(self.e); e["provider_surface_capacity_kg"]=None
  r=self.execute(e=e)
  self.assertFalse(any(x.event_type=="NAMED_SERVICE_REALIZATION" for x in r.events))
  self.assertTrue(any(x.family=="TECHNOLOGY" for x in r.events))
 def test_selective_activation_and_reactivation(self):
  r=self.execute(); self.assertEqual(set(r.activated_actor_ids),{"NASA","FIREFLY_AEROSPACE"})
  self.assertEqual(r.final_active_actor_ids,())
  self.assertEqual(set(r.dormant_actor_ids),set(UNIVERSE)-{"NASA","FIREFLY_AEROSPACE"})
 def test_out_of_window_future_child_not_executed(self):
  r=self.execute(end=2028); self.assertEqual(r.processed_years,(2027,))
  self.assertFalse(any(x.event_type=="POST_DELIVERY_REVIEW" for x in r.events))
 def test_unregistered_type_fails_closed(self):
  s=[{"year":2030,"event_type":"MAGIC_HAPPENS","family":"MAGIC"}]
  with self.assertRaisesRegex(ValueError,"unregistered event type"): self.execute(seeds=s)
 def test_deterministic_replay(self):
  self.assertEqual(self.execute().canonical_sha256,self.execute().canonical_sha256)

if __name__=="__main__": unittest.main()
