from __future__ import annotations

from datetime import datetime, timezone
import math
import unittest

from loom.application.contracts import SpatialState
from loom.navigation.gravity_shadow import (
    GravityShadowError,
    OrdinaryTrajectorySample,
    compare_gravity_shadow,
    ordinary_samples_from_route_trajectory,
)
from loom.spatial.gravity import GravitySource, evaluate_gravity


class GravityShadowTests(unittest.TestCase):
    def test_extracts_only_complete_ordinary_samples(self):
        trajectory = {
            "samples": [
                {"sample_index": 0, "epoch_utc": "2226-01-01T00:00:00Z", "ordinary_pos_x_km": None,
                 "ordinary_pos_y_km": None, "ordinary_pos_z_km": None,
                 "ordinary_vel_x_km_s": None, "ordinary_vel_y_km_s": None, "ordinary_vel_z_km_s": None},
                {"sample_index": 1, "epoch_utc": "2226-01-01T00:00:10Z", "ordinary_pos_x_km": 0.0,
                 "ordinary_pos_y_km": 0.0, "ordinary_pos_z_km": 0.0,
                 "ordinary_vel_x_km_s": 1.0, "ordinary_vel_y_km_s": 0.0, "ordinary_vel_z_km_s": 0.0},
                {"sample_index": 2, "epoch_utc": "2226-01-01T00:00:20Z", "ordinary_pos_x_km": 10.0,
                 "ordinary_pos_y_km": 0.0, "ordinary_pos_z_km": 0.0,
                 "ordinary_vel_x_km_s": 1.0, "ordinary_vel_y_km_s": 0.0, "ordinary_vel_z_km_s": 0.0},
            ]
        }
        rows = ordinary_samples_from_route_trajectory(trajectory)
        self.assertEqual([r.sample_index for r in rows], [1, 2])

    def test_zero_gravity_replays_constant_velocity_reference(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0, 0, 0), (1, 0, 0)),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (60, 0, 0), (1, 0, 0)),
        )

        def gravity(position, epoch):
            return evaluate_gravity(position, (), epoch_utc=epoch)

        report = compare_gravity_shadow(samples, gravity, max_step_s=10.0)
        self.assertAlmostEqual(report.terminal_position_error_km, 0.0, places=9)
        self.assertAlmostEqual(report.terminal_velocity_error_km_s, 0.0, places=9)
        self.assertEqual(report.qualification["authority"], "SHADOW_ONLY_NOT_ROUTE_AUTHORITY")

    def test_gravity_produces_expected_downrange_divergence(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0, 0, 0), (0, 1, 0)),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (0, 60, 0), (0, 1, 0)),
        )
        source_state = SpatialState(
            entity_id="BODY",
            epoch_utc="2226-01-01T00:00:00Z",
            reference_frame="J2000/ECLIPTIC",
            position_km=(1000.0, 0.0, 0.0),
            velocity_km_s=(0.0, 0.0, 0.0),
            provenance={"state_source": "TEST"},
            navigation_grade=True,
        )

        def gravity(position, epoch):
            # Hold the source fixed for this deterministic short-interval test but
            # stamp it at each requested RK4 substage epoch.
            state = SpatialState(
                entity_id="BODY",
                epoch_utc=epoch,
                reference_frame="J2000/ECLIPTIC",
                position_km=source_state.position_km,
                velocity_km_s=source_state.velocity_km_s,
                provenance=source_state.provenance,
                navigation_grade=True,
            )
            return evaluate_gravity(position, (GravitySource("BODY", state, 1000.0),), epoch_utc=epoch)

        report = compare_gravity_shadow(samples, gravity, max_step_s=5.0)
        self.assertGreater(report.terminal_position_error_km, 0.0)
        self.assertGreater(report.terminal_velocity_error_km_s, 0.0)
        self.assertEqual(report.samples[-1].dominant_gravity_source, "BODY")
        self.assertGreater(report.samples[-1].shadow_position_km[0], 0.0)

    def test_rejects_non_monotonic_epochs(self):
        with self.assertRaises(GravityShadowError):
            ordinary_samples_from_route_trajectory({"samples": [
                {"epoch_utc": "2226-01-01T00:00:10Z", "ordinary_pos_x_km": 0, "ordinary_pos_y_km": 0,
                 "ordinary_pos_z_km": 0, "ordinary_vel_x_km_s": 0, "ordinary_vel_y_km_s": 0, "ordinary_vel_z_km_s": 0},
                {"epoch_utc": "2226-01-01T00:00:10Z", "ordinary_pos_x_km": 1, "ordinary_pos_y_km": 0,
                 "ordinary_pos_z_km": 0, "ordinary_vel_x_km_s": 0, "ordinary_vel_y_km_s": 0, "ordinary_vel_z_km_s": 0},
            ]})


if __name__ == "__main__":
    unittest.main()
