from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "qualification" / "synthesis", ROOT / "src", ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from design_ledger import build_wayfarer_phase1_ledger
import shipyard_migrate
import shipyard_phase3
import shipyard_phase4_remass
import shipyard_phase5_remass_audit
import shipyard_phase6_remass_candidates
import shipyard_evidence_viewer


class EvidenceViewerTests(unittest.TestCase):
    def _db(self) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        db = Path(td.name) / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        shipyard_migrate.apply_phase2(db)
        shipyard_phase3.apply_phase3(db)
        shipyard_phase4_remass.apply_phase4(db)
        shipyard_phase5_remass_audit.apply_phase5(db)
        shipyard_phase6_remass_candidates.apply_phase6(db)
        return db

    def test_android_safe_copy_matches_tool_viewer(self):
        self.assertEqual(
            (ROOT / "tools" / "shipyard_evidence_viewer.py").read_bytes(),
            (ROOT / "src" / "shipyard_evidence_viewer.py").read_bytes(),
        )

    def test_viewer_reads_phase6_without_mutation(self):
        db = self._db()
        before = db.read_bytes()
        evidence = shipyard_evidence_viewer.load_evidence(db)
        after = db.read_bytes()
        self.assertEqual(before, after)
        self.assertEqual(evidence["tank_count"], 4)
        self.assertEqual(evidence["candidate_count"], 3)
        self.assertEqual(evidence["comparison_count"], 12)
        statuses = [c["screen_status"] for t in evidence["tanks"] for c in t["comparisons"]]
        self.assertEqual(sum(s.startswith("REJECT_") for s in statuses), 8)
        self.assertEqual(sum(not s.startswith("REJECT_") for s in statuses), 4)

    def test_html_is_explicitly_non_authoritative(self):
        evidence = shipyard_evidence_viewer.load_evidence(self._db())
        page = shipyard_evidence_viewer.render_html(evidence)
        self.assertIn("NO SPATIAL ENVELOPE ADMITTED", page)
        self.assertIn("Water", page)
        self.assertIn("Methane", page)
        self.assertIn("Hydrogen", page)
        self.assertIn("NOT REJECTED", page)
        self.assertIn("REJECTED", page)
        self.assertIn("not physical tank geometry", page)


if __name__ == "__main__":
    unittest.main()
