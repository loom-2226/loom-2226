from __future__ import annotations

"""Read-only current-state path prediction for the Earth-Moon HUD sandbox.

This is deliberately not a maneuver plan and not Navigator authority. It answers
one bounded question: where does the current spacecraft state propagate if no
new maneuver command is applied? Until persistent command execution is earned,
the v1 contract is explicitly ballistic even when the qualification HUD happens
to have its Torch control active.
"""

from datetime import datetime, timezone
import math
from typing import Any

CONTRACT = "LOOM_PREDICTED_PATH_V1"
ASSUMPTION = "BALLISTIC_COAST_CURRENT_STATE"
MAX_HORIZON_S = 7 * 86400.0
MIN_SAMPLE_S = 10.0
MAX_SAMPLE_S = 3600.0
MAX_STEP_S = 10.0
NEAR_ZERO_SPEED_KM_S = 0.01


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _add(a, b):
    return tuple(float(a[i]) + float(b[i]) for i in range(3))


def _scale(a, s: float):
    return tuple(float(x) * float(s) for x in a)


def _mag(a) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in a))


def build_predicted_path(
    session: Any,
    *,
    horizon_s: float = 21600.0,
    sample_s: float = 60.0,
) -> dict[str, Any]:
    """Propagate current state forward without mutating the live session.

    The propagator deliberately reuses the qualification session's gravity
    evaluator, which already resolves the same Earth+Moon field used by live
    flight. Browser code receives sampled geometry and does no orbital mechanics.
    """

    horizon_s = float(horizon_s)
    sample_s = float(sample_s)
    if not (0.0 < horizon_s <= MAX_HORIZON_S):
        raise ValueError(f"prediction horizon must be in (0,{MAX_HORIZON_S:g}] seconds")
    if not (MIN_SAMPLE_S <= sample_s <= MAX_SAMPLE_S):
        raise ValueError(f"sample_s must be in {MIN_SAMPLE_S:g}..{MAX_SAMPLE_S:g}")

    with session.lock:
        epoch = session.sim_epoch
        position = tuple(float(x) for x in session.ship_position)
        velocity = tuple(float(x) for x in session.ship_velocity)
        nose_direction = tuple(float(x) for x in getattr(session, "nose_direction", (0.0, 0.0, 0.0)))
        torch_active = bool(getattr(session, "torch_active", False))
        torch_mode = str(getattr(session, "torch_mode", "UNAVAILABLE"))
        status = str(getattr(session, "status", "UNKNOWN"))

    start_speed = _mag(velocity)
    motion_cue = (
        "GRAVITY_DOMINATED_NEAR_ZERO_SPEED"
        if start_speed < NEAR_ZERO_SPEED_KM_S
        else "VELOCITY_DOMINATED"
    )

    points: list[dict[str, Any]] = [
        {
            "elapsed_s": 0.0,
            "epoch_utc": _iso(epoch),
            "position_earth_centered_km": list(position),
            "velocity_earth_centered_km_s": list(velocity),
        }
    ]

    elapsed = 0.0
    next_sample = sample_s
    while elapsed < horizon_s - 1e-9:
        step = min(MAX_STEP_S, horizon_s - elapsed)
        gravity = session._gravity(epoch, position)
        velocity = _add(velocity, _scale(gravity, step))
        position = _add(position, _scale(velocity, step))
        epoch = datetime.fromtimestamp(epoch.timestamp() + step, tz=timezone.utc)
        elapsed += step
        if elapsed + 1e-9 >= next_sample or elapsed >= horizon_s - 1e-9:
            points.append(
                {
                    "elapsed_s": elapsed,
                    "epoch_utc": _iso(epoch),
                    "position_earth_centered_km": list(position),
                    "velocity_earth_centered_km_s": list(velocity),
                }
            )
            while next_sample <= elapsed + 1e-9:
                next_sample += sample_s

    return {
        "contract": CONTRACT,
        "status": "QUALIFICATION_ONLY",
        "authority": "CURRENT_STATE_FORWARD_PROPAGATION_PRESENTATION_ONLY",
        "navigation_grade": False,
        "mutates_live_state": False,
        "frame": "J2000/ECLIPTIC",
        "assumption": ASSUMPTION,
        "assumption_detail": "NO_NEW_MANEUVER_COMMAND; BALLISTIC EARTH_PLUS_MOON GRAVITY ONLY",
        "start_speed_km_s": start_speed,
        "start_nose_direction_inertial": list(nose_direction),
        "motion_cue": motion_cue,
        "motion_cue_threshold_km_s": NEAR_ZERO_SPEED_KM_S,
        "active_propulsion_ignored": torch_active,
        "active_torch_mode_at_prediction_start": torch_mode if torch_active else None,
        "active_propulsion_reason": (
            "PERSISTENT_COMMAND_CONTINUATION_NOT_YET_EARNED"
            if torch_active
            else "TORCH_INACTIVE_AT_PREDICTION_START"
        ),
        "live_status_at_prediction_start": status,
        "horizon_s": horizon_s,
        "sample_s": sample_s,
        "integration": {
            "method": "SEMI_IMPLICIT_EULER",
            "max_step_s": MAX_STEP_S,
            "gravity": "LOOM_SHARED_EARTH_PLUS_MOON_POINT_MASS",
        },
        "points": points,
    }
