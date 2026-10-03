import json,unittest
from pathlib import Path
from engineering.civprop.contracts.actor_roster_audit_v0_3 import *
P=Path(__file__).resolve().parents[1]/"candidate_inputs"/"LOOM_GROUP_AGENT_SEED_2026_v0.3.json"
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with open(P) as f: cls.seed=json.load(f)
  cls.rows=classify(cls.seed); cls.by={x.actor_id:x for x in cls.rows}
 def test_all_233_classified(self): self.assertEqual((len(self.rows),len(self.by)),(233,233))
 def test_obvious_nonagents(self):
  for x in ("CAP_PUBLIC_EQUITY","CAP_STAR_MARKET","REG_ARTEMIS","INFRA_LUNANET","CERT_SEC_SK1300","SET_ANTARCTIC"):
   self.assertFalse(self.by[x].autonomous_eligible)
 def test_real_operators_remain_agents(self):
  for x in ("CAR_SPACEX","PRO_INTERLUNE","CAP_NBIM","INC_RIO","SUP_LOCKHEED","INFRA_KSAT"):
   self.assertTrue(self.by[x].autonomous_eligible)
 def test_historical_and_proposals_not_agents(self):
  for x in ("PRO_PLANETARY_RESOURCES","PRO_DEEP_SPACE_INDUSTRIES","CERT_LORS101","REG_EU_SPACE_ACT","SUP_ROCKETDYNE"):
   self.assertFalse(self.by[x].autonomous_eligible)
 def test_core_loop_has_competition(self):
  c=coverage(self.rows)
  for role in ("CAPITAL","DEMAND","RISK","TRANSPORT","PROJECT_DEVELOPMENT","MANUFACTURING","INFRASTRUCTURE","REGULATION","CERTIFICATION","INFORMATION"):
   self.assertGreaterEqual(len(c.get(role,())),3,(role,c.get(role)))
if __name__=="__main__":unittest.main()
