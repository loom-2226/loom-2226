"""Deterministic time-state evaluation over canonical E1 trajectory packets.

E2 is a representation/runtime evaluator, not a trajectory solver. It consumes
``TrajectorySolution`` samples already promoted from authoritative Navigator /
Sequence-B output. Exact authoritative samples are returned unchanged.
Ordinary-space state between two authoritative samples in the same segment is
linearly interpolated in time for runtime/playback use and is explicitly marked
non-navigation-grade.

Metric/relational phases never receive invented ordinary-space coordinates. If
a queried epoch lies in a segment without a valid ordinary-space bracket, the
result is explicitly relational/no-ordinary-state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from loom.application import SpatialState, TrajectorySegment, TrajectorySolution

TRAJECTORY_TIME_STATE_VERSION = "LOOM_TRAJECTORY_TIME_STATE_E2_V1"


class TrajectoryTimeStateError(ValueError):
    """Raised when a trajectory cannot be evaluated deterministically."""


def _instant(value: str, name: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise TrajectoryTimeStateError(f"{name} is required")
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise TrajectoryTimeStateError(f"{name} must be ISO-8601") from exc
    if dt.tzinfo is None:
        raise TrajectoryTimeStateError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _same_state(a: SpatialState, b: SpatialState) -> bool:
    return (
        a.entity_id == b.entity_id
        and a.reference_frame == b.reference_frame
        and tuple(a.position_km) == tuple(b.position_km)
        and tuple(a.velocity_km_s) == tuple(b.velocity_km_s)
    )


def _lerp(a: float, b: float, alpha: float) -> float:
    return a + (b - a) * alpha


@dataclass(frozen=True)
class TrajectoryTimeStateV1:
    """Read-only evaluation result for one trajectory at one query epoch."""

    trajectory_id: str
    epoch_utc: str
    segment_id: str
    segment_type: str
    state_kind: str
    evaluation_mode: str
    spatial_state: SpatialState | None = None
    source_epochs: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)
    contract: str = TRAJECTORY_TIME_STATE_VERSION

    @property
    def has_ordinary_state(self) -> bool:
        return self.spatial_state is not None


def _segment_candidates(solution: TrajectorySolution, target: datetime) -> tuple[TrajectorySegment, ...]:
    out: list[TrajectorySegment] = []
    for segment in solution.segments:
        start = _instant(segment.start_epoch, "segment start_epoch")
        end = _instant(segment.end_epoch, "segment end_epoch")
        if start <= target <= end:
            out.append(segment)
    return tuple(out)


def _ordered_samples(segment: TrajectorySegment) -> tuple[tuple[datetime, SpatialState], ...]:
    rows = sorted(
        ((_instant(sample.epoch_utc, "sample epoch_utc"), sample) for sample in segment.samples),
        key=lambda row: row[0],
    )
    for index in range(1, len(rows)):
        if rows[index - 1][0] == rows[index][0] and not _same_state(rows[index - 1][1], rows[index][1]):
            raise TrajectoryTimeStateError(
                f"segment {segment.segment_id} has conflicting ordinary states at one epoch"
            )
    return tuple(rows)


def _evaluate_segment(
    solution: TrajectorySolution,
    segment: TrajectorySegment,
    epoch_utc: str,
    target: datetime,
) -> TrajectoryTimeStateV1:
    samples = _ordered_samples(segment)

    exact = [sample for instant, sample in samples if instant == target]
    if exact:
        first = exact[0]
        if any(not _same_state(first, other) for other in exact[1:]):
            raise TrajectoryTimeStateError(
                f"segment {segment.segment_id} has ambiguous exact state"
            )
        return TrajectoryTimeStateV1(
            trajectory_id=solution.trajectory_id,
            epoch_utc=epoch_utc,
            segment_id=segment.segment_id,
            segment_type=segment.segment_type,
            state_kind="ORDINARY",
            evaluation_mode="EXACT_AUTHORITATIVE_SAMPLE",
            spatial_state=first,
            source_epochs=(first.epoch_utc,),
            payload={"authority": "SOURCE_SAMPLE"},
        )

    left: tuple[datetime, SpatialState] | None = None
    right: tuple[datetime, SpatialState] | None = None
    for row in samples:
        if row[0] < target:
            left = row
        elif row[0] > target:
            right = row
            break

    if left is not None and right is not None:
        left_t, left_state = left
        right_t, right_state = right
        if left_state.entity_id != right_state.entity_id:
            raise TrajectoryTimeStateError("ordinary interpolation bracket changes entity_id")
        if left_state.reference_frame != right_state.reference_frame:
            raise TrajectoryTimeStateError("ordinary interpolation bracket changes reference_frame")
        duration = (right_t - left_t).total_seconds()
        if duration <= 0:
            raise TrajectoryTimeStateError("ordinary interpolation bracket is not strictly ordered")
        alpha = (target - left_t).total_seconds() / duration
        position = tuple(
            _lerp(float(a), float(b), alpha)
            for a, b in zip(left_state.position_km, right_state.position_km)
        )
        velocity = tuple(
            _lerp(float(a), float(b), alpha)
            for a, b in zip(left_state.velocity_km_s, right_state.velocity_km_s)
        )
        state = SpatialState(
            entity_id=left_state.entity_id,
            epoch_utc=epoch_utc,
            reference_frame=left_state.reference_frame,
            position_km=position,
            velocity_km_s=velocity,
            navigation_grade=False,
            provenance={
                "authority": "DERIVED_FROM_AUTHORITATIVE_SAMPLES",
                "evaluator": TRAJECTORY_TIME_STATE_VERSION,
                "method": "LINEAR_IN_TIME",
                "source_segment_id": segment.segment_id,
                "source_epochs": (left_state.epoch_utc, right_state.epoch_utc),
            },
            payload={
                "interpolation_fraction": alpha,
                "source_left": dict(left_state.payload),
                "source_right": dict(right_state.payload),
            },
        )
        return TrajectoryTimeStateV1(
            trajectory_id=solution.trajectory_id,
            epoch_utc=epoch_utc,
            segment_id=segment.segment_id,
            segment_type=segment.segment_type,
            state_kind="ORDINARY",
            evaluation_mode="LINEAR_BETWEEN_AUTHORITATIVE_SAMPLES",
            spatial_state=state,
            source_epochs=(left_state.epoch_utc, right_state.epoch_utc),
            payload={"interpolation_fraction": alpha},
        )

    return TrajectoryTimeStateV1(
        trajectory_id=solution.trajectory_id,
        epoch_utc=epoch_utc,
        segment_id=segment.segment_id,
        segment_type=segment.segment_type,
        state_kind="RELATIONAL",
        evaluation_mode="RELATIONAL_NO_ORDINARY_STATE",
        spatial_state=None,
        source_epochs=(),
        payload={
            "metric_semantics": dict(segment.payload).get("metric_semantics"),
            "ordinary_space_samples_available": bool(segment.samples),
            "reason": "NO_AUTHORITATIVE_ORDINARY_BRACKET_AT_QUERY_EPOCH",
        },
    )


def evaluate_trajectory_at_epoch(
    solution: TrajectorySolution,
    epoch_utc: str,
) -> TrajectoryTimeStateV1:
    """Evaluate a canonical trajectory at ``epoch_utc`` without campaign mutation.

    Evaluation is confined to the solution's authoritative time bounds and to a
    single declared segment. At shared segment boundaries an exact ordinary
    sample takes precedence; otherwise the earlier segment wins deterministically.
    No extrapolation is performed.
    """
    target = _instant(epoch_utc, "epoch_utc")
    departure = _instant(solution.departure_epoch, "departure_epoch")
    arrival = _instant(solution.arrival_epoch, "arrival_epoch")
    if target < departure or target > arrival:
        raise TrajectoryTimeStateError("query epoch lies outside trajectory bounds")

    candidates = _segment_candidates(solution, target)
    if not candidates:
        raise TrajectoryTimeStateError("query epoch is not covered by any trajectory segment")

    results = tuple(_evaluate_segment(solution, segment, epoch_utc, target) for segment in candidates)
    exact = tuple(result for result in results if result.evaluation_mode == "EXACT_AUTHORITATIVE_SAMPLE")
    if exact:
        first = exact[0]
        for other in exact[1:]:
            if first.spatial_state is not None and other.spatial_state is not None and not _same_state(first.spatial_state, other.spatial_state):
                raise TrajectoryTimeStateError("shared segment boundary has conflicting exact ordinary states")
        return first
    return results[0]
