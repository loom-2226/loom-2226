import unittest

from loom.application.contracts import SpatialState
from loom.navigation.targeting import NavigationTargetAdapter, NavigationTargetError


EPOCH = "2226-01-01T00:00:00Z"


class _Resolver:
    def describe_target(self, target_id):
        if target_id == "BAD":
            raise RuntimeError("unknown")
        return {"contract": "LOOM_SPATIAL_TARGET_V1", "target_id": target_id, "state_availability": "RESOLVABLE"}

    def resolve_target_state(self, target_id, epoch_utc):
        if target_id == "BAD":
            raise RuntimeError("unknown")
        return SpatialState(
            entity_id=target_id,
            epoch_utc=epoch_utc,
            reference_frame="J2000/ECLIPTIC",
            position_km=(1.0, 2.0, 3.0),
            velocity_km_s=(4.0, 5.0, 6.0),
            provenance={"state_source": "TEST"},
            navigation_grade=False,
        )


class NavigationTargetAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = NavigationTargetAdapter(_Resolver())

    def test_resolves_same_spatial_state_without_recomputing_physics(self):
        state = self.adapter.resolve_target_state("EARTH_STATION_QUAL_01", EPOCH)
        self.assertEqual(state.entity_id, "EARTH_STATION_QUAL_01")
        self.assertEqual(state.position_km, (1.0, 2.0, 3.0))
        self.assertEqual(state.velocity_km_s, (4.0, 5.0, 6.0))
        self.assertEqual(state.provenance["state_source"], "TEST")

    def test_adapter_has_no_caller_specific_state_path(self):
        first = self.adapter.resolve_target_state("EARTH_STATION_QUAL_01", EPOCH)
        second = self.adapter.resolve_target_state("EARTH_STATION_QUAL_01", EPOCH)
        self.assertEqual(first, second)

    def test_describe_delegates_to_spatial_contract(self):
        desc = self.adapter.describe_target("EARTH_STATION_QUAL_01")
        self.assertEqual(desc["contract"], "LOOM_SPATIAL_TARGET_V1")

    def test_resolution_failure_is_fail_closed(self):
        with self.assertRaises(NavigationTargetError):
            self.adapter.resolve_target_state("BAD", EPOCH)


if __name__ == "__main__":
    unittest.main()
