from __future__ import annotations

"""Q4 geometric plume/interference screen for the Wayfarer RCS candidate.

The current engineering state does not yet define a physical plume half-angle
or final radiator-panel geometry. This module therefore does only what the
repository can presently support without inventing actuator physics:

1. expose the sampled exhaust centerlines implied by the Q4 control screen;
2. prove their local cylindrical-hull direction is outward;
3. derive the maximum local-hull plume half-angle allowed by that geometry;
4. ray-screen those centerlines against current launch and docking envelopes;
5. explicitly refuse finite-cone/radiator qualification until the missing
   plume and radiator geometry exists.

It is an engineering screen, not final plume qualification.
"""

import math
from typing import Any, Sequence

from wayfarer_rcs_control import build_rcs_control_candidate

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"

# Current governed/design-baseline geometry anchors from
# geometry/wayfarer_geometry_seed.sql on the parent engineering branch.
# The launch is represented by its existing working box envelope.
_LAUNCH_AABB = {
    "name": "planetary_launch",
    "min_m": [16.5, -1.95, 3.60],
    "max_m": [27.0, 1.95, 6.70],
    "source": "geometry/wayfarer_geometry_seed.sql launch.* + launch_bay.inner_floor_radius_m",
    "status": "DESIGN_BASELINE",
}

# Existing docking collar uses a z-axis collar at x=16 m, z=-4.5 m with
# 1.6 m diameter and 0.7 m depth. An AABB exactly encloses that current
# placeholder collar geometry for centerline screening.
_DOCK_AABB = {
    "name": "docking_collar",
    "min_m": [15.2, -0.8, -4.85],
    "max_m": [16.8, 0.8, -4.15],
    "source": "src/loom/wayfarer_geometry.py current docking collar placeholder",
    "status": "OPEN_PLACEHOLDER_GEOMETRY",
}


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _ray_aabb_intersection(
    origin: Sequence[float], direction: Sequence[float], bounds: dict[str, Any]
) -> tuple[bool, float | None]:
    """Return whether a forward ray intersects an axis-aligned box."""

    t_min = 0.0
    t_max = float("inf")
    minimum = bounds["min_m"]
    maximum = bounds["max_m"]
    eps = 1.0e-12

    for axis in range(3):
        o = float(origin[axis])
        d = float(direction[axis])
        lo = float(minimum[axis])
        hi = float(maximum[axis])
        if abs(d) <= eps:
            if o < lo or o > hi:
                return False, None
            continue
        t1 = (lo - o) / d
        t2 = (hi - o) / d
        near = min(t1, t2)
        far = max(t1, t2)
        t_min = max(t_min, near)
        t_max = min(t_max, far)
        if t_max < t_min:
            return False, None

    if t_max < 0.0:
        return False, None
    hit_t = max(t_min, 0.0)
    return True, hit_t


def _local_hull_half_angle_margin_deg(exhaust_radial_dot: float) -> float:
    """Angular margin from exhaust axis to the local hull tangent plane.

    The surface normal is radial/outward. If the exhaust axis has radial dot
    r>0, then asin(r) is the angle above the tangent plane. Any idealized
    straight plume cone narrower than this angle remains in the local outward
    half-space. This is only a local cylindrical-hull condition; external
    hardware can still be struck.
    """

    clamped = max(-1.0, min(1.0, float(exhaust_radial_dot)))
    return math.degrees(math.asin(clamped))


def build_rcs_plume_screen() -> dict[str, Any]:
    control = build_rcs_control_candidate()
    screened_mounts: list[dict[str, Any]] = []
    known_objects = (_LAUNCH_AABB, _DOCK_AABB)
    object_hits: dict[str, list[dict[str, Any]]] = {obj["name"]: [] for obj in known_objects}
    local_margins: list[float] = []

    for mount in control["mounts"]:
        samples: list[dict[str, Any]] = []
        surface_normal = mount["surface_normal"]
        for sample in mount["sampled_force_directions"]:
            exhaust = sample["exhaust_unit"]
            radial_dot = _dot(exhaust, surface_normal)
            local_margin = _local_hull_half_angle_margin_deg(radial_dot)
            local_margins.append(local_margin)

            intersections: list[dict[str, Any]] = []
            for obj in known_objects:
                hit, distance = _ray_aabb_intersection(mount["position_m"], exhaust, obj)
                if hit:
                    record = {
                        "mount_id": mount["id"],
                        "sample": sample["name"],
                        "distance_along_centerline_m": distance,
                    }
                    object_hits[obj["name"]].append(record)
                    intersections.append({"object": obj["name"], **record})

            samples.append(
                {
                    "name": sample["name"],
                    "plume_axis_exhaust_unit": list(exhaust),
                    "exhaust_radial_dot": radial_dot,
                    "local_hull_centerline_clear": radial_dot > 0.0,
                    "local_hull_max_half_angle_deg": local_margin,
                    "known_geometry_centerline_intersections": intersections,
                    "finite_plume_half_angle_deg": None,
                    "finite_plume_cone_status": "OPEN_Q4",
                }
            )

        screened_mounts.append(
            {
                "id": mount["id"],
                "band": mount["band"],
                "logical_cluster": mount["logical_cluster"],
                "position_m": list(mount["position_m"]),
                "samples": samples,
            }
        )

    known_screen: dict[str, Any] = {}
    for obj in known_objects:
        hits = object_hits[obj["name"]]
        known_screen[obj["name"]] = {
            "geometry": obj,
            "intersecting_sample_count": len(hits),
            "intersections": hits,
            "disposition": (
                "CENTERLINES_CLEAR_CURRENT_ENVELOPE"
                if not hits
                else "CENTERLINE_INTERFERENCE_PRESENT"
            ),
        }

    return {
        "standard_id": "WAYFARER_Q4_RCS_PLUME_GEOMETRY_SCREEN_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "qualification": "CENTERLINE_AND_LOCAL_HULL_GEOMETRY_SCREEN_ONLY",
        "source_control_screen": control["standard_id"],
        "mounts": screened_mounts,
        "minimum_local_hull_half_angle_margin_deg": min(local_margins),
        "known_geometry_centerline_screen": known_screen,
        "plume_half_angle_deg": None,
        "finite_plume_cone_qualification": "OPEN_Q4_REQUIRES_PLUME_HALF_ANGLE_AND_RADIATOR_GEOMETRY",
        "radiator_interference_status": "OPEN_PHYSICAL_PANEL_GEOMETRY",
        "radiator_note": (
            "Current geometry compiler marks radiator physical panel geometry OPEN. "
            "The x=33..38 m cardinal root locations are useful for mount placement, "
            "but are insufficient for final finite-cone plume clearance."
        ),
        "structural_qualification": "OPEN_Q4",
        "power_thermal_qualification": "OPEN_Q5",
        "notes": [
            "All current sampled exhaust centerlines are screened against the present launch and docking envelopes.",
            "The minimum local hull margin is derived geometrically from the exhaust-axis radial component and does not assume a plume angle.",
            "A plume half-angle is intentionally not invented; finite-cone clearance remains open until actuator/plume physics supplies it.",
            "Radiator panel geometry is explicitly OPEN in the current geometry compiler, so radiator plume clearance cannot be qualified here.",
            "Centerline clearance is necessary but not sufficient for real plume qualification, contamination, heating, structural loading or docking operations.",
        ],
    }
