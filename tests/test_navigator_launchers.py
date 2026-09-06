from pathlib import Path
from unittest.mock import patch
import os
import runpy
import unittest


class NavigatorLauncherRootsTest(unittest.TestCase):
    def _run(self, script, env):
        captured = {}
        def fake_run_path(path, run_name=None):
            captured["path"] = path
            captured["run_name"] = run_name
            captured["env"] = dict(os.environ)
            return {}
        with patch.dict(os.environ, env, clear=True), patch.object(runpy, "run_path", side_effect=fake_run_path):
            runpy.run_path(str(Path(__file__).parents[1] / script), run_name="__main__")
        return captured

    def test_android_separates_app_data_and_campaign_authority(self):
        result = self._run("deploy/android/launch_navigator.py", {
            "LOOM_APP_ROOT": "/tmp/app",
            "LOOM_DATA_ROOT": "/tmp/data",
            "LOOM_CAMPAIGN_ROOT": "/tmp/campaign",
        })
        self.assertEqual(result["path"], str(Path("/tmp/app/src/loom_navigator.py")))
        self.assertEqual(result["env"]["LOOM_APP_ROOT"], str(Path("/tmp/app").resolve()))
        self.assertEqual(result["env"]["LOOM_DATA_ROOT"], str(Path("/tmp/data").resolve()))
        self.assertEqual(result["env"]["LOOM_CAMPAIGN_ROOT"], str(Path("/tmp/campaign").resolve()))
        self.assertEqual(result["env"]["LOOM_HOME"], str(Path("/tmp/app").resolve()))
        self.assertEqual(result["env"]["LOOM_DATA_DIR"], str(Path("/tmp/data").resolve()))

    def test_android_campaign_defaults_to_app(self):
        result = self._run("deploy/android/launch_navigator.py", {
            "LOOM_APP_ROOT": "/tmp/app",
            "LOOM_DATA_ROOT": "/tmp/data",
        })
        self.assertEqual(result["env"]["LOOM_CAMPAIGN_ROOT"], str(Path("/tmp/app").resolve()))

    def test_windows_honors_explicit_roots(self):
        result = self._run("deploy/windows/launch_navigator.py", {
            "LOOM_APP_ROOT": "/tmp/winapp",
            "LOOM_DATA_ROOT": "/tmp/windata",
            "LOOM_CAMPAIGN_ROOT": "/tmp/wincampaign",
        })
        self.assertEqual(result["path"], str(Path("/tmp/winapp/src/loom_navigator.py")))
        self.assertEqual(result["env"]["LOOM_DATA_DIR"], str(Path("/tmp/windata").resolve()))
        self.assertEqual(result["env"]["LOOM_CAMPAIGN_ROOT"], str(Path("/tmp/wincampaign").resolve()))


if __name__ == "__main__":
    unittest.main()
