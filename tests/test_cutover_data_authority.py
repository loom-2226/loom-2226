from loom.runtime import resolve_runtime_roots
import unittest
class DataAuthority(unittest.TestCase):
 def test_data_authority(self):self.assertEqual(str(resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp').data_root),'/storage/emulated/0/Documents/LOOM/data')
if __name__=='__main__':unittest.main()
