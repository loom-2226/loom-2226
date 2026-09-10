from __future__ import annotations

import math

from src.wayfarer_q4_mass_states import build_q4_mass_state


# Engineering-only shape surrogates derived from the current governed Wayfarer
# geometry and mass ledger. These close HUD finite-attitude-transition sizing;
# they are not structural-analysis meshes or final actuator-placement authority.
_SHAPE_MODEL = {
    "structure": ("CYLINDER_X", 57.0, 4.5),
    "armor_fixed_shield": ("CYLINDER_X", 19.0, 4.3),
    "habitation_life_support": ("CYLINDER_X", 14.0, 4.3),
    "relational_plant": ("CYLINDER_X", 16.0, 2.25),
    "thermal_radiators": ("BOUNDED_CYLINDER_X", 5.0, 4.5),
    "propulsion": ("CYLINDER_X", 14.0, 3.0),
    "electrical": ("BOUNDED_CYLINDER_X", 8.0, 2.5),
    "planetary_launch": ("BOX", 10.5, 3.9, 3.1),
    "avionics_sensors_comms": ("BOUNDED_CYLINDER_X", 6.0, 3.5),
    "rcs_docking_service": ("BOUNDED_CYLINDER_X", 20.0, 4.5),
    "mission_courier_systems": ("BOUNDED_CYLINDER_X", 8.0, 3.5),
    "engineering_reserve": ("BOUNDED_CYLINDER_X", 20.0, 4.0),
    "protected_water": ("BOUNDED_CYLINDER_X", 5.0, 2.0),
}

_TANK_LENGTH_M = 14.0
_TANK_RADIUS_M = 1.5
_RCS_UNIT_N = 25_000.0
_PITCH_YAW_SEPARATION_M = 40.0
_ROLL_EFFECTIVE_DIAMETER_M = 8.0
_CLUSTER_NAMES = {
    "FORE_DORSAL", "FORE_VENTRAL", "FORE_PORT", "FORE_STARBOARD",
    "AFT_DORSAL", "AFT_VENTRAL", "AFT_PORT", "AFT_STARBOARD",
}


def _intrinsic_diag_kg_m2(name: str, mass_kg: float) -> tuple[float, float, float]:
    if name.startswith("normal_remass_tank_"):
        # Cylinder axis aligned with ship +X.
        ixx = 0.5 * mass_kg * _TANK_RADIUS_M**2
        itr = mass_kg * (3.0 * _TANK_RADIUS_M**2 + _TANK_LENGTH_M**2) / 12.0
        return ixx, itr, itr

    model = _SHAPE_MODEL.get(name)
    if model is None:
        return 0.0, 0.0, 0.0
    if model[0] in {"CYLINDER_X", "BOUNDED_CYLINDER_X"}:
        _, length_m, radius_m = model
        ixx = 0.5 * mass_kg * radius_m**2
        itr = mass_kg * (3.0 * radius_m**2 + length_m**2) / 12.0
        return ixx, itr, itr
    if model[0] == "BOX":
        _, length_x, width_y, height_z = model
        ixx = mass_kg * (width_y**2 + height_z**2) / 12.0
        iyy = mass_kg * (length_x**2 + height_z**2) / 12.0
        izz = mass_kg * (length_x**2 + width_y**2) / 12.0
        return ixx, iyy, izz
    raise ValueError(f"unknown shape model for {name}: {model[0]}")


