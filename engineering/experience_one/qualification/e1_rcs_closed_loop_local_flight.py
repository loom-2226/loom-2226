from __future__ import annotations

"""Qualification wrapper for E1 closed-loop RCS attitude and local-flight binding."""

from engineering.experience_one.qualification.e1_local_flight_rotational_binding import build_local_flight_rotational_binding


def build_qualification() -> dict:
    binding = build_local_flight_rotational_binding()
    passed = binding["status"] == "PASS"
    return {
        "schema": "LOOM_E1_RCS_CLOSED_LOOP_LOCAL_FLIGHT_V1",
        "status": "PASS" if passed else "FAIL",
        "qualification_axis": "rcs_closed_loop_gnc_and_local_flight_rotational_binding",
        "disposition": (
            "CLOSED_LOOP_RCS_ATTITUDE_RESPONSE_AND_LOCAL_FLIGHT_BINDING_QUALIFIED_HARDWARE_CLOSURE_OPEN"
            if passed
            else "RCS_CLOSED_LOOP_LOCAL_FLIGHT_BINDING_FAIL"
        ),
        "binding": binding,
        "missing_required_evidence": binding["missing_required_evidence"],
        "authority": {
            "certifies_closed_loop_reference_attitude_response": passed,
            "certifies_local_flight_rotational_binding": passed,
            "certifies_final_rcs_hardware": False,
            "certifies_finite_plume_clearance": False,
            "certifies_structural_mounts": False,
            "certifies_minimum_impulse": False,
            "certifies_torch": False,
            "certifies_metric": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


if __name__ == "__main__":
    import json
    result = build_qualification()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=" + result["qualification_axis"])
    print("QUALIFICATION_DISPOSITION=" + result["disposition"])
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + ",".join(result["missing_required_evidence"]))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
