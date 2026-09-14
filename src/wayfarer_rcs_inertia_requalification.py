from __future__ import annotations

"""Re-evaluate recovered Wayfarer RCS authority against current mass/inertia state.

The actuator force/torque envelope is inherited from prior Q4 engineering evidence.
This module does not re-invent nozzle hardware or closed-loop control. It combines
that recovered actuator envelope with the current configuration-aware rigid-body
tensor to produce deterministic angular-acceleration and finite-slew evidence.
"""

import math
from typing import Any

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state

SCHEMA = "LOOM.Wayfarer.RCSInertiaRequalification"
SCHEMA_VERSION = "0.1"
SETTLE_FACTOR = 1.20

# Recovered Q4 engineering envelope from PR #96 / HUD qualification ancestry.
_NOMINAL = {
    "translation_thrust_N": 100_000.0,
    "roll_torque_Nm": 200_000.0,
    "pitch_torque_Nm": 1_000_000.0,
    "yaw_torque_Nm": 1_000_000.0,
}
_DEGRADED = {
    "translation_thrust_N": 75_000.0,
    "roll_torque_Nm": 100_000.0,
    "pitch_torque_Nm": 750_000.0,
    "yaw_torque_Nm": 750_000.0,
}


def _slew_time(angle_deg: float, torque_nm: float, inertia_kg_m2: float) -> float:
    if torque_nm <= 0.0 or inertia_kg_m2 <= 0.0:
        raise ValueError("torque and inertia must be positive")
    alpha = torque_nm / inertia_kg_m2
    return 2.0 * math.sqrt(math.radians(angle_deg) / alpha) * SETTLE_FACTOR


def _case(name: str, tensor: list[list[float]], envelope: dict[str, float], failed_cluster: str | None) -> dict[str, Any]:
    ixx = float(tensor[0][0])
    iyy = float(tensor[1][1])
    izz = float(tensor[2][2])
    torque = {
        "roll": envelope["roll_torque_Nm"],
        "pitch": envelope["pitch_torque_Nm"],
        "yaw": envelope["yaw_torque_Nm"],
    }
    angular = {
        "roll": torque["roll"] / ixx,
        "pitch": torque["pitch"] / iyy,
        "yaw": torque["yaw"] / izz,
    }
    slew = {}
    for axis, inertia, tau in (
        ("roll", ixx, torque["roll"]),
        ("pitch", iyy, torque["pitch"]),
        ("yaw", izz, torque["yaw"]),
    ):
        slew[f"{axis}_90"] = _slew_time(90.0, tau, inertia)
        slew[f"{axis}_180"] = _slew_time(180.0, tau, inertia)

    return {
        "case": name,
        "failed_cluster": failed_cluster,
        "inertia_tensor_kg_m2": tensor,
        "translation_thrust_N": envelope["translation_thrust_N"],
        "torque_authority_Nm": torque,
        "angular_accel_rad_s2": angular,
        "slew_time_s_with_20pct_settle_margin": slew,
        "slew_model": "SYMMETRIC_BANG_BANG_REST_TO_REST_PLUS_20_PERCENT_SETTLE_MARGIN",
        "closed_loop_control_simulated": False,
    }


def build_rcs_inertia_requalification(
    *,
    normal_remass_t: float,
    protected_water_t: float = 50.0,
    launch_docked: bool = True,
) -> dict[str, Any]:
    mass_state = build_mass_inertia_state(
        normal_remass_t=normal_remass_t,
        protected_water_t=protected_water_t,
        launch_docked=launch_docked,
    )
    tensor = mass_state["inertia_tensor_kg_m2"]

    cases: dict[str, Any] = {
        "NOMINAL": _case("NOMINAL", tensor, _NOMINAL, None),
    }
    for cluster in ("A", "B", "C", "D"):
        cases[f"ONE_CLUSTER_OUT_{cluster}"] = _case(
            f"ONE_CLUSTER_OUT_{cluster}", tensor, _DEGRADED, cluster
        )

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "mass_inertia_state": mass_state,
        "cases": cases,
        "torque_source": {
            "lineage": "PR_96_Q4_RCS_CONTROL_AND_BOUNDED_ALLOCATION_ENGINEERING",
            "nominal": _NOMINAL,
            "one_cluster_out": _DEGRADED,
            "semantics": "RECOVERED_ACTUATOR_ENVELOPE_NOT_NEW_HARDWARE_AUTHORITY",
        },
        "torque_source_status": "RECOVERED_Q4_ENGINEERING_ENVELOPE_REQUIRES_EXACT_HEAD_QUALIFICATION",
        "configuration_coupling": {
            "mass_state_is_shared_across_case": True,
            "inertia_state_is_shared_across_case": True,
            "store_depletion_changes_response": True,
            "launch_attachment_changes_response": True,
        },
        "authority": {
            "status": "ENGINEERING_REQUALIFICATION_MODEL",
            "finite_attitude_dynamics_modeled": True,
            "closed_loop_gnc_certified": False,
            "final_thruster_hardware_certified": False,
            "plume_interference_certified": False,
            "structural_mount_loads_certified": False,
            "minimum_impulse_bit_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "QUALIFY_RCS_WRENCH_ALLOCATION_AND_FINITE_ATTITUDE_RESPONSE_THEN_BIND_TO_HUD_NAVIGATOR_LOCAL_FLIGHT",
    }


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            build_rcs_inertia_requalification(
                normal_remass_t=250.0,
                protected_water_t=50.0,
                launch_docked=True,
            ),
            indent=2,
            sort_keys=True,
        )
    )
