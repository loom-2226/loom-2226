from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from update_shipyard import apply_phase2  # noqa: E402


class PersistentShipyardUpdateTests(unittest.TestCase):
    def test_phase2_migration_is_idempotent_and_preserves_single_history_child(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "shipyard_design_ledger.sqlite3"
            first = apply_phase2(db)
            second = apply_phase2(db)
            self.assertFalse(first["already_applied"])
            self.assertTrue(second["already_applied"])
            self.assertEqual(first["state_id"], second["state_id"])
            con = sqlite3.connect(db)
            try:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM functional_region_contract").fetchone()[0], 9)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM shipyard_migration").fetchone()[0], 1)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM design_state").fetchone()[0], 2)
            finally:
                con.close()

    def test_refuses_non_shipyard_sqlite(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "wrong.sqlite3"
            con = sqlite3.connect(db)
            con.execute("CREATE TABLE world_state(x INTEGER)")
            con.commit(); con.close()
            with self.assertRaises(RuntimeError):
                apply_phase2(db)


if __name__ == "__main__":
    unittest.main()
