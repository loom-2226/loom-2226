import tempfile
from pathlib import Path
import unittest
from engineering.civprop.solar_bundle_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
class TestSolarReconAccessV03(unittest.TestCase):
 def test_every_compiled_characterization_destination_has_recon_service_for_every_actor(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td); build_bundle_dir(d); b=load_bundle(d); s=b.scenario
   qs={q.question_id for q in s.mission_knowledge_v1.questions if q.question_kind=='UNRESOLVED_CHARACTERIZATION'}
   dests={m.destination_location_id for m in s.mission_knowledge_v1.missions if m.target_question_id in qs}
   actors={a.actor_id for a in s.actors}
   paths={(x.actor_id,x.destination_location_id) for x in s.accessibility_v1.service_paths if x.mission_class=='ROBOTIC_RESOURCE_RECONNAISSANCE' and x.service_class=='GENERIC_LOGISTICS' and x.status=='UNKNOWN' and 'REQUIRED_TRANSPORT_TECHNOLOGY_UNKNOWN' in x.limiting_constraints}
   missing={(a,d) for a in actors for d in dests if (a,d) not in paths}
   self.assertFalse(missing)
if __name__=='__main__': unittest.main()
