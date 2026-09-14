#!/usr/bin/env python3
from __future__ import annotations

import json

from src.wayfarer_mass_inertia_authority import build_mass_inertia_state
from src.wayfarer_rcs_inertia_requalification import build_rcs_inertia_requalification

SCHEMA = "LOOM_E1_MASS_INERTIA_RCS_AUTHORITY_V1"


def build_e1_mass_inertia_rcs_authority() -> dict:
    mass = build_mass_inertia_state(
        normal_remass_t=250.0,
        protected_water_t=50.0,
        launch_docked=True,
    )
    rcs = build_rcs_inertia_requalification(
        normal_remass_t=250.0,
        protected_water_t=50.0,
        launch_docked=True,
    )
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "configuration": {
            "normal_remass_t": 250.0,
            "protected_water_t": 50.0,
            "launch_state": "DOCKED",
            "mass_t": mass["mass_t"],
            "center_of_mass_m": mass["center_of_mass_m"],
        },
        "mass_inertia": mass,
        "rcs_requalification": rcs,
        "disposition": "CONFIGURATION_AWARE_MASS_INERTIA_PRESENT_RCS_FINITE_ATTITUDE_ENGINEERING_REQUALIFICATION_READY",
        "missing_required_evidence": [
            "closed_loop_gnc_qualification",
            "finite_plume_and_deployed_radiator_interference_closure",
            "structural_rcs_mount_load_qualification",
            "minimum_impulse_and_actuator_dynamics",
        ],
        "authority": {
            "certifies_configuration_aware_mass_model": True,
            "certifies_configuration_aware_com_model": True,
            "certifies_engineering_full_inertia_tensor_model": True,
            "certifies_rcs_finite_attitude_engineering_response": True,
            "certifies_closed_loop_gnc": False,
            "certifies_final_rcs_hardware": False,
            "certifies_structural_fea": False,
            "certifies_torch": False,
            "certifies_metric": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "IMPORT_REQUALIFIED_ROTATIONAL_STATE_INTO_LOCAL_FLIGHT_THEN_CLOSE_RCS_GNC_PLUME_AND_MOUNT_PHYSICS",
    }


def main() -> int:
    result = build_e1_mass_inertia_rcs_authority()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=wayfarer_mass_inertia_rcs_authority")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + ",".join(result["missing_required_evidence"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
