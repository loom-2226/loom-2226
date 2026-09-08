from __future__ import annotations

import json
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


class Phase5RemassAuditTests(unittest.TestCase):
    def _db(self) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        db = Path(td.name) / "shipyard.sqlite3"
        build_wayfarer_phase1_ledger(db)
        shipyard_migrate.apply_phase2(db)
        shipyard_phase3.apply_phase3(db)
        phase4.apply_phase4(db)
        return db

    def test_bounds_are_deterministic_and_do_not_admit_geometry(self):
        a = phase5._bounds(62500.0, 3.0, [26.5, 1.0, 1.0])
        b = phase5._bounds(62500.0, 3.0, [26.5, 1.0, 1.0])
        self.assertEqual(a, b)
        self.assertEqual(a["max_centered_external_length_m"], 11.0)
        self.assertGreater(a["minimum_equivalent_bulk_density_kg_m3"], 0.0)
        self.assertGreater(a["technical_core_radial_clearance_m"], 0.0)
        self.assertGreater(a["adjacent_tank_surface_clearance_m"], 0.0)
        self.assertFalse(a["spatial_envelope_admitted"])

    def test_phase5_records_open_authority_findings_and_corrected_contract(self):
        db = self._db()
        result = phase5.apply_phase5(db)
        self.assertEqual(result["audited_tank_count"], 4)
        self.assertEqual(result["feasibility_bound_count"], 4)
        self.assertEqual(result["corrected_required_input_count_per_tank"], 7)
        self.assertEqual(result["live_sizing_ready_count"], 0)
        self.assertEqual(result["spatial_effect"], "NONE_FEASIBILITY_BOUNDS_ONLY")
        self.assertFalse(result["canon_changed"])
        self.assertFalse(result["production_shipclasses_changed"])
        self.assertFalse(result["flight_dynamics_authority"])
        con = sqlite3.connect(db)
        try:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_input_audit").fetchone()[0], 4)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM remass_feasibility_bound").fetchone()[0], 4)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM discipline_contract_revision").fetchone()[0], 4)
            text = con.execute("SELECT audit_json FROM remass_input_audit ORDER BY source_id LIMIT 1").fetchone()[0]
            audit = json.loads(text)
            self.assertIn("OPEN_CURRENT_AUTHORITY", audit["repository_authority_findings"]["remass_composition"])
            self.assertFalse(audit["can_execute_live_sizing"])
        finally:
            con.close()
        again = phase5.apply_phase5(db)
        self.assertTrue(again["already_applied"])


if __name__ == "__main__":
    unittest.main()
