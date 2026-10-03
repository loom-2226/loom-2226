import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  ci=ROOT/'engineering/civprop/candidate_inputs'
  cls.j=json.loads((ci/'ACTOR_JURISDICTION_2026_V0_3.json').read_text());cls.a=json.loads((ci/'ACTOR_ROSTER_EXECUTION_ONTOLOGY_V0_3.json').read_text())
 def test_all_autonomous_have_link(self):
  mapped={x['actor_id'] for x in self.j['links']}; auto={x['actor_id'] for x in self.a['nodes'] if x['autonomous_eligible']}
  self.assertFalse(auto-mapped)
 def test_relation_typed(self):
  self.assertTrue(all(x['relation'] in {'HOME','OPERATING_OR_INSTITUTIONAL_LINK','MULTINATIONAL'} for x in self.j['links']))
if __name__=='__main__':unittest.main()
