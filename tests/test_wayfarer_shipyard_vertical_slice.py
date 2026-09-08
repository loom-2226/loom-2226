from __future__ import annotations

import sys
import unittest
from pathlib import Path

SYNTH = Path(__file__).resolve().parents[1] / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_shipyard_vertical_slice import run  # noqa: E402


class WayfarerShipyardVerticalSliceTests(unittest.TestCase):
    def test_existing_wayfarer_solver_mutation_evaluator_loop(self):
        row = run(2226)
        self.assertTrue(row["parent_candidate_id"].startswith("CAND-"))
        self.assertTrue(row["child_candidate_id"].startswith("CAND-MUT-"))
        self.assertAlmostEqual(row["child_launch_x_m"] - row["parent_launch_x_m"], 0.25)
        self.assertTrue(row["child_hard_constraints_pass"])
        self.assertEqual(row["proposal_authority"], "PROPOSAL_ONLY")
        self.assertEqual(row["execution_authority"], "CANDIDATE_DERIVATION_ONLY")
        self.assertEqual(row["sol_recommendation"], "ACCEPT")
        self.assertFalse(row["flight_dynamics_authority"])
        self.assertFalse(row["canon_changed"])
        self.assertFalse(row["production_shipclasses_changed"])

    def test_deterministic_replay(self):
        self.assertEqual(run(2226), run(2226))

    def test_sol_requests_visual_evidence_before_stronger_claim(self):
        row = run(2226)
        self.assertIn("insufficient", row["sol_finding"].lower())
        self.assertIn("Render parent and child", row["sol_experiment_request"])


if __name__ == "__main__":
    unittest.main()
