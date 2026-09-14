import unittest
from dataclasses import FrozenInstanceError, MISSING

from src.loom_planetary_environment import (
    EnvironmentProvenance,
    EnvironmentQuery,
    EnvironmentUncertainty,
    PlanetaryEnvironmentState,
)


class TestPlanetaryEnvironmentInterface(unittest.TestCase):
    def test_query_and_state_are_immutable_and_explicit(self):
        query = EnvironmentQuery(
            body_id="NE",
            epoch_utc="2226-08-22T09:07:59Z",
            reference_frame="J2000",
            position_km=(1.0, 2.0, 3.0),
        )
        state = PlanetaryEnvironmentState(
            query=query,
            atmospheric_regime=None,
            mass_density_kg_m3=None,
            magnetic_field_t=None,
            plasma_number_density_m3=None,
            ionizing_radiation_dose_rate_gy_s=None,
            uncertainty=EnvironmentUncertainty(
                model_class="UNQUALIFIED_INTERFACE_ONLY",
                numeric_envelope=None,
                notes=("NO_2226_ENVIRONMENT_MODEL_YET",),
            ),
            provenance=EnvironmentProvenance(
                source_ids=(),
                source_class="INTERFACE_ONLY",
                qualification="NOT_QUALIFIED_FOR_ENDPOINT_USE",
            ),
        )
        self.assertEqual(state.query.body_id, "NE")
        self.assertIsNone(state.mass_density_kg_m3)
        with self.assertRaises(FrozenInstanceError):
            state.query.body_id = "CE"

    def test_interface_has_no_admissibility_or_loom_coherence_fields(self):
        fields = set(PlanetaryEnvironmentState.__dataclass_fields__)
        forbidden = {
            "admissible",
            "admissibility_score",
            "metric_policy",
            "collapse_radius_km",
            "loom_coherence",
        }
        self.assertTrue(fields.isdisjoint(forbidden))

    def test_uncertainty_and_provenance_are_mandatory(self):
        fields = PlanetaryEnvironmentState.__dataclass_fields__
        self.assertIn("uncertainty", fields)
        self.assertIn("provenance", fields)
        self.assertIs(fields["uncertainty"].default, MISSING)
        self.assertIs(fields["uncertainty"].default_factory, MISSING)
        self.assertIs(fields["provenance"].default, MISSING)
        self.assertIs(fields["provenance"].default_factory, MISSING)


if __name__ == "__main__":
    unittest.main()
