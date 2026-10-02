from pathlib import Path
import json,unittest
from engineering.civprop.contracts.group_actor_integration_v0_3 import *
P=str(Path(__file__).resolve().parents[1] / "candidate_inputs" / "LOOM_GROUP_AGENT_SEED_2026_v0.3.json")
class GroupActorIntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with open(P) as f: cls.seed=json.load(f)
  cls.cats=compile_category_contracts(cls.seed)
  cls.actors=integrate_actor_candidates(cls.seed)
 def test_all_14_category_contracts_compile(self):
  self.assertEqual(len(self.cats),14)
  self.assertEqual(set(self.cats),set(self.seed["categories"]))
 def test_all_233_actor_candidates_integrate_once(self):
  self.assertEqual(len(self.actors),233)
  self.assertEqual(len({a.actor_id for a in self.actors}),233)
 def test_categories_remain_behaviorally_distinct(self):
  self.assertEqual(self.cats["CAPITAL"].engine_actor_type,"FINANCER")
  self.assertEqual(self.cats["CARRIER"].engine_actor_type,"TRANSPORT_OPERATOR")
  self.assertEqual(self.cats["CERTIFICATION"].engine_actor_type,"CERTIFIER_OR_CODE_BODY")
  self.assertNotEqual(self.cats["CAPITAL"].decline_codes,self.cats["CERTIFICATION"].decline_codes)
  self.assertNotEqual(self.cats["CARRIER"].belief_lag,self.cats["CERTIFICATION"].belief_lag)
 def test_seed_unknown_budgets_do_not_gain_spending_authority(self):
  self.assertTrue(all(a.budget_status=="UNKNOWN" for a in self.actors))
  self.assertFalse(any(actor_can_commit_budget(a) for a in self.actors))
 def test_decline_vocabulary_is_category_bounded(self):
  self.assertTrue(validate_decline_code(self.cats["CAPITAL"],"HURDLE_NOT_MET"))
  self.assertFalse(validate_decline_code(self.cats["CAPITAL"],"NO_CHAIN_OF_CUSTODY"))
  self.assertTrue(validate_decline_code(self.cats["CERTIFICATION"],"NO_CHAIN_OF_CUSTODY"))
 def test_integration_does_not_promote_seed_confidence_to_authority(self):
  verified=[a for a in self.actors if a.verified_by_search]
  self.assertGreater(len(verified),0)
  self.assertTrue(all(a.authority_class=="NON_CANON_2026_ACTOR_CANDIDATE" for a in verified))
if __name__=="__main__": unittest.main()
