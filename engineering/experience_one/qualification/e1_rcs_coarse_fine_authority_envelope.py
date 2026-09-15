from __future__ import annotations

import json

from src.wayfarer_rcs_coarse_fine_authority_envelope import build_coarse_fine_authority_envelope

SCHEMA = "LOOM_E1_RCS_COARSE_FINE_AUTHORITY_PIXEL_PROBE_V1"
QUALIFICATION_AXIS = "rcs_coarse_fine_realized_wrench_pixel_probe"


def build_qualification() -> dict:
    result = build_coarse_fine_authority_envelope()
    return {
        "schema": SCHEMA,
        "qualification_axis": QUALIFICATION_AXIS,
        "status": result["status"],
        "disposition": result["disposition"],
        "parameter_probe": result["parameter_sweep"],
        "closed_loop_contract": result["closed_loop_contract"],
        "exploration_contract": result["exploration_contract"],
        "authority": {
            "certifies_coarse_fine_pixel_coupling_probe": result["authority"]["coarse_fine_pixel_coupling_probe_qualified"],
            "certifies_full_coarse_fine_parameter_envelope": False,
            "certifies_final_rcs_hardware": False,
            "certifies_minimum_impulse_bit_hardware": False,
            "certifies_valve_dynamics": False,
            "certifies_vectoring_mechanism": False,
            "certifies_working_fluid": False,
            "certifies_plume_clearance": False,
            "certifies_structural_mounts": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "missing_required_evidence": result["remaining_open"],
        "qualified_next_step": result["qualified_next_step"],
    }


if __name__ == "__main__":
    q = build_qualification()
    print(json.dumps(q, indent=2, sort_keys=True))
    print(f"QUALIFICATION_AXIS={QUALIFICATION_AXIS}")
    print(f"QUALIFICATION_DISPOSITION={q['disposition']}")
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + ",".join(q["missing_required_evidence"]))
    raise SystemExit(0 if q["status"] == "PASS" else 1)
