from pathlib import Path
import math
import unittest

from loom.application.contracts import SpatialState
from loom.navigation.targeting import NavigationTargetAdapter
from loom.spatial.celestial_state import CANONICAL_FRAME
from loom.spatial.sqlite_infrastructure_catalog import (
    SQLiteInfrastructureCatalog,
    SQLiteInfrastructureCatalogError,
)


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "data" / "LOOM_2226.sqlite3"
EPOCH = "2226-08-29T05:00:00Z"


PARENT_STATES = {
    "EA": SpatialState(
        entity_id="EA",
        epoch_utc=EPOCH,
        reference_frame=CANONICAL_FRAME,
        position_km=(100_000_000.0, 20_000_000.0, -5_000_000.0),
        velocity_km_s=(1.0, 29.0, 0.2),
        provenance={"state_source": "TEST_SHARED_PARENT"},
        navigation_grade=True,
    ),
    "LU": SpatialState(
        entity_id="LU",
        epoch_utc=EPOCH,
        reference_frame=CANONICAL_FRAME,
        position_km=(100_384_400.0, 20_000_000.0, -5_000_000.0),
        velocity_km_s=(1.0, 30.0, 0.2),
        provenance={"state_source": "TEST_SHARED_PARENT"},
        navigation_grade=False,
    ),
}


def parent_resolver(entity_id: str, epoch_utc: str) -> SpatialState:
    if epoch_utc != EPOCH:
        raise AssertionError("test parent resolver received unexpected epoch")
    return PARENT_STATES[entity_id]


class SQLiteInfrastructureCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = SQLiteInfrastructureCatalog(WORLD, parent_resolver)

    def test_describes_world_identity_without_inventing_parallel_target(self):
        d = self.catalog.describe_target("EAR-O01")
        self.assertEqual(d["target_id"], "EAR-O01")
        self.assertEqual(d["display_name"], "LEO Atlantic Exchange")
        self.assertEqual(d["parent_body"], "EA")
        self.assertEqual(d["location_model_id"], "PM-PLANETOCENTRIC_LOW_ORBIT-v1")
        self.assertEqual(d["orbit_family"], "KEPLERIAN_PLANETOCENTRIC_LOW_ORBIT")
        self.assertFalse(d["navigation_grade"])

    def test_ear_o01_resolves_from_world_elements_and_shared_parent_state(self):
        state = self.catalog.resolve_target_state("EAR-O01", EPOCH)
        parent = PARENT_STATES["EA"]
        rel_p = tuple(state.position_km[i] - parent.position_km[i] for i in range(3))
        rel_v = tuple(state.velocity_km_s[i] - parent.velocity_km_s[i] for i in range(3))
        self.assertAlmostEqual(math.sqrt(sum(v*v for v in rel_p)), 6880.689072, places=6)
        self.assertGreater(math.sqrt(sum(v*v for v in rel_v)), 1.0)
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertFalse(state.navigation_grade)
        self.assertEqual(state.provenance["state_source"], "WORLD_ORBIT_GEOMETRY_PARENT_CENTRIC_KEPLER")
        self.assertEqual(state.provenance["output_track_frame"], "ECLIPJ2000_PARENT_CENTERED")

    def test_representative_conventional_orbiters_all_resolve_nonzero_velocity(self):
        expected = {
            "EAR-O01": "EA",
            "EAR-O03": "EA",
            "EAR-O05": "EA",
            "LOR-P01": "LU",
        }
        for entity_id, parent_id in expected.items():
            with self.subTest(entity_id=entity_id):
                state = self.catalog.resolve_target_state(entity_id, EPOCH)
                parent = PARENT_STATES[parent_id]
                rel_v = tuple(state.velocity_km_s[i] - parent.velocity_km_s[i] for i in range(3))
                self.assertGreater(math.sqrt(sum(v*v for v in rel_v)), 0.1)
                self.assertFalse(state.navigation_grade)
                self.assertEqual(state.provenance["parent_entity_id"], parent_id)

    def test_same_target_epoch_is_deterministic(self):
        a = self.catalog.resolve_target_state("EAR-O03", EPOCH)
        b = self.catalog.resolve_target_state("EAR-O03", EPOCH)
        self.assertEqual(a, b)

    def test_surface_and_cr3bp_models_fail_closed_in_conventional_resolver(self):
        for entity_id in ("EAR-S06", "MCH-P03"):
            with self.subTest(entity_id=entity_id):
                with self.assertRaises(SQLiteInfrastructureCatalogError):
                    self.catalog.resolve_target_state(entity_id, EPOCH)

    def test_navigation_adapter_returns_shared_state_unchanged(self):
        adapter = NavigationTargetAdapter(self.catalog)
        direct = self.catalog.resolve_target_state("EAR-O05", EPOCH)
        through_nav = adapter.resolve_target_state("EAR-O05", EPOCH)
        self.assertEqual(through_nav, direct)


if __name__ == "__main__":
    unittest.main()
