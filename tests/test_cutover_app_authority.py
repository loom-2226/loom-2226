from loom.runtime import resolve_runtime_roots
import unittest
class AppAuthority(unittest.TestCase):
 def test_app_authority(self):self.assertEqual(str(resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp').app_root),'/storage/emulated/0/Documents/LOOM/runtime')
if __name__=='__main__':unittest.main()
