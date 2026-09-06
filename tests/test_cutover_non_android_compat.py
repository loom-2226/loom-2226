from loom.runtime import resolve_runtime_roots
from pathlib import Path
import unittest
class NonAndroid(unittest.TestCase):
 def test_non_android_still_uses_cwd_compatibility(self):
  r=resolve_runtime_roots(env={},cwd='/tmp/loom');self.assertEqual(r.app_root,Path('/tmp/loom').resolve());self.assertEqual(r.campaign_root,r.app_root)
if __name__=='__main__':unittest.main()
