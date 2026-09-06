from __future__ import annotations

import unittest

from loom.application.contracts import SpatialState
from loom.navigation.gravity_guidance_shadow import (
    D2H_GRAVITY_RETARGETING_CONTRACT,
    compare_gravity_guidance_shadow,
)
from loom.navigation.gravity_shadow import GravityShadowError, OrdinaryTrajectorySample
from loom.spatial.gravity import GravitySource, evaluate_gravity


class GravityGuidanceShadowTests(unittest.TestCase):
    def test_zero_gravity_exactly_tracks_hermite_reference(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0,0,0), (1,0,0)),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (60,0,0), (1,0,0)),
            OrdinaryTrajectorySample("2226-01-01T00:02:00Z", (120,0,0), (1,0,0)),
        )

        def gravity(position, epoch):
            return evaluate_gravity(position, (), epoch_utc=epoch)

        report = compare_gravity_guidance_shadow(samples, gravity, max_step_s=5.0)
        self.assertEqual(report.contract, D2H_GRAVITY_RETARGETING_CONTRACT)
        self.assertAlmostEqual(report.terminal_position_error_km, 0.0, places=8)
        self.assertAlmostEqual(report.terminal_velocity_error_km_s, 0.0, places=8)
        self.assertAlmostEqual(report.guidance_correction_delta_v_km_s, 0.0, places=8)
        self.assertFalse(report.qualification["route_mutation"])
        self.assertFalse(report.qualification["campaign_mutation"])

    def test_terminal_retargeting_reduces_gravity_divergence(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0,0,0), (0,1,0)),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (0,60,0), (0,1,0)),
            OrdinaryTrajectorySample("2226-01-01T00:02:00Z", (0,120,0), (0,1,0)),
        )

        def gravity(position, epoch):
            state = SpatialState(
                entity_id="BODY",
                epoch_utc=epoch,
                reference_frame="J2000/ECLIPTIC",
                position_km=(1000.0,0.0,0.0),
                velocity_km_s=(0.0,0.0,0.0),
                provenance={"state_source":"TEST"},
                navigation_grade=True,
            )
            return evaluate_gravity(position,(GravitySource("BODY",state,1000.0),),epoch_utc=epoch)

        unguided = compare_gravity_guidance_shadow(
            samples, gravity, max_step_s=2.0, guidance_accel_limit_km_s2=1e-12
        )
        guided = compare_gravity_guidance_shadow(
            samples, gravity, max_step_s=2.0, guidance_accel_limit_km_s2=0.02
        )
        self.assertLess(guided.terminal_position_error_km, unguided.terminal_position_error_km)
        self.assertLess(guided.terminal_velocity_error_km_s, unguided.terminal_velocity_error_km_s)
        self.assertGreater(guided.guidance_correction_delta_v_km_s, 0.0)
        self.assertLessEqual(guided.max_guidance_correction_km_s2, 0.02 + 1e-12)

    def test_guidance_limit_is_enforced(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0,0,0), (0,0,0)),
            OrdinaryTrajectorySample("2226-01-01T00:00:30Z", (0,0,0), (0,0,0)),
        )

        def gravity(position, epoch):
            state = SpatialState(
                entity_id="BODY",
                epoch_utc=epoch,
                reference_frame="J2000/ECLIPTIC",
                position_km=(10.0,0.0,0.0),
                velocity_km_s=(0.0,0.0,0.0),
                provenance={"state_source":"TEST"},
                navigation_grade=True,
            )
            return evaluate_gravity(position,(GravitySource("BODY",state,1000.0),),epoch_utc=epoch)

        limit = 0.001
        report = compare_gravity_guidance_shadow(samples,gravity,max_step_s=1.0,guidance_accel_limit_km_s2=limit)
        self.assertLessEqual(report.max_guidance_correction_km_s2, limit + 1e-12)

    def test_rejects_non_monotonic_reference_epochs(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (0,0,0), (0,0,0)),
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0,0,0), (0,0,0)),
        )

        def gravity(position, epoch):
            return evaluate_gravity(position, (), epoch_utc=epoch)

        with self.assertRaises(GravityShadowError):
            compare_gravity_guidance_shadow(samples,gravity)


if __name__ == "__main__":
    unittest.main()
