from __future__ import annotations

"""Q4 kinematic RCS vectoring and degraded-controllability screen.

This module consumes the geometry-screened mount hardpoints from
``wayfarer_rcs_placement`` and asks a deliberately narrower question:

    Can a plausible outward-exhaust vectoring envelope span six-dimensional
    force/torque space, including after loss of one cross-strapped logical
    cluster?

It does *not* qualify thrust magnitude, structural loads, plume interactions,
power/thermal duty, minimum impulse bit, control laws, or final nozzle hardware.
Those remain Q4/Q5 work.
"""

import math
from typing import Any, Iterable, Sequence

from wayfarer_rcs_placement import build_rcs_mount_candidate

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
VECTORING_HALF_ANGLE_DEG = 45.0
_REFERENCE_COM = (26.6767, 0.0, 0.1481)
_AXIS_NAMES = ("FX", "FY", "FZ", "TX", "TY", "TZ")
_CLUSTER_IDS = ("A", "B", "C", "D")


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(_dot(v, v))


def _unit(v: Sequence[float]) -> tuple[float, float, float]:
    n = _norm(v)
    if n <= 0.0:
        raise ValueError("zero vector")
    return tuple(float(x) / n for x in v)  # type: ignore[return-value]


def _add(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return tuple(float(a[i]) + float(b[i]) for i in range(3))  # type: ignore[return-value]


def _scale(v: Sequence[float], scalar: float) -> tuple[float, float, float]:
    return tuple(float(x) * scalar for x in v)  # type: ignore[return-value]


def _cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    )


def _rank(columns: Iterable[Sequence[float]], eps: float = 1e-10) -> int:
    cols = [tuple(float(x) for x in col) for col in columns]
    if not cols:
        return 0
    rows = len(cols[0])
    if any(len(col) != rows for col in cols):
        raise ValueError("inconsistent column length")
    matrix = [list(row) for row in zip(*cols)]
    m = len(matrix)
    n = len(matrix[0])
    rank = 0
    for col in range(n):
        pivot = max(range(rank, m), key=lambda r: abs(matrix[r][col]), default=None)
        if pivot is None or abs(matrix[pivot][col]) <= eps:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        for j in range(col, n):
            matrix[rank][j] /= pivot_value
        for r in range(m):
            if r == rank:
                continue
            factor = matrix[r][col]
            if abs(factor) <= eps:
                continue
            for j in range(col, n):
                matrix[r][j] -= factor * matrix[rank][j]
        rank += 1
        if rank == m:
            break
    return rank


def _sample_force_directions(surface_normal: Sequence[float], tangent: Sequence[float]) -> list[dict[str, Any]]:
    """Sample a 45 deg gimbal envelope around an inward-radial force axis.

    ``surface_normal`` points outward from the hull. A conventional external
    nozzle producing outward exhaust gives the ship a force with a negative
    radial component. The sampled envelope therefore centers on ``-normal``
    and tilts toward +/-X or +/-circumferential tangent while preserving an
    outward exhaust component.
    """

    inward = _scale(surface_normal, -1.0)
    axial = (1.0, 0.0, 0.0)
    raw = (
        ("RADIAL_IN", inward),
        ("AXIAL_PLUS", _add(inward, axial)),
        ("AXIAL_MINUS", _add(inward, _scale(axial, -1.0))),
        ("TANGENT_PLUS", _add(inward, tangent)),
        ("TANGENT_MINUS", _add(inward, _scale(tangent, -1.0))),
    )
    result: list[dict[str, Any]] = []
    for name, vector in raw:
        force = _unit(vector)
        exhaust = _scale(force, -1.0)
        result.append(
            {
                "name": name,
                "force_unit_ship": list(force),
                "exhaust_unit": list(exhaust),
                "force_radial_dot": _dot(force, surface_normal),
                "exhaust_radial_dot": _dot(exhaust, surface_normal),
            }
        )
    return result


def _wrench(position: Sequence[float], force: Sequence[float]) -> tuple[float, ...]:
    r = (
        float(position[0]) - _REFERENCE_COM[0],
        float(position[1]) - _REFERENCE_COM[1],
        float(position[2]) - _REFERENCE_COM[2],
    )
    torque = _cross(r, force)
    return tuple(float(x) for x in force) + torque


