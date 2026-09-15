from __future__ import annotations

"""Evidence-gated trade frame for Wayfarer RCS physical realization.

The qualified requirement envelope constrains this trade. This module deliberately
refuses to manufacture future hardware data: candidate families and evaluation axes
are governed here; numerical hardware values require separately provenance-bound
evidence before downselection.
"""

from typing import Any

from src.wayfarer_rcs_physical_requirement_envelope import build_physical_requirement_envelope

SCHEMA = "LOOM.Wayfarer.RCSPhysicalArchitectureTrade"
SCHEMA_VERSION = "0.1"


def build_physical_architecture_trade() -> dict[str, Any]:
    req = build_physical_requirement_envelope()
    if req["status"] != "PASS":
        raise RuntimeError("physical requirement envelope did not pass")

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "source_requirement_claim": req["authority"]["claim"],
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
                "WORKING_FLUID_COMPATIBILITY",
                "EXHAUST_VELOCITY_AND_PROPELLANT_MASS",
                "STORABILITY_AND_FEED_ARCHITECTURE",
                "THERMAL_AND_POWER_LOAD",
                "PLUME_CHEMISTRY_AND_CONTAMINATION",
            ],
            "coarse_fine_actuation": [
                "PEAK_THRUST_COVERAGE",
                "MINIMUM_IMPULSE_CONTROL",
                "RESPONSE_AND_SETTLING",
                "DUTY_CYCLE_TOTAL_IMPULSE_AND_CYCLE_LIFE",
                "FAULT_TOLERANCE",
            ],
            "vectoring_mechanism_candidates": [
                "DIFFERENTIAL_INTERNAL_NOZZLES",
                "FLUIDIC_OR_SECONDARY_INJECTION",
                "MECHANICAL_GIMBAL_IF_EVIDENCE_SUPPORTS",
            ],
            "installation": [
                "FINITE_PLUME_CLEARANCE",
                "DEPLOYED_RADIATOR_AND_EXTERNAL_HARDWARE_INTERFERENCE",
                "MOUNT_LOAD_PATH",
                "LOCAL_STRUCTURE",
                "THERMAL_REJECTION",
            ],
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
            "acceptable_basis": [
                "RECOVERED_LOOM_ENGINEERING_AUTHORITY",
                "TRACEABLE_REAL_WORLD_PROPULSION_OR_ACTUATOR_EVIDENCE",
                "GOVERNED_FUTURE_TECHNOLOGY_EXTRAPOLATION_WITH_EXPLICIT_ASSUMPTIONS",
            ],
            "unproven_future_value_may_be_silently_inserted": False,
        },
        "authority": {
            "claim": "PHYSICAL_ARCHITECTURE_TRADE_FRAME_ONLY",
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
        "qualified_next_step": "GATHER_EVIDENCE_AND_DOWNSELECT_PHYSICAL_RCS_ARCHITECTURE_THEN_RUN_INSTALLATION_FEASIBILITY",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_physical_architecture_trade(), indent=2, sort_keys=True))
