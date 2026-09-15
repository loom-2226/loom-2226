"""Wayfarer E1 torch deposition-partition requirement model.

This artifact deliberately does not invent a fusion efficiency, reaction-product
partition, or vehicle heat-deposition fraction.  It provides the accounting
contract that later physical models must satisfy.
"""

from __future__ import annotations

import json
import math
from typing import Mapping

SCHEMA = "LOOM.Wayfarer.TorchDepositionPartitionRequirementModel"
SCHEMA_VERSION = "0.1"

DIRECT_JET_POWER_W = {
    "ECON": 5_112_451_811_250.0,
    "CRUISE": 11_361_004_025_000.0,
    "EXPEDITE": 11_361_004_025_000.0,
    "FAST": 11_929_054_226_250.0,
    "HARD": 12_781_129_528_125.0,
    "LIMIT": 12_781_129_528_125.0,
}

PARTITION_KEYS = (
    "directed_exhaust",
    "escaping_neutral_radiation",
    "vehicle_deposition",
    "other_accounted_loss",
)


def evaluate_partition_candidate(fractions: Mapping[str, float], mode: str = "LIMIT") -> dict:
    """Evaluate an explicitly supplied source-energy partition.

    The four aggregate channels are an accounting layer, not a claim that
    detailed neutron/photon/charged-particle transport has already been solved.
    """
    if mode not in DIRECT_JET_POWER_W:
        raise ValueError(f"unknown mode: {mode}")
    if set(fractions) != set(PARTITION_KEYS):
        raise ValueError("candidate must provide every aggregate partition channel exactly once")
    vals = {k: float(fractions[k]) for k in PARTITION_KEYS}
    if any((not math.isfinite(v)) or v < 0.0 or v > 1.0 for v in vals.values()):
        raise ValueError("partition fractions must be finite and within [0,1]")
    total = sum(vals.values())
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("partition fractions must close to unity")
    directed = vals["directed_exhaust"]
    if directed <= 0.0:
        raise ValueError("directed exhaust fraction must be positive")

    jet = DIRECT_JET_POWER_W[mode]
    source = jet / directed
    deposition = source * vals["vehicle_deposition"]
    return {
        "mode": mode,
        "direct_jet_power_W": jet,
        "partition": vals,
        "partition_sum": total,
        "required_source_power_W": source,
        "vehicle_deposition_power_W": deposition,
        "source_power_is_electrical_load": False,
        "source_power_is_certified_reactor_power": False,
        "interpretation": "SENSITIVITY_RESULT_FROM_EXPLICIT_CANDIDATE_PARTITION_NOT_CERTIFIED_HARDWARE",
    }


