from loom.runtime import resolve_runtime_roots
import unittest
class FinalGate(unittest.TestCase):
 def test_pixel_tuple(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp')
  self.assertEqual(tuple(map(str,(r.app_root,r.data_root,r.campaign_root))),('/storage/emulated/0/Documents/LOOM/runtime','/storage/emulated/0/Documents/LOOM/data','/storage/emulated/0/Documents/LOOM/campaign'))
if __name__=='__main__':unittest.main()
