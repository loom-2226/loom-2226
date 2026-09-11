from pathlib import Path
import json
import sqlite3
import tempfile
import unittest

from loom.application.contracts import SpatialState
from loom.navigation.targeting import NavigationTargetAdapter
from loom.spatial.earth_luna_router import EarthLunaTargetRouter
from loom.spatial.geometry_catalog import build_earth_luna_geometry_db
from loom.spatial.hud_objects import HUDInfrastructureObjectAdapter
from loom.spatial.sqlite_infrastructure_catalog import SQLiteInfrastructureCatalog


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"
SEED = ROOT / "geometry" / "earth_luna_spatial_geometry_seed.sql"
EPOCH = "2226-08-29T05:00:00Z"


def body_state(entity_id: str, epoch_utc: str) -> SpatialState:
    base = {
        "EA": ((100_000_000.0, 20_000_000.0, 0.0), (0.0, 29.0, 0.0)),
        "LU": ((100_384_400.0, 20_000_000.0, 0.0), (0.0, 30.0, 0.0)),
    }
    p, v = base[entity_id]
    return SpatialState(
        entity_id=entity_id,
        epoch_utc=epoch_utc,
        reference_frame="J2000/ECLIPTIC",
        position_km=p,
        velocity_km_s=v,
        provenance={"state_source": "TEST_SHARED_BODY_STATE"},
        navigation_grade=True,
    )


class _StandardOrbitStub:
    def describe_target(self, target_id: str):
        return {"contract": "LOOM_SPATIAL_TARGET_V1", "target_id": target_id, "target_type": "STANDARD_ORBIT"}

    def resolve_target_state(self, target_id: str, epoch_utc: str):
        return SpatialState(
            entity_id=target_id,
            epoch_utc=epoch_utc,
            reference_frame="J2000/ECLIPTIC",
            position_km=(1.0, 2.0, 3.0),
            velocity_km_s=(0.0, 1.0, 0.0),
            provenance={"state_source": "TEST_STANDARD_ORBIT_RESOLVER"},
            navigation_grade=False,
        )


class EarthLunaHandoffReadyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.geometry = Path(self.tmp.name) / "LOOM_2226_SPATIAL_GEOMETRY.sqlite3"
        build_earth_luna_geometry_db(WORLD, SEED, self.geometry)
        self.facilities = SQLiteInfrastructureCatalog(WORLD, body_state)
        self.hud = HUDInfrastructureObjectAdapter(WORLD, self.facilities, geometry_db_path=self.geometry)
        self.router = EarthLunaTargetRouter(self.geometry, self.facilities, _StandardOrbitStub())

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_world_facilities_receive_non_authoritative_procedural_visual_proxy(self):
        with sqlite3.connect(self.geometry) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM procedural_visual_proxies ORDER BY object_id").fetchall()
            facility_count = conn.execute("SELECT COUNT(*) FROM spatial_objects WHERE object_kind='FACILITY'").fetchone()[0]
        self.assertEqual(len(rows), facility_count)
        self.assertEqual(facility_count, 31)
        for row in rows:
            self.assertEqual(row["geometry_authority"], "VISUALIZATION_ONLY")
            self.assertEqual(row["navigation_authority"], 0)
            self.assertEqual(row["canon_geometry"], 0)
            components = json.loads(row["component_json"])
            self.assertGreater(len(components), 0)
            self.assertTrue(all("primitive" in item for item in components))

    def test_orbital_facilities_get_actual_3d_proxy_role_not_only_symbol(self):
        with sqlite3.connect(self.geometry) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM procedural_visual_proxies WHERE object_id='EAR-O01'").fetchone()
            roles = {r[0] for r in conn.execute("SELECT geometry_role FROM geometry_assets WHERE object_id='EAR-O01'")}
        self.assertIsNotNone(row)
        self.assertEqual(row["proxy_archetype"], "HABITAT_PORT")
        self.assertIn("RENDER_LOW", roles)
        self.assertIn("HUD_SYMBOLIC", roles)

    def test_proxy_geometry_is_normalized_and_does_not_claim_metric_station_dimensions(self):
        with sqlite3.connect(self.geometry) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM procedural_visual_proxies WHERE object_id='EAR-O01'").fetchone()
        self.assertEqual(row["scale_basis"], "NORMALIZED_PRESENTATION_UNITS")
        self.assertIsNone(row["physical_scale_m"])
        text = row["component_json"]
        self.assertNotIn('"meters"', text)
        self.assertNotIn('"metres"', text)

    def test_hud_object_exposes_proxy_without_promoting_navigation_authority(self):
        obj = self.hud.describe_object("EAR-O01")
        proxy = obj["geometry"]["visual_proxy"]
        self.assertEqual(proxy["proxy_archetype"], "HABITAT_PORT")
        self.assertEqual(proxy["geometry_authority"], "VISUALIZATION_ONLY")
        self.assertFalse(proxy["navigation_authority"])
        self.assertFalse(proxy["canon_geometry"])
        self.assertGreater(len(proxy["components"]), 0)

    def test_router_dispatches_facility_and_standard_orbit_through_existing_resolvers(self):
        facility = self.router.resolve_target_state("EAR-O01", EPOCH)
        expected = self.facilities.resolve_target_state("EAR-O01", EPOCH)
        self.assertEqual(facility, expected)
        orbit = self.router.resolve_target_state("ORB-EA-LEO-400", EPOCH)
        self.assertEqual(orbit.entity_id, "ORB-EA-LEO-400")
        self.assertEqual(orbit.provenance["state_source"], "TEST_STANDARD_ORBIT_RESOLVER")

    def test_navigator_adapter_can_use_unified_earth_luna_router_without_recomputing_state(self):
        nav = NavigationTargetAdapter(self.router)
        state = nav.resolve_target_state("EAR-O01", EPOCH)
        self.assertEqual(state, self.facilities.resolve_target_state("EAR-O01", EPOCH))
        described = nav.describe_target("ORB-LU-LLO-100")
        self.assertEqual(described["target_type"], "STANDARD_ORBIT")

    def test_router_lists_facilities_and_standard_orbits_from_geometry_registry(self):
        objects = self.router.list_targets()
        ids = {row["target_id"] for row in objects}
        self.assertIn("EAR-O01", ids)
        self.assertIn("LOR-P01", ids)
        self.assertIn("ORB-EA-LEO-400", ids)
        self.assertIn("ORB-LU-LLO-100", ids)
        self.assertEqual(len([row for row in objects if row["target_type"] == "FACILITY"]), 31)
        self.assertEqual(len([row for row in objects if row["target_type"] == "STANDARD_ORBIT"]), 9)


if __name__ == "__main__":
    unittest.main()
