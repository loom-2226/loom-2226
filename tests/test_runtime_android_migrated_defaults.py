from pathlib import Path
import unittest
from loom.runtime import resolve_runtime_roots

ANDROID = Path('/storage/emulated/0/Documents/LOOM')

class MigratedAndroidDefaultsTest(unittest.TestCase):
    def test_android_defaults_are_migrated_authority(self):
        roots = resolve_runtime_roots(env={'ANDROID_ROOT': '/system'}, cwd='/tmp/irrelevant')
        self.assertEqual(roots.app_root, (ANDROID / 'runtime').resolve())
        self.assertEqual(roots.data_root, (ANDROID / 'data').resolve())
        self.assertEqual(roots.campaign_root, (ANDROID / 'campaign').resolve())
        self.assertEqual(roots.app_source, 'default:android-runtime')
        self.assertEqual(roots.campaign_source, 'default:android-campaign')

if __name__ == '__main__':
    unittest.main()
