from __future__ import annotations

"""Bind qualified E1 rotational dynamics into the Navigator/HUD local-flight seam."""

from typing import Any

from src.wayfarer_rcs_closed_loop_gnc import build_closed_loop_gnc_qualification

SCHEMA = "LOOM_E1_LOCAL_FLIGHT_ROTATIONAL_BINDING_V1"


def build_local_flight_rotational_binding() -> dict[str, Any]:
    gnc = build_closed_loop_gnc_qualification()
    passed = bool(gnc["all_cases_pass"])
    missing = [
        "finite_plume_and_deployed_radiator_interference_closure",
        "structural_rcs_mount_load_qualification",
        "minimum_impulse_and_actuator_dynamics",
        "translation_plus_rotation_coupled_maneuver_qualification",
    ]
    return {
        "schema": SCHEMA,
        "status": "PASS" if passed else "FAIL",
        "disposition": (
            "CLOSED_LOOP_ROTATIONAL_STATE_BOUND_TO_E1_LOCAL_FLIGHT_HARDWARE_CLOSURE_REMAINS"
            if passed
            else "ROTATIONAL_BINDING_FAIL"
        ),
        "closed_loop_gnc": gnc,
        "handoff": {
            "rotational_state_authority": "PYTHON_E1_FLIGHT_DYNAMICS",
            "navigator_role": "TRANSLATIONAL_AND_ROUTE_AUTHORITY_WITH_EXPLICIT_ROTATIONAL_HANDOFF",
            "hud_role": "PRESENTATION_AND_INTENT_ONLY",
            "state_fields_required": [
                "attitude_quaternion",
                "body_rate_rad_s",
                "mass_t",
                "center_of_mass_m",
                "inertia_tensor_kg_m2",
                "rcs_operability_state",
                "failed_rcs_cluster",
            ],
            "instantaneous_flip_substitution_allowed": False,
        },
        "authority": {
            "closed_loop_attitude_response_consumed": passed,
            "instantaneous_attitude_reorientation_forbidden": True,
            "browser_calculation_authority": "ZERO",
            "navigator_may_skip_rotational_elapsed_time": False,
            "hud_may_invent_attitude_state": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "missing_required_evidence": missing,
        "qualified_next_step": "CLOSE_RCS_HARDWARE_INTERFERENCE_AND_ACTUATOR_DYNAMICS_THEN_COUPLE_TRANSLATION_ROTATION",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_local_flight_rotational_binding(), indent=2, sort_keys=True))
