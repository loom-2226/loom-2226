"""Wayfarer E1 torch remass/feed/nozzle closure envelope.

ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION.

T3 consolidates already-earned remass inventory and mode-card flow requirements into
one E1-facing interface. Working-fluid identity, feed hardware, response/pressure and
nozzle efficiency remain explicit technology holds unless supplied for sensitivity.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Tuple

from src.wayfarer_torch_mode_cards import MODE_CARDS, NORMAL_REMASS_KG, PROTECTED_WATER_KG


@dataclass(frozen=True)
class TorchRemassFeedNozzleResult:
    normal_remass_kg: Fraction
    protected_water_kg: Fraction
    mode_flow_velocity: Tuple[Tuple[str, Fraction, Fraction], ...]
    min_mass_flow_kg_s: Fraction
    max_mass_flow_kg_s: Fraction
    turndown_ratio: Fraction
    remass_species: Optional[str]
    feed_hardware: Optional[str]
    feed_response_time_s: Optional[Fraction]
    feed_pressure_pa: Optional[Fraction]
    nozzle_efficiency: Optional[Fraction]
    hardware_certified: bool
    status: str
    holds: Tuple[str, ...]


def _optional_text(name: str, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty explicit string")
    return value


def remass_feed_nozzle_envelope(
    *,
    remass_species: Optional[str] = None,
    feed_hardware: Optional[str] = None,
    feed_response_time_s: Optional[Fraction] = None,
    feed_pressure_pa: Optional[Fraction] = None,
    nozzle_efficiency: Optional[Fraction] = None,
) -> TorchRemassFeedNozzleResult:
    """Return the bounded T3 E1 interface without selecting unknown technology."""
    remass_species = _optional_text("remass species", remass_species)
    feed_hardware = _optional_text("feed hardware", feed_hardware)

    if feed_response_time_s is not None:
        feed_response_time_s = Fraction(feed_response_time_s)
        if feed_response_time_s < 0:
            raise ValueError("feed response time must be non-negative")
    if feed_pressure_pa is not None:
        feed_pressure_pa = Fraction(feed_pressure_pa)
        if feed_pressure_pa <= 0:
            raise ValueError("feed pressure must be positive")
    if nozzle_efficiency is not None:
        nozzle_efficiency = Fraction(nozzle_efficiency)
        if nozzle_efficiency <= 0 or nozzle_efficiency > 1:
            raise ValueError("nozzle efficiency must be in (0, 1]")

    mode_flow_velocity = tuple((name, values[0], values[1]) for name, values in MODE_CARDS.items())
    flows = tuple(values[0] for values in MODE_CARDS.values())
    lo = min(flows)
    hi = max(flows)

    holds = ["PROTECTED_WATER_NOT_NORMAL_REMASS"]
    if remass_species is None:
        holds.append("REMASS_SPECIES_OPEN")
    if feed_hardware is None:
        holds.append("FEED_HARDWARE_OPEN")
    if feed_response_time_s is None:
        holds.append("FEED_RESPONSE_AND_MODE_TRANSITION_TIME_OPEN")
    if feed_pressure_pa is None:
        holds.append("FEED_PRESSURE_AND_PHASE_STABILITY_OPEN")
    if nozzle_efficiency is None:
        holds.append("NOZZLE_EFFICIENCY_OPEN")
    holds.extend((
        "STORAGE_PHASE_DENSITY_TANKAGE_AND_COM_MIGRATION_OPEN",
        "THERMAL_CONDITIONING_AND_IONIZATION_OPEN",
        "VALVE_PUMP_OR_INJECTOR_DYNAMIC_RANGE_AND_LIFETIME_OPEN",
        "FAULT_ISOLATION_AND_SAFE_SHUTDOWN_OPEN",
        "SPECIES_DEPENDENT_ENERGY_TRANSFER_OPEN",
        "MAGNETIZATION_AND_GYRADIUS_OPEN",
        "PLASMA_DETACHMENT_OPEN",
        "DIVERGENCE_OPEN",
        "WALL_OR_COIL_INTERCEPTION_OPEN",
        "EROSION_CONTAMINATION_AND_LIFETIME_OPEN",
    ))

    explicit_candidate = any(
        value is not None
        for value in (remass_species, feed_hardware, feed_response_time_s, feed_pressure_pa, nozzle_efficiency)
    )
    status = "SENSITIVITY_ONLY_EXPLICIT_INPUTS" if explicit_candidate else "E1_REQUIREMENT_ENVELOPE_WITH_TECHNOLOGY_HOLDS"

    return TorchRemassFeedNozzleResult(
        normal_remass_kg=NORMAL_REMASS_KG,
        protected_water_kg=PROTECTED_WATER_KG,
        mode_flow_velocity=mode_flow_velocity,
        min_mass_flow_kg_s=lo,
        max_mass_flow_kg_s=hi,
        turndown_ratio=hi / lo,
        remass_species=remass_species,
        feed_hardware=feed_hardware,
        feed_response_time_s=feed_response_time_s,
        feed_pressure_pa=feed_pressure_pa,
        nozzle_efficiency=nozzle_efficiency,
        hardware_certified=False,
        status=status,
        holds=tuple(holds),
    )
