from __future__ import annotations

import sqlite3
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
import shipyard_evidence_viewer


class Phase8WaterClosureTests(unittest.TestCase):
    def _db(self) -> Path:
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        db = Path(td.name) / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        shipyard_migrate.apply_phase2(db)
        shipyard_phase3.apply_phase3(db)
        shipyard_phase4_remass.apply_phase4(db)
        shipyard_phase5_remass_audit.apply_phase5(db)
        shipyard_phase6_remass_candidates.apply_phase6(db)
        return db

    def test_exact_closure_budget_math(self):
        r = shipyard_phase8_water_closure.evaluate_closure(
            mass_kg=62500.0, density_kg_m3=998.2, max_external_length_m=11.0,
            internal_diameter_m=3.0, ullage_fraction=0.0,
        )
        self.assertEqual(r["geometric_budget_status"], "FEASIBLE_BY_GEOMETRIC_BUDGET_ONLY")
        self.assertGreater(r["max_axial_end_allowance_m"], 2.0)
        self.assertFalse(r["spatial_envelope_admitted"])
        f = shipyard_phase8_water_closure.summarize_frontier(
            mass_kg=62500.0, density_kg_m3=998.2, external_diameter_m=3.0, max_external_length_m=11.0,
        )
        self.assertGreater(f["max_total_volume_penalty_fraction"], 0.19)
        self.assertLess(f["max_total_volume_penalty_fraction"], 0.20)

    def test_phase8_migration_is_research_only_and_idempotent(self):
        db = self._db()
        result = shipyard_phase8_water_closure.apply_phase8(db)
        self.assertFalse(result["already_applied"])
        self.assertEqual(result["frontier_count"], 4)
        self.assertEqual(result["probe_count"], 100)
        self.assertEqual(result["live_engineering_input_admission_count"], 0)
        self.assertFalse(result["water_selected"])
        self.assertEqual(result["spatial_effect"], "NONE_CLOSURE_MAP_ONLY_NO_ENVELOPE_ADMITTED")
        second = shipyard_phase8_water_closure.apply_phase8(db)
        self.assertTrue(second["already_applied"])
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_water_closure_frontier").fetchone()[0], 4)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_water_closure_probe").fetchone()[0], 100)

    def test_viewer_exposes_phase8_without_authority_escalation(self):
        db = self._db(); shipyard_phase8_water_closure.apply_phase8(db)
        before = db.read_bytes(); evidence = shipyard_evidence_viewer.load_evidence(db); after = db.read_bytes()
        self.assertEqual(before, after)
        self.assertIn("phase8", evidence)
        page = shipyard_evidence_viewer.render_html(evidence)
        self.assertIn("Phase 8", page)
        self.assertIn("wall thickness", page)
        self.assertIn("NO SPATIAL ENVELOPE ADMITTED", page)


if __name__ == "__main__":
    unittest.main()
