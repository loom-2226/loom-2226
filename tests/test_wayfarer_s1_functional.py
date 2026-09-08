from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLVER = ROOT / "qualification" / "synthesis" / "wayfarer_s1_solver.py"


class WayfarerS1FunctionalTests(unittest.TestCase):
    def _run(self):
        proc = subprocess.run(
            [sys.executable, str(SOLVER), "--seed", "2226"],
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + "\n" + proc.stderr)
        return proc.stdout, json.loads(proc.stdout)

    def test_cli_is_reproducible_and_generates_legal_non_authoritative_layout(self):
        stdout_a, a = self._run()
        stdout_b, b = self._run()
        self.assertEqual(stdout_a, stdout_b)
        self.assertEqual(a, b)
        self.assertEqual(a["PROCEDURAL_LAYOUT_FEASIBILITY"], "PASS")
        self.assertEqual(a["candidate_id"], "CAND-5719E3F3251DE6E25FDF")
        self.assertEqual(a["search"]["examined_count"], 203)
        self.assertEqual(a["search"]["legal_count"], 203)
        self.assertEqual(a["search"]["rejected_count"], 0)
        self.assertEqual(a["mass_kg"], 1_158_500.0)
        self.assertFalse(a["flight_dynamics_authority"])
        self.assertFalse(a["wayfarer_flight_inertia_qualified"])

        transforms = {row["instance_id"]: row["translation_m"] for row in a["component_transforms"]}
        tank_x = {row["centroid_m"][0] for row in a["tank_point_mass_decomposition"]}
        self.assertEqual(transforms["relational_plant"][0], 26.0)
        self.assertEqual(transforms["planetary_launch"][0], 21.75)
        self.assertEqual(tank_x, {26.5})
        self.assertNotEqual((26.0, 21.75, 26.5), (26.0, 21.8, 25.0))
        self.assertTrue(all(row["passed"] for row in a["hard_constraints"]))
        self.assertTrue(all(value == "OPEN_NOT_USED" for key, value in a["provenance_map"].items() if key.endswith("geometry")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
