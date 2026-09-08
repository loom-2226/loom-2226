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
import shipyard_phase10_remass_feed


class Phase10RemassFeedTests(unittest.TestCase):
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
        return db

    def test_transient_buffer_math_is_explicit_and_non_authoritative(self):
        r = shipyard_phase10_remass_feed.transient_buffer_probe(
            total_flow_kg_s=284.025100625,
            duration_s=10.0,
            screening_density_kg_m3=998.2,
        )
        self.assertAlmostEqual(r["transient_buffer_mass_kg"], 2840.25100625, places=8)
        self.assertAlmostEqual(r["ideal_liquid_buffer_volume_m3"], 2.845372672, places=6)
        self.assertFalse(r["engineering_input_admitted"])
        self.assertFalse(r["spatial_envelope_admitted"])
        self.assertIn("NOT_BURN_DURATION", r["probe_semantics"])

    def test_phase10_decomposes_storage_and_feed_without_selecting_topology(self):
        db = self._db()
        with sqlite3.connect(db) as con:
            before_inputs = con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0]
        result = shipyard_phase10_remass_feed.apply_phase10(db)
        self.assertFalse(result["already_applied"])
        self.assertEqual(result["buffer_probe_count"], 24)
        self.assertEqual(result["feed_topology_candidate_count"], 3)
        self.assertEqual(result["priority_next_experiment_count"], 2)
        self.assertEqual(result["selected_feed_topology_count"], 0)
        self.assertEqual(result["live_engineering_input_admission_count"], 0)
        self.assertEqual(result["spatial_effect"], "NONE_DECOMPOSITION_AND_BUFFER_SENSITIVITY_ONLY")
        self.assertAlmostEqual(result["largest_probe_buffer_mass_kg"], 2840.25100625, places=8)
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_feed_buffer_probe").fetchone()[0], 24)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_feed_topology_candidate").fetchone()[0], 3)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0], before_inputs)
            rows = [row[0] for row in con.execute("SELECT candidate_json FROM remass_feed_topology_candidate")]
            self.assertTrue(all('"selection_status":"NOT_SELECTED"' in row for row in rows))
            self.assertTrue(any("header/reserve/conditioning" in row for row in rows))

    def test_phase10_is_idempotent(self):
        db = self._db()
        shipyard_phase10_remass_feed.apply_phase10(db)
        second = shipyard_phase10_remass_feed.apply_phase10(db)
        self.assertTrue(second["already_applied"])
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM design_state WHERE state_kind='PHASE10_REMASS_FEED_DECOMPOSITION_STATE'").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
