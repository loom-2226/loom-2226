from loom.runtime import resolve_runtime_roots
import unittest
class CampaignAuthority(unittest.TestCase):
 def test_campaign_authority(self):self.assertEqual(str(resolve_runtime_roots(env={'ANDROID_ROOT':'/system'},cwd='/tmp').campaign_root),'/storage/emulated/0/Documents/LOOM/campaign')
if __name__=='__main__':unittest.main()
