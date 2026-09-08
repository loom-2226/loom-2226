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
import shipyard_phase11_remass_feed_bounds


class Phase11RemassFeedBoundsTests(unittest.TestCase):
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
        return db

    def test_analytic_bounds_are_explicit_and_non_authoritative(self):
        head = shipyard_phase11_remass_feed_bounds.inertial_head_bound(
            density_kg_m3=998.2, acceleration_m_s2=7.5 * 9.80665, max_length_m=11.0,
        )
        self.assertGreater(head["maximum_inertial_pressure_span_pa"], 800_000.0)
        self.assertLess(head["maximum_inertial_pressure_span_pa"], 810_000.0)
        self.assertFalse(head["engineering_input_admitted"])
        power = shipyard_phase11_remass_feed_bounds.hydraulic_power_probe(
            mass_flow_kg_s=284.025100625, density_kg_m3=998.2, pressure_rise_pa=10_000_000.0,
        )
        self.assertGreater(power["ideal_hydraulic_power_w"], 2_840_000.0)
        self.assertLess(power["ideal_hydraulic_power_w"], 2_850_000.0)
        self.assertIsNone(power["efficiency_assumed"])
        self.assertIn("NOT_PROPULSION_INLET_PRESSURE", power["probe_semantics"])

    def test_phase11_maps_bounds_and_priority_without_selecting(self):
        db = self._db()
        with sqlite3.connect(db) as con:
            before_inputs = con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0]
        result = shipyard_phase11_remass_feed_bounds.apply_phase11(db)
        self.assertFalse(result["already_applied"])
        self.assertEqual(result["inertial_head_bound_count"], 24)
        self.assertEqual(result["hydraulic_power_probe_count"], 24)
        self.assertEqual(result["selected_feed_architecture_count"], 0)
        self.assertEqual(result["live_engineering_input_admission_count"], 0)
        self.assertEqual(result["research_priority"], "PUMP_OR_HEADER_CONDITIONED_FEED_DESERVES_NEXT_MODELING_PRIORITY")
        self.assertEqual(result["spatial_effect"], "NONE_ANALYTIC_FEED_BOUNDS_ONLY")
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_inertial_head_bound").fetchone()[0], 24)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_hydraulic_power_probe").fetchone()[0], 24)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM engineering_input").fetchone()[0], before_inputs)

    def test_phase11_is_idempotent(self):
        db = self._db()
        shipyard_phase11_remass_feed_bounds.apply_phase11(db)
        second = shipyard_phase11_remass_feed_bounds.apply_phase11(db)
        self.assertTrue(second["already_applied"])
        with sqlite3.connect(db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM design_state WHERE state_kind='PHASE11_REMASS_FEED_PHYSICS_BOUNDS_STATE'").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
