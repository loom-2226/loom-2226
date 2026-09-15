"""Wayfarer E1 physical torch-plume and external-clearance requirement envelope.

No plume angle, nozzle geometry, interaction distance, or clearance margin is
invented. Explicit candidate geometry can be evaluated as sensitivity only.
"""
from __future__ import annotations

import json
import math

MODE_REQUIREMENTS = {
    "ECON": {"exhaust_velocity_km_s": 3000.0, "mass_flow_kg_s": 1.1361004025},
    "CRUISE": {"exhaust_velocity_km_s": 2000.0, "mass_flow_kg_s": 5.6805020125},
    "EXPEDITE": {"exhaust_velocity_km_s": 1000.0, "mass_flow_kg_s": 22.72200805},
    "FAST": {"exhaust_velocity_km_s": 700.0, "mass_flow_kg_s": 48.69001725},
    "HARD": {"exhaust_velocity_km_s": 450.0, "mass_flow_kg_s": 126.23337805555556},
    "LIMIT": {"exhaust_velocity_km_s": 300.0, "mass_flow_kg_s": 284.025100625},
}


def evaluate_plume_candidate(
    mode: str,
    nozzle_exit_radius_m: float,
    plume_half_angle_deg: float,
    plume_length_m: float,
    exclusion_margin_m: float,
) -> dict:
    """Evaluate explicit conical-envelope geometry without certifying plasma physics."""
    if mode not in MODE_REQUIREMENTS:
        raise ValueError("unknown mode")
    vals = [nozzle_exit_radius_m, plume_half_angle_deg, plume_length_m, exclusion_margin_m]
    if any(not math.isfinite(float(v)) for v in vals):
        raise ValueError("candidate values must be finite")
    r0, angle, length, margin = map(float, vals)
    if r0 <= 0.0 or angle <= 0.0 or angle >= 90.0 or length <= 0.0 or margin < 0.0:
        raise ValueError("candidate geometry outside admissible sensitivity bounds")
    radius = r0 + length * math.tan(math.radians(angle))
    return {
        "mode": mode,
        "nozzle_exit_radius_m": r0,
        "plume_half_angle_deg": angle,
        "plume_length_m": length,
        "plume_radius_at_length_m": radius,
        "exclusion_margin_m": margin,
        "clearance_radius_with_margin_m": radius + margin,
        "mode_requirement": MODE_REQUIREMENTS[mode],
        "status": "SENSITIVITY_ONLY_NOT_CERTIFIED",
        "warning": "CONICAL_ENVELOPE_IS_A_CLEARANCE_CONSTRUCTION_NOT_A_PHYSICAL_PLASMA_MODEL",
    }


def build_envelope() -> dict:
    return {
        "schema": "LOOM.Wayfarer.TorchPhysicalPlumeExternalClearanceEnvelope",
        "schema_version": "0.1",
        "status": "PASS",
        "authority": {
            "claim": "E1_TORCH_PHYSICAL_PLUME_AND_EXTERNAL_CLEARANCE_ENVELOPE_ONLY",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "canon_changed": False,
            "physical_plume_certified": False,
            "external_clearance_certified": False,
            "nozzle_geometry_certified": False,
            "radiator_geometry_certified": False,
            "rcs_component_installation_certified": False,
        },
        "recovered_vehicle_interface": {
            "primary_torch_count": 1,
            "architecture": "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE",
            "vehicle_length_m": 57.0,
            "nominal_main_body_diameter_m": 9.0,
            "candidate_nozzle_station_m": [50.0, 57.0],
            "candidate_nozzle_support_aperture_diameter_m": 6.0,
            "candidate_geometry_status": "NON_GOVERNING_CANDIDATE",
        },
        "mode_requirements": MODE_REQUIREMENTS,
        "candidate_inputs": {
            "nozzle_exit_radius_m": None,
            "plume_half_angle_deg": None,
            "plume_length_m": None,
            "exclusion_margin_m": None,
            "near_field_density_profile": None,
            "far_field_divergence_model": None,
            "charged_particle_energy_distribution": None,
            "neutral_fraction": None,
            "plasma_detachment_model": None,
        },
        "required_plume_physics": [
            "mode_dependent_near_field_expansion",
            "magnetic_nozzle_detachment",
            "charged_particle_energy_and_angular_distribution",
            "neutral_and_secondary_species_fraction",
            "far_field_divergence_and_density_decay",
            "backflow_or_recirculation_risk",
            "spacecraft_surface_interception_and_sputter_deposition",
            "electromagnetic_interaction_with_vehicle_fields_and_sensors",
        ],
        "required_clearance_classes": [
            "RCS_THRUSTERS_AND_PLUMES",
            "RADIATORS_DEPLOYED_AND_STOWED",
            "SENSORS_ANTENNAS_AND_COMMUNICATIONS",
            "DOCKING_CARGO_AND_SERVICE_ENVELOPES",
            "AFT_STRUCTURE_AND_NOZZLE_SUPPORT",
            "EXTERNAL_SERVICE_LINES_AND_ACCESS",
        ],
        "derived_requirements": [
            "CLEARANCE_MUST_BE_EVALUATED_BY_TORCH_MODE_NOT_ONE_UNIVERSAL_PLUME_CONE",
            "RCS_AND_TORCH_PLUMES_REQUIRE_MUTUAL_INTERACTION_AND_KEEP_OUT_REVIEW",
            "RADIATOR_CLEARANCE_REQUIRES_BOTH_DEPLOYED_AND_STOWED_CONFIGURATIONS",
            "PLUME_INTERCEPTION_MUST_FEED_BACK_INTO_THE_DEPOSITION_AND_THERMAL_BUDGET",
            "NOZZLE_DETACHMENT_AND_DIVERGENCE_MUST_BE_PHYSICALLY_BOUNDED_BEFORE_COMPONENT_GEOMETRY_FREEZE",
        ],
        "kill_criteria": [
            "physical_plume_cannot_be_bounded_by_mode",
            "plume_intercepts_radiators_rcs_or_other_required_external_hardware",
            "backflow_or_surface_interception_breaks_deposition_budget",
            "plume_field_interaction_breaks_sensor_or_communications_requirements",
            "required_clearance_cannot_fit_vehicle_packaging_without_change_control",
            "nozzle_detachment_or_divergence_remains_unbounded_at_required_modes",
        ],
        "carried_rcs_integration_holds": [
            "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
            "WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD",
            "MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE",
            "VECTORING_DYNAMIC_RESPONSE_AND_LIFE",
            "MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT",
        ],
        "qualified_next_step": "INTEGRATED_TORCH_VEHICLE_ARCHITECTURE_AND_COMPONENT_FREEZE_READINESS_REVIEW",
    }


if __name__ == "__main__":
    print(json.dumps(build_envelope(), indent=2, sort_keys=True))
