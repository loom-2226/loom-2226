from __future__ import annotations

"""Derive the E1 Wayfarer torch performance/remass requirement envelope.

All numerical performance in this module is deterministic arithmetic from recovered
working engineering cards plus the qualified current mass/remass state. It does not
select a reactor cycle, thermal efficiency, fusion gain, nozzle internals, or onboard
electrical architecture. Direct jet power is a kinetic exhaust quantity only.
"""

import math
from typing import Any

from src.wayfarer_torch_baseline_recovery import build_torch_baseline_recovery

SCHEMA = "LOOM.Wayfarer.TorchPerformanceRemassEnvelope"
SCHEMA_VERSION = "0.1"
STANDARD_GRAVITY_M_S2 = 9.80665

# Source-derived working engineering acceleration cards recovered from the current
# Integrated HUD/Navigator architecture baseline. They are working cards, not universal
# spacecraft constants or newly promoted fiction canon.
_ACCELERATION_CARDS_G = {
    "ECON": 0.30,
    "CRUISE": 1.00,
    "EXPEDITE": 2.00,
    "FAST": 3.00,
    "HARD": 5.00,
    "LIMIT": 7.50,
}


def _card(mode: str, acceleration_g: float, ve_km_s: float, wet_mass_t: float) -> dict[str, float]:
    mass_kg = wet_mass_t * 1000.0
    acceleration_m_s2 = acceleration_g * STANDARD_GRAVITY_M_S2
    ve_m_s = ve_km_s * 1000.0
    thrust_N = mass_kg * acceleration_m_s2
    mass_flow_kg_s = thrust_N / ve_m_s
    direct_jet_power_W = 0.5 * thrust_N * ve_m_s
    return {
        "acceleration_g": acceleration_g,
        "acceleration_m_s2": acceleration_m_s2,
        "exhaust_velocity_km_s": ve_km_s,
        "exhaust_velocity_m_s": ve_m_s,
        "initial_thrust_N_at_reference_wet_mass": thrust_N,
        "initial_mass_flow_kg_s_at_reference_wet_mass": mass_flow_kg_s,
        "initial_direct_jet_power_W_at_reference_wet_mass": direct_jet_power_W,
    }


