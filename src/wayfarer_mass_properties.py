from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence


def center_of_mass(elements: Iterable[Mapping[str, float]]) -> dict:
    elems = list(elements)
    total_kg = sum(float(e["mass_t"]) * 1000.0 for e in elems)
    if total_kg <= 0:
        raise ValueError("total mass must be positive")
    com = []
    for axis in ("x_m", "y_m", "z_m"):
        com.append(sum(float(e["mass_t"]) * 1000.0 * float(e.get(axis, 0.0)) for e in elems) / total_kg)
    return {"mass_kg": total_kg, "com_m": tuple(com)}


def point_mass_inertia_tensor(elements: Iterable[Mapping[str, float]]) -> dict:
    """Return inertia about the assembled CoM using element centroids as point masses.

    This is a strict lower-fidelity / lower-bound model because intrinsic component
    shape inertia is not included unless the caller adds it separately. It must not
    be promoted as final Wayfarer actuator canon.
    """
    elems = list(elements)
    state = center_of_mass(elems)
    cx, cy, cz = state["com_m"]
    ixx = iyy = izz = ixy = ixz = iyz = 0.0
    for e in elems:
        m = float(e["mass_t"]) * 1000.0
        x = float(e.get("x_m", 0.0)) - cx
        y = float(e.get("y_m", 0.0)) - cy
        z = float(e.get("z_m", 0.0)) - cz
        ixx += m * (y * y + z * z)
        iyy += m * (x * x + z * z)
        izz += m * (x * x + y * y)
        ixy -= m * x * y
        ixz -= m * x * z
        iyz -= m * y * z
    return {
        **state,
        "tensor_kg_m2": ((ixx, ixy, ixz), (ixy, iyy, iyz), (ixz, iyz, izz)),
        "model_class": "POINT_MASS_CENTROID_ONLY",
        "intrinsic_component_inertia_included": False,
        "qualification_status": "NOT_FINAL",
    }


def add_diagonal_intrinsic(point_tensor: Sequence[Sequence[float]], intrinsic_diag: Sequence[float]) -> tuple:
    if len(intrinsic_diag) != 3:
        raise ValueError("intrinsic_diag must contain Ixx, Iyy, Izz")
    out = [list(row) for row in point_tensor]
    for i in range(3):
        out[i][i] += float(intrinsic_diag[i])
    return tuple(tuple(row) for row in out)


def torque_from_thruster_pair(thrust_each_N: float, moment_arm_m: float) -> float:
    if thrust_each_N < 0 or moment_arm_m < 0:
        raise ValueError("thrust and arm must be non-negative")
    return 2.0 * thrust_each_N * moment_arm_m


def angular_accel_rad_s2(torque_Nm: float, inertia_kg_m2: float) -> float:
    if inertia_kg_m2 <= 0:
        raise ValueError("inertia must be positive")
    return torque_Nm / inertia_kg_m2


def bang_bang_slew_time_s(angle_rad: float, angular_accel_rad_s2_value: float) -> float:
    """Minimum symmetric accelerate/decelerate slew time from rest to rest.

    Ignores rate limits and settling margin. Suitable only for sizing comparisons.
    """
    if angle_rad < 0 or angular_accel_rad_s2_value <= 0:
        raise ValueError("angle must be non-negative and acceleration positive")
    return 2.0 * math.sqrt(angle_rad / angular_accel_rad_s2_value)
