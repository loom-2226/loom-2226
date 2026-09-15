from __future__ import annotations

"""Recover the current Wayfarer torch engineering boundary without inventing detail.

This module is intentionally a baseline recovery artifact.  It gathers the already
established vehicle interfaces and current torch operating cards, carries the RCS
installation holds into the next integrated engineering phase, and keeps candidate
physical packaging distinct from certified component design.
"""

from typing import Any

SCHEMA = "LOOM.Wayfarer.TorchBaselineRecovery"
SCHEMA_VERSION = "0.1"

_EXHAUST_VELOCITY_CARDS_KM_S = {
    "ECON": 3000.0,
    "CRUISE": 2000.0,
    "EXPEDITE": 1000.0,
    "FAST": 700.0,
    "HARD": 450.0,
    "LIMIT": 300.0,
}

_RCS_INTEGRATION_HOLDS = [
    "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
    "WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD",
    "MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE",
    "VECTORING_DYNAMIC_RESPONSE_AND_LIFE",
    "MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT",
]


def build_torch_baseline_recovery() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "vehicle_interfaces": {
            "primary_torch_count": 1,
            "architecture": "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE",
            "reference_wet_mass_t": 1158.5,
            "dry_mass_excluding_working_fluid_water_t": 858.5,
            "working_fluid_water_inventory_t": 300.0,
            "normal_remass_allowance_t": 250.0,
            "protected_water_reserve_t": 50.0,
            "post_normal_remass_reference_mass_t": 908.5,
            "torch_and_high_metric_thermal_field_states_mutually_exclusive": True,
        },
        "exhaust_velocity_cards_km_s": dict(_EXHAUST_VELOCITY_CARDS_KM_S),
        "candidate_packaging": {
            "status": "NON_GOVERNING_CANDIDATE_ENVELOPES",
            "shadow_shield_x_m": [38.0, 43.0],
            "working_shadow_shield_diameter_m": 5.5,
            "reactor_torch_machinery_x_m": [43.0, 50.0],
            "working_reactor_transverse_diameter_m": 4.25,
            "annular_thrust_frame_convergence_x_m": [48.0, 50.0],
            "magnetic_nozzle_x_m": [50.0, 57.0],
            "working_nozzle_aperture_support_diameter_m": 6.0,
            "load_path_rule": "FOUR_MAIN_LONGERONS_CONVERGE_TO_AFT_THRUST_FRAME_AND_ONE_AXIAL_NOZZLE",
        },
        "open_component_detail": [
            "reactor_internals",
            "detailed_shadow_shield_layering",
            "magnetic_coil_geometry",
            "thermal_plumbing",
            "torch_plume_envelope",
        ],
        "carried_rcs_integration_holds": list(_RCS_INTEGRATION_HOLDS),
        "engineering_boundary": {
            "direct_jet_power_is_not_onboard_electrical_load": True,
            "exhaust_velocity_cards_do_not_by_themselves_select_reactor_cycle": True,
            "candidate_packaging_is_not_component_certification": True,
            "next_work_must_close_performance_remass_thermal_and_load_interfaces_before_component_freeze": True,
        },
        "authority": {
            "claim": "E1_TORCH_BASELINE_RECOVERY_ONLY",
            "new_torch_physics_invented": False,
            "reactor_internal_design_certified": False,
            "magnetic_coil_geometry_certified": False,
            "torch_plume_envelope_certified": False,
            "thermal_plumbing_certified": False,
            "candidate_packaging_promoted_to_canon": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "DERIVE_TORCH_PERFORMANCE_AND_REMASS_REQUIREMENT_ENVELOPE_FROM_RECOVERED_OPERATING_CARDS_AND_CURRENT_MASS_STATE",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_torch_baseline_recovery(), indent=2, sort_keys=True))
