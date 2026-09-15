"""Wayfarer E1 torch thermal/shielding/thrust-frame requirement envelope.

This module derives requirements only. It deliberately does not certify a reactor
cycle, torch deposition fraction, radiation partition, shield stack, radiator
geometry, magnetic nozzle hardware, or detailed thrust-frame structure.
"""

import json


JET_POWER_W = {
    "ECON": 5112451811250.0,
    "CRUISE": 11361004024999.998,
    "EXPEDITE": 11361004024999.998,
    "FAST": 11929054226250.002,
    "HARD": 12781129528124.998,
    "LIMIT": 12781129528125.0,
}

INITIAL_THRUST_N = {
    "ECON": 3408301.2075,
    "CRUISE": 11361004.024999999,
    "EXPEDITE": 22722008.049999997,
    "FAST": 34083012.075,
    "HARD": 56805020.12499999,
    "LIMIT": 85207530.1875,
}

# Historical courier values retained only to expose sensitivity. They are not
# promoted to current authority by this model.
ARCHIVED_DEPOSITION_PPM = {
    "SUSTAINED_LOW": 4.0,
    "SUSTAINED_HIGH": 8.0,
    "FAST": 20.0,
    "HARD": 50.0,
    "LIMIT": 100.0,
}

RCS_HOLDS = [
    "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
    "WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD",
    "MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE",
    "VECTORING_DYNAMIC_RESPONSE_AND_LIFE",
    "MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT",
]


def _deposition_case(mode, ppm):
    return {
        "mode": mode,
        "archived_deposition_ppm": ppm,
        "initial_direct_jet_power_W": JET_POWER_W[mode],
        "initial_deposition_W": JET_POWER_W[mode] * ppm * 1e-6,
        "status": "NON_GOVERNING_SENSITIVITY_ONLY",
    }


