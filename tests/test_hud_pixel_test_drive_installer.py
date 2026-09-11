import ast
import unittest

from loom.hud import server


class HudPixelTestDriveInstallerTests(unittest.TestCase):
    def _source(self):
        return (
            server.repo_root() / "deploy" / "android" / "install_hud_test_drive.py"
        ).read_text(encoding="utf-8")

    def test_installer_is_hud_qualification_only(self):
        source = self._source()
        self.assertIn("HUD_TEST_DRIVE_ONLY", source)
        self.assertIn("feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11", source)
        self.assertNotIn("LOOM_CAMPAIGN_ROOT", source)
        self.assertNotIn("LOOM_DATA_ROOT", source)
        self.assertNotIn("campaign/", source)
        self.assertNotIn("data/LOOM_2226", source)

    def test_allowlist_contains_only_expected_runtime_prefixes(self):
        tree = ast.parse(self._source())
        allowlist = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "FILES":
                        allowlist = ast.literal_eval(node.value)
        self.assertIsNotNone(allowlist)
        self.assertGreater(len(allowlist), 10)
        for path in allowlist:
            self.assertTrue(
                path.startswith("src/loom/hud/")
                or path == "deploy/android/launch_hud.py"
                or path.startswith("engineering/current/")
                or path == "engineering/hud/wayfarer_pr96_hud_engineering_snapshot_v0.1.json"
            )

    def test_installer_backs_up_before_replacement(self):
        source = self._source()
        self.assertIn("shutil.copy2", source)
        self.assertIn(".loom_hud_test_drive_backups", source)
        self.assertIn(".loom_hud_test_drive_state.json", source)


if __name__ == "__main__":
    unittest.main()
