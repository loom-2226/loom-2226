import json,unittest
from pathlib import Path
from engineering.civprop.contracts.gate_g_transactional_state_v0_3 import TransactionRequestV03
from engineering.civprop.method_lab.causal_runtime_v0_3 import run_migration_slice
class Migration(unittest.TestCase):
 def test_opt_in_slice_closes_f_through_j(self):
  b=json.loads((Path(__file__).parents[1]/"contracts/actor_machinery_test_baseline_v0_1.json").read_text())
  u=tuple(a["actor_id"] for a in b["actors"])
  opps=({"opportunity_id":"CLPS_A","provider_actor_id":"FIREFLY_AEROSPACE","kind":"PROJECT","required_budget":70.0,"priority":2.0,"provenance_refs":["MIGRATION_CONTROL"]},)
  s={"budgets":{"NASA":100.0},"provider_capacity":{"FIREFLY_AEROSPACE":1.0},"reservations":{},"projects":{},"future_events":[],"provenance_ledger":[],"committed_transaction_ids":[]}
  q={"CLPS_A":TransactionRequestV03("TX_M","CLPS_A","NASA","FIREFLY_AEROSPACE",70,1,"PROJECT_M",2029,"PROJECT_REVIEW",("MIGRATION_CONTROL",))}
  r=run_migration_slice(actor_universe=u,seed_edges=b["seed_edges"],opportunities=opps,budget_value=100,initial_state=s,request_by_opportunity=q,start_year=2029,end_year=2030,installed_capacity_by_project={"PROJECT_M":5})
  self.assertEqual(r.transaction_results[0].status,"COMMITTED")
  self.assertEqual(r.final_state["projects"]["PROJECT_M"]["status"],"ACTIVE")
  self.assertEqual(r.capacity_states[0].usable_capacity,5)
  self.assertEqual(r.endogenous_opportunities[0].status,"ELIGIBLE")
if __name__=="__main__": unittest.main()
