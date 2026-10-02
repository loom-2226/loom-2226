import unittest
from engineering.civprop.contracts.shared_portfolio_competition_v0_3 import *
def o(i,k,c,p=1,e=True):
 return PortfolioOpportunityV03(i,k,c,e,p,("AUTHORED_PHASE9_MACHINERY_TEST",))
class SharedPortfolioTests(unittest.TestCase):
 def test_three_kinds_compete_for_one_budget(self):
  r=allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=10,
   opportunities=(o("M","MISSION",6,3),o("C","CERTIFICATION",4,2),o("P","PROJECT",5,1)))
  d={x.opportunity_id:x.action for x in r.decisions}
  self.assertEqual(d,{"M":"COMMIT","C":"COMMIT","P":"WAIT"}); self.assertEqual(r.ending_budget,0)
 def test_unknown_budget_commits_nothing(self):
  r=allocate_shared_portfolio(actor_id="A",budget_status="UNKNOWN",budget_value=None,
   opportunities=(o("M","MISSION",1),o("P","PROJECT",1),o("C","CERTIFICATION",1)))
  self.assertTrue(all(x.action=="WAIT" and x.reason_codes==("BUDGET_UNKNOWN",) for x in r.decisions))
 def test_ineligible_high_priority_does_not_consume_budget(self):
  r=allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=5,
   opportunities=(o("BAD","MISSION",5,99,False),o("GOOD","PROJECT",5,1)))
  d={x.opportunity_id:x for x in r.decisions}
  self.assertEqual(d["BAD"].action,"WAIT"); self.assertEqual(d["GOOD"].action,"COMMIT")
 def test_competition_changes_counterfactual_commit(self):
  alone=allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=6,
   opportunities=(o("P","PROJECT",6,1),))
  together=allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=6,
   opportunities=(o("M","MISSION",6,2),o("P","PROJECT",6,1)))
  self.assertEqual(alone.decisions[0].action,"COMMIT")
  self.assertEqual({x.opportunity_id:x.action for x in together.decisions}["P"],"WAIT")
 def test_no_hidden_free_budget(self):
  r=allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=7,
   opportunities=(o("M","MISSION",4,3),o("P","PROJECT",4,2),o("C","CERTIFICATION",3,1)))
  spent=sum(x.required_budget for x in r.decisions if x.action=="COMMIT")
  self.assertLessEqual(spent,r.starting_budget); self.assertAlmostEqual(r.ending_budget,r.starting_budget-spent)
 def test_bad_kind_and_missing_provenance_rejected(self):
  with self.assertRaises(ValueError):
   allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=1,
    opportunities=(o("X","MAGIC",1),))
  with self.assertRaises(ValueError):
   allocate_shared_portfolio(actor_id="A",budget_status="KNOWN",budget_value=1,
    opportunities=(PortfolioOpportunityV03("X","MISSION",1,True,1,()),))
if __name__=="__main__": unittest.main()
