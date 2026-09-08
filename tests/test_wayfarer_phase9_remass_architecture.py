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
import shipyard_phase9_remass_architecture


class Phase9RemassArchitectureTests(unittest.TestCase):
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
        return db

    def test_feed_demand_is_deterministic_interface_evidence_only(self):
        r = shipyard_phase9_remass_architecture.derive_feed_demand(
            wet_mass_kg=1_158_500.0,
            acceleration_g=7.5,
            exhaust_velocity_m_s=300_000.0,
        )
        self.assertAlmostEqual(r["derived_total_remass_flow_kg_s"], 284.025100625, places=9)
        self.assertFalse(r["engineering_input_admitted"])
        self.assertEqual(r["authority_status"], "DERIVED_INTERFACE_DEMAND_ONLY")
        self.assertIn("NOT_TANK_FEED_SPLIT", r["demand_semantics"])

    def test_phase9_maps_architectures_but_selects_none(self):
        db = self._db()
        before_inputs = None
        with sqlite3.connect(db) as con:
            before_inputs = con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0]
        result = shipyard_phase9_remass_architecture.apply_phase9(db)
        self.assertFalse(result["already_applied"])
        self.assertEqual(result["feed_demand_count"], 6)
        self.assertEqual(result["architecture_candidate_count"], 5)
        self.assertEqual(result["ready_architecture_count"], 0)
        self.assertEqual(result["selected_architecture_count"], 0)
        self.assertEqual(result["live_engineering_input_admission_count"], 0)
        self.assertEqual(result["spatial_effect"], "NONE_ARCHITECTURE_GATE_ONLY_NO_ENVELOPE_ADMITTED")
        self.assertGreater(result["peak_reference_feed_demand_kg_s"], 284.0)
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_feed_demand").fetchone()[0], 6)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_architecture_candidate").fetchone()[0], 5)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_architecture_gate").fetchone()[0], 1)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0], before_inputs)
            rows = con.execute("SELECT candidate_json FROM remass_architecture_candidate").fetchall()
            self.assertTrue(all('"selection_status":"NOT_SELECTED"' in row[0] for row in rows))
            self.assertTrue(all('"spatial_envelope_admitted":false' in row[0] for row in rows))

    def test_phase9_is_idempotent(self):
        db = self._db()
        shipyard_phase9_remass_architecture.apply_phase9(db)
        second = shipyard_phase9_remass_architecture.apply_phase9(db)
        self.assertTrue(second["already_applied"])
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM design_state WHERE state_kind='PHASE9_REMASS_ARCHITECTURE_GATE_STATE'").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
