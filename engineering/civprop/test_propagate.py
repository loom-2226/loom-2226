import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from engineering.civprop.propagate import GOLDEN, run

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]


class StandalonePropagateTests(unittest.TestCase):
    def test_seed42_matches_frozen_gap13_golden(self):
        self.assertEqual(run(42), json.loads(GOLDEN.read_text()))

    def test_cli_reports_authoritative_fixture_horizon(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "seed43.json"
            proc = subprocess.run(
                [sys.executable, str(HERE / "propagate.py"), "--seed", "43", "--output", str(out)],
                cwd=REPO_ROOT, check=True, text=True, capture_output=True,
            )
            payload = json.loads(out.read_text())
            years = [int(x["year"]) for x in payload["annual_states"]]
            self.assertEqual((min(years), max(years)), (2026, 2036))
            self.assertIn("Period: 2026 -> 2036", proc.stdout)

    def test_verify_reproduces_frozen_baseline(self):
        proc = subprocess.run(
            [sys.executable, str(HERE / "propagate.py"), "--verify"],
            cwd=REPO_ROOT, check=True, text=True, capture_output=True,
        )
        self.assertIn("Golden file integrity: PASS", proc.stdout)
        self.assertIn("Deterministic reproduction: PASS", proc.stdout)
        self.assertIn("RESULT: PASS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
