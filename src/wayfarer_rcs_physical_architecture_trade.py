from __future__ import annotations

"""Evidence-gated trade frame for Wayfarer RCS physical realization."""

from typing import Any

from src.wayfarer_rcs_physical_requirement_envelope import build_physical_requirement_envelope

SCHEMA = "LOOM.Wayfarer.RCSPhysicalArchitectureTrade"
SCHEMA_VERSION = "0.2"
EVIDENCE_RECORD = "engineering/experience_one/evidence/rcs_physical_architecture_evidence_2026-09-15.md"


def build_physical_architecture_trade() -> dict[str, Any]:
    req = build_physical_requirement_envelope()
    if req["status"] != "PASS":
        raise RuntimeError("physical requirement envelope did not pass")

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "source_requirement_claim": req["authority"]["claim"],
        "evidence_record": EVIDENCE_RECORD,
        "candidate_families": [
            {
                "id": "COMPOUND_COARSE_FINE_VECTORED_MOUNT",
                "role": "CURRENT_ENGINEERING_CANDIDATE_FAMILY",
                "description": "one resultant force vector per hardpoint synthesized from coarse and fine authority",
                "selected_hardware": False,
            },
            {
                "id": "ALTERNATE_PHYSICAL_REALIZATION",
                "role": "OPTIONALITY_RESERVE",
                "description": "retained if evidence shows the current compound family cannot satisfy requirements or installation constraints",
                "selected_hardware": False,
            },
        ],
        "trade_axes": {
            "propellant_cycle": [
                "WORKING_FLUID_COMPATIBILITY", "EXHAUST_VELOCITY_AND_PROPELLANT_MASS",
                "STORABILITY_AND_FEED_ARCHITECTURE", "THERMAL_AND_POWER_LOAD",
                "PLUME_CHEMISTRY_AND_CONTAMINATION",
            ],
            "coarse_fine_actuation": [
                "PEAK_THRUST_COVERAGE", "MINIMUM_IMPULSE_CONTROL", "RESPONSE_AND_SETTLING",
                "DUTY_CYCLE_TOTAL_IMPULSE_AND_CYCLE_LIFE", "FAULT_TOLERANCE",
            ],
            "vectoring_mechanism_candidates": [
                "DIFFERENTIAL_INTERNAL_NOZZLES", "FLUIDIC_OR_SECONDARY_INJECTION",
                "MECHANICAL_GIMBAL_IF_EVIDENCE_SUPPORTS",
            ],
            "installation": [
                "FINITE_PLUME_CLEARANCE", "DEPLOYED_RADIATOR_AND_EXTERNAL_HARDWARE_INTERFERENCE",
                "MOUNT_LOAD_PATH", "LOCAL_STRUCTURE", "THERMAL_REJECTION",
            ],
        },
        "evidence_findings": {
            "electronically_valved_variable_injection_geometry_supported": True,
            "fluidic_secondary_injection_tvc_supported": True,
            "mib_response_is_coupled_propulsion_gnc_quantity": True,
            "whole_engine_mechanical_gimbal_required": False,
            "wayfarer_45_degree_vector_cone_physically_demonstrated": False,
            "wayfarer_numeric_hardware_values_supported": False,
            "interpretation": "MECHANISM_FAMILIES_SUPPORTED_NUMERIC_WAYFARER_HARDWARE_NOT_SUPPORTED",
        },
        "selection": {
            "working_fluid": None,
            "exhaust_velocity_m_s": None,
            "minimum_impulse_bit_Ns": None,
            "valve_response_s": None,
            "cycle_life": None,
            "vectoring_mechanism": None,
        },
        "evidence_gate": {
            "required_before_numerical_hardware_downselect": True,
            "public_evidence_collected": True,
            "public_evidence_sufficient_for_mechanism_family_retention": True,
            "public_evidence_sufficient_for_wayfarer_numeric_downselect": False,
            "acceptable_basis_for_next_step": "GOVERNED_FUTURE_TECHNOLOGY_EXTRAPOLATION_WITH_EXPLICIT_ASSUMPTIONS",
            "unproven_future_value_may_be_silently_inserted": False,
        },
        "authority": {
            "claim": "EVIDENCE_BACKED_PHYSICAL_ARCHITECTURE_TRADE_ONLY",
            "final_thruster_hardware_certified": False,
            "working_fluid_certified": False,
            "vectoring_mechanism_certified": False,
            "minimum_impulse_bit_certified": False,
            "valve_dynamics_certified": False,
            "installation_certified": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "BUILD_GOVERNED_RCS_TECHNOLOGY_EXTRAPOLATION_AND_DOWNSELECT_THEN_RUN_INSTALLATION_FEASIBILITY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_physical_architecture_trade(), indent=2, sort_keys=True))