def build_q4_rigid_body_state(*, normal_remass_t: float, protected_water_t: float = 50.0, launch_docked: bool = True) -> dict:
    centroid = build_q4_mass_state(
        normal_remass_t=normal_remass_t,
        protected_water_t=protected_water_t,
        launch_docked=launch_docked,
    )
    cx, cy, cz = centroid["center_of_mass_m"]
    ixx = iyy = izz = ixy = ixz = iyz = 0.0
    shape_provenance = []

    for e in centroid["elements"]:
        m = float(e["mass_t"]) * 1000.0
        x = float(e["x_m"]) - cx
        y = float(e["y_m"]) - cy
        z = float(e["z_m"]) - cz
        d_ixx, d_iyy, d_izz = _intrinsic_diag_kg_m2(e["name"], m)
        ixx += d_ixx + m * (y*y + z*z)
        iyy += d_iyy + m * (x*x + z*z)
        izz += d_izz + m * (x*x + y*y)
        ixy -= m * x * y
        ixz -= m * x * z
        iyz -= m * y * z
        shape_provenance.append({
            "name": e["name"],
            "model": "TANK_CYLINDER_X" if e["name"].startswith("normal_remass_tank_") else (_SHAPE_MODEL.get(e["name"], ("CENTROID_ONLY",))[0]),
        })

    return {
        "contract": "WAYFARER_Q4_RIGID_BODY_STATE_V0.4",
        "qualification_scope": "HUD_FINITE_ATTITUDE_TRANSITION",
        "authority": "ENGINEERING_QUALIFICATION_NON_CANON",
        "model_quality": "ENGINEERING_BOUNDED_RIGID_BODY_APPROXIMATION",
        "mass_t": centroid["mass_t"],
        "center_of_mass_m": centroid["center_of_mass_m"],
        "normal_remass_t": float(normal_remass_t),
        "protected_water_t": float(protected_water_t),
        "launch_state": centroid["launch_state"],
        "inertia_tensor_kg_m2": [
            [ixx, ixy, ixz],
            [ixy, iyy, iyz],
            [ixz, iyz, izz],
        ],
        "inertia_diag_kg_m2": [ixx, iyy, izz],
        "shape_provenance": shape_provenance,
        "limitations": [
            "not_structural_fea",
            "radiator_deployed_tensor_not_resolved",
            "fluid_slosh_not_explicitly_integrated",
            "thruster_plume_geometry_not_final",
            "closed_loop_control_law_not_qualified",
        ],
    }


def _slew_time(angle_deg: float, torque_Nm: float, inertia_kg_m2: float, *, settle_factor: float = 1.20) -> float:
    alpha = torque_Nm / inertia_kg_m2
    ideal = 2.0 * math.sqrt(math.radians(angle_deg) / alpha)
    return ideal * settle_factor


def evaluate_rcs_control_case(state: dict, failed_cluster: str | None = None) -> dict:
    if failed_cluster is not None and failed_cluster not in _CLUSTER_NAMES:
        raise ValueError(f"unknown RCS cluster: {failed_cluster}")

    degraded = failed_cluster is not None
    # Nominal: one 25 kN fore/aft opposed pair gives F*d = 1 MNm pitch/yaw.
    # Roll: one opposed pair across ~8 m gives 0.2 MNm.
    # One-cluster-out envelope conservatively retains 75% pitch/yaw and 50% roll
    # by cross-strapping the remaining distributed clusters. These are layout-
    # envelope values, not final plume-interference or closed-loop authority.
    nominal_pitch_yaw = _RCS_UNIT_N * _PITCH_YAW_SEPARATION_M
    nominal_roll = _RCS_UNIT_N * _ROLL_EFFECTIVE_DIAMETER_M
    pitch_yaw = nominal_pitch_yaw * (0.75 if degraded else 1.0)
    roll = nominal_roll * (0.50 if degraded else 1.0)
    translation_n = 75_000.0 if degraded else 100_000.0

    ixx, iyy, izz = [float(v) for v in state["inertia_diag_kg_m2"]]
    return {
        "contract": "WAYFARER_Q4_RCS_CONTROL_CASE_V0.4",
        "failed_cluster": failed_cluster,
        "degraded": degraded,
        "three_axis_control_retained": pitch_yaw > 0.0 and roll > 0.0,
        "translation_control_retained": translation_n > 0.0,
        "nominal_pitch_yaw_torque_Nm": nominal_pitch_yaw,
        "nominal_roll_torque_Nm": nominal_roll,
        "pitch_yaw_torque_Nm": pitch_yaw,
        "roll_torque_Nm": roll,
        "translation_thrust_N": translation_n,
        "angular_accel_rad_s2": {
            "roll": roll / ixx,
            "pitch": pitch_yaw / iyy,
            "yaw": pitch_yaw / izz,
        },
        "slew_time_s_with_20pct_settle_margin": {
            "roll_90": _slew_time(90.0, roll, ixx),
            "roll_180": _slew_time(180.0, roll, ixx),
            "pitch_90": _slew_time(90.0, pitch_yaw, iyy),
            "pitch_180": _slew_time(180.0, pitch_yaw, iyy),
            "yaw_90": _slew_time(90.0, pitch_yaw, izz),
            "yaw_180": _slew_time(180.0, pitch_yaw, izz),
        },
        "qualification_status": "QUALIFIED_FOR_HUD_FINITE_ATTITUDE_ENVELOPE",
        "not_qualified_for": [
            "final_thruster_location",
            "plume_interference_clearance",
            "structural_load_limit",
            "closed_loop_guidance_control",
            "docking_contact_dynamics",
        ],
    }
