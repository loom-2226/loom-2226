import json

RCS_HOLDS = [
    "PHYSICAL_PLUME_MODEL_AND_CLEARANCE_SWEEP",
    "WORKING_FLUID_CYCLE_EXHAUST_VELOCITY_AND_THERMAL_LOAD",
    "MIB_VALVE_RESPONSE_DUTY_TOTAL_IMPULSE_AND_CYCLE_LIFE",
    "VECTORING_DYNAMIC_RESPONSE_AND_LIFE",
    "MOUNT_LOAD_PATH_LOCAL_STRUCTURE_AND_REINFORCEMENT",
]


def _family(disposition, evidence, partition, nozzle, realizability):
    return {
        "disposition": disposition,
        "evidence_basis": evidence,
        "reaction_product_partition_gate": partition,
        "nozzle_coupling_gate": nozzle,
        "physical_realizability_gate": realizability,
        "component_certified": False,
    }


def build_trade():
    return {
        "schema": "LOOM.Wayfarer.TorchReactorNozzleTechnologyFamilyTrade",
        "schema_version": "0.1",
        "status": "PASS",
        "authority": {
            "claim": "E1_TORCH_REACTOR_NOZZLE_TECHNOLOGY_FAMILY_TRADE_ONLY",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "canon_changed": False,
            "reactor_cycle_certified": False,
            "fuel_cycle_certified": False,
            "magnetic_nozzle_component_design_certified": False,
            "deposition_partition_certified": False,
            "archive_values_promoted_to_current_authority": False,
        },
        "required_vehicle_envelope": {
            "architecture": "AXIAL_FUSION_TORCH_WITH_MAGNETIC_NOZZLE",
            "initial_direct_jet_power_W": {
                "ECON": 5112451811250.0,
                "CRUISE": 11361004025000.0,
                "EXPEDITE": 11361004025000.0,
                "FAST": 11929054226250.0,
                "HARD": 12781129528125.0,
                "LIMIT": 12781129528125.0,
            },
            "initial_axial_thrust_N": {
                "ECON": 3408301.2075,
                "CRUISE": 11361004.025,
                "EXPEDITE": 22722008.05,
                "FAST": 34083012.075,
                "HARD": 56805020.125,
                "LIMIT": 85207530.1875,
            },
            "exhaust_velocity_km_s_range": [300.0, 3000.0],
            "normal_remass_t": 250.0,
            "protected_water_reserve_t": 50.0,
            "candidate_machinery_x_m": [43.0, 50.0],
            "candidate_machinery_transverse_diameter_m": 4.25,
            "candidate_nozzle_x_m": [50.0, 57.0],
            "candidate_nozzle_support_aperture_diameter_m": 6.0,
            "packaging_status": "NON_GOVERNING_CANDIDATE",
        },
        "research_firewall": {
            "status": "EXTERNAL_RESEARCH_SYNTHESIS_NOT_CANON",
            "repo_rh003": "OPEN_STANDING_TARGET_SHIP_BUDGET_CLOSED_MICROPHYSICS_OPEN",
            "principle": "A_REAL_RESEARCH_ANALOG_CAN_SUPPORT_A_FAMILY_TRADE_BUT_CANNOT_CERTIFY_2226_HARDWARE",
            "jet_power_rule": "DIRECT_KINETIC_EXHAUST_POWER_IS_NOT_ELECTRICAL_LOAD_OR_WASTE_HEAT",
        },
        "technology_families": {
            "D_HE3_FRC_DIRECT_FUSION_MAGNETIC_NOZZLE": _family(
                "LEADING_RESEARCH_ANALOG_NOT_CERTIFIED",
                "PPPL_PFRC_DFD_AND_NASA_DHE3_FUSION_PROPULSION_LITERATURE",
                "Quantify primary D-He3 charged products plus unavoidable side-reaction neutron/photon channels by mode; no zero-neutron assumption.",
                "Demonstrate remass entrainment/heating, directed exhaust conversion, plume angle and plasma detachment across 300-3000 km/s without unearned efficiency.",
                "Scale from published MW-class concepts to the required multi-TW kinetic exhaust envelope while closing confinement, fuel supply, magnets, shielding, heat rejection and packaging.",
            ),
            "DD_TRITIUM_SUPPRESSED_FRC_MAGNETIC_NOZZLE": _family(
                "SECONDARY_RESEARCH_ANALOG_HOLD_PARTITION",
                "PPPL_DFD_LITERATURE_IDENTIFIES_TRITIUM_SUPPRESSED_DD_AS_AN_OPTION",
                "Close D-D branches, produced tritium/He3 burn-up policy, neutron spectrum and activation rather than labeling the cycle aneutronic.",
                "Same magnetic-nozzle/remass-coupling and detachment gates as D-He3.",
                "Show that neutron burden, fuel-cycle handling and power density fit vehicle shielding/thermal/package constraints.",
            ),
            "DT_DIRECT_FUSION_MAGNETIC_NOZZLE": _family(
                "HOLD_NEUTRON_AND_THERMAL_PARTITION",
                "MATURE_FUSION_REACTION_BASE_BUT_HIGH_NEUTRON_ENERGY_FRACTION_IS_POORLY_ALIGNED_WITH_DIRECT_CHARGED_PRODUCT_PROPULSION",
                "Explicitly budget 14.1-MeV-neutron-dominant energy, secondary gammas, activation and shield heating.",
                "Prove how sufficient fusion energy reaches remass/directed exhaust rather than becoming inaccessible neutron heating.",
                "Must close shielding mass, coil lifetime, activation, thermal rejection and 57-m vehicle packaging before surviving trade.",
            ),
            "PB11_DIRECT_FUSION_MAGNETIC_NOZZLE": _family(
                "HOLD_REACTIVITY_AND_BREMSSTRAHLUNG_REALIZABILITY",
                "ANEUTRONIC_ATTRACTION_BUT_IAEA_RESEARCH_STILL_IDENTIFIES_FUNDAMENTAL_REACTION_AND_COMMERCIALIZATION_CHALLENGES",
                "Budget alpha products, bremsstrahlung photons, impurities/side reactions and secondary radiation; no 'aneutronic means no radiation' shortcut.",
                "Demonstrate usable coupling of charged fusion products to bulk remass and magnetic nozzle at required thrust and exhaust velocity.",
                "Earn ignition/gain, radiation balance, confinement/power density and machine scale before promotion.",
            ),
            "PULSED_MAGNETIZED_TARGET_FUSION_PROPELLANT_LINER": _family(
                "ALTERNATE_ARCHITECTURE_REFERENCE_NOT_BASELINE_COMPATIBLE_WITHOUT_CHANGE_CONTROL",
                "NASA_FUSION_DRIVEN_ROCKET_STUDIES_USE_PROPELLANT_LINER_TO_CAPTURE_FUSION_ENERGY_AND_MAGNETIC_NOZZLE",
                "Budget capture of photons/neutrons/particles into liner/propellant and resulting local deposition.",
                "Demonstrate pulse-to-directed-exhaust conversion, repetition rate, nozzle impulse loading and plume behavior.",
                "Current Wayfarer authority is an axial fusion torch/magnetic nozzle; pulsed liner architecture requires explicit architecture change review even if physically attractive.",
            ),
        },
        "family_trade_result": {
            "preferred_research_direction": "D_HE3_OR_RELATED_LOW_NEUTRON_HIGH_BETA_FRC_CLASS_WITH_SEPARATE_REMASS_AUGMENTATION",
            "status": "RESEARCH_DIRECTION_ONLY_NOT_REACTOR_OR_FUEL_CERTIFICATION",
            "reason": "It best matches the already-governed axial fusion-torch/magnetic-nozzle topology and has real propulsion literature linking a linear high-beta FRC, low-neutron fuel strategy, remass augmentation and magnetic nozzle. The required LOOM power/thrust scale is orders beyond those analogs and remains an explicit realizability gate.",
            "hard_rule": "NO_FAMILY_SURVIVES_BY_ASSUMING_A_REQUIRED_DEPOSITION_PPM_OR_NOZZLE_EFFICIENCY; BOTH_MUST_BE_DERIVED_OR_BOUNDED_FROM_A_PHYSICAL_PARTITION_MODEL.",
        },
        "deposition_partition_model_requirements": [
            "primary_charged_fusion_products",
            "primary_neutrons",
            "side_reaction_neutrons",
            "bremsstrahlung_and_other_prompt_photons",
            "charged_particle_escape_and_leakage",
            "magnet_nozzle_interception",
            "shield_absorption_and_secondary_heating",
            "activation_and_decay_heat",
            "remass_coupling_fraction",
            "directed_exhaust_fraction",
            "mode_dependence",
        ],
        "physical_realizability_kill_criteria": [
            "cannot_produce_required_kinetic_exhaust_power_without_unbounded_or_unmodeled_input_power",
            "cannot_span_required_thrust_and_300_to_3000_km_s_exhaust_velocity_with_governed_remass",
            "cannot_bound_neutron_photon_and_intercepted_particle_deposition",
            "cannot_close_magnetic_nozzle_detachment_and_efficiency",
            "cannot_fit_candidate_packaging_without_explicit_repackaging_review",
            "cannot_close_magnet_shield_structure_and_thermal_lifetime",
        ],
        "carried_rcs_integration_holds": RCS_HOLDS,
        "remaining_open": [
            "reactor_cycle_and_fusion_architecture",
            "fuel_cycle",
            "fusion_gain_and_specific_power",
            "reaction_product_energy_partition",
            "remass_entrainment_and_heating",
            "plasma_detachment_and_nozzle_efficiency",
            "neutron_photon_and_secondary_transport",
            "magnetic_coil_geometry_stress_and_lifetime",
            "shadow_shield_stack",
            "thermal_plumbing_and_transient_rejection",
            "physical_plume_and_external_clearance",
            "working_fluid_identity_and_feed",
            "thrust_frame_dynamic_side_load_fatigue_and_local_stress",
        ],
        "qualified_next_step": "BUILD_TORCH_DEPOSITION_PARTITION_MODEL_AND_FAMILY_KILL_CRITERIA",
    }


if __name__ == "__main__":
    print(json.dumps(build_trade(), indent=2, sort_keys=True))
