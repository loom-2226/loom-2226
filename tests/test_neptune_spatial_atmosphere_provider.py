import unittest

from src.loom_neptune_spatial_atmosphere import NeptuneSpatialAtmosphereProvider
from src.loom_planetary_environment import EnvironmentQuery
from src.loom_spatial_state_authority import CANONICAL_FRAME, SpatialState


class FakeResolver:
    def __init__(self, position_km=(1000.0, 2000.0, 3000.0), frame=CANONICAL_FRAME, grade=True):
        self.position_km = position_km
        self.frame = frame
        self.grade = grade

    def resolve(self, entity_id, epoch_utc):
        if entity_id != "NE":
            return None
        return SpatialState(
            entity_id="NE",
            epoch_utc=epoch_utc,
            reference_frame=self.frame,
            position_km=self.position_km,
            velocity_km_s=(0.0, 0.0, 0.0),
            provenance={"state_source": "TEST"},
            navigation_grade=self.grade,
            payload={"state_class": "CELESTIAL"},
        )


class TestNeptuneSpatialAtmosphereProvider(unittest.TestCase):
    def test_above_reference_radius_is_derived_from_neptune_center(self):
        provider = NeptuneSpatialAtmosphereProvider(FakeResolver())
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame=CANONICAL_FRAME,
            position_km=(1000.0 + 24622.0 + 1500.0, 2000.0, 3000.0),
        )
        assessment = provider.spatial_assessment(query)
        self.assertAlmostEqual(assessment.relative_radius_km, 26122.0)
        self.assertAlmostEqual(assessment.altitude_from_reference_mean_radius_km, 1500.0)
        self.assertEqual(assessment.geometry_regime, "ABOVE_REFERENCE_MEAN_RADIUS_GEOMETRY")

        state = provider.environment_state(query)
        self.assertEqual(state.atmospheric_regime, "BULK_REFERENCE_H2_HE_CH4_DOMINATED_ATMOSPHERE")
        self.assertIsNone(state.mass_density_kg_m3)

    def test_reference_radius_geometry_is_not_an_atmospheric_cutoff(self):
        provider = NeptuneSpatialAtmosphereProvider(FakeResolver())
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame=CANONICAL_FRAME,
            position_km=(1000.0 + 24622.0, 2000.0, 3000.0),
        )
        state = provider.environment_state(query)
        self.assertIn("MEAN_RADIUS_IS_REFERENCE_GEOMETRY_NOT_ATMOSPHERIC_BOUNDARY", state.uncertainty.notes)
        self.assertIsNone(state.mass_density_kg_m3)
        self.assertIsNone(state.magnetic_field_t)
        self.assertIsNone(state.plasma_number_density_m3)
        self.assertIsNone(state.ionizing_radiation_dose_rate_gy_s)

    def test_fail_closed_on_wrong_frame_or_unqualified_center(self):
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame="OTHER",
            position_km=(0.0, 0.0, 0.0),
        )
        with self.assertRaises(ValueError):
            NeptuneSpatialAtmosphereProvider(FakeResolver()).environment_state(query)

        canonical_query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame=CANONICAL_FRAME,
            position_km=(0.0, 0.0, 0.0),
        )
        with self.assertRaises(ValueError):
            NeptuneSpatialAtmosphereProvider(FakeResolver(grade=False)).environment_state(canonical_query)


if __name__ == "__main__":
    unittest.main()
