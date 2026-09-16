"""Wayfarer E1 metric canon/frontier closure.

This module does not derive fictional metric physics. Governing canon supplies the
metric mechanism and certified clean-environment card. The frozen 2226 Frontier
is consumed only for ordinary support accounting such as PMAD/conversion losses
and radiator flux. Open authorial/physical validation gates remain explicit.
"""
from fractions import Fraction

from src.wayfarer_2226_frontier_accountant import (
    PRODUCER_REGISTER_VERSION,
    SCENARIOS,
    producer_version_hash,
    radiator_flux_w_m2,
)

MODES = {
    "NORMAL": (Fraction(268,1000), Fraction(10), Fraction(20_000), Fraction(3_500_000), Fraction(106)),
    "FAST": (Fraction(437,1000), Fraction(12), Fraction(38_100), Fraction(6_700_000), Fraction(202)),
    "EXPEDITE": (Fraction(519,1000), Fraction(15), Fraction(63_500), Fraction(11_200_000), Fraction(336)),
    "HARD": (Fraction(595,1000), Fraction(30), Fraction(136_000), Fraction(23_900_000), Fraction(719)),
}


def build_metric_closure(scenario="MVP_2226"):
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown frontier scenario: {scenario}")
    s = SCENARIOS[scenario]
    flux = radiator_flux_w_m2(Fraction(900), s.radiator_emissivity)
    modes = {}
    for name, (beta, ramp_s, cold_w, delivered_w, canon_area) in MODES.items():
        upstream = delivered_w / (s.conversion_efficiency * s.pmad_efficiency)
        distribution_heat = upstream - delivered_w
        modes[name] = {
            "beta": beta,
            "ramp_s": ramp_s,
            "cold_load_w": cold_w,
            "delivered_electrical_w": delivered_w,
            "canon_900k_equivalent_area_m2": canon_area,
            "required_upstream_electrical_w": upstream,
            "distribution_heat_w": distribution_heat,
            "distribution_900k_radiator_area_m2": distribution_heat / flux,
        }
    return {
        "schema": "LOOM.Wayfarer.E1MetricCanonFrontierClosure",
        "status": "E1_METRIC_INTERFACE_CLOSED_WITH_PHYSICS_VALIDATION_HOLDS",
        "e1_interface_frozen": True,
        "component_hardware_certified": False,
        "canon_authority": "CANON_II_ENGINEERING_SHIPS_OPERATIONS_V2_4",
        "frontier_authority": "FROZEN_SUPPORT_PRODUCERS_CONSUMED_WITHOUT_NEW_PHYSICS",
        "producer_register_version": PRODUCER_REGISTER_VERSION,
        "producer_version_hash": producer_version_hash(),
        "scenario": scenario,
        "plant": {
            "mass_kg": Fraction(88_000),
            "mc299m_kg": Fraction(10),
            "active_tiles": 100,
            "active_tile_mass_kg": Fraction(1,10),
            "nodes": 208,
            "shared_bank_j": Fraction(2_000_000_000),
            "cryoplant_class_w": Fraction(150_000),
            "reject_temperature_k": Fraction(900),
        },
        "modes": modes,
        "physics_authority": {
            "constitutive_law": "CANON_PHYSICS_AUTHORITY_ONLY",
            "mc299m_properties": "CANON_PHYSICS_AUTHORITY_ONLY",
            "large_system_continuous_field_t": None,
            "saturation_beta": Fraction(678,1000),
            "saturation_certified": False,
        },
        "operating_rules": {
            "torch_high_metric_mutually_exclusive": True,
            "metric_and_loom_share_relational_plant": True,
            "direct_midfield_metric_to_loom_crew_rated": False,
            "ftl_metric_black": True,
            "bank_is_not_free_macroscopic_energy_or_momentum_reservoir": True,
        },
        "open_blocking_e1": (),
        "physics_validation_holds": (
            "FULL_TIME_DEPENDENT_4D_FINITE_RSET_BENCHMARK",
            "METRIC_ENVIRONMENT_CORRECTION_POWER_AND_THERMAL_CALIBRATION",
            "PATH_DEPENDENT_ORDINARY_STATE_PROPAGATOR_CALIBRATION",
            "WAKE_AND_FINITE_CONSERVATION_LEDGER_VALIDATION",
            "NODE_TOPOLOGY_FAILURE_AND_ENVIRONMENTAL_CERTIFICATION_CALIBRATION",
        ),
        "component_certification_holds": (
            "RELATIONAL_PLANT_DETAILED_SUBASSEMBLY_REALIZATION",
            "ACTIVE_TILE_PHYSICAL_LAYOUT_AND_SERVICE_ROUTING",
            "DISTRIBUTED_NODE_PHYSICAL_PLACEMENT_AND_LOCAL_STRUCTURE",
            "CRYOPLANT_AND_PMAD_INSTALLED_HARDWARE_REALIZATION",
            "RADIATOR_INSTALLED_GEOMETRY_MASS_AND_CLEARANCE",
            "RADIATION_FLUENCE_COMPONENT_LIFETIME",
        ),
    }
