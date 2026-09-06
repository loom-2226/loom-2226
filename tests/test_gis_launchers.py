import io
import runpy
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ANDROID_ROOT = Path("/storage/emulated/0/Documents/LOOM")

class GISLauncherTests(unittest.TestCase):
    def _run_launcher(self, relative_path, env):
        captured = {}
        def fake_call(argv, env=None):
            captured["argv"] = list(argv); captured["env"] = dict(env or {}); return 0
        with patch.dict("os.environ", env, clear=True), patch("pathlib.Path.exists", return_value=True), patch("subprocess.call", side_effect=fake_call):
            with self.assertRaises(SystemExit) as raised: runpy.run_path(str(ROOT / relative_path), run_name="__main__")
        self.assertEqual(raised.exception.code, 0); return captured

    def test_android_launcher_honors_explicit_roots(self):
        app="/tmp/loom-app"; data="/tmp/loom-data"; campaign="/tmp/loom-campaign"
        result=self._run_launcher("deploy/android/launch_gis.py", {"LOOM_APP_ROOT":app,"LOOM_DATA_ROOT":data,"LOOM_CAMPAIGN_ROOT":campaign})
        argv=result["argv"]; env=result["env"]
        self.assertEqual(Path(argv[1]),Path(app).resolve()/"src"/"loom_gis.py")
        self.assertIn(str(Path(data).resolve()/"LOOM_2226.sqlite3"),argv)
        self.assertIn(str(Path(data).resolve()/"LOOM_2226_CIVSTATE.sqlite3"),argv)
        self.assertEqual(env["LOOM_CAMPAIGN_ROOT"],str(Path(campaign).resolve()))
        self.assertEqual(env["LOOM_HOME"],str(Path(app).resolve()))
        self.assertNotIn("--nav-planning-offline",argv)

    def test_android_offline_planning_is_explicit_opt_in(self):
        result=self._run_launcher("deploy/android/launch_gis.py", {"LOOM_NAV_PLANNING_OFFLINE":"1"})
        self.assertIn("--nav-planning-offline",result["argv"])

    def test_android_defaults_to_staged_runtime_roots(self):
        result=self._run_launcher("deploy/android/launch_gis.py", {})
        argv=result["argv"]; env=result["env"]
        self.assertEqual(Path(argv[1]),(ANDROID_ROOT/"runtime/src/loom_gis.py").resolve())
        self.assertIn(str((ANDROID_ROOT/"data/LOOM_2226.sqlite3").resolve()),argv)
        self.assertEqual(env["LOOM_APP_ROOT"],str((ANDROID_ROOT/"runtime").resolve()))
        self.assertEqual(env["LOOM_DATA_ROOT"],str((ANDROID_ROOT/"data").resolve()))
        self.assertEqual(env["LOOM_CAMPAIGN_ROOT"],str((ANDROID_ROOT/"campaign").resolve()))
        self.assertNotIn("--nav-planning-offline",argv)

    def test_android_ctrl_c_exits_cleanly_without_traceback(self):
        out = io.StringIO()
        env = {"LOOM_NO_BROWSER":"1"}
        with patch.dict("os.environ", env, clear=True), patch("pathlib.Path.exists", return_value=True), patch("subprocess.call", side_effect=KeyboardInterrupt):
            with redirect_stdout(out), self.assertRaises(SystemExit) as raised:
                runpy.run_path(str(ROOT / "deploy/android/launch_gis.py"), run_name="__main__")
        self.assertEqual(raised.exception.code, 130)
        self.assertIn("LOOM stopped.", out.getvalue())
        self.assertNotIn("Traceback", out.getvalue())

    def test_windows_launcher_honors_explicit_campaign_root(self):
        app="/tmp/loom-app"; data="/tmp/loom-data"; campaign="/tmp/loom-campaign"
        result=self._run_launcher("deploy/windows/launch_gis.py", {"LOOM_APP_ROOT":app,"LOOM_DATA_ROOT":data,"LOOM_CAMPAIGN_ROOT":campaign})
        self.assertEqual(result["env"]["LOOM_CAMPAIGN_ROOT"],str(Path(campaign).resolve()))
        self.assertEqual(result["env"]["LOOM_DATA_ROOT"],str(Path(data).resolve()))

if __name__ == "__main__": unittest.main()
