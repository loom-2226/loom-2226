import copy,json,tempfile
from pathlib import Path
import unittest
from engineering.civprop.long_run_integration_v0_2 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
ROOT=Path(__file__).resolve().parents[3]
class TestMissionKnowledgeV11Validator(unittest.TestCase):
 def test_characterization_does_not_require_resource_belief(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); p=d/'scenario_v1.json'; s=json.loads(p.read_text())
   q=copy.deepcopy(s['mission_knowledge_v1']['questions'][0]); q.update(question_id='TEST_CHARACTERIZATION',question_kind='UNRESOLVED_CHARACTERIZATION',subject_id='TEST::MARS::VOLATILES',location_id='LUNA_SURFACE',prior_probability=None,prior_status='NOT_AUTHORIZED')
   m=copy.deepcopy(s['mission_knowledge_v1']['missions'][0]); m.update(mission_archetype_id='TEST_CHARACTERIZATION_MISSION',target_question_id=q['question_id'],observation_model_id=None)
   dm=copy.deepcopy(s['mission_knowledge_v1']['decision_models'][0]); dm.update(decision_model_id='TEST_CHARACTERIZATION_DECISION',mission_archetype_id=m['mission_archetype_id'],model_kind='AUTHORED_EXPLORATION_PRIORITY_V1')
   s['mission_knowledge_v1']['contract_version']='1.1.0'; s['mission_knowledge_v1']['questions'].append(q); s['mission_knowledge_v1']['missions'].append(m); s['mission_knowledge_v1']['decision_models'].append(dm)
   p.write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
   man=json.loads((d/'manifest_v1.json').read_text()); import hashlib; man['sha256']['scenario_v1.json']=hashlib.sha256(p.read_bytes()).hexdigest(); man['bundle_sha256']=hashlib.sha256(p.read_bytes()+b'\n'+(d/'truth_v1.json').read_bytes()).hexdigest(); (d/'manifest_v1.json').write_text(json.dumps(man,indent=2,sort_keys=True)+'\n')
   # Loader/validator must not demand a fabricated resource belief for the new question.
   load_bundle(d)
if __name__=='__main__': unittest.main()
