"""Wayfarer E1 torch feed-dynamics/nozzle-coupling envelope.

Engineering requirement model only. Unknown physical parameters remain explicit inputs;
no working-fluid species, hardware, response time, or efficiency is selected/certified.
"""
import json
import math

MODES = {
    "ECON": (1.1361004025, 3_000_000.0),
    "CRUISE": (5.6805020125, 2_000_000.0),
    "EXPEDITE": (22.72200805, 1_000_000.0),
    "FAST": (48.69001725, 700_000.0),
    "HARD": (2272200805 / 18000000, 450_000.0),
    "LIMIT": (2272200805 / 8000000, 300_000.0),
}


def _mode_outputs(mode):
    mdot, ve = MODES[mode]
    thrust = mdot * ve
    jet_power = 0.5 * mdot * ve * ve
    return mdot, ve, thrust, jet_power


def build_envelope():
    lo = min(v[0] for v in MODES.values())
    hi = max(v[0] for v in MODES.values())
    return {
        "schema": "LOOM.Wayfarer.TorchFeedDynamicsNozzleCouplingEnvelope",
        "schema_version": "0.1",
        "status": "PASS",
        "authority": {
            "claim": "E1_TORCH_FEED_DYNAMICS_NOZZLE_COUPLING_REQUIREMENT_ENVELOPE_ONLY",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "canon_changed": False,
            "working_fluid_selected": False,
            "hardware_certified": False,
        },
        "candidate_inputs": {
            "species": None,
            "feed_response_time_s": None,
            "coupling_efficiency": None,
            "nozzle_efficiency": None,
            "feed_pressure_Pa": None,
            "conditioning_power_W": None,
            "ionization_state": None,
            "detachment_fraction": None,
            "interception_fraction": None,
        },
        "requirements": {
            "normal_remass_kg": 250000.0,
            "protected_water_kg": 50000.0,
            "mass_flow_kg_s_range": [lo, hi],
            "peak_mass_flow_kg_s": hi,
            "turndown_ratio": hi / lo,
            "effective_exhaust_velocity_m_s_range": [300000.0, 3000000.0],
            "mode_outputs_derived_from": ["mdot_kg_s", "ve_m_s", "F=mdot*ve", "Pjet=0.5*mdot*ve^2"],
        },
        "dynamic_holds": [
            "FEED_RESPONSE_AND_MODE_TRANSITION_TIME",
            "VALVE_PUMP_OR_INJECTOR_DYNAMIC_RANGE_AND_CYCLE_LIFE",
            "PRESSURE_AND_TWO_PHASE_STABILITY",
            "CONDITIONING_AND_IONIZATION_TRANSIENT",
            "FAULT_ISOLATION_AND_SAFE_SHUTDOWN",
        ],
        "nozzle_holds": [
            "SPECIES_DEPENDENT_ENERGY_TRANSFER",
            "MAGNETIZATION_AND_GYRADIUS",
            "PLASMA_DETACHMENT",
            "DIVERGENCE",
            "WALL_OR_COIL_INTERCEPTION",
            "EROSION_CONTAMINATION_AND_LIFETIME",
        ],
        "firewall": "PROTECTED_50_T_WATER_RESERVE_IS_NOT_NORMAL_REMASS",
        "qualified_next_step": "Z3_FIXED_DURATION_SEGMENT_AND_CONFIGURATION_SYNTHESIS",
    }


def evaluate_candidate(mode, feed_response_time_s, coupling_efficiency, nozzle_efficiency):
    if mode not in MODES:
        raise ValueError("mode must be an earned non-OFF torch card")
    if feed_response_time_s is None or not math.isfinite(feed_response_time_s) or feed_response_time_s < 0:
        raise ValueError("feed response time must be explicit, finite, and nonnegative")
    for name, value in (("coupling efficiency", coupling_efficiency), ("nozzle efficiency", nozzle_efficiency)):
        if value is None or not math.isfinite(value) or value <= 0 or value > 1:
            raise ValueError(f"{name} must be in (0,1]")
    mdot, ve, thrust, jet_power = _mode_outputs(mode)
    directed_efficiency = coupling_efficiency * nozzle_efficiency
    return {
        "mode": mode,
        "mdot_kg_s": mdot,
        "ve_m_s": ve,
        "thrust_N": thrust,
        "jet_power_W": jet_power,
        "feed_response_time_s": feed_response_time_s,
        "coupling_efficiency": coupling_efficiency,
        "nozzle_efficiency": nozzle_efficiency,
        "combined_directed_efficiency": directed_efficiency,
        "required_pre_coupling_power_W": jet_power / directed_efficiency,
        "status": "SENSITIVITY_ONLY_EXPLICIT_INPUTS",
        "certified": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_envelope(), indent=2, sort_keys=True))
