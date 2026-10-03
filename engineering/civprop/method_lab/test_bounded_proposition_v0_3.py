import json,unittest
from pathlib import Path
from .actor_activation_v0_3 import ActorRegistryV03
from .earth_actor_matching_v0_3 import activate_opportunity
from .bounded_proposition_v0_3 import run_proposition_cycle,PropositionDisposition
from ..contracts.earth_opportunity_trigger_v0_3 import triggers
ROOT=Path(__file__).resolve().parents[3];CI=ROOT/'engineering/civprop/candidate_inputs'
def J(n):return json.loads((CI/n).read_text())
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=J('ACTOR_BASELINE_2026_V0_3.json');cls.audit=J('ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json')
  cls.j=J('ACTOR_JURISDICTION_2026_V0_3.json');cls.e=J('EARTH_COUNTRY_OPPORTUNITY_2026_V0_3.json')
 def run_aus(self):
  reg=ActorRegistryV03.from_actor_baseline(self.base,self.audit)
  rows=[r for r in self.e['rows'] if r['iso3']=='AUS'];ts=triggers(rows)
  for t in ts:activate_opportunity(trigger=t,registry=reg,jurisdiction_links=self.j['links'])
  tb={t.context_id:t for t in ts};rb={f"EARTH:{r['year']}:{r['iso3']}:{r['sector']}":r for r in rows}
  return reg,run_proposition_cycle(registry=reg,triggers_by_id=tb,rows_by_context=rb)
 def test_first_real_earth_cycle_forms_exploration(self):
  reg,ds=self.run_aus();self.assertTrue(ds)
  self.assertIn(PropositionDisposition.EXPLORE,{x.disposition for x in ds})
 def test_portfolio_competition_defers_viable_proposition(self):
  reg,ds=self.run_aus();self.assertIn(PropositionDisposition.DEFER,{x.disposition for x in ds})
  by={}
  for x in ds:by.setdefault(x.actor_id,[]).append(x)
  self.assertTrue(any({z.disposition for z in xs}>={PropositionDisposition.EXPLORE,PropositionDisposition.DEFER} for xs in by.values()))
 def test_no_transactional_authority(self):
  reg,ds=self.run_aus()
  self.assertTrue(all(not reg.may_emit_consequential_action(x.actor_id) for x in ds))
  self.assertTrue(all(x.semantics=='EXPLORATORY_INTENT_ONLY_NO_TRANSACTION_OR_PROJECT_AUTHORITY' for x in ds))
 def test_deterministic(self):
  _,a=self.run_aus();_,b=self.run_aus();self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
