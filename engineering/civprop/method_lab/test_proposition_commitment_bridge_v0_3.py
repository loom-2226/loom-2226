import unittest
from .proposition_commitment_bridge_v0_3 import *
from ..contracts.gate_h_closed_loop_causality_v0_3 import run_closed_loop

REF=("AUTHORED_STEP_8B_POSITIVE_QUALIFICATION_CONTROL",)
def auths():
 return tuple(known(x,*REF) for x in REQUIRED_AUTHORITIES)
def prop(authorities=None):
 return AssembledPropositionV03("PROP_CONTROL","BUYER","PROVIDER",40.0,1.0,
   auths() if authorities is None else authorities,("INSURER","CERTIFIER","CARRIER"),REF)
def state():
 return {"budgets":{"BUYER":100.0},"provider_capacity":{"PROVIDER":2.0},"reservations":{},
         "projects":{},"future_events":[],"provenance_ledger":[],"committed_transaction_ids":[]}

class T(unittest.TestCase):
 def test_positive_control_commits_through_gate_g_and_changes_downstream_state(self):
  out,r=commit_assembled_proposition(state=state(),proposition=prop(),project_id="PROJECT_CONTROL",commit_year=2027)
  self.assertEqual(r.feasibility.status,"FEASIBLE");self.assertEqual(r.transaction_status,"COMMITTED")
  self.assertEqual(out["projects"]["PROJECT_CONTROL"]["status"],"COMMITTED")
  loop=run_closed_loop(committed_state=out,start_year=2027,end_year=2028)
  self.assertEqual(loop.final_state["projects"]["PROJECT_CONTROL"]["status"],"ACTIVE")
  self.assertEqual([x.status for x in loop.events],["PASSED","STATE_CHANGED"])
 def test_unknown_authority_blocks_before_gate_g_without_state_mutation(self):
  aa=list(auths());aa[3]=unknown("TRANSPORT_FEASIBILITY","AUTHORED_UNKNOWN_CONTROL")
  before=state();out,r=commit_assembled_proposition(state=before,proposition=prop(tuple(aa)),project_id="P",commit_year=2027)
  self.assertEqual(r.transaction_status,"NOT_ATTEMPTED");self.assertIn("TRANSPORT_FEASIBILITY_UNKNOWN",r.transaction_reason_codes)
  self.assertEqual(out,before);self.assertNotIn("P",out["projects"])
 def test_unsatisfied_authority_blocks_before_gate_g(self):
  aa=list(auths());aa[5]=FeasibilityAuthorityV03("CERTIFICATION",AuthorityStatus.KNOWN,False,("AUTHORED_NEGATIVE_CONTROL",))
  out,r=commit_assembled_proposition(state=state(),proposition=prop(tuple(aa)),project_id="P",commit_year=2027)
  self.assertEqual(r.transaction_status,"NOT_ATTEMPTED");self.assertIn("CERTIFICATION_UNSATISFIED",r.transaction_reason_codes)
 def test_gate_g_still_independently_blocks_unknown_budget(self):
  s=state();s["budgets"]={}
  out,r=commit_assembled_proposition(state=s,proposition=prop(),project_id="P",commit_year=2027)
  self.assertEqual(r.feasibility.status,"FEASIBLE");self.assertEqual(r.transaction_status,"ROLLED_BACK")
  self.assertEqual(r.transaction_reason_codes,("BUDGET_UNKNOWN",));self.assertEqual(out,s)
 def test_real_exploratory_actor_capacity_is_not_spendable_budget(self):
  class I: actor_id="PRO_HONEYBEE"; estimate_status="DERIVED_ESTIMATED"
  class D: proposition_id="PROP:PRO_HONEYBEE:EARTH:2026:AUS:BULK_MATERIALS"; context_id="EARTH:2026:AUS:BULK_MATERIALS"
  p=assemble_from_exploratory_responses(decision=D(),origin_identity=I(),responses=(),required_budget=1.0)
  f=assess_feasibility(p)
  self.assertEqual(f.status,"BLOCKED");self.assertIn("SPENDABLE_BUDGET_UNKNOWN",f.reason_codes)
  self.assertTrue(all(x.status==AuthorityStatus.UNKNOWN for x in p.authorities))
 def test_deterministic(self):
  a=commit_assembled_proposition(state=state(),proposition=prop(),project_id="P",commit_year=2027)
  b=commit_assembled_proposition(state=state(),proposition=prop(),project_id="P",commit_year=2027)
  self.assertEqual(a,b)
if __name__=="__main__":unittest.main()
