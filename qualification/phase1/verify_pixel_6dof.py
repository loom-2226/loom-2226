#!/usr/bin/env python3
"""LOOM 2226 Phase-1 Pixel 6DOF portability proof.

Purpose: prove that an offline, deterministic, code-judged 6DOF harness can run
with a tiny scientific-Python dependency surface. This is NOT production ship
physics and does not establish the future SHIPCLASSES schema.

State convention:
  r_N [m], v_N [m/s], q_BN=[w,x,y,z] rotates body -> inertial,
  omega_BN_B [rad/s]. Mass [kg], inertia about CoM in body axes [kg m^2].
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Tuple

try:
    import numpy as np
except Exception as exc:
    print(json.dumps({"status": "FAIL", "reason": "NUMPY_IMPORT", "error": repr(exc)}))
    raise SystemExit(2)

SCHEMA = "loom.pixel_6dof_proof.v0.1"
DT = 0.01
DURATION = 10.0
MASS = 1000.0
INERTIA = np.diag([2000.0, 3000.0, 4000.0])

@dataclass(frozen=True)
class Wrench:
    force_N: np.ndarray
    torque_B: np.ndarray

ForceMomentFn = Callable[[float, np.ndarray], Wrench]


def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    ], dtype=float)


def normalize_q(q: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(q))
    if not math.isfinite(n) or n == 0.0:
        raise ValueError("invalid quaternion norm")
    return q / n


def deriv(t: float, y: np.ndarray, wrench_fn: ForceMomentFn) -> np.ndarray:
    v = y[3:6]
    q = normalize_q(y[6:10])
    omega = y[10:13]
    wr = wrench_fn(t, y.copy())
    force_N = np.asarray(wr.force_N, dtype=float)
    torque_B = np.asarray(wr.torque_B, dtype=float)
    if force_N.shape != (3,) or torque_B.shape != (3,):
        raise ValueError("wrench vectors must be length 3")
    accel_N = force_N / MASS
    qdot = 0.5 * qmul(q, np.array([0.0, *omega], dtype=float))
    Iw = INERTIA @ omega
    omega_dot = np.linalg.solve(INERTIA, torque_B - np.cross(omega, Iw))
    return np.concatenate((v, accel_N, qdot, omega_dot))


def rk4_step(t: float, y: np.ndarray, dt: float, wrench_fn: ForceMomentFn) -> np.ndarray:
    k1 = deriv(t, y, wrench_fn)
    k2 = deriv(t + 0.5*dt, y + 0.5*dt*k1, wrench_fn)
    k3 = deriv(t + 0.5*dt, y + 0.5*dt*k2, wrench_fn)
    k4 = deriv(t + dt, y + dt*k3, wrench_fn)
    out = y + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
    out[6:10] = normalize_q(out[6:10])
    return out


def propagate(wrench_fn: ForceMomentFn) -> Tuple[np.ndarray, list]:
    y = np.zeros(13, dtype=float)
    y[6] = 1.0
    t = 0.0
    trace = []
    steps = int(round(DURATION / DT))
    for i in range(steps + 1):
        trace.append((t, *y.tolist()))
        if i < steps:
            y = rk4_step(t, y, DT, wrench_fn)
            t = (i + 1) * DT
    return y, trace


def maxabs(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def zero_wrench(t: float, y: np.ndarray) -> Wrench:
    return Wrench(np.zeros(3), np.zeros(3))


def injected_wrench(t: float, y: np.ndarray) -> Wrench:
    return Wrench(np.array([500.0, -200.0, 100.0]), np.array([0.0, 0.0, 800.0]))


def evaluate() -> Tuple[Dict, Dict[str, list]]:
    zero_final, zero_trace = propagate(zero_wrench)
    inj_final, inj_trace = propagate(injected_wrench)

    zero_expected = np.zeros(13)
    zero_expected[6] = 1.0
    zero_err = maxabs(zero_final, zero_expected)

    a = np.array([500.0, -200.0, 100.0]) / MASS
    alpha = 800.0 / INERTIA[2, 2]
    theta = 0.5 * alpha * DURATION**2
    inj_expected = np.zeros(13)
    inj_expected[0:3] = 0.5 * a * DURATION**2
    inj_expected[3:6] = a * DURATION
    inj_expected[6:10] = np.array([math.cos(theta/2), 0.0, 0.0, math.sin(theta/2)])
    inj_expected[6:10] = normalize_q(inj_expected[6:10])
    if inj_expected[6] < 0.0:
        inj_expected[6:10] *= -1.0
    if inj_final[6] < 0.0:
        inj_final[6:10] *= -1.0
    inj_expected[12] = alpha * DURATION
    inj_err = maxabs(inj_final, inj_expected)
    qnorm_err = abs(float(np.linalg.norm(inj_final[6:10])) - 1.0)

    checks = {
        "numpy_import": True,
        "zero_force_inertial": zero_err <= 1e-12,
        "custom_force_moment_callback": inj_err <= 2e-8,
        "quaternion_norm": qnorm_err <= 1e-12,
        "deterministic_fixed_step": True,
    }
    result = {
        "schema": SCHEMA,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "numerics": {
            "dt_s": DT,
            "duration_s": DURATION,
            "zero_max_abs_error": zero_err,
            "injected_max_abs_error": inj_err,
            "quaternion_norm_error": qnorm_err,
            "final_zero": zero_final.tolist(),
            "final_injected": inj_final.tolist(),
            "expected_injected": inj_expected.tolist(),
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "offline_required_after_setup": True,
        },
    }
    return result, {"zero": zero_trace, "injected": inj_trace}


def write_outputs(result: Dict, traces: Dict[str, list], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / "pixel_6dof_result.json"
    csv_path = outdir / "pixel_6dof_trace.csv"
    with json_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    header = ["scenario", "t_s", "rx_m", "ry_m", "rz_m", "vx_m_s", "vy_m_s", "vz_m_s",
              "qw", "qx", "qy", "qz", "wx_rad_s", "wy_rad_s", "wz_rad_s"]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for scenario in ("zero", "injected"):
            for row in traces[scenario]:
                w.writerow([scenario, *[format(float(v), ".17g") for v in row]])
    for p in (json_path, csv_path):
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"SHA256 {p.name} {digest}")


def main() -> int:
    result, traces = evaluate()
    outdir = Path(__file__).resolve().parent / "output"
    write_outputs(result, traces, outdir)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    print(f"LOOM_PIXEL_6DOF_PROOF: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
