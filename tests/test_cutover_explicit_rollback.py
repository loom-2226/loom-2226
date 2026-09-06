from loom.runtime import resolve_runtime_roots
from pathlib import Path
import unittest
class ExplicitRollback(unittest.TestCase):
 def test_explicit_legacy_root_remains_available(self):
  old='/storage/emulated/0/Download/LOOM_TEST';r=resolve_runtime_roots(app_root=old,campaign_root=old,env={'ANDROID_ROOT':'/system'})
  self.assertEqual(r.app_root,Path(old).resolve());self.assertEqual(r.campaign_root,Path(old).resolve())
if __name__=='__main__':unittest.main()
