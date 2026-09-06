from loom.runtime import resolve_runtime_roots
import unittest
class CampaignSeparation(unittest.TestCase):
 def test_campaign_separate_from_application(self):
  r=resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp');self.assertNotEqual(r.campaign_root,r.app_root);self.assertEqual(r.campaign_root.parent,r.app_root.parent)
if __name__=='__main__':unittest.main()
