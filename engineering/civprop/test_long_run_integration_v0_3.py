import tempfile,unittest
from pathlib import Path
from engineering.civprop.long_run_integration_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
class T(unittest.TestCase):
 def test_compatibility_entry_builds_valid_bundle(self):
  with tempfile.TemporaryDirectory() as td:
   b=load_bundle(build_bundle_dir(Path(td))); self.assertEqual((b.scenario.start_year,b.scenario.end_year),(2026,2226))
