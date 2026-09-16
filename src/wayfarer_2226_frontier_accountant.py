"""Integrated accountant for the provisional Wayfarer 2226 frontier register.

ENGINEERING SCENARIO TOOL / NOT DOWNSTREAM AUTHORITY.

This module accounts only ordinary-engineering producer quantities admitted by
the bounded horizon pass. It does not invent a magnet field, fusion source
specific power, RCS exhaust velocity, E2 momentum partner, or metric
constitutive law.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from typing import Dict

STEFAN_BOLTZMANN_W_M2_K4 = Fraction(5670374419, 100_000_000_000_000_000)
PRODUCER_REGISTER_VERSION = "WAYFARER_2226_ENGINEERING_FRONTIER_REGISTER_v1.0-rc1"

# Hostile-review H2 compaction: reusable ordinary-engineering producers only.
# Architecture/mechanism-dependent F7/F8 outputs remain consumer-derived.
PRODUCER_QUANTITIES = (
    # F1 fields / superconductors / magnets (5)
    "f1_engineering_current_density_factor",
    "f1_installed_magnet_mass_burden_factor",
    "f1_cryogenic_parasitic_burden_factor",
    "f1_stored_energy_protection_capability_factor",
    "f1_radiation_fluence_lifetime_factor",
    # F2 power conversion / PMAD (4)
    "f2_conversion_efficiency",
    "f2_pmad_efficiency",
    "f2_installed_specific_power_factor",
    "f2_environment_radiation_derating",
    # F3 storage, only after technology/load-duration selection (4)
    "f3_usable_specific_energy_factor",
    "f3_specific_power_factor",
    "f3_round_trip_efficiency",
    "f3_cycle_lifetime_factor",
    # F4 structures / extreme materials (5)
    "f4_installed_specific_load_factor",
    "f4_high_temperature_service_delta_k",
    "f4_creep_fatigue_lifetime_factor",
    "f4_radiation_fluence_lifetime_factor",
    "f4_plasma_erosion_lifetime_factor",
    # F5 thermal transport / radiators (5)
    "f5_radiator_temperature_class",
    "f5_effective_emissivity",
    "f5_installed_radiator_mass_burden_factor",
    "f5_heat_transport_capacity_factor",
    "f5_freeze_turndown_capability_factor",
    # F6 fluids / cryogenics / feed (4)
    "f6_tankage_burden_factor_by_storage_class",
    "f6_active_cryogenic_burden_factor",
    "f6_retention_capability",
    "f6_feed_system_burden_turndown_response",
)


@dataclass(frozen=True)
class FrontierScenario:
    conversion_efficiency: Fraction
    pmad_efficiency: Fraction
    radiator_emissivity: Fraction
    pmad_specific_power_factor: Fraction
    structural_specific_load_factor: Fraction
    radiation_lifetime_factor: Fraction
    radiator_areal_mass_factor: Fraction
    cryogenic_parasitic_factor: Fraction
    tank_mass_factor: Fraction
    feed_specific_power_burden_factor: Fraction


SCENARIOS: Dict[str, FrontierScenario] = {
    "CONSERVATIVE_2226": FrontierScenario(Fraction(97,100), Fraction(94,100), Fraction(85,100), Fraction(3), Fraction(3,2), Fraction(2), Fraction(3,4), Fraction(7,10), Fraction(4,5), Fraction(7,10)),
    "MVP_2226": FrontierScenario(Fraction(98,100), Fraction(96,100), Fraction(90,100), Fraction(5), Fraction(2), Fraction(3), Fraction(1,2), Fraction(1,2), Fraction(3,5), Fraction(1,2)),
    "AGGRESSIVE_2226": FrontierScenario(Fraction(99,100), Fraction(98,100), Fraction(95,100), Fraction(10), Fraction(3), Fraction(5), Fraction(1,3), Fraction(1,3), Fraction(1,2), Fraction(1,3)),
}


def _fraction_token(value: Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def producer_payload():
    """Return the deterministic producer-authority payload used for pinning.

    The payload deliberately includes only the compact producer identity and the
    scenario values currently consumed by the accountant. Unresolved mechanism
    outputs are excluded and therefore cannot become authority through hashing.
    """
    scenarios = {}
    for name in sorted(SCENARIOS):
        scenarios[name] = {
            key: _fraction_token(value)
            for key, value in sorted(asdict(SCENARIOS[name]).items())
        }
    return {
        "producer_register_version": PRODUCER_REGISTER_VERSION,
        "producer_quantity_count": len(PRODUCER_QUANTITIES),
        "producer_quantities": PRODUCER_QUANTITIES,
        "scenarios": scenarios,
        "large_system_continuous_field_t": "UNSET",
        "mechanism_authority": "NONE",
    }


def producer_version_hash() -> str:
    encoded = json.dumps(producer_payload(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def radiator_flux_w_m2(temperature_k: Fraction, emissivity: Fraction) -> Fraction:
    temperature_k = Fraction(temperature_k)
    emissivity = Fraction(emissivity)
    if temperature_k <= 0:
        raise ValueError("radiator temperature must be positive")
    if emissivity <= 0 or emissivity >= 1:
        raise ValueError("radiator emissivity must be in (0,1)")
    return emissivity * STEFAN_BOLTZMANN_W_M2_K4 * temperature_k**4


def conversion_chain(source_electrical_power_w: Fraction, scenario: str):
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown frontier scenario: {scenario}")
    p0 = Fraction(source_electrical_power_w)
    if p0 < 0:
        raise ValueError("source electrical power must be non-negative")
    s = SCENARIOS[scenario]
    after_conversion = p0 * s.conversion_efficiency
    load_power = after_conversion * s.pmad_efficiency
    return {
        "source_electrical_power_w": p0,
        "after_conversion_w": after_conversion,
        "load_power_w": load_power,
        "conversion_loss_w": p0 - after_conversion,
        "pmad_loss_w": after_conversion - load_power,
        "total_distribution_heat_w": p0 - load_power,
    }


def assess_frontier_case(
    scenario: str,
    *,
    source_electrical_power_w: Fraction = Fraction(0),
    radiator_temperature_k: Fraction = Fraction(900),
):
    """Return bounded cross-frontier accounting state for one scenario."""
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown frontier scenario: {scenario}")
    s = SCENARIOS[scenario]
    power = conversion_chain(source_electrical_power_w, scenario)
    flux = radiator_flux_w_m2(radiator_temperature_k, s.radiator_emissivity)
    heat = power["total_distribution_heat_w"]
    area = Fraction(0) if heat == 0 else heat / flux

    holds = [
        "F1_FIELD_REQUIRES_COUPLED_MODEL",
        "F3_STORAGE_REQUIRES_LOAD_DURATION_AND_TECHNOLOGY_CLASS",
        "F4_SHIELDING_REQUIRES_SPECTRUM_MATERIAL_GEOMETRY",
        "F5_INSTALLED_RADIATOR_MASS_REQUIRES_LIKE_FOR_LIKE_BASELINE",
        "F6_RCS_CYCLE_AND_WORKING_FLUID_OPEN",
        "F7_FUSION_SOURCE_AND_NOZZLE_PHYSICS_OPEN",
        "F8_E2_MOMENTUM_PARTNER_OPEN",
        "F8_METRIC_CONSTITUTIVE_LAW_OUTSIDE_FRONTIER_AUTHORITY",
    ]

    return {
        "scenario": scenario,
        "authority": "PROVISIONAL_ACCOUNTING_ONLY_NOT_DOWNSTREAM_AUTHORITY",
        "producer_register_version": PRODUCER_REGISTER_VERSION,
        "producer_version_hash": producer_version_hash(),
        "downstream_authority": "REVALIDATION_REQUIRED_BEFORE_LOAD_BEARING_USE",
        "consumed_frontiers": ("F1_FIELDS", "F2_POWER", "F3_STORAGE", "F4_MATERIALS", "F5_THERMAL", "F6_FLUIDS"),
        "conversion_efficiency": s.conversion_efficiency,
        "pmad_efficiency": s.pmad_efficiency,
        "pmad_specific_power_factor": s.pmad_specific_power_factor,
        "structural_specific_load_factor": s.structural_specific_load_factor,
        "radiation_lifetime_factor": s.radiation_lifetime_factor,
        "radiator_emissivity": s.radiator_emissivity,
        "radiator_areal_mass_factor": s.radiator_areal_mass_factor,
        "cryogenic_parasitic_factor": s.cryogenic_parasitic_factor,
        "tank_mass_factor": s.tank_mass_factor,
        "feed_specific_power_burden_factor": s.feed_specific_power_burden_factor,
        "source_electrical_power_w": Fraction(source_electrical_power_w),
        "delivered_load_power_w": power["load_power_w"],
        "pmad_and_conversion_heat_w": heat,
        "radiator_temperature_k": Fraction(radiator_temperature_k),
        "radiator_flux_w_m2": flux,
        "radiator_area_for_pmad_and_conversion_m2": area,
        "large_system_continuous_field_t": None,
        "fusion_source_specific_power_w_kg": None,
        "rcs_exhaust_velocity_m_s": None,
        "e2_momentum_partner": None,
        "metric_constitutive_law": None,
        "holds": tuple(holds),
    }
