from __future__ import annotations

"""E1 RCS vehicle-architecture installation feasibility boundary.

A vehicle architecture may be frozen for downstream integrated engineering while
component installation remains held on unresolved physical plume, thermal, life,
and structural evidence. This module does not manufacture those missing values.
"""

from typing import Any

from src.wayfarer_rcs_technology_downselect import build_technology_downselect

SCHEMA = "LOOM.Wayfarer.RCSInstallationFeasibility"
SCHEMA_VERSION = "0.1"


def build_installation_feasibility() -> dict[str, Any]:
    architecture = build_technology_downselect()
    if architecture["status"] != "PASS":
        raise RuntimeError("RCS technology downselect did not pass")

    inputs = architecture["installation_inputs"]
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_WITH_DEFERRED_COMPONENT_DETAIL",
        "source_architecture_claim": architecture["authority"]["claim"],
        "installation_basis": {
            "mount_count": inputs["mount_count"],
            "vector_cone_basis": inputs["candidate_vector_cone"],
            "mount_architecture": architecture["selection"]["mount_architecture"],
            "coarse_actuation_family": architecture["selection"]["coarse_actuation"],
            "fine_actuation_family": architecture["selection"]["fine_actuation"],
            "vectoring_architecture": architecture["selection"]["vectoring_architecture"],
        },
        "installation_axes": {
            "finite_plume": "REQUIRED_BEFORE_COMPONENT_INSTALLATION_RELEASE",
            "radiator_external_hardware": "CONFIGURATION_SWEEP_REQUIRED_WITH_PHYSICAL_PLUME_MODEL",
            "thermal": "COMPONENT_HEAT_LOAD_AND_REJECTION_REQUIRED_AFTER_CYCLE_SELECTION",
            "structure": "MOUNT_LOAD_PATH_AND_LOCAL_REINFORCEMENT_REQUIRED",
        },
        "feasibility_logic": {
            "vehicle_level_mount_geometry_and_control_architecture_qualified": True,
            "current_architecture_exposes_required_installation_interfaces": True,
            "unresolved_component_physics_can_be_carried_as_explicit_integration_holds": True,
            "absence_of_component_values_is_not_treated_as_clearance": True,
            "torch_integration_will_materially_constrain_thermal_structure_and_plume_environment": True,
        },
        "component_installation_holds": [
            "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
            "WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD",
            "MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE",
            "VECTORING_DYNAMIC_RESPONSE_AND_LIFE",
            "MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT",
        ],
        "freeze_decision": {
            "scope": "E1_RCS_VEHICLE_ARCHITECTURE",
            "decision": "FREEZE_WITH_COMPONENT_INSTALLATION_HOLDS",
            "torch_work_may_begin": True,
            "component_installation_release": False,
            "meaning": "freeze mount/control/architecture interfaces; carry unresolved physical component details into integrated vehicle engineering",
        },
        "authority": {
            "claim": "E1_RCS_VEHICLE_ARCHITECTURE_FEASIBLE_WITH_EXPLICIT_COMPONENT_INSTALLATION_HOLDS",
            "vehicle_architecture_freeze_authorized": True,
            "finite_plume_clearance_certified": False,
            "thermal_installation_certified": False,
            "structural_mount_loads_certified": False,
            "component_detailed_design_certified": False,
            "propellant_selected": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "BEGIN_TORCH_ENGINEERING_WITH_RCS_INSTALLATION_HOLDS_CARRIED_AS_INTEGRATION_CONSTRAINTS",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_installation_feasibility(), indent=2, sort_keys=True))
