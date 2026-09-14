import unittest

from src.loom_neptune_hydrostatic_reference_model import (
    NeptuneHydrostaticReferenceModel,
)


class NeptuneHydrostaticReferenceModelTests(unittest.TestCase):
    def setUp(self):
        self.model = NeptuneHydrostaticReferenceModel()

    def test_model_is_bounded_to_historical_reference_layer(self):
        self.assertEqual(self.model.altitude_min_km, 0.0)
        self.assertEqual(self.model.altitude_max_km, 40.0)
        self.assertEqual(self.model.source_epoch_class, "VOYAGER2_1989_HISTORICAL_REFERENCE")
        self.assertFalse(self.model.qualified_for_2226_endpoint)
        self.assertEqual(self.model.admissibility_authority, "ZERO")
        self.assertEqual(self.model.loom_coherence_authority, "ZERO")

    def test_temperature_is_explicit_linear_reference_assumption(self):
        self.assertAlmostEqual(self.model.temperature_k(0.0), 72.0)
        self.assertAlmostEqual(self.model.temperature_k(20.0), 62.0)
        self.assertAlmostEqual(self.model.temperature_k(40.0), 52.0)
        with self.assertRaises(ValueError):
            self.model.temperature_k(40.1)

    def test_hydrostatic_pressure_envelope_is_independent_validation_not_forced_fit(self):
        envelope = self.model.pressure_envelope_pa(40.0)
        self.assertGreater(envelope.minimum_pa, 10000.0)
        self.assertLess(envelope.minimum_pa, 12000.0)
        self.assertGreater(envelope.maximum_pa, 13000.0)
        self.assertLess(envelope.maximum_pa, 13100.0)
        self.assertEqual(envelope.observed_reference_pa, 10000.0)
        self.assertGreater(envelope.minimum_relative_error, 0.17)
        self.assertLess(envelope.minimum_relative_error, 0.18)
        self.assertGreater(envelope.maximum_relative_error, 0.30)
        self.assertLess(envelope.maximum_relative_error, 0.31)

    def test_density_is_model_output_not_observed_or_2226_state(self):
        envelope = self.model.density_envelope_kg_m3(40.0)
        self.assertGreater(envelope.minimum, 0.0)
        self.assertGreater(envelope.maximum, envelope.minimum)
        self.assertEqual(envelope.authority, "HISTORICAL_REFERENCE_MODEL_ONLY")
        self.assertFalse(envelope.observed)
        self.assertFalse(envelope.qualified_for_2226_endpoint)


if __name__ == "__main__":
    unittest.main()
