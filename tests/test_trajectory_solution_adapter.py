import unittest

from loom.navigation.route_layer import LoomRouteLayerV1
from loom.navigation.trajectory_solution_adapter import (
    TRAJECTORY_PACKET_ADAPTER_VERSION,
    TrajectoryPacketAdapterError,
    trajectory_solution_from_route_layer,
)


def sample(index, epoch, phase, *, position=None, velocity=None, metric_state=None):
    row = {
        "sample_index": index,
        "epoch_utc": epoch,
        "phase_code": phase,
        "metric_state_code": metric_state,
    }
    if position is not None:
        row.update(
            ordinary_pos_x_km=position[0],
            ordinary_pos_y_km=position[1],
            ordinary_pos_z_km=position[2],
        )
    if velocity is not None:
        row.update(
            ordinary_vel_x_km_s=velocity[0],
            ordinary_vel_y_km_s=velocity[1],
            ordinary_vel_z_km_s=velocity[2],
        )
    return row


def route_layer(rows):
    return LoomRouteLayerV1(
        route_id="route-1",
        flight_id="flight-1",
        origin="MARS",
        destination="CERES",
        departure_epoch="2226-08-22T00:00:00Z",
        arrival_epoch="2226-08-22T03:00:00Z",
        strategy="EXPEDITE",
        status="PLANNED",
        payload={
            "geometry_mode": "AUTHORITATIVE_SEQUENCE_B_MIXED_GEOMETRY",
            "trajectory": {
                "authority": "PYTHON_AUTHORED_SEQUENCE_B",
                "renderer_rule": "INDEX_ONLY_NO_INFERENCE",
                "coordinate_frame": "J2000_ECLIPTIC",
                "sample_count": len(rows),
                "samples": rows,
                "metric_semantics": "RELATIONAL DISPLACEMENT / NOT ORDINARY-SPACE OCCUPANCY",
                "ordinary_semantics": "PYTHON-AUTHORED ORDINARY TRAJECTORY",
                "events": [{"event": "collapse"}],
                "route_plan_id": "rp-1",
                "solution_key": "EXPEDITE|HIGH",
            },
        },
    )


class TrajectorySolutionAdapterTests(unittest.TestCase):
    def test_promotes_campaign_stamped_typed_solution_without_trajectory_math(self):
        rows = [
            sample(0, "2226-08-22T00:00:00Z", "DEPARTURE", position=(1, 2, 3), velocity=(0.1, 0.2, 0.3)),
            sample(1, "2226-08-22T00:30:00Z", "DEPARTURE", position=(2, 3, 4), velocity=(0.2, 0.3, 0.4)),
            sample(2, "2226-08-22T01:00:00Z", "METRIC_TRANSIT", metric_state="ESTABLISHED"),
            sample(3, "2226-08-22T02:00:00Z", "METRIC_TRANSIT", metric_state="TRANSIT"),
            sample(4, "2226-08-22T02:30:00Z", "TERMINAL", position=(9, 8, 7), velocity=(0.4, 0.3, 0.2)),
            sample(5, "2226-08-22T03:00:00Z", "TERMINAL", position=(10, 9, 8), velocity=(0.3, 0.2, 0.1)),
        ]
        solution = trajectory_solution_from_route_layer(
            route_layer(rows),
            campaign_revision=9,
            solution_epoch="2226-08-22T00:00:00Z",
        )

        self.assertEqual(solution.campaign_revision, 9)
        self.assertEqual(solution.origin, "MARS")
        self.assertEqual(solution.destination, "CERES")
        self.assertEqual(solution.reference_frame, "J2000_ECLIPTIC")
        self.assertEqual(len(solution.segments), 3)
        self.assertEqual(solution.provenance["adapter"], TRAJECTORY_PACKET_ADAPTER_VERSION)
        self.assertEqual(solution.payload["sample_count"], 6)

    def test_metric_phase_preserves_rows_without_inventing_ordinary_space_state(self):
        rows = [
            sample(0, "2226-08-22T00:00:00Z", "DEPARTURE", position=(1, 2, 3), velocity=(0.1, 0.2, 0.3)),
            sample(1, "2226-08-22T01:00:00Z", "METRIC_TRANSIT", metric_state="ESTABLISHED"),
            sample(2, "2226-08-22T02:00:00Z", "METRIC_TRANSIT", metric_state="TRANSIT"),
            sample(3, "2226-08-22T03:00:00Z", "TERMINAL", position=(10, 9, 8), velocity=(0.3, 0.2, 0.1)),
        ]
        solution = trajectory_solution_from_route_layer(
            route_layer(rows), campaign_revision=9, solution_epoch="2226-08-22T00:00:00Z"
        )
        metric = solution.segments[1]
        self.assertEqual(metric.segment_type, "METRIC_TRANSIT")
        self.assertEqual(metric.samples, ())
        self.assertIsNone(metric.start_state)
        self.assertIsNone(metric.end_state)
        self.assertFalse(metric.payload["ordinary_space_samples_available"])
        self.assertEqual(len(metric.payload["source_timeline_rows"]), 2)

    def test_ordinary_samples_are_promoted_as_explicit_xyz_states(self):
        rows = [
            sample(0, "2226-08-22T00:00:00Z", "TORCH", position=(1, 2, 3), velocity=(0.1, 0.2, 0.3)),
            sample(1, "2226-08-22T00:10:00Z", "TORCH", position=(4, 5, 6), velocity=(0.4, 0.5, 0.6)),
        ]
        solution = trajectory_solution_from_route_layer(
            route_layer(rows), campaign_revision=9, solution_epoch="2226-08-22T00:00:00Z"
        )
        segment = solution.segments[0]
        self.assertEqual(segment.samples[0].position_km, (1.0, 2.0, 3.0))
        self.assertEqual(segment.samples[-1].velocity_km_s, (0.4, 0.5, 0.6))
        self.assertEqual(segment.samples[0].payload["sample_index"], 0)

    def test_missing_sequence_b_samples_fails_closed(self):
        layer = LoomRouteLayerV1(
            route_id="route-1",
            flight_id="flight-1",
            origin="MARS",
            destination="CERES",
            departure_epoch="2226-08-22T00:00:00Z",
            arrival_epoch="2226-08-22T03:00:00Z",
            strategy="EXPEDITE",
            status="PLANNED",
            payload={},
        )
        with self.assertRaises(TrajectoryPacketAdapterError):
            trajectory_solution_from_route_layer(
                layer, campaign_revision=9, solution_epoch="2226-08-22T00:00:00Z"
            )


if __name__ == "__main__":
    unittest.main()
