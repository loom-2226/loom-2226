"""Navigator-facing adapter for the shared LOOM spatial target resolver.

This module performs no orbital math and no campaign mutation. It gives
Navigator a stable seam for named targets while preserving the spatial layer as
the single state-resolution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from loom.application.contracts import SpatialState


class SpatialTargetResolverProtocol(Protocol):
    def describe_target(self, target_id: str) -> dict[str, Any]: ...
    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState: ...


class NavigationTargetError(RuntimeError):
    """Raised when Navigator cannot obtain a target through the shared resolver."""


@dataclass(frozen=True)
class NavigationTargetAdapter:
    resolver: SpatialTargetResolverProtocol

    def describe_target(self, target_id: str) -> dict[str, Any]:
        try:
            return self.resolver.describe_target(target_id)
        except Exception as exc:
            raise NavigationTargetError(f"cannot describe spatial target {target_id}: {exc}") from exc

    def resolve_target_state(self, target_id: str, epoch_utc: str) -> SpatialState:
        """Return the spatial layer's state unchanged.

        The adapter intentionally adds no caller identity, coordinate fallback,
        orbit calculation, or target normalization. Manual, LLM, NPC and system
        planners therefore see the same physical state for the same target/epoch.
        """
        try:
            state = self.resolver.resolve_target_state(target_id, epoch_utc)
        except Exception as exc:
            raise NavigationTargetError(
                f"cannot resolve spatial target {target_id} at {epoch_utc}: {exc}"
            ) from exc
        if state.entity_id != str(target_id).strip():
            raise NavigationTargetError("spatial resolver returned a different entity_id")
        if state.epoch_utc != epoch_utc:
            raise NavigationTargetError("spatial resolver returned a different epoch")
        return state
