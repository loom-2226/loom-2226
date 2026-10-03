import json,unittest
from pathlib import Path
from .actor_activation_v0_3 import ActorRegistryV03
from .earth_actor_matching_v0_3 import activate_opportunity
from .bounded_proposition_v0_3 import run_proposition_cycle,PropositionDisposition
from .counterparty_recruitment_v0_3 import decompose_and_recruit,respond_to_requests,RecruitmentDisposition
from ..contracts.earth_opportunity_trigger_v0_3 import triggers
ROOT=Path(__file__).resolve().parents[3];CI=ROOT/'engineering/civprop/candidate_inputs'
def J(n):return json.loads((CI/n).read_text())
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=J('ACTOR_BASELINE_2026_V0_3.json');cls.audit=J('ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json')
  cls.j=J('ACTOR_JURISDICTION_2026_V0_3.json');cls.e=J('EARTH_COUNTRY_OPPORTUNITY_2026_V0_3.json')
 def cycle(self):
  reg=ActorRegistryV03.from_actor_baseline(self.base,self.audit)
  rows=[r for r in self.e['rows'] if r['iso3']=='AUS'];ts=triggers(rows)
  for t in ts:activate_opportunity(trigger=t,registry=reg,jurisdiction_links=self.j['links'])
  ds=run_proposition_cycle(registry=reg,triggers_by_id={t.context_id:t for t in ts},
      rows_by_context={f"EARTH:{r['year']}:{r['iso3']}:{r['sector']}":r for r in rows})
  # Deterministic real Earth-derived prospector proposition gives a rich dependency set.
  choices=[x for x in ds if x.disposition==PropositionDisposition.EXPLORE and
           reg.state(x.actor_id).identity.category=='PROSPECTOR']
  self.assertTrue(choices)
  dec=sorted(choices,key=lambda x:(x.proposition_id,x.context_id))[0]
  ident=reg.state(dec.actor_id).identity
  reqs=decompose_and_recruit(decision=dec,registry=reg,jurisdiction_links=self.j['links'],
      proposition_category=ident.category,iso3='AUS',sector=dec.context_id.rsplit(':',1)[-1],
      provenance_refs=('STEP_8A_FIRST_REAL_EARTH_TEST',))
  return reg,dec,reqs,respond_to_requests(registry=reg,requests=reqs)
 def test_recruits_multiple_distinct_roles(self):
  reg,dec,reqs,resps=self.cycle()
  self.assertGreaterEqual(len({x.target_category for x in reqs}),2)
  self.assertGreaterEqual(len({x.responder_actor_id for x in resps}),2)
 def test_requests_have_provenance_and_no_action_authority(self):
  reg,dec,reqs,resps=self.cycle()
  self.assertTrue(all(x.provenance_refs for x in reqs))
  recruited={a for x in reqs for a in x.candidate_actor_ids}
  self.assertTrue(recruited)
  self.assertTrue(all(not reg.may_emit_consequential_action(a) for a in recruited))
  self.assertTrue(all(x.semantics.endswith('NO_TRANSACTION_AUTHORITY') for x in reqs))
 def test_only_target_category_is_recruited(self):
  reg,dec,reqs,resps=self.cycle()
  for req in reqs:
   self.assertTrue(all(reg.state(a).identity.category==req.target_category for a in req.candidate_actor_ids))
   self.assertTrue(all(reg.state(a).identity.autonomous_eligible for a in req.candidate_actor_ids))
 def test_counterparties_make_bounded_exploratory_responses(self):
  reg,dec,reqs,resps=self.cycle()
  self.assertTrue(resps)
  self.assertIn(RecruitmentDisposition.ACCEPT_EXPLORATION,{x.disposition for x in resps})
  self.assertTrue(all(not reg.may_emit_consequential_action(x.responder_actor_id) for x in resps))
  self.assertTrue(all(x.semantics.endswith('NO_CONTRACT_OR_PROJECT_AUTHORITY') for x in resps))
 def test_deterministic(self):
  _,d1,q1,r1=self.cycle();_,d2,q2,r2=self.cycle()
  self.assertEqual(d1,d2);self.assertEqual(q1,q2);self.assertEqual(r1,r2)
if __name__=='__main__':unittest.main()