def build_envelope():
    mode_loads = {
        mode: {
            "initial_axial_thrust_N": thrust,
            "requirement": "THRUST_FRAME_AND_PRIMARY_LOAD_PATH_MUST_REACT_AT_LEAST_THIS_KNOWN_QUASI_STATIC_AXIAL_THRUST_BEFORE_UNEARNED_DESIGN_FACTORS",
        }
        for mode, thrust in INITIAL_THRUST_N.items()
    }

    sensitivity = {
        "SUSTAINED_LOW_4_PPM": _deposition_case("CRUISE", 4.0),
        "SUSTAINED_HIGH_8_PPM": _deposition_case("CRUISE", 8.0),
        "FAST_20_PPM": _deposition_case("FAST", 20.0),
        "HARD_50_PPM": _deposition_case("HARD", 50.0),
        "LIMIT_100_PPM": _deposition_case("LIMIT", 100.0),
    }

    return {
        "schema": "LOOM.Wayfarer.TorchThermalShieldThrustFrameRequirementEnvelope",
        "schema_version": "0.1",
        "status": "PASS",
        "authority": {
            "claim": "E1_TORCH_THERMAL_SHIELDING_AND_THRUST_FRAME_REQUIREMENT_ENVELOPE_ONLY",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "canon_changed": False,
            "reactor_cycle_certified": False,
            "waste_heat_fraction_certified": False,
            "radiation_partition_certified": False,
            "shadow_shield_stack_certified": False,
            "thrust_frame_design_certified": False,
            "physical_radiator_geometry_certified": False,
            "archive_values_promoted_to_current_authority": False,
        },
        "source_status": {
            "current_authority": {
                "primary_torch_count": 1,
                "architecture": "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE",
                "radiator_count": 4,
                "high_drive_reject_interface_K": 900.0,
                "metric_equivalent_radiator_area_m2_at_900K": {
                    "NORMAL": 106.0,
                    "FAST": 202.0,
                    "EXPEDITE": 336.0,
                    "HARD": 719.0,
                },
                "torch_and_high_metric_mutual_exclusion": True,
            },
            "candidate_packaging": {
                "shadow_shield_x_m": [38.0, 43.0],
                "working_shield_diameter_m": 5.5,
                "reactor_thrust_frame_x_m": [43.0, 50.0],
                "working_reactor_transverse_diameter_m": 4.25,
                "thrust_frame_convergence_x_m": [48.0, 50.0],
                "magnetic_nozzle_x_m": [50.0, 57.0],
                "working_nozzle_aperture_support_diameter_m": 6.0,
                "load_path_concept": "FOUR_MAIN_LONGERONS_CONVERGE_TO_ONE_AFT_THRUST_FRAME_AND_ONE_AXIAL_NOZZLE",
                "status": "NON_GOVERNING_CANDIDATE",
            },
            "archived_provenance": {
                "status": "SENSITIVITY_INPUT_ONLY_NOT_CURRENT_AUTHORITY",
                "torch_deposition_ppm": ARCHIVED_DEPOSITION_PPM,
                "fast_stowed_heat_capacity_GJ": [50.0, 60.0],
                "historical_high_T_radiator_effective_area_m2": 1600.0,
                "historical_total_effective_radiator_area_m2": [3600.0, 4000.0],
            },
        },
        "thermal_requirement_envelope": {
            "jet_power_interpretation": "KINETIC_EXHAUST_POWER_NOT_ELECTRICAL_LOAD_OR_WASTE_HEAT",
            "certified_torch_deposition_fraction": None,
            "required_partition_model": [
                "photons",
                "neutrons_and_side_reactions",
                "magnet_and_nozzle_interception",
                "charged_particle_leakage",
                "secondary_heating",
                "mode_dependence",
            ],
            "archived_deposition_sensitivity": {
                "non_governing": True,
                "purpose": "QUANTIFY_CONSEQUENCE_IF_HISTORICAL_PPM_ENVELOPE_IS_LATER_REEARNED_NOT_CERTIFY_IT_NOW",
                "cases": sensitivity,
            },
            "radiator_requirement": "TORCH_HEAT_REJECTION_CANNOT_BE_CERTIFIED_UNTIL_DEPOSITION_PARTITION_AND_TRANSIENT_DUTY_ARE_EARNED",
            "buffer_requirement": "TRANSIENT_BUFFER_CAPACITY_CANNOT_BE_CREDITED_TO_TORCH_QUALIFICATION_FROM_ARCHIVE_VALUES_ALONE",
        },
        "shielding_requirement_envelope": {
            "directional_shadow_shield_required": True,
            "protected_forward_zone": "OCCUPIED_AND_SENSITIVE_FORWARD_SHIP_SYSTEMS",
            "must_budget": [
                "prompt_photon_transport",
                "neutron_and_secondary_transport",
                "charged_particle_leakage",
                "scattering_and_streaming_paths",
                "activation_and_decay_heat",
                "shield_heating_and_rejection",
            ],
            "materials_and_layering": None,
            "certification_state": "REQUIREMENTS_ONLY",
        },
        "thrust_frame_requirement_envelope": {
            "modes": mode_loads,
            "governing_known_axial_load_mode": "LIMIT",
            "governing_known_initial_axial_thrust_N": INITIAL_THRUST_N["LIMIT"],
            "structural_design_factor": None,
            "dynamic_amplification_factor": None,
            "fatigue_spectrum": None,
            "nozzle_side_load_envelope": None,
            "requirement": "FOUR_LONGERON_TO_AFT_FRAME_LOAD_PATH_MUST_CLOSE_LIMIT_AXIAL_THRUST_PLUS_LATER_EARNED_DYNAMIC_SIDE_LOAD_FATIGUE_AND_LOCAL_STRESS_FACTORS",
        },
        "carried_rcs_integration_holds": RCS_HOLDS,
        "remaining_open": [
            "reactor_cycle_and_fusion_architecture",
            "conversion_and_nozzle_efficiency",
            "reactor_and_nozzle_waste_heat_fraction",
            "neutron_photon_and_plasma_radiation_partition",
            "shadow_shield_materials_and_layering",
            "magnetic_nozzle_coil_geometry_and_stress",
            "thermal_plumbing_and_transient_rejection",
            "physical_torch_plume_envelope_and_external_hardware_clearance",
            "working_fluid_identity_and_feed_implementation",
            "thrust_frame_structural_design_factor_and_local_stress",
            "thrust_frame_dynamic_side_load_and_fatigue_spectrum",
            "physical_radiator_geometry_and_torch_clearance",
        ],
        "qualified_next_step": "REACTOR_NOZZLE_TECHNOLOGY_FAMILY_TRADE_WITH_DEPOSITION_PARTITION_AND_PHYSICAL_REALIZABILITY_GATES",
    }


if __name__ == "__main__":
    print(json.dumps(build_envelope(), indent=2, sort_keys=True))
