import json,unittest
from pathlib import Path
from .actor_activation_v0_3 import ActorRegistryV03
from .earth_actor_matching_v0_3 import match_opportunity,activate_opportunity
from ..contracts.earth_opportunity_trigger_v0_3 import triggers
ROOT=Path(__file__).resolve().parents[3]
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  ci=ROOT/'engineering/civprop/candidate_inputs'
  cls.base=json.loads((ci/'ACTOR_BASELINE_2026_V0_3.json').read_text())
  cls.audit=json.loads((ci/'ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json').read_text())
  cls.j=json.loads((ci/'ACTOR_JURISDICTION_2026_V0_3.json').read_text())
  cls.e=json.loads((ci/'EARTH_COUNTRY_OPPORTUNITY_2026_V0_3.json').read_text())
  cls.reg=ActorRegistryV03.from_actor_baseline(cls.base,cls.audit)
 def test_all_80_have_matchable_contexts(self):
  ts=triggers(self.e['rows']); by={}
  for t in ts:
   m=match_opportunity(trigger=t,registry=self.reg,jurisdiction_links=self.j['links'])
   by.setdefault(t.iso3,0);by[t.iso3]+=bool(m.actor_ids)
  self.assertEqual(len(by),80);self.assertTrue(all(v==10 for v in by.values()))
 def test_small_neighborhood(self):
  for t in triggers(self.e['rows']):
   m=match_opportunity(trigger=t,registry=self.reg,jurisdiction_links=self.j['links'])
   self.assertLess(len(m.actor_ids),80)
 def test_no_authority_semantic(self):
  t=triggers(self.e['rows'])[0];m=match_opportunity(trigger=t,registry=self.reg,jurisdiction_links=self.j['links'])
  self.assertEqual(m.semantics,'RELEVANCE_ONLY_NO_TRANSACTION_AUTHORITY')
 def test_activation_is_relevance_only(self):
  reg=ActorRegistryV03.from_actor_baseline(self.base,self.audit)
  t=triggers(self.e['rows'])[0];m=activate_opportunity(trigger=t,registry=reg,jurisdiction_links=self.j['links'])
  self.assertTrue(m.actor_ids)
  self.assertTrue(all(reg.state(a).level.value=='RELEVANT' for a in m.actor_ids))
  self.assertTrue(all(not reg.may_emit_consequential_action(a) for a in m.actor_ids))
if __name__=='__main__':unittest.main()
