"""HUD/local-flight presentation contracts.

The HUD is a consumer of authoritative/derived state. It does not own
navigation, ephemeris, orbital, vehicle, or campaign authority.
"""

from .contracts import (
    AuthorityClass,
    Availability,
    FlightViewState,
    HudMode,
    HudStatePacket,
    QuaternionXYZW,
    ReferenceFrame,
    SceneObject,
    SceneObjectRole,
    SpatialScenePacket,
    StateDatum,
    SyntheticVisionMode,
    Vector3,
    mock_hud_packet,
)
from .projection import (
    CameraProjection,
    edge_indicator_position,
    project_camera_vector,
    project_world_point,
    rotate_vector,
    subtract,
    world_to_camera,
)

__all__ = [
    "AuthorityClass",
    "Availability",
    "CameraProjection",
    "FlightViewState",
    "HudMode",
    "HudStatePacket",
    "QuaternionXYZW",
    "ReferenceFrame",
    "SceneObject",
    "SceneObjectRole",
    "SpatialScenePacket",
    "StateDatum",
    "SyntheticVisionMode",
    "Vector3",
    "edge_indicator_position",
    "mock_hud_packet",
    "project_camera_vector",
    "project_world_point",
    "rotate_vector",
    "subtract",
    "world_to_camera",
]
