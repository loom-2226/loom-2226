from __future__ import annotations

import pytest

from loom.application import SpatialState, TrajectorySegment, TrajectorySolution
from loom.navigation import (
    TRAJECTORY_VISUAL_SAMPLING_VERSION,
    TrajectoryVisualSamplingConfig,
    TrajectoryVisualSamplingError,
    sample_trajectory_for_visualization,
)


FRAME = "TEST_FRAME"


def _state(epoch: str, x: float) -> SpatialState:
    return SpatialState(
        entity_id="SHIP",
        epoch_utc=epoch,
        reference_frame=FRAME,
        position_km=(x, 0.0, 0.0),
        velocity_km_s=(10.0, 0.0, 0.0),
        navigation_grade=True,
    )


def _solution() -> TrajectorySolution:
    s0 = _state("2226-01-01T00:00:00Z", 0.0)
    s1 = _state("2226-01-01T00:10:00Z", 6000.0)
    s2 = _state("2226-01-01T00:20:00Z", 12000.0)
    return TrajectorySolution(
        trajectory_id="e3-test",
        campaign_revision=10,
        solution_epoch="2226-01-01T00:00:00Z",
        origin="A",
        destination="B",
        reference_frame=FRAME,
        departure_epoch="2226-01-01T00:00:00Z",
        arrival_epoch="2226-01-01T00:30:00Z",
        segments=(
            TrajectorySegment(
                segment_id="ordinary",
                segment_type="TORCH",
                start_epoch="2226-01-01T00:00:00Z",
                end_epoch="2226-01-01T00:20:00Z",
                samples=(s0, s1, s2),
            ),
            TrajectorySegment(
                segment_id="metric",
                segment_type="METRIC",
                start_epoch="2226-01-01T00:20:00Z",
                end_epoch="2226-01-01T00:30:00Z",
                samples=(),
                payload={"metric_semantics": "RELATIONAL"},
            ),
        ),
    )


def test_adaptive_sampling_is_deterministic_and_preserves_event_epochs() -> None:
    config = TrajectoryVisualSamplingConfig(
        dense_step_seconds=60.0,
        cruise_step_seconds=300.0,
        dense_window_seconds=120.0,
    )
    first = sample_trajectory_for_visualization(_solution(), config)
    second = sample_trajectory_for_visualization(_solution(), config)

    assert first.contract == TRAJECTORY_VISUAL_SAMPLING_VERSION
    assert first == second
    assert first.event_epochs == (
        "2226-01-01T00:00:00Z",
        "2226-01-01T00:20:00Z",
        "2226-01-01T00:30:00Z",
    )


def test_sampling_is_dense_near_boundaries_and_sparse_in_cruise() -> None:
    result = sample_trajectory_for_visualization(
        _solution(),
        TrajectoryVisualSamplingConfig(
            dense_step_seconds=60.0,
            cruise_step_seconds=300.0,
            dense_window_seconds=120.0,
        ),
    )
    epochs = {sample.epoch_utc for sample in result.samples}

    assert "2226-01-01T00:01:00Z" in epochs
    assert "2226-01-01T00:02:00Z" in epochs
    assert "2226-01-01T00:07:00Z" in epochs
    assert "2226-01-01T00:10:00Z" in epochs
    assert "2226-01-01T00:19:00Z" in epochs
    assert "2226-01-01T00:20:00Z" in epochs


def test_authoritative_source_samples_are_retained_exactly() -> None:
    solution = _solution()
    result = sample_trajectory_for_visualization(
        solution,
        TrajectoryVisualSamplingConfig(
            dense_step_seconds=120.0,
            cruise_step_seconds=420.0,
            dense_window_seconds=0.0,
        ),
    )
    by_epoch = {sample.epoch_utc: sample for sample in result.samples}

    source = solution.segments[0].samples[1]
    retained = by_epoch[source.epoch_utc]
    assert retained.evaluation_mode == "EXACT_AUTHORITATIVE_SAMPLE"
    assert retained.spatial_state is source


def test_metric_phase_never_gets_invented_ordinary_coordinates() -> None:
    result = sample_trajectory_for_visualization(
        _solution(),
        TrajectoryVisualSamplingConfig(
            dense_step_seconds=60.0,
            cruise_step_seconds=180.0,
            dense_window_seconds=60.0,
        ),
    )
    metric_rows = [
        sample
        for sample in result.samples
        if sample.segment_id == "metric" and sample.epoch_utc != "2226-01-01T00:20:00Z"
    ]

    assert metric_rows
    assert all(sample.state_kind == "RELATIONAL" for sample in metric_rows)
    assert all(sample.spatial_state is None for sample in metric_rows)
    assert all(sample.evaluation_mode == "RELATIONAL_NO_ORDINARY_STATE" for sample in metric_rows)


def test_interpolated_visual_samples_are_non_navigation_grade() -> None:
    result = sample_trajectory_for_visualization(
        _solution(),
        TrajectoryVisualSamplingConfig(
            dense_step_seconds=60.0,
            cruise_step_seconds=300.0,
            dense_window_seconds=120.0,
        ),
    )
    sample = next(row for row in result.samples if row.epoch_utc == "2226-01-01T00:01:00Z")

    assert sample.evaluation_mode == "LINEAR_BETWEEN_AUTHORITATIVE_SAMPLES"
    assert sample.spatial_state is not None
    assert sample.spatial_state.navigation_grade is False


def test_sample_cap_fails_closed() -> None:
    with pytest.raises(TrajectoryVisualSamplingError, match="max_samples"):
        sample_trajectory_for_visualization(
            _solution(),
            TrajectoryVisualSamplingConfig(
                dense_step_seconds=1.0,
                cruise_step_seconds=1.0,
                dense_window_seconds=0.0,
                max_samples=10,
            ),
        )
