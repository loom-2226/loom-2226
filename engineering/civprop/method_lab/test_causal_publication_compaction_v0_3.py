import unittest
from types import SimpleNamespace
from engineering.civprop.method_lab.causal_world_v0_3 import apply_causal_publication_semantics

class CausalPublicationCompactionV03Tests(unittest.TestCase):
 def test_earth_unowned_fields_fail_closed(self):
  b=SimpleNamespace(scenario=SimpleNamespace(demographic_authority_v1={'active':True}))
  p={'annual_states':[{'year':2100,'location_id':'EARTH_SURFACE','biological_population':7.0,'workforce':2.0,'capacities':{'habitat':8.0,'power':1.0}},
                      {'year':2100,'location_id':'LUNA_SURFACE','biological_population':0.0,'workforce':0.0,'capacities':{'habitat':0.0}}]}
  out=apply_causal_publication_semantics(p,b)
  e=out['annual_states'][0]; l=out['annual_states'][1]
  self.assertIsNone(e['workforce']); self.assertIsNone(e['capacities']['habitat'])
  self.assertEqual(e['capacities']['power'],1.0)
  self.assertEqual(e['state_authority']['biological_population'],'EARTH_PROMOTED_DEMOGRAPHIC_AUTHORITY')
  self.assertEqual(l['workforce'],0.0); self.assertNotIn('state_authority',l)

 def test_no_authority_no_rewrite(self):
  b=SimpleNamespace(scenario=SimpleNamespace(demographic_authority_v1=None))
  p={'annual_states':[{'location_id':'EARTH_SURFACE','workforce':2.0,'capacities':{'habitat':8.0}}]}
  self.assertEqual(apply_causal_publication_semantics(p,b)['annual_states'][0]['workforce'],2.0)

if __name__=='__main__': unittest.main()
