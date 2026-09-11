from pathlib import Path
import tempfile
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.geometry_catalog import build_earth_luna_geometry_db
from loom.spatial.sqlite_standard_orbit_resolver import SQLiteStandardOrbitResolver

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"
SEED = ROOT / "geometry" / "earth_luna_spatial_geometry_seed.sql"
EPOCH = "2226-08-29T05:00:00Z"


def body_state(entity_id: str, epoch_utc: str) -> SpatialState:
    return SpatialState(
        entity_id=entity_id,
        epoch_utc=epoch_utc,
        reference_frame="J2000/ECLIPTIC",
        position_km=(100_000_000.0 if entity_id == "EA" else 100_384_400.0, 20_000_000.0, 0.0),
        velocity_km_s=(0.0, 29.0 if entity_id == "EA" else 30.0, 0.0),
        provenance={"state_source": "TEST_SHARED_BODY_STATE"},
        navigation_grade=True,
    )


def body_properties(entity_id: str):
    if entity_id == "EA":
        return {"radius_km": 6378.137, "mu_km3_s2": 398600.4355, "source": "TEST_WORLD_EQUIVALENT"}
    if entity_id == "LU":
        return {"radius_km": 1737.4, "mu_km3_s2": 4902.800118, "source": "TEST_WORLD_EQUIVALENT"}
    raise KeyError(entity_id)


class SQLiteStandardOrbitResolverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.geometry = Path(self.tmp.name) / "spatial.sqlite3"
        build_earth_luna_geometry_db(WORLD, SEED, self.geometry)
        self.resolver = SQLiteStandardOrbitResolver(self.geometry, body_state, body_properties)

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_nine_standard_orbits_are_describable(self):
        rows = self.resolver.list_targets()
        self.assertEqual(len(rows), 9)
        self.assertEqual({r["target_type"] for r in rows}, {"STANDARD_ORBIT"})

    def test_earth_and_lunar_reference_orbits_resolve_through_shared_propagator(self):
        earth = self.resolver.resolve_target_state("ORB-EA-LEO-400", EPOCH)
        moon = self.resolver.resolve_target_state("ORB-LU-LLO-100", EPOCH)
        self.assertEqual(earth.entity_id, "ORB-EA-LEO-400")
        self.assertEqual(moon.entity_id, "ORB-LU-LLO-100")
        self.assertNotEqual(earth.velocity_km_s, (0.0, 0.0, 0.0))
        self.assertNotEqual(moon.velocity_km_s, (0.0, 0.0, 0.0))
        self.assertFalse(earth.navigation_grade)
        self.assertFalse(moon.navigation_grade)

    def test_description_preserves_engineering_reference_status(self):
        desc = self.resolver.describe_target("ORB-EA-GEO-REF")
        self.assertEqual(desc["target_type"], "STANDARD_ORBIT")
        self.assertEqual(desc["status"], "ENGINEERING_REFERENCE")
        self.assertFalse(desc["navigation_grade"])
        self.assertEqual(desc["parent_body"], "EA")

    def test_unknown_or_non_orbit_id_fails_closed(self):
        with self.assertRaises(Exception):
            self.resolver.resolve_target_state("EAR-O01", EPOCH)
        with self.assertRaises(Exception):
            self.resolver.resolve_target_state("NO-SUCH-ORBIT", EPOCH)


if __name__ == "__main__":
    unittest.main()
