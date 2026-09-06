from loom.runtime import resolve_runtime_roots
from pathlib import Path
import unittest
class Overrides(unittest.TestCase):
 def test_environment_override(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system','LOOM_APP_ROOT':'/x/a','LOOM_DATA_ROOT':'/x/d','LOOM_CAMPAIGN_ROOT':'/x/c'})
  self.assertEqual((r.app_root,r.data_root,r.campaign_root),(Path('/x/a').resolve(),Path('/x/d').resolve(),Path('/x/c').resolve()))
if __name__=='__main__':unittest.main()
