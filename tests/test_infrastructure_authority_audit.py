from __future__ import annotations

from pathlib import Path
import json
import unittest

from loom.infrastructure_authority_audit import MATRIX_CONTRACT, infrastructure_authority_matrix


class InfrastructureAuthorityAuditTests(unittest.TestCase):
    def test_exact_repo_infrastructure_authority_matrix(self) -> None:
        root = Path(__file__).resolve().parents[1]
        world = root / "data" / "LOOM_2226.sqlite3"
        result = infrastructure_authority_matrix(world)
        self.assertEqual(result["contract"], MATRIX_CONTRACT)
        self.assertEqual(result["summary"]["row_count"], 127)
        self.assertEqual(len(result["rows"]), 127)
        self.assertTrue(all("node_id" in row and "entity_id" in row for row in result["rows"]))
        self.assertTrue(all(row["surface_coordinates_structured"] is False for row in result["rows"]))
        self.assertTrue(all(row["docking_transition_geometry_structured"] is False for row in result["rows"]))
        print("F_PA_INFRASTRUCTURE_MATRIX_SUMMARY=" + json.dumps(result["summary"], sort_keys=True))
        print("F_PA_INFRASTRUCTURE_MATRIX_ROWS=" + json.dumps(result["rows"], sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
