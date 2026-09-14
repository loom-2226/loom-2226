import unittest

from src.loom_planetary_environment import EnvironmentQuery
from src.loom_neptune_atmosphere_reference_provider import NeptuneAtmosphereReferenceProvider


class TestNeptuneAtmosphereReferenceProvider(unittest.TestCase):
    def setUp(self):
        self.provider = NeptuneAtmosphereReferenceProvider()
        self.query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame="J2000",
            position_km=(26085.768742219727, 0.0, 0.0),
        )

    def test_returns_only_earned_bulk_atmosphere_reference(self):
        state = self.provider.environment_state(self.query)
        self.assertEqual(
            state.atmospheric_regime,
            "BULK_REFERENCE_H2_HE_CH4_DOMINATED_ATMOSPHERE",
        )
        self.assertIsNone(state.mass_density_kg_m3)
        self.assertIsNone(state.magnetic_field_t)
        self.assertIsNone(state.plasma_number_density_m3)
        self.assertIsNone(state.ionizing_radiation_dose_rate_gy_s)

    def test_reference_is_explicitly_not_local_2226_endpoint_state(self):
        state = self.provider.environment_state(self.query)
        self.assertEqual(
            state.provenance.qualification,
            "BODY_LEVEL_REFERENCE_ONLY_NOT_LOCAL_2226_ENDPOINT_STATE",
        )
        self.assertIn("NASA_NEPTUNE_FACTS", state.provenance.source_ids)
        self.assertIn("VOYAGER2_RADIO_OCCULTATION", state.provenance.source_ids)
        self.assertIn("NO_LOCAL_DENSITY_MODEL", state.uncertainty.notes)
        self.assertIn("NO_2226_ATMOSPHERIC_PROFILE", state.uncertainty.notes)
        self.assertIsNone(state.uncertainty.numeric_envelope)

    def test_rejects_non_neptune_queries(self):
        bad = EnvironmentQuery(
            body_id="CE",
            epoch_utc=self.query.epoch_utc,
            reference_frame=self.query.reference_frame,
            position_km=self.query.position_km,
        )
        with self.assertRaises(ValueError):
            self.provider.environment_state(bad)


if __name__ == "__main__":
    unittest.main()
