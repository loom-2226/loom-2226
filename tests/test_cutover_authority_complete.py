from pathlib import Path
import unittest
from loom.runtime import resolve_runtime_roots
A=Path('/storage/emulated/0/Documents/LOOM')
class CompleteCutoverAuthority(unittest.TestCase):
 def test_termux_defaults_ignore_legacy_cwd(self):
  r=resolve_runtime_roots(env={'TERMUX_VERSION':'x'},cwd='/storage/emulated/0/Download/LOOM_TEST')
  self.assertEqual((r.app_root,r.data_root,r.campaign_root),((A/'runtime').resolve(),(A/'data').resolve(),(A/'campaign').resolve()))
if __name__=='__main__':unittest.main()
