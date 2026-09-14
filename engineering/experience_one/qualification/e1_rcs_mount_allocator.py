from __future__ import annotations

import json

from src.wayfarer_rcs_mount_allocator import build_mount_allocation_qualification

SCHEMA = "LOOM_E1_RCS_MOUNT_ALLOCATOR_V1"


def build_qualification() -> dict:
    allocation = build_mount_allocation_qualification()
    status = allocation["status"]
    return {
        "schema": SCHEMA,
        "status": status,
        "qualification_axis": "rcs_current_configuration_mount_level_bounded_allocation",
        "disposition": allocation["disposition"],
        "allocation": allocation,
        "missing_required_evidence": [
            "mount_level_force_allocation_in_the_time_loop",
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "BIND_REQUALIFIED_MOUNT_ALLOCATOR_INTO_COUPLED_LOCAL_FLIGHT_WITH_EXPLICIT_ACTUATOR_CONTRACT",
        "authority": {
            "certifies_current_configuration_mount_level_bounded_allocation": status == "PASS",
            "certifies_time_domain_mount_allocation": False,
            "certifies_minimum_impulse": False,
            "certifies_plume_clearance": False,
            "certifies_structural_mounts": False,
            "certifies_final_rcs_hardware": False,
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
