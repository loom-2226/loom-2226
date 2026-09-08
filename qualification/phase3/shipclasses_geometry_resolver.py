from __future__ import annotations

import json
import math
import sqlite3
from typing import Dict, Tuple

Vector3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]


class PhysicalTransformError(ValueError):
    pass


def _qnorm(q: Quat) -> Quat:
    n = math.sqrt(sum(v * v for v in q))
    if not math.isfinite(n) or n <= 0:
        raise PhysicalTransformError("Invalid quaternion norm")
    return tuple(v / n for v in q)  # type: ignore[return-value]


def _qmul(a: Quat, b: Quat) -> Quat:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def _qconj(q: Quat) -> Quat:
    return (q[0], -q[1], -q[2], -q[3])


def rotate(q: Quat, v: Vector3) -> Vector3:
    q = _qnorm(q)
    p = (0.0, *v)
    r = _qmul(_qmul(q, p), _qconj(q))
    return (r[1], r[2], r[3])


def compose(parent_t: Vector3, parent_q: Quat, local_t: Vector3, local_q: Quat):
    rq = rotate(parent_q, local_t)
    t = tuple(parent_t[i] + rq[i] for i in range(3))
    q = _qnorm(_qmul(_qnorm(parent_q), _qnorm(local_q)))
    return t, q


def resolve_component_poses(conn: sqlite3.Connection) -> Dict[str, Tuple[Vector3, Quat]]:
    conn.row_factory = sqlite3.Row
    comps = {
        r["component_id"]: r["parent_component_id"]
        for r in conn.execute("SELECT component_id,parent_component_id FROM physical_component")
    }
    transforms = {}
    for r in conn.execute("SELECT component_id,tx_m,ty_m,tz_m,qw,qx,qy,qz FROM component_transform"):
        transforms[r["component_id"]] = (
            (float(r["tx_m"]), float(r["ty_m"]), float(r["tz_m"])),
            (float(r["qw"]), float(r["qx"]), float(r["qy"]), float(r["qz"])),
        )

    resolved = {}
    visiting = set()

    def one(component_id):
        if component_id in resolved:
            return resolved[component_id]
        if component_id in visiting:
            raise PhysicalTransformError(f"Transform cycle at {component_id}")
        visiting.add(component_id)
        if component_id not in transforms:
            raise PhysicalTransformError(f"Missing transform for {component_id}")
        local_t, local_q = transforms[component_id]
        parent = comps.get(component_id)
        if parent is None:
            pose = (local_t, _qnorm(local_q))
        else:
            if parent not in comps:
                raise PhysicalTransformError(f"Unknown parent {parent}")
            parent_t, parent_q = one(parent)
            pose = compose(parent_t, parent_q, local_t, local_q)
        visiting.remove(component_id)
        resolved[component_id] = pose
        return pose

    for component_id in comps:
        one(component_id)
    return resolved


def local_point_to_body(pose, point: Vector3) -> Vector3:
    t, q = pose
    r = rotate(q, point)
    return tuple(t[i] + r[i] for i in range(3))  # type: ignore[return-value]


def resolve_mass_centroids_B(conn: sqlite3.Connection):
    conn.row_factory = sqlite3.Row
    poses = resolve_component_poses(conn)
    result = {}
    for r in conn.execute("SELECT mass_element_id,component_id,cx_m,cy_m,cz_m FROM mass_element"):
        result[r["mass_element_id"]] = local_point_to_body(
            poses[r["component_id"]],
            (float(r["cx_m"]), float(r["cy_m"]), float(r["cz_m"])),
        )
    return result


def resolve_geometry_primitive_poses(conn: sqlite3.Connection):
    conn.row_factory = sqlite3.Row
    poses = resolve_component_poses(conn)
    result = {}
    for r in conn.execute("SELECT primitive_id,component_id,local_pose_json FROM geometry_primitive"):
        payload = json.loads(r["local_pose_json"] or "{}")
        t = tuple(float(v) for v in payload.get("translation_m", [0, 0, 0]))
        q = tuple(float(v) for v in payload.get("quaternion_wxyz", [1, 0, 0, 0]))
        result[r["primitive_id"]] = compose(*poses[r["component_id"]], t, q)
    return result


def compute_mass_properties_transformed(conn: sqlite3.Connection):
    conn.row_factory = sqlite3.Row
    centroids = resolve_mass_centroids_B(conn)
    rows = list(conn.execute("SELECT mass_element_id,reference_mass_kg FROM mass_element"))
    total = sum(float(r["reference_mass_kg"]) for r in rows)
    if total <= 0 or not math.isfinite(total):
        raise PhysicalTransformError("Invalid total mass")
    com = [
        sum(float(r["reference_mass_kg"]) * centroids[r["mass_element_id"]][i] for r in rows) / total
        for i in range(3)
    ]
    return {"mass_kg": total, "center_of_mass_B_m": com}
