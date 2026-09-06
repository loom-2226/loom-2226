from pathlib import Path
import unittest
from loom.runtime import resolve_runtime_roots
ANDROID=Path('/storage/emulated/0/Documents/LOOM')
class CutoverV2Test(unittest.TestCase):
 def test_android_resolver_defaults(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp/old')
  self.assertEqual(r.app_root,(ANDROID/'runtime').resolve());self.assertEqual(r.data_root,(ANDROID/'data').resolve());self.assertEqual(r.campaign_root,(ANDROID/'campaign').resolve())
if __name__=='__main__':unittest.main()
