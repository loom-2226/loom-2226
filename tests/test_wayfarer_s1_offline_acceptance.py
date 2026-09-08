from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "qualification" / "synthesis" / "wayfarer_s1_offline_acceptance.py"


class WayfarerS1OfflineAcceptanceTests(unittest.TestCase):
    def test_offline_acceptance_entry_point(self):
        proc = subprocess.run(
            [sys.executable, str(ACCEPTANCE)],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
        self.assertIn("WAYFARER_S1_OFFLINE_ACCEPTANCE = PASS", proc.stdout)
        self.assertIn("PROCEDURAL_LAYOUT_FEASIBILITY = PASS", proc.stdout)
        self.assertIn("candidate_id = CAND-5719E3F3251DE6E25FDF", proc.stdout)
        self.assertIn("flight_dynamics_authority = false", proc.stdout)
        self.assertIn("wayfarer_flight_inertia_qualified = false", proc.stdout)
        self.assertIn("canon_changed = false", proc.stdout)
        self.assertIn("production_shipclasses_changed = false", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
