import unittest

from src.loom_neptune_atmosphere_reference_anchors import (
    NEPTUNE_VOYAGER2_REFERENCE_ANCHORS,
    NeptuneAtmosphereReferenceAnchor,
    reference_anchor_by_id,
)


class NeptuneAtmosphereReferenceAnchorsTests(unittest.TestCase):
    def test_anchor_set_contains_only_earned_discrete_reference_points(self):
        self.assertEqual(len(NEPTUNE_VOYAGER2_REFERENCE_ANCHORS), 2)
        one_bar = reference_anchor_by_id("VOYAGER2_NEPTUNE_1BAR_REFERENCE")
        tropopause = reference_anchor_by_id("VOYAGER2_NEPTUNE_TROPOPAUSE_REFERENCE")

        self.assertIsInstance(one_bar, NeptuneAtmosphereReferenceAnchor)
        self.assertEqual(one_bar.pressure_pa, 100000.0)
        self.assertEqual(one_bar.temperature_k, 72.0)
        self.assertEqual(one_bar.temperature_uncertainty_k, 2.0)
        self.assertEqual(one_bar.altitude_from_one_bar_km, 0.0)

        self.assertEqual(tropopause.pressure_pa, 10000.0)
        self.assertEqual(tropopause.temperature_k, 52.0)
        self.assertEqual(tropopause.temperature_uncertainty_k, 2.0)
        self.assertEqual(tropopause.altitude_from_one_bar_km, 40.0)
        self.assertEqual(tropopause.h2_number_fraction_min, 0.78)
        self.assertEqual(tropopause.h2_number_fraction_max, 0.84)

    def test_reference_points_are_historical_not_2226_local_state(self):
        for anchor in NEPTUNE_VOYAGER2_REFERENCE_ANCHORS:
            self.assertEqual(anchor.source_epoch_class, "VOYAGER2_1989_HISTORICAL_REFERENCE")
            self.assertFalse(anchor.qualified_for_2226_endpoint)
            self.assertEqual(anchor.interpolation_authority, "ZERO")
            self.assertEqual(anchor.extrapolation_authority, "ZERO")
            self.assertIn("LINDAL", anchor.source_ids)

    def test_no_density_or_admissibility_payload_is_smuggled_into_anchors(self):
        forbidden = {
            "mass_density_kg_m3",
            "admissible",
            "admissibility_score",
            "metric_policy",
            "collapse_radius_km",
            "loom_coherence",
        }
        fields = set(NeptuneAtmosphereReferenceAnchor.__dataclass_fields__)
        self.assertFalse(fields & forbidden)


if __name__ == "__main__":
    unittest.main()
