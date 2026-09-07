"""Deterministic adaptive visualization sampling for canonical trajectories.

E3 is a presentation/runtime representation layer. It never solves trajectories,
changes campaign state, or invents ordinary-space motion through relational
metric phases. It consumes canonical ``TrajectorySolution`` packets and delegates
state-at-time resolution to the E2 evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from loom.application import TrajectorySolution

from .trajectory_time_state import TrajectoryTimeStateV1, evaluate_trajectory_at_epoch

TRAJECTORY_VISUAL_SAMPLING_VERSION = "LOOM_TRAJECTORY_VISUAL_SAMPLING_E3_V1"


class TrajectoryVisualSamplingError(ValueError):
    """Raised when a deterministic visualization sampling plan is invalid."""


def _instant(value: str, name: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise TrajectoryVisualSamplingError(f"{name} is required")
    probe = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        dt = datetime.fromisoformat(probe)
    except ValueError as exc:
        raise TrajectoryVisualSamplingError(f"{name} must be ISO-8601") from exc
    if dt.tzinfo is None:
        raise TrajectoryVisualSamplingError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _epoch_text(value: datetime) -> str:
    utc = value.astimezone(timezone.utc)
    text = utc.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return text[:-8] + "Z" if text.endswith(".000000Z") else text


@dataclass(frozen=True)
class TrajectoryVisualSamplingConfig:
    """Deterministic density controls for visualization-only sampling."""

    dense_step_seconds: float = 30.0
    cruise_step_seconds: float = 300.0
    dense_window_seconds: float = 120.0
    max_samples: int = 4096

    def __post_init__(self) -> None:
        dense = float(self.dense_step_seconds)
        cruise = float(self.cruise_step_seconds)
        window = float(self.dense_window_seconds)
        if dense <= 0 or cruise <= 0:
            raise TrajectoryVisualSamplingError("sampling steps must be greater than zero")
        if cruise < dense:
            raise TrajectoryVisualSamplingError("cruise_step_seconds must be >= dense_step_seconds")
        if window < 0:
            raise TrajectoryVisualSamplingError("dense_window_seconds must be non-negative")
        if isinstance(self.max_samples, bool) or int(self.max_samples) != self.max_samples or int(self.max_samples) < 2:
            raise TrajectoryVisualSamplingError("max_samples must be an integer >= 2")
        object.__setattr__(self, "dense_step_seconds", dense)
        object.__setattr__(self, "cruise_step_seconds", cruise)
        object.__setattr__(self, "dense_window_seconds", window)
        object.__setattr__(self, "max_samples", int(self.max_samples))


@dataclass(frozen=True)
class TrajectoryVisualSampleSetV1:
    """Read-only adaptive visualization samples over one canonical trajectory."""

    trajectory_id: str
    samples: tuple[TrajectoryTimeStateV1, ...]
    event_epochs: tuple[str, ...]
    payload: Mapping[str, Any] = field(default_factory=dict)
    contract: str = TRAJECTORY_VISUAL_SAMPLING_VERSION

    @property
    def ordinary_sample_count(self) -> int:
        return sum(1 for sample in self.samples if sample.has_ordinary_state)

    @property
    def relational_sample_count(self) -> int:
        return len(self.samples) - self.ordinary_sample_count


def _segment_epochs(solution: TrajectorySolution, config: TrajectoryVisualSamplingConfig) -> tuple[datetime, ...]:
    epochs: set[datetime] = set()
    for segment in solution.segments:
        start = _instant(segment.start_epoch, "segment start_epoch")
        end = _instant(segment.end_epoch, "segment end_epoch")
        if end < start:
            raise TrajectoryVisualSamplingError(f"segment {segment.segment_id} ends before it starts")

        epochs.add(start)
        epochs.add(end)
        for sample in segment.samples:
            instant = _instant(sample.epoch_utc, "sample epoch_utc")
            if start <= instant <= end:
                epochs.add(instant)

        cursor = start
        while cursor < end:
            from_start = (cursor - start).total_seconds()
            to_end = (end - cursor).total_seconds()
            dense = (
                from_start < config.dense_window_seconds
                or to_end <= config.dense_window_seconds
            )
            step = config.dense_step_seconds if dense else config.cruise_step_seconds
            next_cursor = min(cursor + timedelta(seconds=step), end)
            if next_cursor <= cursor:
                raise TrajectoryVisualSamplingError("sampling cursor failed to advance")
            epochs.add(next_cursor)
            if len(epochs) > config.max_samples:
                raise TrajectoryVisualSamplingError("adaptive sampling exceeded max_samples")
            cursor = next_cursor

    departure = _instant(solution.departure_epoch, "departure_epoch")
    arrival = _instant(solution.arrival_epoch, "arrival_epoch")
    epochs.add(departure)
    epochs.add(arrival)
    if len(epochs) > config.max_samples:
        raise TrajectoryVisualSamplingError("adaptive sampling exceeded max_samples")
    return tuple(sorted(epochs))


def sample_trajectory_for_visualization(
    solution: TrajectorySolution,
    config: TrajectoryVisualSamplingConfig | None = None,
) -> TrajectoryVisualSampleSetV1:
    """Produce deterministic visualization samples without campaign mutation.

    Segment boundaries and authoritative source samples are always retained.
    Sampling becomes denser near each segment boundary and sparser during cruise.
    Each epoch is resolved through the E2 evaluator, so metric/relational phases
    remain explicitly without ordinary-space coordinates and no interpolation can
    cross a segment/metric gap.
    """
    cfg = config or TrajectoryVisualSamplingConfig()
    epochs = _segment_epochs(solution, cfg)
    samples = tuple(
        evaluate_trajectory_at_epoch(solution, _epoch_text(epoch))
        for epoch in epochs
    )

    event_epochs = {
        _epoch_text(_instant(solution.departure_epoch, "departure_epoch")),
        _epoch_text(_instant(solution.arrival_epoch, "arrival_epoch")),
    }
    for segment in solution.segments:
        event_epochs.add(_epoch_text(_instant(segment.start_epoch, "segment start_epoch")))
        event_epochs.add(_epoch_text(_instant(segment.end_epoch, "segment end_epoch")))

    return TrajectoryVisualSampleSetV1(
        trajectory_id=solution.trajectory_id,
        samples=samples,
        event_epochs=tuple(sorted(event_epochs, key=lambda value: _instant(value, "event_epoch"))),
        payload={
            "dense_step_seconds": cfg.dense_step_seconds,
            "cruise_step_seconds": cfg.cruise_step_seconds,
            "dense_window_seconds": cfg.dense_window_seconds,
            "max_samples": cfg.max_samples,
            "sampling_authority": "VISUALIZATION_ONLY",
            "state_evaluator": "LOOM_TRAJECTORY_TIME_STATE_E2_V1",
        },
    )
