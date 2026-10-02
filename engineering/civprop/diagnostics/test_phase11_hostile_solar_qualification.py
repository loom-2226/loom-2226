import json,unittest
from pathlib import Path
from engineering.civprop.contracts.group_actor_integration_v0_3 import *
from engineering.civprop.contracts.shared_portfolio_competition_v0_3 import *
from engineering.civprop.contracts.knowledge_transmission_v0_3 import *
P=str(Path(__file__).resolve().parents[1] / "candidate_inputs" / "LOOM_GROUP_AGENT_SEED_2026_v0.3.json")
class HostileSolarQualificationV03(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with open(P) as f: cls.seed=json.load(f)
 def test_all_seed_budgets_unknown_and_nonspendable(self):
  actors=integrate_actor_candidates(self.seed)
  self.assertEqual(len(actors),233)
  self.assertTrue(all(a.budget_status=="UNKNOWN" and not actor_can_commit_budget(a) for a in actors))
 def test_unknown_budget_defeats_high_priority(self):
  o=PortfolioOpportunityV03("X","MISSION",1,True,10**12,("HOSTILE",))
  r=allocate_shared_portfolio(actor_id="A",opportunities=(o,),budget_status="UNKNOWN",budget_value=None)
  self.assertEqual(r.decisions[0].reason_codes,("BUDGET_UNKNOWN",))
 def test_information_channel_cannot_be_invented(self):
  class C: actor_id="A"; claim_id="C"
  with self.assertRaisesRegex(ValueError,"UNDECLARED_INFORMATION_CHANNEL"):
   transmit_claim(claim=C(),source_actor_id="A",recipient_actor_id="B",
    channel="GLOBAL_SHARED_KNOWLEDGE",lag_class="L0",visibility="PUBLIC",
    released_year=2100,delivery_authorized=True)
 def test_lag_cannot_be_bypassed_by_calendar(self):
  class C: actor_id="A"; claim_id="C"
  c=C(); t=transmit_claim(claim=c,source_actor_id="A",recipient_actor_id="B",
   channel="PUBLICATION",lag_class="L3",visibility="PUBLIC",released_year=2026,
   delivery_authorized=True)
  with self.assertRaisesRegex(PermissionError,"LAG_NOT_SATISFIED"):
   receive_claim(transmission=t,claim=c,lag_satisfied=False,received_year=2226)
 def test_gap016_and_gap014_still_declared_open(self):
  text="\n".join(p.read_text() for p in Path("engineering/civprop/diagnostics").glob("phase*_results_2026_10_02/*.md"))
  self.assertIn("GAP-016",text); self.assertIn("GAP-014",text)
 def test_no_phase_claims_promotion(self):
  for p in Path("engineering/civprop/diagnostics").glob("phase*_results_2026_10_02/*.md"):
   s=p.read_text()
   if "Phase " in s:
    self.assertTrue(("NON_CANON" in s or "NON-CANON" in s),str(p))
if __name__=="__main__": unittest.main()
