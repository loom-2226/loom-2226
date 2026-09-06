from loom.runtime import resolve_runtime_roots
import unittest
class NoLegacyAuthority(unittest.TestCase):
 def test_old_download_root_is_not_default_authority(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/storage/emulated/0/Download/LOOM_TEST')
  self.assertNotIn('/Download/LOOM_TEST',str(r.app_root));self.assertNotIn('/Download/LOOM_TEST',str(r.campaign_root))
if __name__=='__main__':unittest.main()
