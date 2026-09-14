from __future__ import annotations

import json

from src.wayfarer_rcs_actuator_requirement_envelope import build_actuator_requirement_envelope

SCHEMA = "LOOM_E1_RCS_ACTUATOR_REQUIREMENT_ENVELOPE_V1"


def build_qualification() -> dict:
    envelope = build_actuator_requirement_envelope()
    status = envelope["status"]
    return {
        "schema": SCHEMA,
        "status": status,
        "qualification_axis": "rcs_actuator_sampled_demand_requirement_envelope",
        "disposition": envelope["disposition"],
        "actuator_requirement_envelope": envelope,
        "missing_required_evidence": list(envelope["remaining_open"]),
        "qualified_next_step": envelope["qualified_next_step"],
        "authority": {
            "certifies_sampled_actuator_demand_envelope": status == "PASS",
            "certifies_minimum_impulse_bit_hardware": False,
            "certifies_valve_dynamics": False,
            "certifies_gimbal_dynamics": False,
            "certifies_final_rcs_hardware": False,
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
