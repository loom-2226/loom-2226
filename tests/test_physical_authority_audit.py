from __future__ import annotations

from pathlib import Path
import json
import unittest

from loom.physical_authority_audit import AUDIT_CONTRACT, audit_pair


class PhysicalAuthorityAuditTests(unittest.TestCase):
    def test_exact_repo_sqlite_inventory(self) -> None:
        root = Path(__file__).resolve().parents[1]
        world = root / "data" / "LOOM_2226.sqlite3"
        civ = root / "data" / "LOOM_2226_CIVSTATE.sqlite3"
        result = audit_pair(world, civ)
        self.assertEqual(result["contract"], AUDIT_CONTRACT)
        self.assertGreater(result["world"]["table_count"], 0)
        self.assertGreater(result["civstate"]["table_count"], 0)
        self.assertIn("infrastructure_nodes", result["world"]["tables"])
        self.assertIn("spatial_states", result["world"]["tables"])
        self.assertIn("ephemeris_states", result["world"]["tables"])
        summary = {
            "contract": result["contract"],
            "world_sha256": result["world"]["sha256"],
            "world_size_bytes": result["world"]["size_bytes"],
            "world_table_count": result["world"]["table_count"],
            "civstate_sha256": result["civstate"]["sha256"],
            "civstate_size_bytes": result["civstate"]["size_bytes"],
            "civstate_table_count": result["civstate"]["table_count"],
            "world_feature_hits": result["world"]["feature_hits"],
            "civstate_feature_hits": result["civstate"]["feature_hits"],
            "key_world_tables": {
                name: {
                    "row_count": result["world"]["tables"][name]["row_count"],
                    "columns": result["world"]["tables"][name]["columns"],
                }
                for name in (
                    "infrastructure_nodes",
                    "spatial_states",
                    "ephemeris_states",
                    "celestial_dynamics",
                    "entity_location_models",
                    "placement_models",
                    "orbit_geometry_models",
                    "orbit_snapshots",
                    "transport_hubs",
                )
                if name in result["world"]["tables"]
            },
        }
        print("F_PA_EXACT_GIT_SQLITE_AUDIT=" + json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
