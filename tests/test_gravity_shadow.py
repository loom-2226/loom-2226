from __future__ import annotations

from datetime import datetime, timezone
import math
import unittest

from loom.application.contracts import SpatialState
from loom.navigation.gravity_shadow import (
    GravityShadowError,
    OrdinaryTrajectorySample,
    REFERENCE_EPOCH_NORMALIZATION_CONTRACT,
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

    def test_canonicalizes_equivalent_same_instant_terminal_samples(self):
        trajectory = {"samples": [
            {"sample_index": 98, "epoch_utc": "2226-06-15T18:06:00Z",
             "ordinary_pos_x_km": 1.0, "ordinary_pos_y_km": 2.0, "ordinary_pos_z_km": 3.0,
             "ordinary_vel_x_km_s": 4.0, "ordinary_vel_y_km_s": 5.0, "ordinary_vel_z_km_s": 6.0},
            {"sample_index": 99, "epoch_utc": "2226-06-15T18:07:05.015714Z",
             "ordinary_pos_x_km": 7.0, "ordinary_pos_y_km": 8.0, "ordinary_pos_z_km": 9.0,
             "ordinary_vel_x_km_s": 10.0, "ordinary_vel_y_km_s": 11.0, "ordinary_vel_z_km_s": 12.0},
            {"sample_index": 100, "epoch_utc": "2226-06-15T18:07:05.015714+00:00",
             "ordinary_pos_x_km": 7.0, "ordinary_pos_y_km": 8.0, "ordinary_pos_z_km": 9.0,
             "ordinary_vel_x_km_s": 10.0, "ordinary_vel_y_km_s": 11.0, "ordinary_vel_z_km_s": 12.0},
        ]}
        rows = ordinary_samples_from_route_trajectory(trajectory)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[-1].sample_index, 100)
        self.assertLess(datetime.fromisoformat(rows[0].epoch_utc.replace("Z", "+00:00")),
                        datetime.fromisoformat(rows[1].epoch_utc.replace("Z", "+00:00")))

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
        self.assertEqual(report.qualification["reference_epoch_normalization"], REFERENCE_EPOCH_NORMALIZATION_CONTRACT)

    def test_compare_defensively_canonicalizes_duplicate_reference_samples(self):
        samples = (
            OrdinaryTrajectorySample("2226-01-01T00:00:00Z", (0, 0, 0), (1, 0, 0), sample_index=1),
            OrdinaryTrajectorySample("2226-01-01T00:01:00Z", (60, 0, 0), (1, 0, 0), sample_index=2),
            OrdinaryTrajectorySample("2226-01-01T00:01:00+00:00", (60, 0, 0), (1, 0, 0), sample_index=3),
        )

        def gravity(position, epoch):
            return evaluate_gravity(position, (), epoch_utc=epoch)

        report = compare_gravity_shadow(samples, gravity, max_step_s=10.0)
        self.assertEqual(report.sample_count, 2)
        self.assertAlmostEqual(report.terminal_position_error_km, 0.0, places=9)

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

    def test_rejects_conflicting_same_instant_epochs(self):
        with self.assertRaises(GravityShadowError):
            ordinary_samples_from_route_trajectory({"samples": [
                {"sample_index": 1, "epoch_utc": "2226-01-01T00:00:00Z", "ordinary_pos_x_km": -1,
                 "ordinary_pos_y_km": 0, "ordinary_pos_z_km": 0, "ordinary_vel_x_km_s": 0,
                 "ordinary_vel_y_km_s": 0, "ordinary_vel_z_km_s": 0},
                {"sample_index": 2, "epoch_utc": "2226-01-01T00:00:10Z", "ordinary_pos_x_km": 0,
                 "ordinary_pos_y_km": 0, "ordinary_pos_z_km": 0, "ordinary_vel_x_km_s": 0,
                 "ordinary_vel_y_km_s": 0, "ordinary_vel_z_km_s": 0},
                {"sample_index": 3, "epoch_utc": "2226-01-01T00:00:10+00:00", "ordinary_pos_x_km": 1,
                 "ordinary_pos_y_km": 0, "ordinary_pos_z_km": 0, "ordinary_vel_x_km_s": 0,
                 "ordinary_vel_y_km_s": 0, "ordinary_vel_z_km_s": 0},
            ]})


if __name__ == "__main__":
    unittest.main()
