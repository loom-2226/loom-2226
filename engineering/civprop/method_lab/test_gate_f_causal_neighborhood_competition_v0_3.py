import json,unittest
from pathlib import Path
from engineering.civprop.contracts.gate_f_causal_neighborhood_competition_v0_3 import derive_scoped_neighborhood,arbitrate_scoped_competition
P=Path(__file__).resolve().parents[1]/"contracts/actor_machinery_test_baseline_v0_1.json"
class GateF(unittest.TestCase):
 def setUp(self):
  self.b=json.loads(P.read_text()); self.u=tuple(a["actor_id"] for a in self.b["actors"]); self.edges=self.b["seed_edges"]
  self.opps=(
   {"opportunity_id":"CLPS_A","provider_actor_id":"FIREFLY_AEROSPACE","kind":"PROJECT","required_budget":70.0,"priority":2.0,"provenance_refs":["AUTHORED_GATE_F_CONTROL"]},
   {"opportunity_id":"CLPS_B","provider_actor_id":"INTUITIVE_MACHINES","kind":"PROJECT","required_budget":60.0,"priority":1.0,"provenance_refs":["AUTHORED_GATE_F_CONTROL"]})
 def execute(self,opps=None,budget=100.0,status="KNOWN"):
  return arbitrate_scoped_competition(trigger_actor_id="NASA",scope_token="CLPS",
   seed_edges=self.edges,actor_universe=self.u,opportunities=self.opps if opps is None else opps,
   budget_status=status,budget_value=budget)
 def test_neighborhood_derived_from_scoped_edges(self):
  n=derive_scoped_neighborhood(trigger_actor_id="NASA",scope_token="CLPS",seed_edges=self.edges,actor_universe=self.u)
  self.assertEqual(set(n.actor_ids),{"NASA","FIREFLY_AEROSPACE","INTUITIVE_MACHINES","ASTROBOTIC"})
  self.assertEqual(len(n.supporting_edges),3)
 def test_unrelated_hls_launch_edges_excluded(self):
  n=derive_scoped_neighborhood(trigger_actor_id="NASA",scope_token="CLPS",seed_edges=self.edges,actor_universe=self.u)
  self.assertNotIn("SPACEX",n.actor_ids); self.assertNotIn("BLUE_ORIGIN",n.actor_ids)
 def test_shared_budget_prevents_double_spend(self):
  r=self.execute(); self.assertEqual(r.winning_opportunity_ids,("CLPS_A",)); self.assertEqual(r.losing_opportunity_ids,("CLPS_B",))
  self.assertEqual(r.committed_budget,70.0); self.assertEqual(r.ending_budget,30.0)
  self.assertIn("INSUFFICIENT_SHARED_BUDGET",r.branches[1].reason_codes)
 def test_input_order_does_not_change_result(self):
  a=self.execute(); b=self.execute(opps=tuple(reversed(self.opps)))
  self.assertEqual(a.winning_opportunity_ids,b.winning_opportunity_ids); self.assertEqual(a.ending_budget,b.ending_budget)
 def test_priority_then_id_is_deterministic(self):
  opps=tuple(dict(x,priority=1.0,required_budget=60.0) for x in self.opps)
  r=self.execute(opps=opps,budget=60.0); self.assertEqual(r.winning_opportunity_ids,("CLPS_A",))
 def test_unknown_budget_commits_nothing(self):
  r=self.execute(status="UNKNOWN",budget=None); self.assertEqual(r.winning_opportunity_ids,()); self.assertIsNone(r.ending_budget)
  self.assertTrue(all("BUDGET_UNKNOWN" in x.reason_codes for x in r.branches))
 def test_outside_provider_rejected(self):
  bad=(dict(self.opps[0],provider_actor_id="SPACEX"),)
  with self.assertRaisesRegex(ValueError,"outside derived neighborhood"): self.execute(opps=bad)
 def test_missing_provenance_rejected(self):
  bad=(dict(self.opps[0],provenance_refs=[]),)
  with self.assertRaisesRegex(ValueError,"MISSING_OPPORTUNITY_PROVENANCE"): self.execute(opps=bad)
 def test_dormancy_is_derived(self):
  r=self.execute(); self.assertEqual(set(r.activated_actor_ids),{"NASA","FIREFLY_AEROSPACE","INTUITIVE_MACHINES","ASTROBOTIC"})
  self.assertEqual(set(r.dormant_actor_ids),set(self.u)-set(r.activated_actor_ids))
 def test_budget_conservation(self):
  r=self.execute(); self.assertAlmostEqual(r.committed_budget+r.ending_budget,100.0)
 def test_deterministic_replay(self):
  self.assertEqual(self.execute().canonical_sha256,self.execute().canonical_sha256)
if __name__=="__main__": unittest.main()