def build_requirement_model() -> dict:
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "authority": {
            "claim": "E1_TORCH_DEPOSITION_PARTITION_AND_FAMILY_KILL_CRITERIA_ONLY",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "canon_changed": False,
            "reactor_cycle_certified": False,
            "fuel_cycle_certified": False,
            "deposition_partition_certified": False,
            "nozzle_efficiency_certified": False,
            "thermal_system_certified": False,
        },
        "power_firewall": {
            "rule": "JET_KINETIC_POWER_IS_NOT_SOURCE_POWER_OR_VEHICLE_WASTE_HEAT",
            "direct_jet_power_W": DIRECT_JET_POWER_W,
            "source_power_rule": "SOURCE_POWER_MAY_ONLY_BE_DERIVED_WHEN_AN_EXPLICIT_DIRECTED_EXHAUST_FRACTION_IS_SUPPLIED",
            "vehicle_heat_rule": "VEHICLE_DEPOSITION_MAY_ONLY_BE_DERIVED_WHEN_AN_EXPLICIT_PHYSICAL_DEPOSITION_FRACTION_IS_SUPPLIED",
        },
        "candidate_inputs": {
            "directed_exhaust_fraction": None,
            "vehicle_deposition_fraction": None,
            "source_power_W": None,
            "reason": "NO_PHYSICAL_PARTITION_BOUNDS_HAVE_YET_BEEN_EARNED",
        },
        "required_detailed_channels": [
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
        "aggregate_accounting_contract": {
            "channels": list(PARTITION_KEYS),
            "closure": "SUM_EQUALS_ONE",
            "note": "Detailed physical channels must map into these aggregates without double counting; this aggregate layer does not replace transport physics.",
        },
        "family_kill_gates": {
            "D_HE3_FRC_DIRECT_FUSION_MAGNETIC_NOZZLE": {
                "status": "OPEN_NEEDS_PARTITION_BOUNDS",
                "survives_if": "side-reaction neutron/photon, interception and remass/nozzle coupling can be physically bounded at Wayfarer scale",
                "forbidden_shortcut": "PRIMARY_CHARGED_PRODUCTS_DO_NOT_IMPLY_ZERO_NEUTRON_OR_ZERO_HEAT_SYSTEM",
            },
            "DD_TRITIUM_SUPPRESSED_FRC_MAGNETIC_NOZZLE": {
                "status": "OPEN_NEEDS_BRANCH_AND_SECONDARY_BURN_MODEL",
                "survives_if": "D-D branches, produced tritium/He3 disposition, neutron spectrum and activation close within vehicle constraints",
            },
            "DT_DIRECT_FUSION_MAGNETIC_NOZZLE": {
                "status": "HIGH_RISK_NEUTRON_PARTITION_HOLD",
                "survives_if": "neutron-dominant source energy can close shielding, thermal, magnet lifetime and packaging while still supplying required directed jet power",
            },
            "PB11_DIRECT_FUSION_MAGNETIC_NOZZLE": {
                "status": "OPEN_NEEDS_RADIATION_AND_GAIN_BOUNDS",
                "survives_if": "bremsstrahlung/radiation balance, ignition/gain, impurities/side reactions and remass coupling close physically",
            },
            "PULSED_MAGNETIZED_TARGET_FUSION_PROPELLANT_LINER": {
                "status": "ARCHITECTURE_CHANGE_REVIEW_REQUIRED",
                "survives_if": "explicit change control accepts pulsed architecture and pulse-to-exhaust/structure/thermal physics closes",
            },
        },
        "archived_ppm_sensitivity": {
            "status": "NON_GOVERNING_PROVENANCE_ONLY",
            "values_ppm": [4, 8, 20, 50, 100],
            "rule": "MAY_BE_USED_TO_ILLUSTRATE_CONSEQUENCES_BUT_NOT_AS_A_REQUIRED_OR_ACHIEVABLE_DEPOSITION_FRACTION",
        },
        "derived_vehicle_requirement": "THE_250_T_NORMAL_REMASS_INVENTORY_REQUIRES_AN_EXPLICIT_ENERGY_AND_MOMENTUM_COUPLING_PATH_FROM_FUSION_SOURCE_TO_BULK_REMASS; RAW_FUSION_PRODUCTS_ALONE_CANNOT_SILENTLY_ACCOUNT_FOR_GOVERNED_REMASS_CONSUMPTION",
        "kill_criteria": [
            "partition_cannot_close_without_unmodeled_energy",
            "required_source_power_diverges_or_depends_on_assumed_efficiency",
            "neutral_radiation_or_vehicle_deposition_cannot_be_bounded",
            "remass_coupling_cannot_span_governed_thrust_and_exhaust_velocity",
            "magnetic_nozzle_interception_detachment_or_efficiency_cannot_be_bounded",
            "shield_magnet_structure_thermal_lifetime_or_packaging_cannot_close",
        ],
        "qualified_next_step": "TORCH_REMASS_COUPLING_AND_MAGNETIC_NOZZLE_EFFICIENCY_ENVELOPE",
    }


if __name__ == "__main__":
    print(json.dumps(build_requirement_model(), indent=2, sort_keys=True))
