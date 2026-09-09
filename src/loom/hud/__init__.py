"""HUD/local-flight presentation contracts.

The HUD is a consumer of authoritative/derived state. It does not own
navigation, ephemeris, orbital, vehicle, or campaign authority.
"""

from .contracts import (
    AuthorityClass,
    Availability,
    HudMode,
    HudStatePacket,
    SceneObject,
    SceneObjectRole,
    SpatialScenePacket,
    StateDatum,
    Vector3,
    mock_hud_packet,
)

__all__ = [
    "AuthorityClass",
    "Availability",
    "HudMode",
    "HudStatePacket",
    "SceneObject",
    "SceneObjectRole",
    "SpatialScenePacket",
    "StateDatum",
    "Vector3",
    "mock_hud_packet",
]
