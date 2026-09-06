import unittest

from loom.application.contracts import SpatialState
from loom.spatial.gravity import GravitySource, evaluate_gravity


EPOCH = "2226-06-15T09:59:34Z"
FRAME = "J2000/ECLIPTIC"


class NavigationPhysicsV2GravityFunctionalTest(unittest.TestCase):
    def test_direct_parent_and_propagated_moon_both_contribute_without_regrading_state(self):
        # Synthetic geometry intentionally isolates the integration contract. The
        # numerical GM values here are test fixtures, not LOOM celestial constants.
        parent = SpatialState(
            entity_id="BODY:PARENT",
            epoch_utc=EPOCH,
            reference_frame=FRAME,
            position_km=(1000.0, 0.0, 0.0),
            velocity_km_s=(0.0, 0.0, 0.0),
            navigation_grade=True,
            provenance={"state_source": "DIRECT_TEST_VECTOR"},
            payload={"state_class": "CELESTIAL"},
        )
        moon = SpatialState(
            entity_id="BODY:MOON",
            epoch_utc=EPOCH,
            reference_frame=FRAME,
            position_km=(900.0, 0.0, 0.0),
            velocity_km_s=(0.0, 0.0, 0.0),
            navigation_grade=False,
            provenance={
                "state_source": "PROPAGATED_PARENT_CENTRIC_TEST_VECTOR",
                "parent_entity_id": "BODY:PARENT",
            },
            uncertainty={"position_km": 2.0},
            payload={"state_class": "CELESTIAL"},
        )
        sources = (
            GravitySource(
                entity_id=parent.entity_id,
                state=parent,
                mu_km3_s2=1000.0,
                provenance={"mu_source": "TEST_FIXTURE"},
            ),
            GravitySource(
                entity_id=moon.entity_id,
                state=moon,
                mu_km3_s2=100.0,
                provenance={"mu_source": "TEST_FIXTURE"},
                uncertainty=moon.uncertainty,
            ),
        )

        result = evaluate_gravity((0.0, 0.0, 0.0), sources, epoch_utc=EPOCH)

        self.assertEqual(len(result.contributions), 2)
        by_id = {row.entity_id: row for row in result.contributions}
        self.assertIn("BODY:PARENT", by_id)
        self.assertIn("BODY:MOON", by_id)
        self.assertTrue(by_id["BODY:PARENT"].navigation_grade_state)
        self.assertFalse(by_id["BODY:MOON"].navigation_grade_state)
        self.assertEqual(
            by_id["BODY:MOON"].provenance["state"]["state_source"],
            "PROPAGATED_PARENT_CENTRIC_TEST_VECTOR",
        )
        self.assertGreater(result.total_acceleration_km_s2[0], 0.0)
        self.assertEqual(result.total_acceleration_km_s2[1:], (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
