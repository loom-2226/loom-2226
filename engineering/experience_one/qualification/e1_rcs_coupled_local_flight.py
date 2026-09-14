from __future__ import annotations

import json

from src.wayfarer_rcs_coupled_local_flight import build_coupled_local_flight_qualification

SCHEMA = "LOOM_E1_RCS_COUPLED_LOCAL_FLIGHT_V1"


def build_qualification() -> dict:
    coupled = build_coupled_local_flight_qualification()
    status = "PASS" if coupled["all_cases_pass"] else "FAIL"
    return {
        "schema": SCHEMA,
        "status": status,
        "qualification_axis": "rcs_coupled_translation_rotation_local_flight",
        "disposition": coupled["disposition"],
        "coupled_local_flight": coupled,
        "missing_required_evidence": [
            "mount_level_force_allocation_in_the_time_loop",
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "CLOSE_RCS_ACTUATOR_MOUNT_AND_PLUME_HARDWARE_OR_DECLARE_OPERATIONAL_INTERLOCKS",
        "authority": {
            "certifies_coupled_net_wrench_vehicle_dynamics": status == "PASS",
            "certifies_mount_level_time_domain_allocation": False,
            "certifies_final_rcs_hardware": False,
            "certifies_minimum_impulse": False,
            "certifies_plume_clearance": False,
            "certifies_structural_mounts": False,
            "certifies_torch": False,
            "certifies_metric": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


if __name__ == "__main__":
    payload = build_qualification()
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=" + payload["qualification_axis"])
    print("QUALIFICATION_DISPOSITION=" + payload["disposition"])
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + ",".join(payload["missing_required_evidence"]))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)
