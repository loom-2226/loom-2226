import unittest

from src.loom_spatial_state_authority import (
    CANONICAL_FRAME,
    CelestialStateError,
    HybridCelestialStateService,
    ParentCentricOrbitModel,
    SpatialState,
)


class SpatialStateAuthorityTests(unittest.TestCase):
    def direct(self, entity_id, epoch):
        if entity_id != "EARTH":
            return None
        return SpatialState(
            entity_id="EARTH",
            epoch_utc=epoch,
            reference_frame=CANONICAL_FRAME,
            position_km=(1.0, 2.0, 3.0),
            velocity_km_s=(4.0, 5.0, 6.0),
            provenance={"state_source": "TEST_DIRECT"},
            navigation_grade=True,
        )

    def test_direct_state_preserves_position_velocity_epoch_frame_and_provenance(self):
        service = HybridCelestialStateService(self.direct, {})
        state = service.resolve("EARTH", "2226-08-22T00:00:00Z")
        self.assertEqual(state.position_km, (1.0, 2.0, 3.0))
        self.assertEqual(state.velocity_km_s, (4.0, 5.0, 6.0))
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertEqual(state.provenance["state_source"], "TEST_DIRECT")
        self.assertTrue(state.navigation_grade)

    def test_propagated_child_is_never_silently_navigation_grade(self):
        model = ParentCentricOrbitModel(
            entity_id="MOON",
            parent_entity_id="EARTH",
            element_epoch_utc="2226-08-22T00:00:00Z",
            semi_major_axis_km=384400.0,
            eccentricity=0.01,
            inclination_deg=5.0,
            raan_deg=0.0,
            arg_periapsis_deg=0.0,
            mean_anomaly_deg=0.0,
            parent_mu_km3_s2=398600.4418,
            model_id="TEST_MOON",
            provenance={"anchor": "TEST"},
            uncertainty={"unmodeled_perturbations": True},
        )
        service = HybridCelestialStateService(self.direct, {"MOON": model})
        state = service.resolve("MOON", "2226-08-22T01:00:00Z")
        self.assertFalse(state.navigation_grade)
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertEqual(state.provenance["state_source"], "PROPAGATED_PARENT_CENTRIC_KEPLER")
        self.assertEqual(state.provenance["parent_entity_id"], "EARTH")
        self.assertTrue(state.uncertainty["unmodeled_perturbations"])

    def test_unknown_body_fails_closed(self):
        service = HybridCelestialStateService(self.direct, {})
        with self.assertRaises(CelestialStateError):
            service.resolve("UNKNOWN", "2226-08-22T00:00:00Z")

    def test_wrong_direct_frame_fails_closed(self):
        def wrong_frame(entity_id, epoch):
            return SpatialState(entity_id, epoch, "WRONG", (0, 0, 0), (0, 0, 0), {}, True)
        service = HybridCelestialStateService(wrong_frame, {})
        with self.assertRaises(CelestialStateError):
            service.resolve("EARTH", "2226-08-22T00:00:00Z")

    def test_wrong_direct_epoch_fails_closed(self):
        def wrong_epoch(entity_id, epoch):
            return SpatialState(entity_id, "2226-08-23T00:00:00Z", CANONICAL_FRAME, (0, 0, 0), (0, 0, 0), {}, True)
        service = HybridCelestialStateService(wrong_epoch, {})
        with self.assertRaises(CelestialStateError):
            service.resolve("EARTH", "2226-08-22T00:00:00Z")

    def test_parent_cycle_fails_closed(self):
        def none(entity_id, epoch):
            return None
        common = dict(element_epoch_utc="2226-08-22T00:00:00Z", semi_major_axis_km=1000.0,
                      eccentricity=0.0, inclination_deg=0.0, raan_deg=0.0,
                      arg_periapsis_deg=0.0, mean_anomaly_deg=0.0,
                      parent_mu_km3_s2=1000.0)
        models = {
            "A": ParentCentricOrbitModel(entity_id="A", parent_entity_id="B", model_id="A", **common),
            "B": ParentCentricOrbitModel(entity_id="B", parent_entity_id="A", model_id="B", **common),
        }
        with self.assertRaises(CelestialStateError):
            HybridCelestialStateService(none, models).resolve("A", "2226-08-22T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
