from __future__ import annotations

"""Deterministic execution boundary for qualification-only flight commands.

This path intentionally mutates the live in-memory HUD qualification state
through the shared typed flight-command contract. It never writes campaign or
canon state. Manual orbital-frame Torch burns resolve their inertial direction
from the current live spacecraft state, earn Q4 finite attitude time with the
Torch off, then execute through the existing deterministic session physics.
"""

import math
import time
from typing import Any

from loom.hud.flight_command_contract import CommandKind, CommandOrigin, FlightCommand
from loom.hud.wayfarer_attitude_envelope import transition_between_directions_s

CONTRACT = "LOOM_FLIGHT_EXECUTION_RECEIPT_V1"
MAX_BURN_S = 60.0
MIN_SPEED_KM_S = 0.01
MAX_STEP_S = 10.0
ORBITAL_BURN_DIRECTIONS = {
    "PROGRADE",
    "RETROGRADE",
    "RADIAL_OUT",
    "RADIAL_IN",
    "NORMAL",
    "ANTINORMAL",
}


def _mag(v) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _unit(v) -> tuple[float, float, float]:
    m = _mag(v)
    if m <= 0.0:
        raise ValueError("zero vector cannot define burn direction")
    return tuple(float(x) / m for x in v)


def _cross(a, b) -> tuple[float, float, float]:
    ax, ay, az = (float(x) for x in a)
    bx, by, bz = (float(x) for x in b)
    return (
        ay * bz - az * by,
        az * bx - ax * bz,
        ax * by - ay * bx,
    )


def _resolve_orbital_burn_target(session: Any, direction: str) -> tuple[float, float, float]:
    """Resolve a manual burn direction from the current live orbital frame.

    PROGRADE/RETROGRADE follow the instantaneous velocity vector. RADIAL_OUT
    and RADIAL_IN use the Earth-centred position vector. NORMAL/ANTINORMAL use
    the instantaneous specific-angular-momentum direction r x v. Degenerate
    frames fail closed rather than manufacturing an arbitrary direction.
    """

    if direction in {"PROGRADE", "RETROGRADE"}:
        speed = _mag(session.ship_velocity)
        if speed < MIN_SPEED_KM_S:
            raise ValueError(f"velocity-aligned burn requires speed >= {MIN_SPEED_KM_S:g} km/s")
        velocity_unit = _unit(session.ship_velocity)
        sign = 1.0 if direction == "PROGRADE" else -1.0
        return tuple(sign * x for x in velocity_unit)

    if direction in {"RADIAL_OUT", "RADIAL_IN"}:
        radial_unit = _unit(session.ship_position)
        sign = 1.0 if direction == "RADIAL_OUT" else -1.0
        return tuple(sign * x for x in radial_unit)

    if direction in {"NORMAL", "ANTINORMAL"}:
        angular_momentum = _cross(session.ship_position, session.ship_velocity)
        if _mag(angular_momentum) <= 1e-12:
            raise ValueError("normal burn requires a non-degenerate orbital plane")
        normal_unit = _unit(angular_momentum)
        sign = 1.0 if direction == "NORMAL" else -1.0
        return tuple(sign * x for x in normal_unit)

    raise ValueError(
        "direction must be one of " + ", ".join(sorted(ORBITAL_BURN_DIRECTIONS))
    )


def _run_steps(session: Any, duration_s: float) -> float:
    elapsed = 0.0
    while elapsed < duration_s - 1e-9:
        step = min(MAX_STEP_S, duration_s - elapsed)
        session._step(step)
        elapsed += step
    return elapsed


