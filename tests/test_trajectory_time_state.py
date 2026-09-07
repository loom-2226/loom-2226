import unittest

from loom.application import SpatialState, TrajectorySegment, TrajectorySolution
from loom.navigation import (
    TRAJECTORY_TIME_STATE_VERSION,
    TrajectoryTimeStateError,
    evaluate_trajectory_at_epoch,
)


def _state(epoch, x, vx=1.0):
    return SpatialState(
        entity_id="SHIP",
        epoch_utc=epoch,
        reference_frame="ECLIPTIC_J2000",
        position_km=(x, 0.0, 0.0),
        velocity_km_s=(vx, 0.0, 0.0),
        navigation_grade=True,
        provenance={"authority": "TEST"},
    )


def _solution(*segments):
    return TrajectorySolution(
        trajectory_id="traj-test",
        campaign_revision=10,
        solution_epoch="2226-06-15T10:00:00Z",
        origin="CERES",
        destination="MARS",
        reference_frame="ECLIPTIC_J2000",
        departure_epoch="2226-06-15T10:00:00Z",
        arrival_epoch="2226-06-15T10:30:00Z",
        segments=tuple(segments),
    )


class TrajectoryTimeStateTests(unittest.TestCase):
    def test_exact_sample_is_returned_without_regrading(self):
        a = _state("2226-06-15T10:00:00Z", 0.0)
        b = _state("2226-06-15T10:10:00Z", 600.0)
        seg = TrajectorySegment(
            "S1", "ORDINARY", "2226-06-15T10:00:00Z", "2226-06-15T10:10:00Z",
            start_state=a, end_state=b, samples=(a, b),
        )
        result = evaluate_trajectory_at_epoch(_solution(seg), "2226-06-15T10:10:00Z")
        self.assertEqual(result.contract, TRAJECTORY_TIME_STATE_VERSION)
        self.assertEqual(result.evaluation_mode, "EXACT_AUTHORITATIVE_SAMPLE")
        self.assertIs(result.spatial_state, b)
        self.assertTrue(result.spatial_state.navigation_grade)

    def test_interpolates_only_between_authoritative_ordinary_samples(self):
        a = _state("2226-06-15T10:00:00Z", 0.0, 1.0)
        b = _state("2226-06-15T10:10:00Z", 600.0, 3.0)
        seg = TrajectorySegment(
            "S1", "ORDINARY", "2226-06-15T10:00:00Z", "2226-06-15T10:10:00Z",
            start_state=a, end_state=b, samples=(a, b),
        )
        result = evaluate_trajectory_at_epoch(_solution(seg), "2226-06-15T10:05:00Z")
        self.assertEqual(result.evaluation_mode, "LINEAR_BETWEEN_AUTHORITATIVE_SAMPLES")
        self.assertEqual(result.state_kind, "ORDINARY")
        self.assertEqual(tuple(result.spatial_state.position_km), (300.0, 0.0, 0.0))
        self.assertEqual(tuple(result.spatial_state.velocity_km_s), (2.0, 0.0, 0.0))
        self.assertFalse(result.spatial_state.navigation_grade)
        self.assertEqual(result.source_epochs, (a.epoch_utc, b.epoch_utc))

    def test_metric_segment_returns_relational_without_invented_xyz(self):
        dep = TrajectorySegment(
            "S1", "DEPARTURE", "2226-06-15T10:00:00Z", "2226-06-15T10:05:00Z",
            samples=(
                _state("2226-06-15T10:00:00Z", 0.0),
                _state("2226-06-15T10:05:00Z", 300.0),
            ),
        )
        metric = TrajectorySegment(
            "S2", "METRIC_TRANSIT", "2226-06-15T10:05:00Z", "2226-06-15T10:25:00Z",
            samples=(),
            payload={"metric_semantics": "RELATIONAL_NOT_ORDINARY_OCCUPANCY"},
        )
        arr = TrajectorySegment(
            "S3", "ARRIVAL", "2226-06-15T10:25:00Z", "2226-06-15T10:30:00Z",
            samples=(
                _state("2226-06-15T10:25:00Z", 900.0),
                _state("2226-06-15T10:30:00Z", 1200.0),
            ),
        )
        result = evaluate_trajectory_at_epoch(_solution(dep, metric, arr), "2226-06-15T10:15:00Z")
        self.assertEqual(result.state_kind, "RELATIONAL")
        self.assertEqual(result.evaluation_mode, "RELATIONAL_NO_ORDINARY_STATE")
        self.assertIsNone(result.spatial_state)
        self.assertEqual(result.segment_id, "S2")

    def test_does_not_extrapolate_ordinary_state_into_unbracketed_epoch(self):
        a = _state("2226-06-15T10:00:00Z", 0.0)
        seg = TrajectorySegment(
            "S1", "ORDINARY_TO_METRIC", "2226-06-15T10:00:00Z", "2226-06-15T10:10:00Z",
            samples=(a,),
        )
        result = evaluate_trajectory_at_epoch(_solution(seg), "2226-06-15T10:05:00Z")
        self.assertEqual(result.evaluation_mode, "RELATIONAL_NO_ORDINARY_STATE")
        self.assertIsNone(result.spatial_state)

    def test_outside_solution_bounds_fails_closed(self):
        seg = TrajectorySegment(
            "S1", "ORDINARY", "2226-06-15T10:00:00Z", "2226-06-15T10:30:00Z",
            samples=(
                _state("2226-06-15T10:00:00Z", 0.0),
                _state("2226-06-15T10:30:00Z", 1800.0),
            ),
        )
        with self.assertRaisesRegex(TrajectoryTimeStateError, "outside trajectory bounds"):
            evaluate_trajectory_at_epoch(_solution(seg), "2226-06-15T09:59:59Z")

    def test_conflicting_duplicate_sample_epoch_fails_closed(self):
        a = _state("2226-06-15T10:00:00Z", 0.0)
        b = _state("2226-06-15T10:00:00Z", 1.0)
        seg = TrajectorySegment(
            "S1", "ORDINARY", "2226-06-15T10:00:00Z", "2226-06-15T10:30:00Z",
            samples=(a, b, _state("2226-06-15T10:30:00Z", 1800.0)),
        )
        with self.assertRaisesRegex(TrajectoryTimeStateError, "conflicting ordinary states"):
            evaluate_trajectory_at_epoch(_solution(seg), "2226-06-15T10:15:00Z")


if __name__ == "__main__":
    unittest.main()
