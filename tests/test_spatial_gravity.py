import math
import unittest

from loom.application.contracts import SpatialState
from loom.spatial.gravity import (
    CANONICAL_GRAVITY_FRAME,
    GravityModelError,
    GravitySource,
    acceleration_from_source,
    evaluate_gravity,
)


EPOCH = "2226-06-15T09:59:34Z"


def state(entity_id, xyz, *, navigation_grade=True, provenance=None):
    return SpatialState(
        entity_id=entity_id,
        epoch_utc=EPOCH,
        reference_frame=CANONICAL_GRAVITY_FRAME,
        position_km=xyz,
        velocity_km_s=(0.0, 0.0, 0.0),
        navigation_grade=navigation_grade,
        provenance=provenance or {"state_source": "TEST"},
        payload={"state_class": "CELESTIAL"},
    )


class GravityFoundationTest(unittest.TestCase):
    def test_inverse_square_acceleration_points_toward_source(self):
        src = GravitySource("BODY:A", state("BODY:A", (10.0, 0.0, 0.0)), 100.0)
        c = acceleration_from_source((0.0, 0.0, 0.0), src)
        self.assertAlmostEqual(c.magnitude_km_s2, 1.0)
        self.assertEqual(c.acceleration_km_s2, (1.0, 0.0, 0.0))
        self.assertAlmostEqual(c.separation_km, 10.0)

    def test_vector_sum_is_deterministic_and_cancels_symmetric_sources(self):
        sources = (
            GravitySource("BODY:RIGHT", state("BODY:RIGHT", (10.0, 0.0, 0.0)), 100.0),
            GravitySource("BODY:LEFT", state("BODY:LEFT", (-10.0, 0.0, 0.0)), 100.0),
        )
        result = evaluate_gravity((0.0, 0.0, 0.0), sources, epoch_utc=EPOCH)
        self.assertAlmostEqual(result.total_magnitude_km_s2, 0.0, places=15)
        self.assertEqual([c.entity_id for c in result.contributions], ["BODY:LEFT", "BODY:RIGHT"])

    def test_influence_threshold_excludes_only_small_force_not_low_grade_state(self):
        near_propagated = GravitySource(
            "BODY:MOON",
            state("BODY:MOON", (10.0, 0.0, 0.0), navigation_grade=False, provenance={"state_source": "PROPAGATED"}),
            100.0,
            provenance={"mu_source": "TEST_CONSTANT"},
        )
        far_direct = GravitySource(
            "BODY:FAR",
            state("BODY:FAR", (1000.0, 0.0, 0.0), navigation_grade=True),
            1.0,
        )
        result = evaluate_gravity(
            (0.0, 0.0, 0.0),
            (near_propagated, far_direct),
            epoch_utc=EPOCH,
            minimum_acceleration_km_s2=1e-4,
        )
        self.assertEqual([c.entity_id for c in result.contributions], ["BODY:MOON"])
        self.assertFalse(result.contributions[0].navigation_grade_state)
        self.assertEqual(result.excluded_below_threshold, ("BODY:FAR",))

    def test_mixed_epochs_fail_closed(self):
        other = SpatialState(
            entity_id="BODY:B",
            epoch_utc="2226-06-15T10:00:00Z",
            reference_frame=CANONICAL_GRAVITY_FRAME,
            position_km=(20.0, 0.0, 0.0),
            velocity_km_s=(0.0, 0.0, 0.0),
        )
        with self.assertRaises(GravityModelError):
            evaluate_gravity(
                (0.0, 0.0, 0.0),
                (
                    GravitySource("BODY:A", state("BODY:A", (10.0, 0.0, 0.0)), 100.0),
                    GravitySource("BODY:B", other, 100.0),
                ),
                epoch_utc=EPOCH,
            )

    def test_frame_mismatch_fails_closed(self):
        bad = SpatialState(
            entity_id="BODY:A",
            epoch_utc=EPOCH,
            reference_frame="BODY_FIXED",
            position_km=(10.0, 0.0, 0.0),
            velocity_km_s=(0.0, 0.0, 0.0),
        )
        with self.assertRaises(GravityModelError):
            GravitySource("BODY:A", bad, 100.0)

    def test_duplicate_source_fails_closed(self):
        src = GravitySource("BODY:A", state("BODY:A", (10.0, 0.0, 0.0)), 100.0)
        with self.assertRaises(GravityModelError):
            evaluate_gravity((0.0, 0.0, 0.0), (src, src), epoch_utc=EPOCH)

    def test_singularity_guard_is_not_silently_softened(self):
        src = GravitySource("BODY:A", state("BODY:A", (0.0, 0.0, 0.0)), 100.0)
        with self.assertRaises(GravityModelError):
            acceleration_from_source((0.0, 0.0, 0.0), src)


if __name__ == "__main__":
    unittest.main()
