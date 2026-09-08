from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from phase2_functional_regions import (  # noqa: E402
    AUTHORITY,
    SPATIAL_STATUS,
    TARGET_SOURCES,
    Phase2FunctionalRegionError,
    build_contracts,
    build_phase2_ledger,
    validate_contract,
)


class WayfarerPhase2FunctionalRegionTests(unittest.TestCase):
    def test_contracts_are_deterministic_and_never_invent_envelopes(self):
        a = build_contracts()
        b = build_contracts()
        self.assertEqual(a, b)
        self.assertEqual(tuple(row.source_id for row in a), TARGET_SOURCES)
        for row in a:
            validate_contract(row)
            self.assertIsNone(row.spatial_envelope_m)
            self.assertEqual(row.spatial_status, SPATIAL_STATUS)
            self.assertEqual(row.authority_status, AUTHORITY)
            self.assertTrue(row.unresolved_sizing_inputs)
            self.assertFalse(row.flight_dynamics_authority)
            self.assertFalse(row.canon_changed)
            self.assertFalse(row.production_shipclasses_changed)

    def test_phase2_ledger_replaces_vague_open_items_with_specific_obligations(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "phase2.sqlite3"
            result = build_phase2_ledger(path)
            self.assertEqual(result["functional_region_count"], len(TARGET_SOURCES))
            con = sqlite3.connect(path)
            try:
                rows = con.execute("SELECT source_id,spatial_status,contract_json FROM functional_region_contract ORDER BY source_id").fetchall()
                self.assertEqual(len(rows), len(TARGET_SOURCES))
                self.assertTrue(all(row[1] == SPATIAL_STATUS for row in rows))
                state_text = con.execute("SELECT state_json FROM design_state WHERE state_id=?", (result["state_id"],)).fetchone()[0]
                state = json.loads(state_text)
                open_items = state["packaging"]["open_items"]
                for source_id in TARGET_SOURCES:
                    self.assertNotIn(f"NO_ADMITTED_VOLUME::{source_id}", open_items)
                    self.assertTrue(any(item.startswith(f"FUNCTIONAL_REGION_ENVELOPE_OPEN::{source_id}::") for item in open_items))
                self.assertEqual(len(state["phase2_functional_regions"]), len(TARGET_SOURCES))
            finally:
                con.close()

    def test_contract_authority_escalation_fails_closed(self):
        row = build_contracts()[0]
        bad = row.__class__(**{**row.__dict__, "spatial_envelope_m": (1.0, 1.0, 1.0)})
        with self.assertRaises(Phase2FunctionalRegionError):
            validate_contract(bad)


if __name__ == "__main__":
    unittest.main()
