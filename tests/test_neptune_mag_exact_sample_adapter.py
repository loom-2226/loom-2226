import unittest

from src.loom_neptune_mag_exact_sample_adapter import (
    HistoricalMagneticFieldSample,
    NeptuneMagExactSampleProvider,
)
from src.loom_planetary_environment import EnvironmentQuery


class NeptuneMagExactSampleAdapterTests(unittest.TestCase):
    def setUp(self):
        self.sample = HistoricalMagneticFieldSample(
            body_id="NE",
            epoch_utc="1989-08-25T03:56:00Z",
            reference_frame="NEPTUNE_LONGITUDE_SYSTEM",
            position_km=(24765.0, 0.0, 0.0),
            magnetic_field_nt=(100.0, -20.0, 5.0),
            source_id="QUALIFICATION_FIXTURE_NOT_PDS_OBSERVATION",
            sample_cadence_s=12.0,
            coordinate_semantics="R_RADIAL_OUTWARD_PHI_EAST_LONGITUDINAL_THETA_COLATITUDINAL",
        )
        self.provider = NeptuneMagExactSampleProvider(self.sample)

    def test_exact_sample_maps_vector_nt_to_tesla(self):
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc=self.sample.epoch_utc,
            reference_frame=self.sample.reference_frame,
            position_km=self.sample.position_km,
        )
        state = self.provider.environment_state(query)
        expected = (1.0e-7, -2.0e-8, 5.0e-9)
        self.assertIsNotNone(state.magnetic_field_t)
        for actual, target in zip(state.magnetic_field_t, expected):
            self.assertAlmostEqual(actual, target, places=18)
        self.assertIsNone(state.plasma_number_density_m3)
        self.assertIsNone(state.mass_density_kg_m3)
        self.assertEqual(state.provenance.source_ids, (self.sample.source_id,))
        self.assertEqual(state.uncertainty.model_class, "HISTORICAL_MEASURED_EXACT_SAMPLE_NO_INTERPOLATION")

    def test_epoch_mismatch_fails_closed(self):
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame=self.sample.reference_frame,
            position_km=self.sample.position_km,
        )
        with self.assertRaises(ValueError):
            self.provider.environment_state(query)

    def test_position_or_frame_mismatch_fails_closed(self):
        wrong_position = EnvironmentQuery(
            body_id="NE",
            epoch_utc=self.sample.epoch_utc,
            reference_frame=self.sample.reference_frame,
            position_km=(24766.0, 0.0, 0.0),
        )
        with self.assertRaises(ValueError):
            self.provider.environment_state(wrong_position)

        wrong_frame = EnvironmentQuery(
            body_id="NE",
            epoch_utc=self.sample.epoch_utc,
            reference_frame="J2000/ECLIPTIC",
            position_km=self.sample.position_km,
        )
        with self.assertRaises(ValueError):
            self.provider.environment_state(wrong_frame)

    def test_authority_stays_historical_only(self):
        self.assertEqual(self.provider.spatial_interpolation_authority, "ZERO")
        self.assertEqual(self.provider.temporal_extrapolation_authority, "ZERO")
        self.assertEqual(self.provider.endpoint_2226_authority, "ZERO")
        self.assertEqual(self.provider.admissibility_authority, "ZERO")
        self.assertEqual(self.provider.loom_coherence_authority, "ZERO")


if __name__ == "__main__":
    unittest.main()
