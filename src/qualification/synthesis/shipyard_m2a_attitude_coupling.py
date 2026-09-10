from __future__ import annotations

import math
from typing import Any

Q4_SOURCE_COMMIT = "e2df887d5e901eed9378c7aeb7d4964040b9a7e6"
Q4_SOURCE_ARTIFACT = "engineering/current/wayfarer_q4_hud_attitude_envelope_v0.4.json"
Q4_SOURCE_MODEL = "src/wayfarer_q4_rigid_body.py"
AUTHORITY = "Q4_HUD_FINITE_ATTITUDE_ENGINEERING_QUALIFICATION"

TOTAL_WET_MASS_KG = 1_158_500.0
PROTECTED_WATER_KG = 50_000.0
NORMAL_REMASS_KG = 250_000.0
PITCH_YAW_TORQUE_NM = 1_000_000.0
SETTLE_FACTOR = 1.20

# Q4-v0.4 shape/mass ledger, copied verbatim in substance and pinned above.
# Only longitudinal positions admitted by Shipyard are varied per candidate.
_FIXED = (
    ("structure", 150_000.0, 28.0, "CYLINDER", 57.0, 4.5),
    ("armor_fixed_shield", 105_000.0, 9.5, "CYLINDER", 19.0, 4.3),
    ("habitation_life_support", 45_000.0, 8.0, "CYLINDER", 14.0, 4.3),
    ("thermal_radiators", 90_000.0, 35.0, "CYLINDER", 5.0, 4.5),
    ("propulsion", 160_000.0, 46.5, "CYLINDER", 14.0, 3.0),
    ("electrical", 55_000.0, 31.0, "CYLINDER", 8.0, 2.5),
    ("avionics_sensors_comms", 20_000.0, 12.0, "CYLINDER", 6.0, 3.5),
    ("rcs_docking_service", 25_000.0, 28.0, "CYLINDER", 20.0, 4.5),
    ("mission_courier_systems", 20_000.0, 17.0, "CYLINDER", 8.0, 3.5),
    ("engineering_reserve", 67_500.0, 28.0, "CYLINDER", 20.0, 4.0),
    ("protected_water", 50_000.0, 12.5, "CYLINDER", 5.0, 2.0),
)

RELATIONAL_MASS_KG = 88_000.0
RELATIONAL_LENGTH_M = 16.0
RELATIONAL_RADIUS_M = 2.25
LAUNCH_MASS_KG = 33_000.0
LAUNCH_DIMS_M = (10.5, 3.9, 3.1)
LAUNCH_Z_M = 5.2
TANK_COUNT = 4
TANK_MASS_KG = 62_500.0
TANK_RADIUS_FROM_AXIS_M = 2.7
TANK_LENGTH_M = 14.0
TANK_RADIUS_M = 1.5


def _intrinsic_pitch_cylinder(mass_kg: float, length_m: float, radius_m: float) -> float:
    return mass_kg * (3.0 * radius_m * radius_m + length_m * length_m) / 12.0


def _intrinsic_pitch_box(mass_kg: float, length_x_m: float, width_y_m: float, height_z_m: float) -> float:
    return mass_kg * (length_x_m * length_x_m + height_z_m * height_z_m) / 12.0


def _slew_time_s(angle_deg: float, inertia_kg_m2: float, torque_nm: float = PITCH_YAW_TORQUE_NM) -> float:
    alpha = torque_nm / inertia_kg_m2
    return 2.0 * math.sqrt(math.radians(angle_deg) / alpha) * SETTLE_FACTOR


