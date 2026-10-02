import copy,unittest
from engineering.civprop.contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03,commit_transaction
from engineering.civprop.contracts.gate_h_closed_loop_causality_v0_3 import run_closed_loop

def committed():
 s={"budgets":{"NASA":100.0},"provider_capacity":{"FIREFLY_AEROSPACE":1.0},"reservations":{},"projects":{},"future_events":[],"provenance_ledger":[],"committed_transaction_ids":[]}
 q=TransactionRequestV03("TX_A","CLPS_A","NASA","FIREFLY_AEROSPACE",70,1,"PROJECT_A",2029,"PROJECT_REVIEW",("AUTHORED_GATE_H_CONTROL",))
 out,r=commit_transaction(state=s,request=q); assert r.status=="COMMITTED"; return out

class GateH(unittest.TestCase):
 def test_gate_g_future_event_is_consumed_automatically(self):
  r=run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031)
  self.assertEqual(r.processed_years,(2029,2030)); self.assertEqual([x.event_type for x in r.events],["PROJECT_REVIEW","PROJECT_ACTIVATION"])
 def test_review_reads_committed_state_and_causes_child(self):
  r=run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031)
  self.assertEqual(r.events[0].status,"PASSED"); self.assertEqual(r.events[1].parent_ids,(r.events[0].event_id,))
 def test_closed_loop_mutates_project_state(self):
  r=run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031)
  self.assertEqual(r.final_state["projects"]["PROJECT_A"]["status"],"ACTIVE")
 def test_ablation_without_project_blocks_and_no_child(self):
  s=committed(); del s["projects"]["PROJECT_A"]
  r=run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
  self.assertEqual(len(r.events),1); self.assertEqual(r.events[0].reason_codes,("PROJECT_ABSENT",)); self.assertEqual(r.processed_years,(2029,))
 def test_ablation_without_reservation_blocks_and_no_child(self):
  s=committed(); s["reservations"].clear()
  r=run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
  self.assertEqual(len(r.events),1); self.assertEqual(r.events[0].reason_codes,("RESERVATION_ABSENT",))
 def test_ablation_uncommitted_project_blocks(self):
  s=committed(); s["projects"]["PROJECT_A"]["status"]="CANCELLED"
  r=run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
  self.assertEqual(r.events[0].reason_codes,("PROJECT_NOT_COMMITTED",))
 def test_activation_requires_prior_review_state_change(self):
  s=committed(); s["future_events"]=[{"event_id":"DIRECT","year":2030,"event_type":"PROJECT_ACTIVATION","project_id":"PROJECT_A","provenance_refs":["AUTHORED_GATE_H_CONTROL"]}]
  r=run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
  self.assertEqual(r.events[0].reason_codes,("ACTIVATION_NOT_AUTHORIZED",)); self.assertEqual(r.final_state["projects"]["PROJECT_A"]["status"],"COMMITTED")
 def test_missing_provenance_blocks(self):
  s=committed(); s["future_events"][0]["provenance_refs"]=[]
  r=run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
  self.assertEqual(r.events[0].reason_codes,("MISSING_PROVENANCE",))
 def test_out_of_window_child_does_not_execute(self):
  r=run_closed_loop(committed_state=committed(),start_year=2029,end_year=2029)
  self.assertEqual([x.event_type for x in r.events],["PROJECT_REVIEW"]); self.assertEqual(r.final_state["projects"]["PROJECT_A"]["status"],"ACTIVATION_AUTHORIZED")
 def test_only_relevant_actors_wake(self):
  r=run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031)
  self.assertTrue(all(set(x.actor_ids)<= {"NASA","FIREFLY_AEROSPACE"} for x in r.events))
 def test_deterministic_replay(self):
  self.assertEqual(run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031).canonical_sha256,
                   run_closed_loop(committed_state=committed(),start_year=2029,end_year=2031).canonical_sha256)
 def test_unregistered_event_fails_closed(self):
  s=committed(); s["future_events"][0]["event_type"]="MAGIC"
  with self.assertRaisesRegex(ValueError,"unregistered closed-loop"): run_closed_loop(committed_state=s,start_year=2029,end_year=2031)
if __name__=="__main__": unittest.main()
