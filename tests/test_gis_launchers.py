import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class GISLauncherTests(unittest.TestCase):
    def _run_launcher(self, relative_path, env):
        captured = {}

        def fake_call(argv, env=None):
            captured["argv"] = list(argv)
            captured["env"] = dict(env or {})
            return 0

        with patch.dict("os.environ", env, clear=True), patch("pathlib.Path.exists", return_value=True), patch("subprocess.call", side_effect=fake_call):
            with self.assertRaises(SystemExit) as raised:
                runpy.run_path(str(ROOT / relative_path), run_name="__main__")
        self.assertEqual(raised.exception.code, 0)
        return captured

    def test_android_launcher_separates_app_data_and_preserves_campaign_at_app(self):
        app = "/tmp/loom-app"
        data = "/tmp/loom-data"
        result = self._run_launcher("deploy/android/launch_gis.py", {"LOOM_APP_ROOT": app, "LOOM_DATA_ROOT": data})
        argv = result["argv"]
        env = result["env"]
        self.assertEqual(Path(argv[1]), Path(app).resolve() / "src" / "loom_gis.py")
        self.assertIn(str(Path(data).resolve() / "LOOM_2226.sqlite3"), argv)
        self.assertIn(str(Path(data).resolve() / "LOOM_2226_CIVSTATE.sqlite3"), argv)
        self.assertEqual(env["LOOM_CAMPAIGN_ROOT"], str(Path(app).resolve()))
        self.assertEqual(env["LOOM_HOME"], str(Path(app).resolve()))
        self.assertIn("--nav-planning-offline", argv)

    def test_windows_launcher_honors_explicit_campaign_root(self):
        app = "/tmp/loom-app"
        data = "/tmp/loom-data"
        campaign = "/tmp/loom-campaign"
        result = self._run_launcher("deploy/windows/launch_gis.py", {"LOOM_APP_ROOT": app, "LOOM_DATA_ROOT": data, "LOOM_CAMPAIGN_ROOT": campaign})
        self.assertEqual(result["env"]["LOOM_CAMPAIGN_ROOT"], str(Path(campaign).resolve()))
        self.assertEqual(result["env"]["LOOM_DATA_ROOT"], str(Path(data).resolve()))


if __name__ == "__main__":
    unittest.main()
