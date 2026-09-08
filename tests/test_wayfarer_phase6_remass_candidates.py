from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "qualification" / "synthesis", ROOT / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from design_ledger import build_wayfarer_phase1_ledger  # noqa: E402
import shipyard_migrate  # noqa: E402
import shipyard_phase3  # noqa: E402
import shipyard_phase4_remass as phase4  # noqa: E402
import shipyard_phase5_remass_audit as phase5  # noqa: E402
import shipyard_phase6_remass_candidates as phase6  # noqa: E402


class Phase6RemassCandidateTests(unittest.TestCase):
    def _db(self) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        db = Path(td.name) / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        shipyard_migrate.apply_phase2(db)
        shipyard_phase3.apply_phase3(db)
        phase4.apply_phase4(db)
        phase5.apply_phase5(db)
        return db

    def test_density_screen_semantics(self):
        self.assertEqual(phase6.classify_candidate(1000.0, 600.0), "NOT_REJECTED_BY_DENSITY_BOUND_ONLY")
        self.assertEqual(phase6.classify_candidate(500.0, 600.0), "REJECT_OUTER_ENVELOPE_DENSITY_BOUND")
        with self.assertRaises(RuntimeError):
            phase6.classify_candidate(0.0, 600.0)

    def test_phase6_compares_but_does_not_select_or_admit(self):
        db = self._db()
        con = sqlite3.connect(db)
        before_inputs = con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0]
        con.close()

        result = phase6.apply_phase6(db)
        self.assertEqual(result["candidate_model_count"], 3)
        self.assertEqual(result["tank_count"], 4)
        self.assertEqual(result["comparison_count"], 12)
        self.assertEqual(result["selected_candidate_count"], 0)
        self.assertEqual(result["live_engineering_input_admission_count"], 0)
        self.assertEqual(result["spatial_effect"], "NONE_SCREENING_ONLY_NO_ENVELOPE_ADMITTED")
        self.assertFalse(result["canon_changed"])
        self.assertFalse(result["production_shipclasses_changed"])
        self.assertFalse(result["flight_dynamics_authority"])
        self.assertEqual(result["rejected_comparison_count"] + result["not_rejected_comparison_count"], 12)

        con = sqlite3.connect(db)
        try:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_candidate_model").fetchone()[0], 3)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_candidate_comparison").fetchone()[0], 12)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0], before_inputs)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_candidate_comparison WHERE screen_status='REJECT_OUTER_ENVELOPE_DENSITY_BOUND'").fetchone()[0], result["rejected_comparison_count"])
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_candidate_comparison WHERE screen_status='NOT_REJECTED_BY_DENSITY_BOUND_ONLY'").fetchone()[0], result["not_rejected_comparison_count"])
        finally:
            con.close()

        again = phase6.apply_phase6(db)
        self.assertTrue(again["already_applied"])


if __name__ == "__main__":
    unittest.main()
