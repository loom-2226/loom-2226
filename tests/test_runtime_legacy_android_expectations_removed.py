import unittest
from pathlib import Path
from loom.runtime import resolve_runtime_roots

class PostMigrationAuthorityTest(unittest.TestCase):
    def test_android_no_longer_defaults_campaign_to_app_or_app_to_cwd(self):
        roots=resolve_runtime_roots(env={'TERMUX_VERSION':'0.118'},cwd='/storage/emulated/0/Download/LOOM_TEST')
        self.assertEqual(roots.app_root,Path('/storage/emulated/0/Documents/LOOM/runtime').resolve())
        self.assertEqual(roots.campaign_root,Path('/storage/emulated/0/Documents/LOOM/campaign').resolve())
        self.assertNotEqual(roots.app_root,Path('/storage/emulated/0/Download/LOOM_TEST').resolve())
        self.assertNotEqual(roots.campaign_root,roots.app_root)

if __name__=='__main__':unittest.main()
