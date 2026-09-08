from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from wayfarer_phase5_adapter import build_wayfarer_connection, resolve_wayfarer_mass_com

Vector3 = Sequence[float]
Matrix3 = list[list[float]]


class InertiaAuditError(ValueError):
    pass


def point_mass_parallel_axis_tensor(
    contributions: Iterable[Mapping[str, object]],
    com_B_m: Vector3,
) -> Matrix3:
    c = [float(v) for v in com_B_m]
    if len(c) != 3 or not all(math.isfinite(v) for v in c):
        raise InertiaAuditError("INVALID_COM")

    I: Matrix3 = [[0.0, 0.0, 0.0] for _ in range(3)]
    for row in contributions:
        m = float(row["mass_kg"])
        p = [float(v) for v in row["centroid_B_m"]]
        if m < 0.0 or not math.isfinite(m) or len(p) != 3 or not all(math.isfinite(v) for v in p):
            raise InertiaAuditError("INVALID_CONTRIBUTION")
        d = [p[i] - c[i] for i in range(3)]
        d2 = sum(v * v for v in d)
        for i in range(3):
            for j in range(3):
                I[i][j] += m * ((d2 if i == j else 0.0) - d[i] * d[j])
    return I


def symmetry_error(I: Matrix3) -> float:
    return max(abs(float(I[i][j]) - float(I[j][i])) for i in range(3) for j in range(3))


def determinant3(I: Matrix3) -> float:
    return (
        I[0][0] * (I[1][1] * I[2][2] - I[1][2] * I[2][1])
        - I[0][1] * (I[1][0] * I[2][2] - I[1][2] * I[2][0])
        + I[0][2] * (I[1][0] * I[2][1] - I[1][1] * I[2][0])
    )


def is_positive_semidefinite_symmetric3(I: Matrix3, tol: float = 1e-6) -> bool:
    if symmetry_error(I) > tol:
        return False
    principal = [
        I[0][0], I[1][1], I[2][2],
        I[0][0] * I[1][1] - I[0][1] * I[1][0],
        I[0][0] * I[2][2] - I[0][2] * I[2][0],
        I[1][1] * I[2][2] - I[1][2] * I[2][1],
        determinant3(I),
    ]
    scale = max(1.0, max(abs(float(v)) for row in I for v in row))
    return min(float(v) for v in principal) >= -tol * scale * scale * scale


def audit_configuration(repo_root: Path, launch_state: str) -> dict[str, object]:
    conn = build_wayfarer_connection(repo_root)
    try:
        mp = resolve_wayfarer_mass_com(conn, launch_state, repo_root=repo_root)
    finally:
        conn.close()

    mass = float(mp["mass_kg"])
    com = [float(v) for v in mp["center_of_mass_B_m"]]
    contributions = list(mp["contributions"])
    I_parallel = point_mass_parallel_axis_tensor(contributions, com)

    # Current prototype contains no qualified centroidal inertia tensor for the
    # physical vehicle. Even rows declared POINT_MASS are simulation placeholders,
    # not evidence of zero physical centroidal inertia.
    unresolved_mass = sum(float(row["mass_kg"]) for row in contributions)

    return {
        "launch_state": launch_state,
        "mass_kg": mass,
        "center_of_mass_B_m": com,
        "parallel_axis_I_B_kg_m2": I_parallel,
        "parallel_axis_symmetry_error": symmetry_error(I_parallel),
        "parallel_axis_psd": is_positive_semidefinite_symmetric3(I_parallel),
        "unresolved_centroidal_inertia_mass_kg": unresolved_mass,
        "unresolved_centroidal_inertia_mass_fraction": unresolved_mass / mass,
        "flight_dynamics_authority": False,
        "authority_code": "WAYFARER_INERTIA_OPEN_NOT_QUALIFIED",
    }


def build_audit(repo_root: Path) -> dict[str, object]:
    return {
        "schema": "loom.phase5b_wayfarer_inertia_audit.v0.1",
        "docked": audit_configuration(repo_root, "DOCKED"),
        "absent": audit_configuration(repo_root, "ABSENT"),
        "disposition": "PARTIAL_PARALLEL_AXIS_ONLY_NOT_FLIGHT_AUTHORITY",
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    result = build_audit(repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