def execute_velocity_aligned_burn(
    session: Any,
    *,
    direction: str,
    duration_s: float,
    torch_mode: str,
    requested_by: str | None = None,
) -> dict[str, Any]:
    """Execute a short manual orbital-frame finite-thrust burn on live HUD state.

    The legacy function name is retained as the compatibility seam used by the
    current HUD server endpoint. Direction resolution now supports the six
    conventional local orbital directions: prograde, retrograde, radial out,
    radial in, normal and antinormal.

    Attitude transition time is taken from the imported Q4 envelope; Torch
    remains off during that transition. Continuous rotational dynamics are not
    claimed: orientation is set to the target only after the earned transition
    time has elapsed.
    """

    direction = str(direction).upper().strip()
    duration_s = float(duration_s)
    torch_mode = str(torch_mode).upper().strip()
    if direction not in ORBITAL_BURN_DIRECTIONS:
        raise ValueError(
            "direction must be one of " + ", ".join(sorted(ORBITAL_BURN_DIRECTIONS))
        )
    if not (0.0 < duration_s <= MAX_BURN_S):
        raise ValueError(f"qualification burn duration must be in (0,{MAX_BURN_S:g}] seconds")

    with session.lock:
        session._advance_locked()
        if str(getattr(session, "status", "")) != "RUNNING":
            raise ValueError("qualification session must be RUNNING")
        cards = getattr(session, "TORCH_CARDS", None)
        if cards is None:
            # RealtimeFlightQualification keeps the engineering cards at module scope.
            from loom.hud.realtime_flight_qualification import TORCH_CARDS
            cards = TORCH_CARDS
        if torch_mode not in cards:
            raise ValueError(f"unknown torch mode: {torch_mode}")
        if float(getattr(session, "remass_t", 0.0)) <= 0.0:
            raise ValueError("normal remass exhausted")

        target = _resolve_orbital_burn_target(session, direction)
        transition = transition_between_directions_s(
            session.nose_direction,
            target,
            axis="pitch",
            degraded=False,
        )

        start_epoch = session.sim_epoch
        start_position = tuple(float(x) for x in session.ship_position)
        start_velocity = tuple(float(x) for x in session.ship_velocity)
        start_remass = float(session.remass_t)
        start_wet = float(session.wet_mass_t)

        command = FlightCommand(
            kind=CommandKind.TORCH_BURN,
            origin=CommandOrigin.MANUAL,
            duration_s=duration_s,
            torch_mode=torch_mode,
            target_direction_inertial=target,
            requested_by=requested_by,
        )

        session.torch_active = False
        transition_elapsed = _run_steps(session, float(transition["transition_time_s"]))
        session.nose_direction = target
        session.torch_mode = torch_mode
        session.torch_active = True
        burn_elapsed = _run_steps(session, duration_s)
        session.torch_active = False
        session.last_wall = time.monotonic()

        end_velocity = tuple(float(x) for x in session.ship_velocity)
        return {
            "contract": CONTRACT,
            "status": "EXECUTED_QUALIFICATION_ONLY",
            "authority": "DETERMINISTIC_HUD_QUALIFICATION_EXECUTOR",
            "command": command.payload(),
            "direction_reference": direction,
            "direction_basis": "CURRENT_LIVE_EARTH_CENTERED_ORBITAL_FRAME",
            "mutates_live_qualification_state": True,
            "campaign_mutation": False,
            "navigation_grade": False,
            "attitude_transition": {
                **transition,
                "simulated_rotation_path": False,
                "orientation_assignment": "AT_END_OF_Q4_ENVELOPE_TIME",
                "torch_during_transition": False,
            },
            "execution": {
                "transition_elapsed_s": transition_elapsed,
                "burn_elapsed_s": burn_elapsed,
                "requested_burn_s": duration_s,
                "torch_mode": torch_mode,
                "cutoff_after_command": True,
            },
            "start": {
                "epoch_utc": start_epoch.isoformat(),
                "position_earth_centered_km": list(start_position),
                "velocity_earth_centered_km_s": list(start_velocity),
                "speed_km_s": _mag(start_velocity),
                "remass_t": start_remass,
                "wet_mass_t": start_wet,
            },
            "end": {
                "epoch_utc": session.sim_epoch.isoformat(),
                "position_earth_centered_km": list(session.ship_position),
                "velocity_earth_centered_km_s": list(end_velocity),
                "speed_km_s": _mag(end_velocity),
                "remass_t": float(session.remass_t),
                "wet_mass_t": float(session.wet_mass_t),
            },
            "remass_used_t": start_remass - float(session.remass_t),
            "attitude_dynamics_authority": "Q4_FINITE_TRANSITION_TIME_ONLY_NO_CLOSED_LOOP_ROTATIONAL_DYNAMICS",
        }
