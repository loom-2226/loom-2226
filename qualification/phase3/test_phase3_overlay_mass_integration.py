from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from shipclasses_resolver import compute_mass_properties

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql"
SEED = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"
OVERLAY = ROOT / "LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql"


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for path in (SCHEMA, SEED, OVERLAY):
        conn.executescript(path.read_text(encoding="utf-8"))
    return conn


class Phase3OverlayMassIntegrationTests(unittest.TestCase):
    def assertVecAlmostEqual(self, a, b, places=12):
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, places=places)

    def test_overlay_preserves_docked_reference_mass_and_com(self):
        result = compute_mass_properties(db(), {"launch_state": "DOCKED"})
        self.assertAlmostEqual(result["mass_kg"], 1158500.0, places=6)
        self.assertVecAlmostEqual(
            result["center_of_mass_B_m"],
            [26.676650841605525, 0.0, 0.14812257229175657],
        )

    def test_overlay_preserves_absent_reference_mass_and_com(self):
        result = compute_mass_properties(db(), {"launch_state": "ABSENT"})
        self.assertAlmostEqual(result["mass_kg"], 1125500.0, places=6)
        self.assertVecAlmostEqual(
            result["center_of_mass_B_m"],
            [26.819635717458908, 0.0, 0.0],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
