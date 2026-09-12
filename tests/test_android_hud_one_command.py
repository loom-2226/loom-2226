import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "deploy" / "android" / "launch_hud.py"


class AndroidHudOneCommandTests(unittest.TestCase):
    def test_launcher_self_updates_current_git_branch_fail_closed(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("git fetch --prune origin", source)
        self.assertIn("git merge --ff-only", source)
        self.assertIn("LOOM_HUD_SKIP_UPDATE", source)
        self.assertIn("refusing auto-update with local Git changes", source)

    def test_launcher_defaults_app_root_to_its_git_checkout(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("CHECKOUT_ROOT", source)
        self.assertIn("Path(__file__).resolve().parents[2]", source)
        self.assertIn("LOOM_DATA_ROOT", source)
        self.assertIn("LOOM_CAMPAIGN_ROOT", source)

    def test_launcher_does_not_modify_data_or_campaign(self):
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertNotIn("shutil.copy", source)
        self.assertNotIn("copytree", source)
        self.assertNotIn("rmtree", source)


if __name__ == "__main__":
    unittest.main()
