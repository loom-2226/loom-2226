from pathlib import Path
import tempfile
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.earth_luna_runtime import build_earth_luna_runtime
from loom.spatial.geometry_catalog import build_earth_luna_geometry_db

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


class EarthLunaRuntimeFactoryTests(unittest.TestCase):
    def test_factory_wires_registry_hud_scene_and_standard_orbits_without_duplicate_constants(self):
        with tempfile.TemporaryDirectory() as td:
            geometry = Path(td) / "spatial.sqlite3"
            build_earth_luna_geometry_db(WORLD, SEED, geometry)
            runtime = build_earth_luna_runtime(WORLD, geometry, body_state)
            self.assertEqual(len(runtime.router.list_targets()), 40)
            self.assertEqual(runtime.body_properties.get("EA")["radius_km"], 6371.0084)
            self.assertEqual(runtime.router.resolve_target_state("EAR-O01", EPOCH).entity_id, "EAR-O01")
            self.assertEqual(runtime.router.resolve_target_state("ORB-LU-LLO-100", EPOCH).entity_id, "ORB-LU-LLO-100")
            scene = runtime.scene.build_scene(EPOCH)
            self.assertEqual(scene["target_count"], 40)


if __name__ == "__main__":
    unittest.main()
