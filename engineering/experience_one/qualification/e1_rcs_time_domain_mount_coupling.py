from __future__ import annotations

import json

from src.wayfarer_rcs_time_domain_mount_coupling import build_time_domain_mount_coupling_qualification

SCHEMA = "LOOM_E1_RCS_TIME_DOMAIN_MOUNT_COUPLING_V1"


def build_qualification() -> dict:
    coupling = build_time_domain_mount_coupling_qualification()
    status = coupling["status"]
    return {
        "schema": SCHEMA,
        "status": status,
        "qualification_axis": "rcs_mount_level_force_allocation_in_time_loop",
        "disposition": coupling["disposition"],
        "coupling": coupling,
        "missing_required_evidence": [
            "minimum_impulse_bit_and_valve_gimbal_dynamics",
            "finite_plume_and_external_hardware_interference",
            "structural_rcs_mount_loads",
        ],
        "qualified_next_step": "QUALIFY_ACTUATOR_DISCRETIZATION_AND_VALVE_GIMBAL_DYNAMICS_WITHOUT_INVENTING_HARDWARE_PARAMETERS",
        "authority": {
            "certifies_time_domain_mount_allocation": status == "PASS",
            "certifies_allocated_wrench_drives_vehicle_state": status == "PASS",
            "certifies_minimum_impulse": False,
            "certifies_valve_gimbal_dynamics": False,
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
