from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANDROID = Path('/storage/emulated/0/Documents/LOOM')


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


class RuntimeCutoverContractTest(unittest.TestCase):
    def test_runtime_resolver_accepts_cutover_roots(self):
        runtime = load_module('src/loom/runtime.py', 'loom_runtime_cutover_test')
        roots = runtime.resolve_runtime_roots(
            env={
                'LOOM_APP_ROOT': str(ANDROID / 'runtime'),
                'LOOM_DATA_ROOT': str(ANDROID / 'data'),
                'LOOM_CAMPAIGN_ROOT': str(ANDROID / 'campaign'),
                'ANDROID_ROOT': '/system',
            }
        )
        self.assertEqual(roots.app_root, (ANDROID / 'runtime').resolve())
        self.assertEqual(roots.data_root, (ANDROID / 'data').resolve())
        self.assertEqual(roots.campaign_root, (ANDROID / 'campaign').resolve())

    def test_updater_android_defaults_match_cutover_roots(self):
        updater = load_module('deploy/loom_update.py', 'loom_update_cutover_test')
        roots = updater.platform_roots(environ={'ANDROID_ROOT': '/system'})
        self.assertEqual(roots.app_root, (ANDROID / 'runtime').resolve())
        self.assertEqual(roots.data_root, (ANDROID / 'data').resolve())

    def test_migration_activation_contract_matches_launchers(self):
        migrate = load_module('deploy/loom_migrate.py', 'loom_migrate_cutover_test')
        self.assertEqual(migrate.ACTIVATION_CONTRACT, 'LOOM_RUNTIME_ROOTS_ACTIVATION_V1')
        target = ANDROID
        expected = {
            'app_root': str((target / 'runtime').resolve()),
            'data_root': str((target / 'data').resolve()),
            'campaign_root': str((target / 'campaign').resolve()),
        }
        self.assertEqual(expected['app_root'], '/storage/emulated/0/Documents/LOOM/runtime')
        self.assertEqual(expected['data_root'], '/storage/emulated/0/Documents/LOOM/data')
        self.assertEqual(expected['campaign_root'], '/storage/emulated/0/Documents/LOOM/campaign')


if __name__ == '__main__':
    unittest.main()