def _candidate_elements(artifact) -> list[dict[str, float | str]]:
    choices = artifact.choices
    required = ("relational_x_m", "launch_x_m", "tank_x_m")
    if any(key not in choices for key in required):
        raise ValueError("compiled candidate lacks required Shipyard longitudinal choices")

    rows: list[dict[str, float | str]] = []
    for name, mass, x, kind, length, radius in _FIXED:
        rows.append({
            "name": name,
            "mass_kg": mass,
            "x_m": x,
            "z_m": 0.0,
            "intrinsic_pitch": _intrinsic_pitch_cylinder(mass, length, radius),
        })

    rows.append({
        "name": "relational_plant",
        "mass_kg": RELATIONAL_MASS_KG,
        "x_m": float(choices["relational_x_m"]),
        "z_m": 0.0,
        "intrinsic_pitch": _intrinsic_pitch_cylinder(RELATIONAL_MASS_KG, RELATIONAL_LENGTH_M, RELATIONAL_RADIUS_M),
    })
    lx = float(choices["launch_x_m"])
    rows.append({
        "name": "planetary_launch",
        "mass_kg": LAUNCH_MASS_KG,
        "x_m": lx,
        "z_m": LAUNCH_Z_M,
        "intrinsic_pitch": _intrinsic_pitch_box(LAUNCH_MASS_KG, *LAUNCH_DIMS_M),
    })
    tx = float(choices["tank_x_m"])
    tank_intrinsic = _intrinsic_pitch_cylinder(TANK_MASS_KG, TANK_LENGTH_M, TANK_RADIUS_M)
    for idx in range(TANK_COUNT):
        angle = math.pi / 4.0 + idx * math.pi / 2.0
        z = TANK_RADIUS_FROM_AXIS_M * math.sin(angle)
        rows.append({
            "name": f"normal_remass_tank_{idx + 1}",
            "mass_kg": TANK_MASS_KG,
            "x_m": tx,
            "z_m": z,
            "intrinsic_pitch": tank_intrinsic,
        })
    return rows


def candidate_attitude_signature(artifact) -> dict[str, Any]:
    rows = _candidate_elements(artifact)
    mass = sum(float(row["mass_kg"]) for row in rows)
    if not math.isclose(mass, TOTAL_WET_MASS_KG, rel_tol=0.0, abs_tol=1e-6):
        raise ValueError(f"Q4/Shipyard mass ledger mismatch: {mass}")
    cx = sum(float(row["mass_kg"]) * float(row["x_m"]) for row in rows) / mass
    cz = sum(float(row["mass_kg"]) * float(row["z_m"]) for row in rows) / mass
    iyy = 0.0
    for row in rows:
        m = float(row["mass_kg"])
        dx = float(row["x_m"]) - cx
        dz = float(row["z_m"]) - cz
        iyy += float(row["intrinsic_pitch"]) + m * (dx * dx + dz * dz)

    return {
        "candidate_id": artifact.candidate_id,
        "pitch_inertia_kg_m2": iyy,
        "pitch_90_s": _slew_time_s(90.0, iyy),
        "pitch_180_s": _slew_time_s(180.0, iyy),
        "center_of_mass_x_m": cx,
        "center_of_mass_z_m": cz,
        "layout_choices": {
            "relational_x_m": float(artifact.choices["relational_x_m"]),
            "launch_x_m": float(artifact.choices["launch_x_m"]),
            "tank_x_m": float(artifact.choices["tank_x_m"]),
        },
        "authority": AUTHORITY,
        "q4_source_commit": Q4_SOURCE_COMMIT,
        "q4_source_artifact": Q4_SOURCE_ARTIFACT,
        "q4_source_model": Q4_SOURCE_MODEL,
        "flight_dynamics_authority": False,
        "canon_changed": False,
    }


def maneuver_aware_leg_summary(artifact, raw_leg: dict[str, Any]) -> dict[str, Any]:
    if raw_leg.get("solver_model") != "NAV-V1-A":
        raise ValueError("M2-A coupling requires an actual NAV-V1-A leg result")
    raw_time = float(raw_leg["arrival"]["total_nav_time_s"])
    signature = candidate_attitude_signature(artifact)
    # The only universally required finite transition we can admit without
    # inventing a departure attitude is the 180-degree burn-to-brake reversal.
    flip = float(signature["pitch_180_s"])
    return {
        "candidate_id": artifact.candidate_id,
        "raw_navigator_time_s": raw_time,
        "brake_flip_time_s": flip,
        "maneuver_aware_total_time_s": raw_time + flip,
        "terminal_remass_used_t": float(raw_leg["terminal_burn"]["remass_used_t"]),
        "raw_navigator_output_modified": False,
        "m2a_disposition": "COUPLED_MISSION_DIFFERENTIATION_DEMONSTRATED",
        "qualification_scope": "SHIPYARD_LAYOUT_TO_Q4_ATTITUDE_TO_NAVIGATOR_MISSION_TIME",
        "authority": AUTHORITY,
        "q4_source_commit": Q4_SOURCE_COMMIT,
        "flight_dynamics_authority": False,
        "navigator_authority_changed": False,
        "canon_changed": False,
    }
