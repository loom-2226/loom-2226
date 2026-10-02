from pathlib import Path
import copy,unittest
from engineering.civprop.contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03,commit_transaction,state_sha256,commit_winning_branches

def state():
 return {"budgets":{"NASA":100.0},"provider_capacity":{"FIREFLY_AEROSPACE":1.0,"INTUITIVE_MACHINES":1.0},
  "reservations":{},"projects":{},"future_events":[],"provenance_ledger":[],"committed_transaction_ids":[]}
def req(provider="FIREFLY_AEROSPACE",oid="CLPS_A",tid="TX_A",project="PROJECT_A",budget=70.0,cap=1.0):
 return TransactionRequestV03(tid,oid,"NASA",provider,budget,cap,project,2029,"PROJECT_REVIEW",("AUTHORED_GATE_G_CONTROL",))

class GateG(unittest.TestCase):
 def test_atomic_commit_changes_all_ledgers(self):
  s,r=commit_transaction(state=state(),request=req()); self.assertEqual(r.status,"COMMITTED")
  self.assertEqual(s["budgets"]["NASA"],30.0); self.assertEqual(s["provider_capacity"]["FIREFLY_AEROSPACE"],0.0)
  self.assertIn("TX_A",s["reservations"]); self.assertIn("PROJECT_A",s["projects"])
  self.assertEqual(len(s["future_events"]),1); self.assertEqual(len(s["provenance_ledger"]),1)
 def test_every_injected_partial_failure_rolls_back_byte_equivalent_state(self):
  for point in ("AFTER_BUDGET","AFTER_RESERVATION","AFTER_PROJECT","AFTER_EVENT","AFTER_PROVENANCE"):
   with self.subTest(point=point):
    original=state(); s,r=commit_transaction(state=original,request=req(),inject_failure_at=point)
    self.assertEqual(r.status,"ROLLED_BACK"); self.assertEqual(state_sha256(s),state_sha256(original)); self.assertEqual(r.pre_state_sha256,r.post_state_sha256)
 def test_insufficient_budget_rolls_back(self):
  s0=state(); s,r=commit_transaction(state=s0,request=req(budget=101)); self.assertEqual(r.reason_codes,("INSUFFICIENT_BUDGET",)); self.assertEqual(s,s0)
 def test_insufficient_capacity_rolls_back(self):
  s0=state(); s,r=commit_transaction(state=s0,request=req(cap=2)); self.assertEqual(r.reason_codes,("INSUFFICIENT_PROVIDER_CAPACITY",)); self.assertEqual(s,s0)
 def test_unknown_capacity_rolls_back(self):
  s0=state(); del s0["provider_capacity"]["FIREFLY_AEROSPACE"]; s,r=commit_transaction(state=s0,request=req()); self.assertEqual(r.reason_codes,("PROVIDER_CAPACITY_UNKNOWN",)); self.assertEqual(s,s0)
 def test_missing_provenance_rolls_back(self):
  q=req(); q=TransactionRequestV03(q.transaction_id,q.opportunity_id,q.customer_actor_id,
   q.provider_actor_id,q.required_budget,q.provider_capacity_units,q.project_id,
   q.future_event_year,q.future_event_type,())
  s0=state(); s,r=commit_transaction(state=s0,request=q); self.assertEqual(r.reason_codes,("MISSING_PROVENANCE",)); self.assertEqual(s,s0)
 def test_duplicate_transaction_cannot_double_spend(self):
  s,r1=commit_transaction(state=state(),request=req()); snap=copy.deepcopy(s)
  s2,r2=commit_transaction(state=s,request=req()); self.assertEqual(r2.reason_codes,("DUPLICATE_TRANSACTION",)); self.assertEqual(s2,snap)
 def test_project_collision_rolls_back_everything(self):
  s0=state(); s0["projects"]["PROJECT_A"]={"status":"EXISTING"}; s,r=commit_transaction(state=s0,request=req())
  self.assertEqual(r.status,"ROLLED_BACK"); self.assertEqual(s,s0)
 def test_future_event_has_transaction_parent_and_provenance(self):
  s,r=commit_transaction(state=state(),request=req()); e=s["future_events"][0]
  self.assertEqual(e["parent_transaction_id"],"TX_A"); self.assertEqual(e["provenance_refs"],["AUTHORED_GATE_G_CONTROL"])
 def test_only_gate_f_winner_commits(self):
  branches=({"opportunity_id":"CLPS_A","action":"COMMIT"},{"opportunity_id":"CLPS_B","action":"WAIT"})
  requests={"CLPS_A":req(),"CLPS_B":req(provider="INTUITIVE_MACHINES",oid="CLPS_B",tid="TX_B",project="PROJECT_B",budget=60)}
  s,rs=commit_winning_branches(state=state(),branches=branches,request_by_opportunity=requests)
  self.assertEqual(len(rs),1); self.assertIn("PROJECT_A",s["projects"]); self.assertNotIn("PROJECT_B",s["projects"])
  self.assertEqual(s["provider_capacity"]["INTUITIVE_MACHINES"],1.0)
 def test_gate_f_real_arbitration_drives_only_winner_transaction(self):
  import json
  from engineering.civprop.contracts.gate_f_causal_neighborhood_competition_v0_3 import arbitrate_scoped_competition
  p=Path(__file__).resolve().parents[1]/"contracts/actor_machinery_test_baseline_v0_1.json"
  b=json.loads(p.read_text()); u=tuple(a["actor_id"] for a in b["actors"])
  opps=(
   {"opportunity_id":"CLPS_A","provider_actor_id":"FIREFLY_AEROSPACE","kind":"PROJECT","required_budget":70.0,"priority":2.0,"provenance_refs":["AUTHORED_GATE_G_CONTROL"]},
   {"opportunity_id":"CLPS_B","provider_actor_id":"INTUITIVE_MACHINES","kind":"PROJECT","required_budget":60.0,"priority":1.0,"provenance_refs":["AUTHORED_GATE_G_CONTROL"]})
  f=arbitrate_scoped_competition(trigger_actor_id="NASA",scope_token="CLPS",seed_edges=b["seed_edges"],
    actor_universe=u,opportunities=opps,budget_status="KNOWN",budget_value=100.0)
  branches=tuple({"opportunity_id":x.opportunity_id,"action":x.action} for x in f.branches)
  requests={"CLPS_A":req(),"CLPS_B":req(provider="INTUITIVE_MACHINES",oid="CLPS_B",tid="TX_B",project="PROJECT_B",budget=60)}
  s,rs=commit_winning_branches(state=state(),branches=branches,request_by_opportunity=requests)
  self.assertEqual(f.winning_opportunity_ids,("CLPS_A",)); self.assertEqual(len(rs),1)
  self.assertEqual(s["budgets"]["NASA"],30.0); self.assertEqual(s["provider_capacity"]["FIREFLY_AEROSPACE"],0.0)
  self.assertEqual(s["provider_capacity"]["INTUITIVE_MACHINES"],1.0); self.assertNotIn("PROJECT_B",s["projects"])
 def test_deterministic_commit_hash(self):
  a,ra=commit_transaction(state=state(),request=req()); b,rb=commit_transaction(state=state(),request=req())
  self.assertEqual(ra.post_state_sha256,rb.post_state_sha256); self.assertEqual(a,b)
if __name__=="__main__": unittest.main()
