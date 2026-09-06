import tempfile
import unittest
from pathlib import Path

from loom.runtime import export_runtime_environment, resolve_runtime_roots


class RuntimeRootsTest(unittest.TestCase):
    def test_explicit_roots_win(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(
                app_root=root / "app",
                data_root=root / "world",
                campaign_root=root / "campaign",
                env={"LOOM_APP_ROOT": "/wrong", "LOOM_HOME": "/also-wrong"},
                cwd=root,
            )
            self.assertEqual(roots.app_root, (root / "app").resolve())
            self.assertEqual(roots.data_root, (root / "world").resolve())
            self.assertEqual(roots.campaign_root, (root / "campaign").resolve())
            self.assertEqual(roots.app_source, "explicit")

    def test_dedicated_environment_precedes_loom_home(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(
                env={
                    "LOOM_APP_ROOT": str(root / "app"),
                    "LOOM_DATA_ROOT": str(root / "data"),
                    "LOOM_CAMPAIGN_ROOT": str(root / "campaign"),
                    "LOOM_HOME": str(root / "legacy"),
                },
                cwd=root,
            )
            self.assertEqual(roots.app_root, (root / "app").resolve())
            self.assertEqual(roots.data_root, (root / "data").resolve())
            self.assertEqual(roots.campaign_root, (root / "campaign").resolve())
            self.assertEqual(roots.app_source, "env:LOOM_APP_ROOT")

    def test_loom_home_compatibility_keeps_phase6_campaign_at_app_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            legacy = root / "LOOM_TEST"
            roots = resolve_runtime_roots(env={"LOOM_HOME": str(legacy)}, cwd=root)
            self.assertEqual(roots.app_root, legacy.resolve())
            self.assertEqual(roots.campaign_root, legacy.resolve())
            self.assertEqual(roots.campaign_source, "compat:app-root")

    def test_default_is_non_mutating_and_derived_from_cwd(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(env={}, cwd=root)
            self.assertEqual(roots.app_root, root.resolve())
            self.assertEqual(roots.data_root, (root / "data").resolve())
            self.assertEqual(roots.campaign_root, root.resolve())
            self.assertFalse((root / "data").exists())

    def test_injected_android_environment_selects_migrated_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(env={"ANDROID_ROOT": "/system"}, cwd=root)
            base = Path("/storage/emulated/0/Documents/LOOM")
            self.assertEqual(roots.app_root, (base / "runtime").resolve())
            self.assertEqual(roots.data_root, (base / "data").resolve())
            self.assertEqual(roots.campaign_root, (base / "campaign").resolve())
            self.assertEqual(roots.app_source, "default:android-runtime")
            self.assertEqual(roots.data_source, "default:android-documents")
            self.assertEqual(roots.campaign_source, "default:android-campaign")

    def test_empty_injected_environment_does_not_leak_process_android_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(env={}, cwd=root)
            self.assertEqual(roots.data_root, (root / "data").resolve())

    def test_export_sets_new_contract_and_legacy_home(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            roots = resolve_runtime_roots(
                app_root=root / "app",
                data_root=root / "data",
                campaign_root=root / "campaign",
                env={},
                cwd=root,
            )
            env = {}
            export_runtime_environment(roots, env=env)
            self.assertEqual(env["LOOM_APP_ROOT"], str((root / "app").resolve()))
            self.assertEqual(env["LOOM_DATA_ROOT"], str((root / "data").resolve()))
            self.assertEqual(env["LOOM_CAMPAIGN_ROOT"], str((root / "campaign").resolve()))
            self.assertEqual(env["LOOM_HOME"], env["LOOM_APP_ROOT"])


if __name__ == "__main__":
    unittest.main()
