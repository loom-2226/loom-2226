from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from shipclasses_resolver import PhysicalContractError, compute_mass_properties, validate_configuration_transition

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.executescript(SEED.read_text(encoding="utf-8"))
    return conn


class WayfarerPhase3Tests(unittest.TestCase):
    def assertVecAlmostEqual(self, a, b, places=12):
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, places=places)

    def test_docked_wet_reference(self):
        r = compute_mass_properties(db(), {"launch_state": "DOCKED"})
        self.assertAlmostEqual(r["mass_kg"], 1158500.0, places=6)
        self.assertVecAlmostEqual(r["center_of_mass_B_m"], [26.676650841605525, 0.0, 0.14812257229175657])

    def test_absent_wet_reference(self):
        r = compute_mass_properties(db(), {"launch_state": "ABSENT"})
        self.assertAlmostEqual(r["mass_kg"], 1125500.0, places=6)
        self.assertVecAlmostEqual(r["center_of_mass_B_m"], [26.819635717458908, 0.0, 0.0])

    def test_protected_water_fails_closed(self):
        with self.assertRaises(PhysicalContractError):
            compute_mass_properties(
                db(),
                {"launch_state": "DOCKED"},
                {"store_normal_remass": 0.0, "store_protected_water": 0.0},
            )

    def test_reference_dry_ledger_excludes_all_stores(self):
        conn = db()
        for state, expected in {"DOCKED": 858500.0, "ABSENT": 825500.0}.items():
            launch_active = state != "ABSENT"
            mass = sum(
                float(r[0])
                for r in conn.execute(
                    "SELECT reference_mass_kg FROM mass_element WHERE component_id <> 'planetary_launch' OR ?",
                    (1 if launch_active else 0,),
                )
            )
            self.assertAlmostEqual(mass, expected, places=6)

    def test_no_double_count_300t_inventory(self):
        r = compute_mass_properties(db(), {"launch_state": "DOCKED"})
        store_mass = sum(
            c["mass_kg"] for c in r["contributions"] if c["source_id"].startswith("store_")
        )
        self.assertEqual(store_mass, 300000.0)

    def test_illegal_state_fails_closed(self):
        with self.assertRaises(PhysicalContractError):
            compute_mass_properties(db(), {"launch_state": "MAGIC"})

    def test_transition_gate(self):
        conn = db()
        ok = validate_configuration_transition(conn, "launch_state", "DOCKED", "EXTRACTING")
        self.assertTrue(ok["allowed"])
        with self.assertRaises(PhysicalContractError):
            validate_configuration_transition(conn, "launch_state", "DOCKED", "ABSENT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
