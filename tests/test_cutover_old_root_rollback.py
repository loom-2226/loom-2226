from loom.runtime import resolve_runtime_roots
import unittest
class Rollback(unittest.TestCase):
 def test_old_root_can_be_explicit(self):
  old='/storage/emulated/0/Download/LOOM_TEST';r=resolve_runtime_roots(app_root=old,campaign_root=old,data_root='/storage/emulated/0/Documents/LOOM/data',env={'ANDROID_ROOT':'/system'});self.assertEqual(str(r.app_root),old);self.assertEqual(str(r.campaign_root),old)
if __name__=='__main__':unittest.main()
