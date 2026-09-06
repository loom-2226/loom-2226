from loom.runtime import resolve_runtime_roots
import unittest
class Sources(unittest.TestCase):
 def test_sources(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp')
  self.assertEqual((r.app_source,r.data_source,r.campaign_source),('default:android-runtime','default:android-documents','default:android-campaign'))
if __name__=='__main__':unittest.main()
