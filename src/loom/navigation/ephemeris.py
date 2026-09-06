"""Ephemeris provider boundary for LOOM navigation.

Phase 2 does not introduce a second ephemeris implementation. The legacy
adapter delegates to Sequence H's canonical dependency index and promotes only
stable envelope metadata. The full authoritative legacy result remains in the
snapshot payload for lossless transition.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import EphemerisSnapshot, NavigationContext


@dataclass
class LegacySequenceHEphemerisProvider:
    """Read-only adapter over Sequence H canonical ephemeris/dependency truth."""

    sequence_h: Any

    def snapshot(self, context: NavigationContext, epoch: str | None = None) -> EphemerisSnapshot:
        if context.acquisition is None:
            raise RuntimeError("ephemeris snapshot requires authoritative Sequence-H acquisition")
        if context.cache_dir is None:
            raise RuntimeError("ephemeris snapshot requires the Sequence-H cache directory")

        canonical, validation = self.sequence_h.build_canonical_dependency_index(
            context.acquisition, context.cache_dir
        )
        resolved_epoch = epoch or context.campaign_state.get("epoch_utc")
        if not resolved_epoch:
            raise RuntimeError("ephemeris snapshot requires an epoch")

        # Do not guess or normalize the internal canonical schema during Phase 2.
        # Consumers that need body-specific rows continue to use the opaque payload
        # until Phase 3 defines the typed GIS/navigation route-layer contract.
        payload = {
            "provider": "LEGACY_SEQUENCE_H_CANONICAL",
            "canonical_dependency_index": canonical,
            "axis_validation": validation,
        }
        return EphemerisSnapshot(
            epoch_utc=resolved_epoch,
            bodies={},
            payload=payload,
        )
