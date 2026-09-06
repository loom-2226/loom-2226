"""Authoritative 3D spatial state runtime for LOOM Stage C.

The runtime owns frame-graph traversal and state conversion. It is presentation-
agnostic and deterministic for a fixed epoch/input state set.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from loom.application.contracts import SpatialState
from .frames import SpatialFrame, SpatialTransformError, transform_state


class SpatialRuntimeError(RuntimeError):
    """Raised when the spatial graph or state request is invalid."""


@dataclass
class SpatialRuntime:
    root_frame_id: str
    frames: Mapping[str, SpatialFrame]

    def __post_init__(self) -> None:
        self.root_frame_id = str(self.root_frame_id).strip()
        self.frames = dict(self.frames)
        if not self.root_frame_id:
            raise SpatialRuntimeError("root_frame_id is required")
        root = self.frames.get(self.root_frame_id)
        if root is None:
            raise SpatialRuntimeError("root frame is not registered")
        if root.parent_frame is not None:
            raise SpatialRuntimeError("root frame must not have a parent")
        for frame_id, frame in self.frames.items():
            if frame_id != frame.frame_id:
                raise SpatialRuntimeError("frame registry key differs from frame_id")
            if frame.parent_frame is not None and frame.parent_frame not in self.frames:
                raise SpatialRuntimeError(f"unknown parent frame: {frame.parent_frame}")
        for frame_id in self.frames:
            self._path_to_root(frame_id)

    def _path_to_root(self, frame_id: str) -> list[str]:
        if frame_id not in self.frames:
            raise SpatialRuntimeError(f"unknown frame: {frame_id}")
        path: list[str] = []
        seen: set[str] = set()
        current: str | None = frame_id
        while current is not None:
            if current in seen:
                raise SpatialRuntimeError("frame graph contains a cycle")
            seen.add(current)
            path.append(current)
            current = self.frames[current].parent_frame
        if path[-1] != self.root_frame_id:
            raise SpatialRuntimeError("frame does not resolve to configured root")
        return path

    def transform(self, state: SpatialState, target_frame_id: str) -> SpatialState:
        """Transform state through the explicit frame tree to ``target_frame_id``."""
        source_id = state.reference_frame
        if source_id not in self.frames:
            raise SpatialRuntimeError(f"state uses unknown frame: {source_id}")
        if target_frame_id not in self.frames:
            raise SpatialRuntimeError(f"unknown target frame: {target_frame_id}")
        if source_id == target_frame_id:
            return state

        source_path = self._path_to_root(source_id)
        target_path = self._path_to_root(target_frame_id)
        target_set = set(target_path)
        common = next((fid for fid in source_path if fid in target_set), None)
        if common is None:
            raise SpatialRuntimeError("frames have no common root")

        current = state
        current_id = source_id
        while current_id != common:
            source = self.frames[current_id]
            parent_id = source.parent_frame
            assert parent_id is not None
            try:
                current = transform_state(current, source, self.frames[parent_id])
            except SpatialTransformError as exc:
                raise SpatialRuntimeError(str(exc)) from exc
            current_id = parent_id

        down: list[str] = []
        cursor = target_frame_id
        while cursor != common:
            down.append(cursor)
            parent = self.frames[cursor].parent_frame
            assert parent is not None
            cursor = parent
        for child_id in reversed(down):
            try:
                current = transform_state(current, self.frames[current_id], self.frames[child_id])
            except SpatialTransformError as exc:
                raise SpatialRuntimeError(str(exc)) from exc
            current_id = child_id
        return current

    def normalize_states(
        self,
        states: Iterable[SpatialState],
        *,
        target_frame_id: str | None = None,
        epoch_utc: str | None = None,
    ) -> tuple[SpatialState, ...]:
        """Return deterministic, entity-sorted states in one explicit frame/epoch."""
        target = target_frame_id or self.root_frame_id
        out: list[SpatialState] = []
        seen: set[str] = set()
        for state in states:
            if state.entity_id in seen:
                raise SpatialRuntimeError(f"duplicate entity_id: {state.entity_id}")
            seen.add(state.entity_id)
            if epoch_utc is not None and state.epoch_utc != epoch_utc:
                raise SpatialRuntimeError("state epoch differs from requested scene epoch")
            out.append(self.transform(state, target))
        return tuple(sorted(out, key=lambda item: item.entity_id))
