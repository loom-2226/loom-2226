import json
import math
from pathlib import Path
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.targets import (
    SpatialTarget,
    SpatialTargetCatalog,
    SpatialTargetError,
    SpatialTargetResolver,
    TargetStateUnavailable,
    load_target_catalog,
)


EPOCH = "2226-01-01T00:00:00Z"


class SpatialTargetResolverTests(unittest.TestCase):
    def setUp(self):
        self.body_states = {
            "EA": SpatialState(
                entity_id="EA",
                epoch_utc=EPOCH,
                reference_frame="J2000/ECLIPTIC",
                position_km=(1000000.0, 2000000.0, 3000000.0),
                velocity_km_s=(1.0, 2.0, 3.0),
                provenance={"state_source": "TEST_BODY_STATE"},
                navigation_grade=True,
            ),
            "LU": SpatialState(
                entity_id="LU",
                epoch_utc=EPOCH,
                reference_frame="J2000/ECLIPTIC",
                position_km=(1384400.0, 2000000.0, 3000000.0),
                velocity_km_s=(1.0, 3.0, 3.0),
                provenance={"state_source": "TEST_BODY_STATE"},
                navigation_grade=True,
            ),
        }
        # Test-only authoritative-property fixture. Runtime target code must not
        # define Earth/Moon GM constants of its own.
        self.body_properties = {
            "EA": {"radius_km": 6378.137, "mu_km3_s2": 398600.435436, "source": "TEST"},
            "LU": {"radius_km": 1737.4, "mu_km3_s2": 4902.800118, "source": "TEST"},
        }
        catalog_path = Path(__file__).resolve().parents[1] / "src" / "loom" / "spatial" / "catalogs" / "earth_luna_v0.1.json"
        self.catalog = load_target_catalog(catalog_path)
        self.resolver = SpatialTargetResolver(
            self.catalog,
            body_state_resolver=lambda body_id, epoch: self.body_states[body_id],
            body_property_resolver=lambda body_id: self.body_properties[body_id],
        )

    def _relative(self, state, body_id):
        body = self.body_states[body_id]
        return tuple(state.position_km[i] - body.position_km[i] for i in range(3)), tuple(
            state.velocity_km_s[i] - body.velocity_km_s[i] for i in range(3)
        )

    def test_earth_400km_reference_orbit_resolves_circular(self):
        state = self.resolver.resolve_target_state("EARTH_LEO_400_REFERENCE", EPOCH)
        rel_p, rel_v = self._relative(state, "EA")
        radius = math.sqrt(sum(x * x for x in rel_p))
        speed = math.sqrt(sum(x * x for x in rel_v))
        expected_radius = self.body_properties["EA"]["radius_km"] + 400.0
        expected_speed = math.sqrt(self.body_properties["EA"]["mu_km3_s2"] / expected_radius)
        self.assertAlmostEqual(radius, expected_radius, places=6)
        self.assertAlmostEqual(speed, expected_speed, places=9)
        self.assertAlmostEqual(sum(rel_p[i] * rel_v[i] for i in range(3)), 0.0, places=6)

    def test_lunar_100km_reference_orbit_resolves_circular(self):
        state = self.resolver.resolve_target_state("LUNA_LLO_100_REFERENCE", EPOCH)
        rel_p, rel_v = self._relative(state, "LU")
        radius = math.sqrt(sum(x * x for x in rel_p))
        expected = self.body_properties["LU"]["radius_km"] + 100.0
        self.assertAlmostEqual(radius, expected, places=6)
        self.assertGreater(math.sqrt(sum(x * x for x in rel_v)), 0.0)

    def test_station_is_phased_on_declared_orbit_and_not_body_center(self):
        state = self.resolver.resolve_target_state("EARTH_STATION_QUAL_01", EPOCH)
        rel_p, rel_v = self._relative(state, "EA")
        radius = math.sqrt(sum(x * x for x in rel_p))
        self.assertAlmostEqual(radius, self.body_properties["EA"]["radius_km"] + 400.0, places=6)
        self.assertGreater(radius, 0.0)
        self.assertGreater(math.sqrt(sum(x * x for x in rel_v)), 0.0)
        self.assertEqual(state.payload["orbit_id"], "EARTH_LEO_400_REFERENCE")
        self.assertEqual(state.payload["target_type"], "ORBITAL_STATION")

    def test_resolution_is_deterministic_and_consumer_independent(self):
        manual = self.resolver.resolve_target_state("LUNA_STATION_QUAL_01", EPOCH)
        llm = self.resolver.resolve_target_state("LUNA_STATION_QUAL_01", EPOCH)
        npc = self.resolver.resolve_target_state("LUNA_STATION_QUAL_01", EPOCH)
        self.assertEqual(manual, llm)
        self.assertEqual(llm, npc)

    def test_provenance_survives_resolution(self):
        state = self.resolver.resolve_target_state("EARTH_LEO_400_REFERENCE", EPOCH)
        self.assertEqual(state.provenance["target_catalog"], "LOOM_EARTH_LUNA_TARGET_CATALOG_V0_1")
        self.assertEqual(state.provenance["central_body_property_source"], "TEST")
        self.assertIn("target_provenance", state.provenance)
        self.assertFalse(state.navigation_grade)

    def test_unknown_target_fails_closed(self):
        with self.assertRaises(SpatialTargetError):
            self.resolver.resolve_target_state("DOES_NOT_EXIST", EPOCH)

    def test_surface_port_fails_closed_without_body_fixed_transform(self):
        target = SpatialTarget.from_mapping({
            "target_id": "TEST_SURFACE_PORT",
            "target_type": "GROUND_PORT",
            "display_name": "Test-only surface port",
            "parent_body": "EA",
            "reference_frame": "EARTH_BODY_FIXED",
            "status": "NON_CANON",
            "state_availability": "REQUIRES_BODY_FIXED_TRANSFORM",
            "state_method": "BODY_FIXED_GEODETIC",
            "navigation_grade": False,
            "provenance": {"source": "UNIT_TEST_ONLY"},
            "operational_metadata": {},
            "surface_location": {
                "latitude_deg": 0.0,
                "longitude_deg": 0.0,
                "elevation_m": 0.0,
                "reference_datum": "TEST_DATUM"
            }
        })
        catalog = SpatialTargetCatalog(
            catalog_id="TEST",
            version="1",
            targets={target.target_id: target},
            provenance={"source": "UNIT_TEST"},
        )
        resolver = SpatialTargetResolver(
            catalog,
            body_state_resolver=lambda body_id, epoch: self.body_states[body_id],
            body_property_resolver=lambda body_id: self.body_properties[body_id],
        )
        with self.assertRaises(TargetStateUnavailable):
            resolver.resolve_target_state("TEST_SURFACE_PORT", EPOCH)

    def test_catalog_does_not_embed_gravitational_constants(self):
        path = Path(__file__).resolve().parents[1] / "src" / "loom" / "spatial" / "catalogs" / "earth_luna_v0.1.json"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("mu_km3_s2", text)
        self.assertNotIn("398600", text)
        self.assertNotIn("4902.8", text)

    def test_ground_and_surface_catalogs_are_explicitly_empty_not_fabricated(self):
        path = Path(__file__).resolve().parents[1] / "src" / "loom" / "spatial" / "catalogs" / "earth_luna_v0.1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["earth_ground_ports"], [])
        self.assertEqual(payload["lunar_surface_ports"], [])
        self.assertEqual(payload["surface_resolution_status"], "UNAVAILABLE_PENDING_GOVERNED_PORTS_AND_BODY_ORIENTATION")


if __name__ == "__main__":
    unittest.main()
