from __future__ import annotations

from pathlib import Path
import json
import unittest

from loom.civstate_boundary_audit import CIVSTATE_BOUNDARY_CONTRACT, civstate_boundary_audit


class CIVSTATEBoundaryAuditTests(unittest.TestCase):
    def test_exact_repo_civstate_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        world = root / "data" / "LOOM_2226.sqlite3"
        civ = root / "data" / "LOOM_2226_CIVSTATE.sqlite3"
        result = civstate_boundary_audit(world, civ)
        self.assertEqual(result["contract"], CIVSTATE_BOUNDARY_CONTRACT)
        self.assertGreater(result["civstate_table_count"], 0)
        self.assertEqual(sum(result["classification_counts"].values()), result["civstate_table_count"])
        self.assertIn("transport_hubs", result)
        print("F_PA_CIVSTATE_BOUNDARY=" + json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
