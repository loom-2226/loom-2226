import pathlib
import subprocess
import sys
import unittest


class PixelAssistedRepairSmokeTests(unittest.TestCase):
    def setUp(self):
        self.repo = pathlib.Path(__file__).resolve().parents[1]

    def test_smoke_fixture_runs_on_termux_without_hardcoded_posix_tmp(self):
        proc = subprocess.run(
            [sys.executable, "engineering/pixel/assisted_repair_smoke_fixture.py"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("ASSISTED_REPAIR_SMOKE=PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
