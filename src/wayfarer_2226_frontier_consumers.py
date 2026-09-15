"""Cross-authority consumer exercise for the Wayfarer 2226 frontier accountant.

Integration witness only. Canon and E1 inputs coexist; unresolved hardware stays None.
A canon load is a required delivered load, so ordinary conversion/PMAD losses are paid
UPSTREAM rather than reducing the already-certified consumer requirement.
"""
from fractions import Fraction

from src.wayfarer_2226_frontier_accountant import radiator_flux_w_m2, SCENARIOS

METRIC_MODES = {
    "NORMAL": {"beta": Fraction(268,1000), "cryo_electrical_w": Fraction(3_500_000), "canon_900k_equiv_m2": Fraction(106)},
    "FAST": {"beta": Fraction(437,1000), "cryo_electrical_w": Fraction(6_700_000), "canon_900k_equiv_m2": Fraction(202)},
    "EXPEDITE": {"beta": Fraction(519,1000), "cryo_electrical_w": Fraction(11_200_000), "canon_900k_equiv_m2": Fraction(336)},
    "HARD": {"beta": Fraction(595,1000), "cryo_electrical_w": Fraction(23_900_000), "canon_900k_equiv_m2": Fraction(719)},
}


def build_consumer_exercise(scenario: str):
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown frontier scenario: {scenario}")
    s = SCENARIOS[scenario]
    flux = radiator_flux_w_m2(Fraction(900), s.radiator_emissivity)

    metric = {"plant_mass_kg": Fraction(88_000), "mc299m_kg": Fraction(10), "active_tiles": 100, "node_count": 208, "shared_bank_j": Fraction(2_000_000_000), "cryoplant_class_w": Fraction(150_000), "reject_temperature_k": Fraction(900)}
    for name, card in METRIC_MODES.items():
        delivered = card["cryo_electrical_w"]
        required_upstream = delivered / (s.conversion_efficiency * s.pmad_efficiency)
        heat = required_upstream - delivered
        metric[name] = {
            "beta": card["beta"],
            "canon_cryo_electrical_w": delivered,
            "canon_900k_equivalent_area_m2": card["canon_900k_equiv_m2"],
            "frontier_delivered_load_w": delivered,
            "frontier_required_upstream_electrical_w": required_upstream,
            "frontier_distribution_heat_w": heat,
            "frontier_distribution_radiator_area_m2": heat / flux,
        }

    return {
        "scenario": scenario,
        "authority": "INTEGRATION_EXERCISE_ONLY_NO_CANON_OR_E1_MUTATION",
        "authority_inputs": ("CANON_II_V2_4", "CANON_II_WAYFARER_SCHEMATIC_V2_4A", "E1_RCS_FROZEN_INTERFACE", "E1_TORCH_T5_FROZEN_INTERFACE"),
        "metric": metric,
        "torch": {
            "architecture": "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE", "wet_mass_kg": Fraction(1_158_500), "dry_mass_kg": Fraction(858_500), "normal_remass_kg": Fraction(250_000), "protected_water_kg": Fraction(50_000), "post_normal_remass_mass_kg": Fraction(908_500), "feed_turndown_ratio": Fraction(250), "mass_flow_min_kg_s": Fraction("1.1361004025"), "mass_flow_max_kg_s": Fraction("284.025100625"), "radiator_count": 4, "reject_temperature_k": Fraction(900), "governing_known_axial_load_n": Fraction("85207530.1875"),
            "source_specific_power_w_kg": None, "source_directed_fraction": None, "magnetic_nozzle_field_t": None, "working_fluid": None, "vehicle_deposition_fraction": None,
        },
        "rcs": {
            "architecture": "COMPOUND_COARSE_FINE_VECTORED_MOUNT", "mount_count": 16, "mount_force_cap_n": Fraction(25_000), "nominal_translation_n": Fraction(100_000), "degraded_translation_n": Fraction(75_000), "nominal_pitch_yaw_torque_nm": Fraction(1_000_000), "nominal_roll_torque_nm": Fraction(200_000), "max_sampled_mount_thrust_n": Fraction("20844.756650298394"), "sampled_mib_upper_bound_n_s": Fraction("9.281346527990696"),
            "working_fluid": None, "exhaust_velocity_m_s": None, "hardware_mib_n_s": None, "valve_response_s": None, "cycle_life": None, "physical_plume": None,
        },
        "packaging": {"main_body_length_m": Fraction(57), "main_body_diameter_m": Fraction(9), "launch_bay_x_m": (Fraction(16), Fraction(28)), "radiator_count": 4, "aft_rcs_x_m": Fraction("44.5"), "torch_shadow_shield_candidate_x_m": (Fraction(38), Fraction(43)), "torch_source_frame_candidate_x_m": (Fraction(43), Fraction(50)), "torch_nozzle_candidate_x_m": (Fraction(50), Fraction(57))},
        "operating_rules": {"torch_high_metric_mutually_exclusive": True, "protected_water_not_normal_torch_remass": True, "launch_docked_absent_state_must_be_explicit": True, "metric_and_loom_share_relational_plant": True},
        "unresolved_cross_consumer": ("TORCH_SOURCE_REALIZABILITY_AND_ENERGY_PARTITION", "TORCH_MAGNETIC_NOZZLE_PHYSICS_LIFETIME_AND_PLUME", "RCS_WORKING_FLUID_EXHAUST_VELOCITY_MIB_VALVE_CYCLE_PLUME", "RCS_MOUNT_LOCAL_STRUCTURE_AND_REINFORCEMENT", "RADIATOR_INSTALLED_MASS_GEOMETRY_VIEW_AND_CLEARANCE", "RADIATION_FLUENCE_AND_COMPONENT_LIFETIME", "METRIC_ENVIRONMENT_CORRECTION_POWER_AND_THERMAL_CLOSURE", "METRIC_RSET_FINAL_NUMERICAL_VALIDATION"),
    }
