from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "qualification" / "synthesis", ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from design_ledger import build_wayfarer_phase1_ledger
import shipyard_migrate
import shipyard_phase3
import shipyard_phase4_remass
import shipyard_phase5_remass_audit
import shipyard_phase6_remass_candidates
import shipyard_phase8_water_closure
import shipyard_phase9_remass_architecture
import shipyard_phase10_remass_feed
import shipyard_phase11_remass_feed_bounds
import shipyard_evidence_viewer


class Phase12EvidenceViewerTests(unittest.TestCase):
    def _db(self) -> Path:
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        db = Path(td.name) / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        shipyard_migrate.apply_phase2(db)
        shipyard_phase3.apply_phase3(db)
        shipyard_phase4_remass.apply_phase4(db)
        shipyard_phase5_remass_audit.apply_phase5(db)
        shipyard_phase6_remass_candidates.apply_phase6(db)
        shipyard_phase8_water_closure.apply_phase8(db)
        shipyard_phase9_remass_architecture.apply_phase9(db)
        shipyard_phase10_remass_feed.apply_phase10(db)
        shipyard_phase11_remass_feed_bounds.apply_phase11(db)
        return db

    def test_viewer_is_read_only_and_exposes_phases_9_to_11(self):
        db = self._db()
        before = db.read_bytes()
        evidence = shipyard_evidence_viewer.load_evidence(db)
        after = db.read_bytes()
        self.assertEqual(before, after)
        self.assertIn("phase9", evidence)
        self.assertIn("phase10", evidence)
        self.assertIn("phase11", evidence)
        self.assertEqual(len(evidence["phase9"]["demands"]), 6)
        self.assertEqual(len(evidence["phase9"]["architectures"]), 5)
        self.assertEqual(len(evidence["phase10"]["buffer_probes"]), 24)
        self.assertEqual(len(evidence["phase10"]["topologies"]), 3)
        self.assertEqual(len(evidence["phase11"]["inertial_heads"]), 24)
        self.assertEqual(len(evidence["phase11"]["hydraulic_probes"]), 24)

    def test_html_preserves_authority_firewall(self):
        db = self._db()
        page = shipyard_evidence_viewer.render_html(shipyard_evidence_viewer.load_evidence(db))
        self.assertIn("Phase 9 — Remass architecture gate", page)
        self.assertIn("Phase 10 — Feed decomposition", page)
        self.assertIn("Phase 11 — Feed physics bounds", page)
        self.assertIn("PUMP_OR_HEADER_CONDITIONED_FEED_DESERVES_NEXT_MODELING_PRIORITY", page)
        self.assertIn("No tank architecture selected", page)
        self.assertIn("No feed topology or header size selected", page)
        self.assertIn("Pressure-rise probes are not propulsion inlet requirements", page)
        self.assertIn("NO SPATIAL ENVELOPE ADMITTED", page)


if __name__ == "__main__":
    unittest.main()
