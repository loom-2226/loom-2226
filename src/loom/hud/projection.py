from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, hypot, radians, sqrt, tan
from typing import Iterable, Tuple

from .contracts import QuaternionXYZW, Vector3


@dataclass(frozen=True)
class CameraProjection:
    screen_x: float
    screen_y: float
    bearing_deg: float
    elevation_deg: float
    in_front: bool
    on_screen: bool
    camera_vector: Vector3


def subtract(a: Vector3, b: Vector3) -> Vector3:
    return Vector3(a.x - b.x, a.y - b.y, a.z - b.z)


def _normalized_quaternion(q: QuaternionXYZW) -> QuaternionXYZW:
    x, y, z, w = q
    norm = sqrt(x * x + y * y + z * z + w * w)
    if norm == 0.0:
        raise ValueError("camera quaternion must be non-zero")
    return (x / norm, y / norm, z / norm, w / norm)


def rotate_vector(q_xyzw: QuaternionXYZW, v: Vector3) -> Vector3:
    """Rotate vector by quaternion using the Hamilton convention.

    FlightViewState defines this quaternion as camera-from-inertial, so callers
    pass inertial relative vectors here and receive camera-frame vectors.
    Camera axes are +X forward, +Y right, +Z up.
    """
    qx, qy, qz, qw = _normalized_quaternion(q_xyzw)
    # Efficient q * v * q^-1 vector form.
    tx = 2.0 * (qy * v.z - qz * v.y)
    ty = 2.0 * (qz * v.x - qx * v.z)
    tz = 2.0 * (qx * v.y - qy * v.x)
    return Vector3(
        v.x + qw * tx + (qy * tz - qz * ty),
        v.y + qw * ty + (qz * tx - qx * tz),
        v.z + qw * tz + (qx * ty - qy * tx),
    )


def world_to_camera(
    *,
    object_position_inertial: Vector3,
    ship_position_inertial: Vector3,
    camera_from_inertial_xyzw: QuaternionXYZW,
) -> Vector3:
    relative = subtract(object_position_inertial, ship_position_inertial)
    return rotate_vector(camera_from_inertial_xyzw, relative)


def project_camera_vector(
    camera_vector: Vector3,
    *,
    viewport_width_px: float,
    viewport_height_px: float,
    fov_y_deg: float,
) -> CameraProjection:
    if viewport_width_px <= 0 or viewport_height_px <= 0:
        raise ValueError("viewport dimensions must be positive")
    if not (1.0 <= fov_y_deg < 179.0):
        raise ValueError("fov_y_deg must be in [1, 179)")

    forward, right, up = camera_vector.x, camera_vector.y, camera_vector.z
    bearing = degrees(atan2(right, forward))
    elevation = degrees(atan2(up, hypot(forward, right)))
    in_front = forward > 0.0

    aspect = viewport_width_px / viewport_height_px
    tan_half_y = tan(radians(fov_y_deg) / 2.0)
    tan_half_x = tan_half_y * aspect

    if not in_front:
        return CameraProjection(
            screen_x=viewport_width_px / 2.0,
            screen_y=viewport_height_px / 2.0,
            bearing_deg=bearing,
            elevation_deg=elevation,
            in_front=False,
            on_screen=False,
            camera_vector=camera_vector,
        )

    nx = (right / forward) / tan_half_x
    ny = (up / forward) / tan_half_y
    screen_x = (nx + 1.0) * 0.5 * viewport_width_px
    screen_y = (1.0 - ny) * 0.5 * viewport_height_px
    on_screen = -1.0 <= nx <= 1.0 and -1.0 <= ny <= 1.0

    return CameraProjection(
        screen_x=screen_x,
        screen_y=screen_y,
        bearing_deg=bearing,
        elevation_deg=elevation,
        in_front=True,
        on_screen=on_screen,
        camera_vector=camera_vector,
    )


def project_world_point(
    *,
    object_position_inertial: Vector3,
    ship_position_inertial: Vector3,
    camera_from_inertial_xyzw: QuaternionXYZW,
    viewport_width_px: float,
    viewport_height_px: float,
    fov_y_deg: float,
) -> CameraProjection:
    camera_vector = world_to_camera(
        object_position_inertial=object_position_inertial,
        ship_position_inertial=ship_position_inertial,
        camera_from_inertial_xyzw=camera_from_inertial_xyzw,
    )
    return project_camera_vector(
        camera_vector,
        viewport_width_px=viewport_width_px,
        viewport_height_px=viewport_height_px,
        fov_y_deg=fov_y_deg,
    )


def edge_indicator_position(
    projection: CameraProjection,
    *,
    viewport_width_px: float,
    viewport_height_px: float,
    margin_px: float = 24.0,
) -> Tuple[float, float]:
    """Clamp an off-screen bearing to the viewport edge for symbology only."""
    cx, cy = viewport_width_px / 2.0, viewport_height_px / 2.0
    dx = projection.screen_x - cx
    dy = projection.screen_y - cy
    if dx == 0.0 and dy == 0.0:
        # Behind-camera case: use bearing/elevation direction instead.
        dx = tan(radians(projection.bearing_deg))
        dy = -tan(radians(projection.elevation_deg))
        if dx == 0.0 and dy == 0.0:
            dy = -1.0

    half_w = max(1.0, cx - margin_px)
    half_h = max(1.0, cy - margin_px)
    scale = max(abs(dx) / half_w, abs(dy) / half_h, 1e-12)
    return (cx + dx / scale, cy + dy / scale)
