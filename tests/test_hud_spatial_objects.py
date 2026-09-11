from pathlib import Path
import tempfile
import unittest

from loom.application.contracts import SpatialState
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


class HUDInfrastructureObjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.geometry = Path(self.tmp.name) / "LOOM_2226_SPATIAL_GEOMETRY.sqlite3"
        build_earth_luna_geometry_db(WORLD, SEED, self.geometry)
        self.state_catalog = SQLiteInfrastructureCatalog(WORLD, body_state)
        self.adapter = HUDInfrastructureObjectAdapter(
            WORLD,
            self.state_catalog,
            geometry_db_path=self.geometry,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_describe_ear_o01_exposes_thin_world_backed_hud_contract(self):
        obj = self.adapter.describe_object("EAR-O01")
        self.assertEqual(obj["contract"], "LOOM_HUD_SPATIAL_OBJECT_V1")
        self.assertEqual(obj["detail_scope"], "THIN_WORLD_BACKED_V1")
        self.assertEqual(obj["detail_policy"], "STATION_COMPLEXITY_DEFERRED")
        self.assertEqual(obj["entity_id"], "EAR-O01")
        self.assertEqual(obj["display_name"], "LEO Atlantic Exchange")
        self.assertEqual(obj["facility_type"], "ORBITAL_HABITAT_PORT")
        self.assertEqual(obj["engineering"]["structural_archetype"], "HABITAT_PORT")
        self.assertIsNone(obj["engineering"]["characteristic_length_m"])
        self.assertEqual(obj["transport"]["local_traffic_class"], "EXTREME")
        self.assertEqual(obj["transport"]["loom_access"], "PRIMARY GATE")
        self.assertEqual(obj["media"]["asset_role"], "HERO")
        self.assertEqual(obj["media"]["review_status"], "APPROVED_REFERENCE")
        self.assertTrue(obj["media"]["media_key"])
        self.assertEqual(obj["geometry"]["object_id"], "EAR-O01")
        self.assertIn("HUD_SYMBOLIC", obj["geometry"]["available_roles"])
        self.assertEqual(obj["geometry"]["default_symbol"], "FACILITY")

    def test_boundary_note_prevents_station_complexity_from_being_implied(self):
        obj = self.adapter.describe_object("EAR-O01")
        note = obj["media"]["boundary_note"]
        self.assertIn("Exact physical scale", note)
        self.assertIn("berth count", note)
        self.assertIsNone(obj["engineering"]["dry_mass_kg"])
        self.assertIsNone(obj["engineering"]["pressurized_volume_m3"])

    def test_resolve_object_reuses_shared_spatial_state_unchanged(self):
        expected = self.state_catalog.resolve_target_state("EAR-O01", EPOCH)
        obj = self.adapter.resolve_object("EAR-O01", EPOCH)
        state = obj["spatial_state"]
        self.assertEqual(tuple(state["position_km"]), tuple(expected.position_km))
        self.assertEqual(tuple(state["velocity_km_s"]), tuple(expected.velocity_km_s))
        self.assertEqual(state["reference_frame"], expected.reference_frame)
        self.assertEqual(state["navigation_grade"], expected.navigation_grade)
        self.assertEqual(state["provenance"], expected.provenance)

    def test_metadata_description_does_not_require_state_resolvability(self):
        obj = self.adapter.describe_object("EAR-S06")
        self.assertEqual(obj["entity_id"], "EAR-S06")
        self.assertEqual(obj["facility_type"], "SURFACE_SPACEPORT")
        self.assertEqual(obj["state"]["availability"], "REQUIRES_SHARED_RESOLVER")
        self.assertNotIn("spatial_state", obj)

    def test_unknown_target_fails_closed(self):
        with self.assertRaises(Exception):
            self.adapter.describe_object("NO-SUCH-TARGET")


if __name__ == "__main__":
    unittest.main()
