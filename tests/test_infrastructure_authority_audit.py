from __future__ import annotations

from collections import defaultdict
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

        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in result["rows"]:
            grouped[row["runtime_frame_usability"]].append(
                {
                    "node_id": str(row["node_id"]),
                    "node_name": str(row["node_name"]),
                    "facility_type": str(row["facility_type"]),
                    "frame_family": str(row["frame_family"]),
                    "geometry_kind": str(row["geometry_kind"]),
                    "navigation_grade": str(row["state_navigation_grade_bool"]),
                }
            )

        compact = {key: grouped[key] for key in sorted(grouped)}
        self.assertEqual(sum(len(rows) for rows in compact.values()), 127)
        self.assertTrue(any(row["frame_family"] == "SURFACE_BODY_FIXED" for row in result["rows"]))
        self.assertTrue(any(row["frame_family"] == "CR3BP_ROTATING" for row in result["rows"]))

        # Evidence emission is deliberately non-presumptive: F-PA records the exact
        # Git database classification before adding stronger simulator-qualification gates.
        print("F_PA_INFRASTRUCTURE_MATRIX_SUMMARY=" + json.dumps(result["summary"], sort_keys=True))
        print("F_PA_RUNTIME_USABILITY_GROUPS=" + json.dumps(compact, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
