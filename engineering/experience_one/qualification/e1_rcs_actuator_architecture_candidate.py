from __future__ import annotations

import json

from src.wayfarer_rcs_actuator_architecture_candidate import build_actuator_architecture_candidate

SCHEMA = "LOOM_E1_RCS_ACTUATOR_ARCHITECTURE_CANDIDATE_V1"


def build_qualification() -> dict:
    candidate = build_actuator_architecture_candidate()
    return {
        "schema": SCHEMA,
        "status": candidate["status"],
        "qualification_axis": "rcs_actuator_architecture_candidate_selection",
        "disposition": candidate["disposition"],
        "actuator_architecture_candidate": candidate,
        "authority": {
            "certifies_architecture_class_for_next_engineering_step": True,
            "certifies_final_rcs_hardware": False,
            "certifies_minimum_impulse_bit_hardware": False,
            "certifies_valve_dynamics": False,
            "certifies_vectoring_mechanism": False,
            "certifies_working_fluid": False,
            "certifies_plume_clearance": False,
            "certifies_structural_mounts": False,
            "certifies_torch": False,
            "certifies_metric": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "missing_required_evidence": candidate["remaining_open"],
        "qualified_next_step": candidate["qualified_next_step"],
    }


if __name__ == "__main__":
    out = build_qualification()
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QUALIFICATION_AXIS={out['qualification_axis']}")
    print(f"QUALIFICATION_DISPOSITION={out['disposition']}")
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + ",".join(out["missing_required_evidence"]))
