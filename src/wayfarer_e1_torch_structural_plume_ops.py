"""Wayfarer E1 T4 structural/plume/operational integration envelope.

This binds already-earned torch requirements to the vehicle. It deliberately
preserves component-level structural, plume, RCS, shield, magnet and thermal
unknowns as holds rather than inventing 2226 hardware parameters.
"""
from __future__ import annotations

from src.wayfarer_torch_thermal_shield_thrust_frame_envelope import build_envelope as build_structural_source
from src.wayfarer_torch_plume_clearance_envelope import build_envelope as build_plume_source


def build_structural_plume_ops_envelope() -> dict:
    structural = build_structural_source()
    plume = build_plume_source()
    frame = structural["thrust_frame_requirement_envelope"]
    candidate = structural["source_status"]["candidate_packaging"]

    thrusts = {mode: row["initial_axial_thrust_N"] for mode, row in frame["modes"].items()}

    return {
        "schema": "LOOM.Wayfarer.E1TorchStructuralPlumeOperationalIntegrationEnvelope",
        "schema_version": "0.1",
        "status": "E1_INTEGRATION_ENVELOPE_WITH_TECHNOLOGY_HOLDS",
        "authority": {
            "claim": "E1_T4_INTERFACE_INTEGRATION_ONLY",
            "campaign_state_mutation": "ZERO",
            "canon_changed": False,
            "thrust_frame_certified": False,
            "physical_plume_certified": False,
            "rcs_installation_certified": False,
            "thermal_hardware_certified": False,
        },
        "axial_thrust_envelope_N": thrusts,
        "governing_known_axial_load_mode": frame["governing_known_axial_load_mode"],
        "structural_interface": {
            "primary_load_path": "FOUR_LONGERON_AXIAL_THRUST_FRAME_INTERFACE",
            "governing_known_initial_axial_thrust_N": frame["governing_known_initial_axial_thrust_N"],
            "structural_design_factor": frame["structural_design_factor"],
            "dynamic_amplification_factor": frame["dynamic_amplification_factor"],
            "side_load_fraction": None,
            "fatigue_spectrum": frame["fatigue_spectrum"],
            "local_reinforcement_design": None,
            "holds": [
                "STRUCTURAL_DESIGN_FACTOR_OPEN",
                "DYNAMIC_AMPLIFICATION_OPEN",
                "NOZZLE_SIDE_LOAD_OPEN",
                "FATIGUE_SPECTRUM_OPEN",
                "LOCAL_STRESS_AND_REINFORCEMENT_OPEN",
            ],
        },
        "aft_packaging_interface": {
            "shadow_shield_x_m": candidate["shadow_shield_x_m"],
            "reactor_thrust_frame_x_m": candidate["reactor_thrust_frame_x_m"],
            "magnetic_nozzle_x_m": candidate["magnetic_nozzle_x_m"],
            "load_path_concept": candidate["load_path_concept"],
            "status": candidate["status"],
        },
        "plume_external_clearance_interface": {
            "plume_half_angle_deg": None,
            "plume_length_m": None,
            "clearance_margin_m": None,
            "required_clearance_classes": plume["required_clearance_classes"],
            "derived_requirements": plume["derived_requirements"],
            "kill_criteria": plume["kill_criteria"],
            "holds": [
                "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
                "MODE_DEPENDENT_DIVERGENCE_AND_DENSITY_OPEN",
                "DETACHMENT_AND_BACKFLOW_OPEN",
                "SURFACE_INTERCEPTION_AND_DEPOSITION_OPEN",
            ],
        },
        "rcs_integration_holds": list(plume["carried_rcs_integration_holds"]),
        "thermal_and_lifetime_holds": [
            "SHIELD_MAGNET_AND_THERMAL_LIFETIME_OPEN",
            "TORCH_DEPOSITION_PARTITION_OPEN",
            "TRANSIENT_THERMAL_REJECTION_DUTY_OPEN",
            "PHYSICAL_RADIATOR_GEOMETRY_AND_TORCH_CLEARANCE_OPEN",
        ],
        "operational_interface": {
            "torch_high_metric_mutually_exclusive": True,
            "exclusions": [
                "NO_TORCH_OPERATION_DURING_HIGH_METRIC_THERMAL_OR_FIELD_OPERATION",
                "NO_NORMAL_TORCH_CONSUMPTION_OF_PROTECTED_WATER_RESERVE",
                "NO_COMPONENT_GEOMETRY_FREEZE_FROM_CANDIDATE_PACKAGING",
                "NO_EXTERNAL_HARDWARE_FREEZE_BEFORE_PHYSICAL_PLUME_CLEARANCE",
            ],
            "holds": [
                "TRANSITION_PRECONDITIONS_OPEN_PENDING_FEED_FIELD_THERMAL_AND_ATTITUDE_DYNAMICS",
                "SAFE_SHUTDOWN_AND_FAULT_ISOLATION_DYNAMICS_OPEN",
                "RCS_TORCH_MUTUAL_PLUME_INTERACTION_OPEN",
            ],
        },
        "t5_readiness": "T4_INTERFACE_BOUNDED_COMPONENT_CERTIFICATION_HOLDS_CARRIED_FORWARD",
    }