def _screen(mounts: list[dict[str, Any]]) -> dict[str, Any]:
    columns: list[tuple[float, ...]] = []
    for mount in mounts:
        for sample in mount["sampled_force_directions"]:
            columns.append(_wrench(mount["position_m"], sample["force_unit_ship"]))

    rank = _rank(columns)
    axis_bounds = {
        _AXIS_NAMES[i]: {
            "min_per_unit_thrust": min(col[i] for col in columns),
            "max_per_unit_thrust": max(col[i] for col in columns),
        }
        for i in range(6)
    }
    bidirectional = {
        axis: bounds["min_per_unit_thrust"] < -1e-9 and bounds["max_per_unit_thrust"] > 1e-9
        for axis, bounds in axis_bounds.items()
    }
    return {
        "surviving_mount_count": len(mounts),
        "sampled_wrench_count": len(columns),
        "wrench_rank": rank,
        "full_six_dof_rank": rank == 6,
        "bidirectional_axes": bidirectional,
        "axis_bounds": axis_bounds,
        "disposition": (
            "PASS_KINEMATIC_SCREEN_NOT_FORCE_QUALIFICATION"
            if rank == 6 and all(bidirectional.values())
            else "FAIL_KINEMATIC_SCREEN"
        ),
    }


def build_rcs_control_candidate() -> dict[str, Any]:
    placement = build_rcs_mount_candidate()
    mounts: list[dict[str, Any]] = []
    logical_clusters: dict[str, dict[str, Any]] = {
        cluster: {"mount_ids": [], "bands": []} for cluster in _CLUSTER_IDS
    }

    for band in placement["bands"]:
        for index, source_mount in enumerate(band["mounts"]):
            cluster_id = _CLUSTER_IDS[index]
            mount = {
                "id": source_mount["id"],
                "band": band["name"],
                "logical_cluster": cluster_id,
                "position_m": list(source_mount["position_m"]),
                "surface_normal": list(source_mount["surface_normal"]),
                "circumferential_tangent": list(source_mount["circumferential_tangent"]),
                "sampled_force_directions": _sample_force_directions(
                    source_mount["surface_normal"], source_mount["circumferential_tangent"]
                ),
            }
            mounts.append(mount)
            logical_clusters[cluster_id]["mount_ids"].append(mount["id"])
            logical_clusters[cluster_id]["bands"].append(mount["band"])

    nominal = _screen(mounts)
    degraded: dict[str, Any] = {}
    for failed_cluster in _CLUSTER_IDS:
        surviving = [m for m in mounts if m["logical_cluster"] != failed_cluster]
        degraded[failed_cluster] = {
            **_screen(surviving),
            "failed_cluster": failed_cluster,
        }

    return {
        "standard_id": "WAYFARER_Q4_RCS_CONTROL_SCREEN_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "qualification": "KINEMATIC_CONTROLLABILITY_SCREEN_ONLY",
        "mount_placement_standard": placement["standard_id"],
        "reference_wet_com_m": list(_REFERENCE_COM),
        "vectoring_model": "OUTWARD_EXHAUST_HEMISPHERE_45_DEG_SAMPLED_GIMBAL",
        "vectoring_half_angle_deg": VECTORING_HALF_ANGLE_DEG,
        "logical_cluster_definition": (
            "four cross-strapped logical clusters A-D; each cluster contains one mount from each axial band"
        ),
        "logical_clusters": logical_clusters,
        "mounts": mounts,
        "controllability": {
            "NOMINAL": nominal,
            "ONE_CLUSTER_OUT": degraded,
        },
        "plume_clearance_status": "LOCAL_OUTWARD_HEMISPHERE_ONLY",
        "structural_qualification": "OPEN_Q4",
        "power_thermal_qualification": "OPEN_Q5",
        "minimum_impulse_bit_status": "OPEN_Q4",
        "one_cluster_out_force_authority": "BOUNDED_BY_Q4_HUD_ENVELOPE_NOT_REDERIVED_HERE",
        "closed_loop_control_status": "OPEN_Q4",
        "notes": [
            "Rank-six wrench space is a necessary kinematic screen, not proof of dynamically usable authority.",
            "Bidirectional component coverage does not replace nonlinear allocation, saturation, plume, thermal or structural analysis.",
            "The 45-degree sampled envelope is an engineering candidate for geometry/control screening only; final nozzle vectoring remains unqualified.",
            "Cross-strapped A-D grouping matches the existing Q4 degraded envelope assumption that one cluster loss leaves distributed surviving authority.",
            "Final one-cluster-out qualification still requires force allocation with actuator limits plus Q5 power/thermal closure.",
        ],
    }
