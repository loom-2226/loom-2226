import json,tempfile,unittest
from pathlib import Path
from engineering.civprop.long_run_integration_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
class T(unittest.TestCase):
 def test_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td); build_bundle_dir(p); b=load_bundle(p); ids={x.location_id for x in b.scenario.locations}; self.assertIn('MARS_ORBIT',ids); self.assertIn('CERES_ORBIT',ids); sv=[x for x in b.scenario.accessibility_v1.service_paths if x.service_id.startswith('PLACEHOLDER_SOLARV03::')]; self.assertTrue(sv); self.assertTrue(all(x.status=='FEASIBLE' for x in sv))
 def test_gaps(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td); build_bundle_dir(p); g=json.loads((p/'compiler_manifest_v1.json').read_text())['gap_resolution']; self.assertEqual([g[x] for x in ('GAP-014','GAP-015','GAP-016')],['OPEN']*3)
