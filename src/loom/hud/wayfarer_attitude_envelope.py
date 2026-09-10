from __future__ import annotations

import math
from typing import Iterable

from loom.hud.wayfarer_engineering_state import (
    ENGINEERING_SOURCE_BRANCH,
    ENGINEERING_SOURCE_COMMIT,
    load_wayfarer_engineering_state,
)

CONTRACT = "LOOM_HUD_WAYFARER_ATTITUDE_ENVELOPE_V1"
ENGINEERING_SOURCE_ARTIFACT = "engineering/current/wayfarer_q4_hud_attitude_envelope_v0.4.json"

_ENGINEERING_STATE = load_wayfarer_engineering_state()
_ATTITUDE = _ENGINEERING_STATE["attitude"]
AUTHORITY = _ATTITUDE["status"]


def _reference_times() -> dict[str, dict[str, dict[float, float]]]:
    cases = _ATTITUDE["control_cases"]
    out: dict[str, dict[str, dict[float, float]]] = {}
    for case_name, output_name in (("NOMINAL", "nominal"), ("ONE_CLUSTER_OUT", "degraded")):
        slew = cases[case_name]["reference_wet_docked_slew_s"]
        out[output_name] = {
            "roll": {90.0: float(slew["roll_90"]), 180.0: float(slew["roll_180"])},
            "pitch": {90.0: float(slew["pitch_90"]), 180.0: float(slew["pitch_180"])},
            "yaw": {90.0: float(slew["yaw_90"]), 180.0: float(slew["yaw_180"])},
        }
    return out


_REFERENCE_TIMES_S = _reference_times()


def _unit(v: Iterable[float]) -> tuple[float, float, float]:
    vals = tuple(float(x) for x in v)
    if len(vals) != 3:
        raise ValueError("attitude direction must be three-dimensional")
    mag = math.sqrt(sum(x * x for x in vals))
    if mag <= 0.0:
        raise ValueError("zero vector cannot define attitude")
    return tuple(x / mag for x in vals)


def angle_between_deg(a: Iterable[float], b: Iterable[float]) -> float:
    ua = _unit(a)
    ub = _unit(b)
    dot = max(-1.0, min(1.0, sum(ua[i] * ub[i] for i in range(3))))
    return math.degrees(math.acos(dot))


def attitude_transition_time_s(angle_deg: float, *, axis: str = "pitch", degraded: bool = False) -> float:
    angle = float(angle_deg)
    axis_key = str(axis).lower()
    if axis_key not in {"roll", "pitch", "yaw"}:
        raise ValueError(f"unknown attitude axis: {axis}")
    if not (0.0 <= angle <= 180.0):
        raise ValueError("angle_deg must be in 0..180")
    if angle == 0.0:
        return 0.0
    case = "degraded" if degraded else "nominal"
    anchors = _REFERENCE_TIMES_S[case][axis_key]
    if angle <= 90.0:
        return anchors[90.0] * math.sqrt(angle / 90.0)
    return anchors[180.0] * math.sqrt(angle / 180.0)


def transition_between_directions_s(current_direction, target_direction, *, axis: str = "pitch", degraded: bool = False) -> dict:
    angle = angle_between_deg(current_direction, target_direction)
    return {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "engineering_source_branch": ENGINEERING_SOURCE_BRANCH,
        "engineering_source_commit": ENGINEERING_SOURCE_COMMIT,
        "engineering_source_artifact": ENGINEERING_SOURCE_ARTIFACT,
        "axis": axis.lower(),
        "angle_deg": angle,
        "transition_time_s": attitude_transition_time_s(angle, axis=axis, degraded=degraded),
        "control_case": "ONE_CLUSTER_OUT" if degraded else "NOMINAL",
        "closed_loop_control_authority": False,
        "instantaneous_attitude_reset_allowed": bool(_ATTITUDE["instantaneous_attitude_reset_allowed"]),
    }