def build_torch_performance_remass_envelope() -> dict[str, Any]:
    baseline = build_torch_baseline_recovery()
    if baseline["status"] != "PASS":
        raise RuntimeError("torch baseline recovery did not pass")

    vi = baseline["vehicle_interfaces"]
    wet_t = float(vi["reference_wet_mass_t"])
    post_t = float(vi["post_normal_remass_reference_mass_t"])
    remass_t = float(vi["normal_remass_allowance_t"])
    reserve_t = float(vi["protected_water_reserve_t"])
    exhaust = baseline["exhaust_velocity_cards_km_s"]

    cards = {
        mode: _card(mode, _ACCELERATION_CARDS_G[mode], float(exhaust[mode]), wet_t)
        for mode in _ACCELERATION_CARDS_G
    }

    mass_ratio = wet_t / post_t
    full_burn: dict[str, dict[str, float]] = {}
    for mode, row in cards.items():
        ve_m_s = row["exhaust_velocity_m_s"]
        a_m_s2 = row["acceleration_m_s2"]

        # For a constant acceleration/exhaust-velocity card, thrust follows instantaneous
        # mass: F=m*a, mdot=m*a/ve. Integrating dm/dt=-m*a/ve gives the duration below.
        burn_duration_s = (ve_m_s / a_m_s2) * math.log(mass_ratio)
        ideal_delta_v_m_s = ve_m_s * math.log(mass_ratio)
        final_thrust_N = post_t * 1000.0 * a_m_s2
        final_mass_flow_kg_s = final_thrust_N / ve_m_s
        final_direct_jet_power_W = 0.5 * final_thrust_N * ve_m_s

        full_burn[mode] = {
            "burn_model": "CONSTANT_ACCELERATION_AND_EXHAUST_VELOCITY_CARD_WITH_THRUST_TRACKING_INSTANTANEOUS_MASS",
            "burn_duration_s": burn_duration_s,
            "burn_duration_min": burn_duration_s / 60.0,
            "ideal_delta_v_km_s": ideal_delta_v_m_s / 1000.0,
            "normal_remass_consumed_t": remass_t,
            "protected_water_consumed_t": 0.0,
            "final_mass_t": post_t,
            "final_thrust_N": final_thrust_N,
            "final_mass_flow_kg_s": final_mass_flow_kg_s,
            "final_direct_jet_power_W": final_direct_jet_power_W,
        }

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "source": {
            "torch_baseline_schema": baseline["schema"],
            "torch_baseline_claim": baseline["authority"]["claim"],
            "acceleration_card_source": "engineering/current/LOOM_2226_Integrated_HUD_Navigator_Architecture_and_Work_Plan_v1.0.md",
            "acceleration_card_status": "SOURCE_DERIVED_WORKING_ENGINEERING_CARDS_NOT_UNIVERSAL_SPACECRAFT_CONSTANTS",
            "standard_gravity_m_s2": STANDARD_GRAVITY_M_S2,
        },
        "operating_cards": cards,
        "normal_remass_envelope": {
            "reference_wet_mass_t": wet_t,
            "normal_remass_available_t": remass_t,
            "protected_water_reserve_t": reserve_t,
            "post_normal_remass_reference_mass_t": post_t,
            "mass_ratio_wet_to_post_normal_remass": mass_ratio,
            "constant_card_full_normal_remass_burn": full_burn,
            "reserve_rule": "NORMAL_TORCH_REMASS_ENVELOPE_STOPS_BEFORE_PROTECTED_50_T_WATER_RESERVE",
        },
        "physics_contract": {
            "initial_thrust": "F=m*a at reference wet mass",
            "mass_flow": "mdot=F/ve",
            "direct_jet_power": "Pjet=0.5*F*ve=0.5*mdot*ve^2",
            "constant_card_mass_evolution": "dm/dt=-m*a/ve",
            "constant_card_ideal_delta_v": "dv=ve*ln(m0/m1)",
            "jet_power_interpretation": "KINETIC_EXHAUST_POWER_NOT_ONBOARD_ELECTRICAL_LOAD_OR_WASTE_HEAT",
        },
        "carried_rcs_integration_holds": list(baseline["carried_rcs_integration_holds"]),
        "remaining_open": [
            "reactor_cycle_and_fusion_architecture",
            "conversion_and_nozzle_efficiency",
            "reactor_and_nozzle_waste_heat_fraction",
            "neutron_photon_and_plasma_radiation_partition",
            "shadow_shield_materials_and_layering",
            "magnetic_nozzle_coil_geometry_and_stress",
            "thrust_frame_structural_load_paths_and_factors",
            "physical_torch_plume_envelope_and_external_hardware_clearance",
            "working_fluid_identity_and_feed_implementation",
        ],
        "authority": {
            "claim": "E1_TORCH_PERFORMANCE_REMASS_REQUIREMENT_ENVELOPE_ONLY",
            "working_card_arithmetic_derived": True,
            "reactor_cycle_certified": False,
            "thermal_efficiency_certified": False,
            "waste_heat_certified": False,
            "shielding_certified": False,
            "nozzle_component_design_certified": False,
            "thrust_frame_certified": False,
            "plume_clearance_certified": False,
            "working_fluid_identity_certified": False,
            "jet_power_promoted_to_electrical_load": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "DERIVE_TORCH_THERMAL_SHIELDING_AND_THRUST_FRAME_REQUIREMENT_ENVELOPES_WITH_REACTOR_CYCLE_STILL_OPEN",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_torch_performance_remass_envelope(), indent=2, sort_keys=True))
