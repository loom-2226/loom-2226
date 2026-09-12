import re
import unittest

from loom.hud import server


class HudAndroidLauncherTests(unittest.TestCase):
    def test_android_launcher_build_marker_matches_checked_in_hud(self):
        html = server.validate_assets().read_text(encoding="utf-8")
        match = re.search(r'name="loom-hud-build" content="([^"]+)"', html)
        self.assertIsNotNone(match)
        build = match.group(1)

        launcher = (
            server.repo_root() / "deploy" / "android" / "launch_hud.py"
        ).read_text(encoding="utf-8")
        self.assertIn(f'BUILD_MARKER="{build}"', launcher)

    def test_android_launcher_remains_local_and_split_root(self):
        launcher = (
            server.repo_root() / "deploy" / "android" / "launch_hud.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"127.0.0.1"', launcher)
        self.assertIn("LOOM_APP_ROOT", launcher)
        self.assertIn("LOOM_DATA_ROOT", launcher)
        self.assertIn("LOOM_CAMPAIGN_ROOT", launcher)
        self.assertIn("termux-open-url", launcher)


if __name__ == "__main__":
    unittest.main()
