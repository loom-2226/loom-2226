import tempfile
from pathlib import Path
import unittest
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
class TestSolarBundleMissionKnowledgeV03(unittest.TestCase):
 def test_qualified_catalog_compiles_without_priors_or_binary_models(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); b=load_bundle(d); p=b.scenario.mission_knowledge_v1
   chars=[q for q in p.questions if q.question_kind=='UNRESOLVED_CHARACTERIZATION']
   self.assertEqual(len(chars),344)
   self.assertTrue(all(q.prior_probability is None for q in chars))
   ids={q.question_id for q in chars}; missions=[m for m in p.missions if m.target_question_id in ids]
   self.assertEqual(len(missions),344); self.assertTrue(all(m.observation_model_id is None for m in missions))
   dms=[x for x in p.decision_models if x.mission_archetype_id in {m.mission_archetype_id for m in missions}]
   self.assertEqual(len(dms),344); self.assertTrue(all(x.model_kind=='AUTHORED_EXPLORATION_PRIORITY_V1' for x in dms)); self.assertTrue(all(x.success_value.value is None for x in dms))
if __name__=='__main__': unittest.main()
