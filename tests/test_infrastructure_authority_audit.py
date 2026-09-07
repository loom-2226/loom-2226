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
        summary = result["summary"]

        self.assertEqual(result["contract"], MATRIX_CONTRACT)
        self.assertEqual(summary["row_count"], 127)
        self.assertEqual(len(result["rows"]), 127)
        self.assertTrue(all("node_id" in row and "entity_id" in row for row in result["rows"]))
        self.assertTrue(all(row["surface_coordinates_structured"] is False for row in result["rows"]))
        self.assertTrue(all(row["docking_transition_geometry_structured"] is False for row in result["rows"]))

        # Exact governed WORLD authority: all infrastructure placements are still
        # engineering references, complete enough to constrain design but not
        # navigation-grade and therefore not directly usable as Navigator truth.
        self.assertEqual(summary["position_authority"], {"ENGINEERING_REFERENCE": 127})
        self.assertEqual(summary["location_navigation_grade"], {"False": 127})
        self.assertEqual(summary["orbit_navigation_grade"], {"False": 127})
        self.assertEqual(summary["state_navigation_grade"], {"False": 127})
        self.assertEqual(summary["state_authority"], {"AUTHORITATIVE_NON_NAVIGATION_GRADE": 127})
        self.assertEqual(summary["spatial_derivability_initial"], {"CONSTRAINED_DESIGN_REQUIRED": 127})
        self.assertEqual(summary["simulator_navigation_readiness"], {"NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED": 127})

        # Frame-method compatibility is a separate question from navigation grade.
        # 66 rows use declared inertial frame families compatible with the current
        # translation-only method; 61 use rotating/body-fixed families that require
        # additional transform authority. This does not promote any row to nav grade.
        self.assertEqual(
            summary["runtime_frame_method_compatibility"],
            {
                "CURRENT_TRANSLATION_ONLY_INERTIAL_METHOD_COMPATIBLE": 66,
                "ROTATING_OR_BODY_FIXED_METHOD_UNSUPPORTED": 61,
            },
        )
        self.assertEqual(summary["frame_family"]["PARENT_BODY_FIXED"], 53)
        self.assertEqual(summary["keplerian_orbit_definition_complete"], {"False": 63, "True": 64})

        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in result["rows"]:
            grouped[row["simulator_navigation_readiness"]].append(
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

        print("F_PA_INFRASTRUCTURE_MATRIX_SUMMARY=" + json.dumps(summary, sort_keys=True))
        print("F_PA_NAVIGATION_READINESS_GROUPS=" + json.dumps(compact, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
