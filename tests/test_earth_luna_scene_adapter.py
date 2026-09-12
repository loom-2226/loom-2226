from pathlib import Path
import tempfile
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.earth_luna_router import EarthLunaTargetRouter
from loom.spatial.earth_luna_scene import EarthLunaHUDSceneAdapter
from loom.spatial.geometry_catalog import build_earth_luna_geometry_db
from loom.spatial.hud_objects import HUDInfrastructureObjectAdapter
from loom.spatial.sqlite_infrastructure_catalog import SQLiteInfrastructureCatalog
from loom.spatial.sqlite_standard_orbit_resolver import SQLiteStandardOrbitResolver

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"
SEED = ROOT / "geometry" / "earth_luna_spatial_geometry_seed.sql"
EPOCH = "2226-08-29T05:00:00Z"


def body_state(entity_id: str, epoch_utc: str) -> SpatialState:
    values = {
        "EA": ((100_000_000.0, 20_000_000.0, 0.0), (0.0, 29.0, 0.0)),
        "LU": ((100_384_400.0, 20_000_000.0, 0.0), (0.0, 30.0, 0.0)),
    }
    p, v = values[entity_id]
    return SpatialState(entity_id=entity_id, epoch_utc=epoch_utc, reference_frame="J2000/ECLIPTIC", position_km=p, velocity_km_s=v, provenance={"state_source": "TEST"}, navigation_grade=True)


def body_properties(entity_id: str):
    return {
        "EA": {"radius_km": 6378.137, "mu_km3_s2": 398600.4355, "source": "TEST"},
        "LU": {"radius_km": 1737.4, "mu_km3_s2": 4902.800118, "source": "TEST"},
    }[entity_id]


class EarthLunaHUDSceneAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.geometry = Path(self.tmp.name) / "spatial.sqlite3"
        build_earth_luna_geometry_db(WORLD, SEED, self.geometry)
        facility = SQLiteInfrastructureCatalog(WORLD, body_state)
        orbit = SQLiteStandardOrbitResolver(self.geometry, body_state, body_properties)
        router = EarthLunaTargetRouter(self.geometry, facility, orbit)
        hud = HUDInfrastructureObjectAdapter(WORLD, facility, geometry_db_path=self.geometry)
        self.scene = EarthLunaHUDSceneAdapter(router, hud)

    def tearDown(self):
        self.tmp.cleanup()

    def test_scene_indexes_all_40_targets_without_fabricating_missing_state(self):
        payload = self.scene.build_scene(EPOCH)
        self.assertEqual(payload["contract"], "LOOM_EARTH_LUNA_SCENE_V1")
        self.assertEqual(payload["epoch_utc"], EPOCH)
        self.assertEqual(payload["target_count"], 40)
        self.assertEqual(len(payload["standard_orbits"]), 9)
        self.assertEqual(len(payload["facilities"]), 31)
        ear_o01 = next(x for x in payload["facilities"] if x["entity_id"] == "EAR-O01")
        ear_s06 = next(x for x in payload["facilities"] if x["entity_id"] == "EAR-S06")
        self.assertEqual(ear_o01["state"]["availability"], "RESOLVED")
        self.assertIn("spatial_state", ear_o01)
        self.assertEqual(ear_s06["state"]["availability"], "REQUIRES_SHARED_RESOLVER")
        self.assertNotIn("spatial_state", ear_s06)

    def test_scene_standard_orbits_have_resolved_state_and_ring_presentation(self):
        payload = self.scene.build_scene(EPOCH)
        leo = next(x for x in payload["standard_orbits"] if x["target_id"] == "ORB-EA-LEO-400")
        self.assertEqual(leo["state"]["availability"], "RESOLVED")
        self.assertEqual(leo["presentation"]["geometry_role"], "ORBIT_RING")
        self.assertEqual(leo["spatial_state"]["entity_id"], "ORB-EA-LEO-400")

    def test_scene_declares_authority_and_deferred_complexity_policy(self):
        payload = self.scene.build_scene(EPOCH)
        self.assertEqual(payload["state_authority"], "SHARED_SPATIAL_NAVIGATION_SERVICES")
        self.assertEqual(payload["geometry_authority"], "VISUALIZATION_ONLY_FOR_PROXIES")
        self.assertEqual(payload["station_detail_policy"], "STATION_COMPLEXITY_DEFERRED")


if __name__ == "__main__":
    unittest.main()
