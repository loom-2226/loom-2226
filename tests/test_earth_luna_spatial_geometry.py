from pathlib import Path
import sqlite3
import tempfile
import unittest

from loom.spatial.geometry_catalog import build_earth_luna_geometry_db


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"
SEED = ROOT / "geometry" / "earth_luna_spatial_geometry_seed.sql"


def _build():
    tmp = tempfile.TemporaryDirectory()
    out = Path(tmp.name) / "LOOM_2226_SPATIAL_GEOMETRY.sqlite3"
    build_earth_luna_geometry_db(WORLD, SEED, out)
    conn = sqlite3.connect(out)
    conn.row_factory = sqlite3.Row
    return tmp, conn


class EarthLunaSpatialGeometryTests(unittest.TestCase):
    def test_world_backed_earth_luna_facilities_are_imported_without_renaming(self):
        tmp, conn = _build()
        try:
            rows = conn.execute(
                "SELECT object_id, object_kind, world_entity_id FROM spatial_objects "
                "WHERE world_entity_id IS NOT NULL ORDER BY object_id"
            ).fetchall()
            self.assertEqual(len(rows), 31)
            self.assertTrue(all(r["object_kind"] == "FACILITY" for r in rows))
            self.assertTrue(all(r["object_id"] == r["world_entity_id"] for r in rows))
            ids = {r["object_id"] for r in rows}
            self.assertTrue({"EAR-O01", "EAR-O05", "EAR-S06", "LOR-P01", "LSP-P01", "MCH-P02"} <= ids)
        finally:
            conn.close(); tmp.cleanup()

    def test_world_spatial_model_bindings_reference_existing_world_models_without_copying_state(self):
        tmp, conn = _build()
        try:
            rows = conn.execute("SELECT * FROM world_spatial_model_bindings ORDER BY object_id").fetchall()
            self.assertEqual(len(rows), 31)
            by_id = {r["object_id"]: r for r in rows}

            leo = by_id["EAR-O01"]
            self.assertEqual(leo["location_model_id"], "PM-PLANETOCENTRIC_LOW_ORBIT-v1")
            self.assertEqual(leo["frame_family"], "PARENT_EQUATORIAL_INERTIAL")
            self.assertEqual(leo["orbit_family"], "KEPLERIAN_PLANETOCENTRIC_LOW_ORBIT")
            self.assertEqual(leo["navigation_grade"], 0)

            surface = by_id["EAR-S06"]
            self.assertEqual(surface["location_model_id"], "PM-SURFACE_BODY_FIXED-v1")
            self.assertEqual(surface["frame_family"], "PARENT_BODY_FIXED")
            self.assertEqual(surface["orbit_family"], "SURFACE_FIXED")

            l2 = by_id["MCH-P03"]
            self.assertEqual(l2["frame_family"], "EARTH_MOON_ROTATING")
            self.assertEqual(l2["orbit_family"], "CR3BP_LINEARIZED_L2_REFERENCE")

            columns = {r[1].lower() for r in conn.execute("PRAGMA table_info(world_spatial_model_bindings)")}
            self.assertFalse({"semi_major_axis_km", "mean_anomaly_deg", "position_x_km", "velocity_x_km_s"} & columns)
        finally:
            conn.close(); tmp.cleanup()

    def test_standard_orbits_are_first_class_non_facility_targets(self):
        tmp, conn = _build()
        try:
            rows = conn.execute(
                "SELECT object_id, object_kind, parent_body_id, operational_role "
                "FROM spatial_objects WHERE object_kind='STANDARD_ORBIT' ORDER BY object_id"
            ).fetchall()
            ids = {r["object_id"] for r in rows}
            self.assertTrue({
                "ORB-EA-LEO-400", "ORB-EA-POLAR-500", "ORB-EA-MEO-20200",
                "ORB-EA-GEO-REF", "ORB-LU-LLO-100", "ORB-LU-POLAR-100",
                "ORB-LU-HIGH-1000",
            } <= ids)
            self.assertTrue(all(r["world_entity_id"] is None for r in conn.execute(
                "SELECT world_entity_id FROM spatial_objects WHERE object_kind='STANDARD_ORBIT'"
            )))
        finally:
            conn.close(); tmp.cleanup()

    def test_geometry_database_declares_definition_only_state_authority_boundary(self):
        tmp, conn = _build()
        try:
            metadata = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM runtime_metadata")}
            self.assertEqual(metadata["database_role"], "DEFINITION_AND_OPERATIONAL_GEOMETRY")
            self.assertEqual(metadata["state_authority"], "SHARED_SPATIAL_NAVIGATION_SERVICES")
            self.assertEqual(metadata["propagated_state_storage"], "FORBIDDEN")
            forbidden = {
                "position_x_km", "position_y_km", "position_z_km",
                "velocity_x_km_s", "velocity_y_km_s", "velocity_z_km_s",
                "x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s",
            }
            for table in (
                "spatial_objects", "facility_world_bindings", "world_spatial_model_bindings",
                "standard_orbits", "local_frames", "geometry_assets", "operational_interfaces",
                "approach_corridors", "keepout_volumes", "visual_profiles",
            ):
                columns = {r[1].lower() for r in conn.execute(f"PRAGMA table_info({table})")}
                self.assertFalse(columns & forbidden, (table, columns & forbidden))
        finally:
            conn.close(); tmp.cleanup()

    def test_geometry_assets_support_external_or_embedded_glb_without_making_render_mesh_navigation_authority(self):
        tmp, conn = _build()
        try:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(geometry_assets)")}
            self.assertTrue({"asset_uri", "asset_sha256", "asset_blob", "mime_type", "geometry_role"} <= cols)
            roles = {r[0] for r in conn.execute("SELECT DISTINCT geometry_role FROM geometry_assets")}
            self.assertIn("HUD_SYMBOLIC", roles)
            nav_roles = {r[0] for r in conn.execute("SELECT DISTINCT geometry_role FROM geometry_assets WHERE navigation_authority=1")}
            self.assertNotIn("RENDER_HIGH", nav_roles)
            self.assertNotIn("RENDER_LOW", nav_roles)
        finally:
            conn.close(); tmp.cleanup()

    def test_operational_geometry_tables_exist_for_future_hud_and_rendezvous_detail(self):
        tmp, conn = _build()
        try:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({
                "runtime_metadata", "spatial_objects", "standard_orbits", "facility_world_bindings",
                "world_spatial_model_bindings", "local_frames", "geometry_assets",
                "operational_interfaces", "approach_corridors", "keepout_volumes", "visual_profiles",
            } <= tables)
        finally:
            conn.close(); tmp.cleanup()

    def test_builder_is_deterministic_for_seeded_object_inventory(self):
        tmp1, conn1 = _build(); tmp2, conn2 = _build()
        try:
            q = "SELECT object_id,object_kind,parent_body_id,operational_role,status FROM spatial_objects ORDER BY object_id"
            a = [tuple(r) for r in conn1.execute(q)]
            b = [tuple(r) for r in conn2.execute(q)]
            self.assertEqual(a, b)
        finally:
            conn1.close(); conn2.close(); tmp1.cleanup(); tmp2.cleanup()


if __name__ == "__main__":
    unittest.main()
