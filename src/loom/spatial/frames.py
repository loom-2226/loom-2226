"""Explicit reference-frame transforms for LOOM spatial state.

Stage C keeps the first transform model deliberately conservative: inertial
frames are translated by an explicit origin state only. No renderer may invent
or infer physical frame transforms. Rotating/body-fixed transforms are reserved
until an authoritative orientation model is promoted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from loom.application.contracts import SpatialState


class SpatialTransformError(RuntimeError):
    """Raised when a requested physical frame transform is unsupported/invalid."""


def _vec3(values: Sequence[float]) -> tuple[float, float, float]:
    out = tuple(float(v) for v in values)
    if len(out) != 3:
        raise SpatialTransformError("expected exactly three vector components")
    return out  # type: ignore[return-value]


def _add(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    aa, bb = _vec3(a), _vec3(b)
    return tuple(aa[i] + bb[i] for i in range(3))  # type: ignore[return-value]


def _sub(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    aa, bb = _vec3(a), _vec3(b)
    return tuple(aa[i] - bb[i] for i in range(3))  # type: ignore[return-value]


@dataclass(frozen=True)
class SpatialFrame:
    """One explicit spatial frame definition.

    ``origin_state`` must itself be expressed in ``parent_frame``. Stage C V1
    supports translation-only inertial transforms. Orientation/rotation must be
    absent until the authoritative body-orientation model is introduced.
    """

    frame_id: str
    parent_frame: str | None = None
    origin_state: SpatialState | None = None
    inertial: bool = True

    def __post_init__(self) -> None:
        frame = str(self.frame_id).strip()
        if not frame:
            raise SpatialTransformError("frame_id is required")
        object.__setattr__(self, "frame_id", frame)
        if self.parent_frame is not None:
            parent = str(self.parent_frame).strip()
            if not parent:
                raise SpatialTransformError("parent_frame cannot be blank")
            object.__setattr__(self, "parent_frame", parent)
        if self.parent_frame is None and self.origin_state is not None:
            raise SpatialTransformError("root frame cannot have an origin_state")
        if self.parent_frame is not None and self.origin_state is None:
            raise SpatialTransformError("non-root frame requires origin_state")
        if self.origin_state is not None:
            if self.origin_state.reference_frame != self.parent_frame:
                raise SpatialTransformError("origin_state must be expressed in parent_frame")
            if self.origin_state.orientation:
                raise SpatialTransformError("rotating/body-fixed transforms are not yet authorized")
        if not self.inertial:
            raise SpatialTransformError("non-inertial transforms are not yet authorized")


def relative_state(subject: SpatialState, origin: SpatialState, *, frame_id: str) -> SpatialState:
    """Express ``subject`` relative to ``origin`` at the same epoch/frame."""
    if subject.epoch_utc != origin.epoch_utc:
        raise SpatialTransformError("relative states require identical epochs")
    if subject.reference_frame != origin.reference_frame:
        raise SpatialTransformError("relative states require the same source frame")
    return SpatialState(
        entity_id=subject.entity_id,
        epoch_utc=subject.epoch_utc,
        reference_frame=frame_id,
        position_km=_sub(subject.position_km, origin.position_km),
        velocity_km_s=_sub(subject.velocity_km_s, origin.velocity_km_s),
        provenance={**dict(subject.provenance), "relative_origin": origin.entity_id},
        navigation_grade=subject.navigation_grade,
        uncertainty=subject.uncertainty,
        payload=subject.payload,
    )


def transform_state(state: SpatialState, source: SpatialFrame, target: SpatialFrame) -> SpatialState:
    """Translate a state between directly related inertial frames.

    V1 intentionally allows only parent<->child translation. Multi-hop traversal
    is owned by :class:`SpatialRuntime`, which resolves an explicit frame graph.
    """
    if state.reference_frame != source.frame_id:
        raise SpatialTransformError("state reference_frame does not match source frame")
    if source.frame_id == target.frame_id:
        return state

    if target.parent_frame == source.frame_id:
        origin = target.origin_state
        assert origin is not None
        if origin.epoch_utc != state.epoch_utc:
            raise SpatialTransformError("frame origin epoch differs from state epoch")
        return SpatialState(
            entity_id=state.entity_id,
            epoch_utc=state.epoch_utc,
            reference_frame=target.frame_id,
            position_km=_sub(state.position_km, origin.position_km),
            velocity_km_s=_sub(state.velocity_km_s, origin.velocity_km_s),
            provenance=state.provenance,
            navigation_grade=state.navigation_grade,
            uncertainty=state.uncertainty,
            payload=state.payload,
        )

    if source.parent_frame == target.frame_id:
        origin = source.origin_state
        assert origin is not None
        if origin.epoch_utc != state.epoch_utc:
            raise SpatialTransformError("frame origin epoch differs from state epoch")
        return SpatialState(
            entity_id=state.entity_id,
            epoch_utc=state.epoch_utc,
            reference_frame=target.frame_id,
            position_km=_add(state.position_km, origin.position_km),
            velocity_km_s=_add(state.velocity_km_s, origin.velocity_km_s),
            provenance=state.provenance,
            navigation_grade=state.navigation_grade,
            uncertainty=state.uncertainty,
            payload=state.payload,
        )

    raise SpatialTransformError("frames are not directly related")
