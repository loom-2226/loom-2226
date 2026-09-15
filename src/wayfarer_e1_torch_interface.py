"""Wayfarer E1 primary-torch interface contract.

ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION.

This module exposes only earned vehicle/card behavior. Physical closure quantities that
remain unresolved are explicit Optional fields with no defaults beyond None. Direct
kinetic jet power is not electrical load and is not automatically vehicle waste heat.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional

from src.wayfarer_torch_mode_cards import (
    MODE_CARDS,
    NORMAL_REMASS_KG,
    PROTECTED_WATER_KG,
    mode_outputs,
)


class E1TorchState(str, Enum):
    OFF = "OFF"
    SAFE = "SAFE"
    ACTIVE = "ACTIVE"


@dataclass(frozen=True)
class OpenPhysicalClosure:
    """Component-closure inputs intentionally unavailable to the E1 card interface."""

    source_directed_fraction: Optional[Fraction] = None
    fusion_gain_q: Optional[Fraction] = None
    source_specific_power_w_per_kg: Optional[Fraction] = None
    neutron_deposition_fraction: Optional[Fraction] = None
    photon_deposition_fraction: Optional[Fraction] = None
    intercepted_particle_fraction: Optional[Fraction] = None
    nozzle_efficiency: Optional[Fraction] = None
    remass_species: Optional[str] = None
    feed_hardware: Optional[str] = None


@dataclass(frozen=True)
class E1TorchInterfaceResult:
    mode: Optional[str]
    torch_state: E1TorchState
    vehicle_mass_kg: Fraction
    normal_remass_kg: Fraction
    protected_water_kg: Fraction
    mdot_kg_s: Fraction
    exhaust_velocity_m_s: Fraction
    thrust_n: Fraction
    direct_kinetic_jet_power_w: Fraction
    acceleration_m_s2: Fraction
    physical_closure: OpenPhysicalClosure


def _validate_inventory(normal_remass_kg: Fraction, protected_water_kg: Fraction) -> None:
    if normal_remass_kg < 0 or normal_remass_kg > NORMAL_REMASS_KG:
        raise ValueError("normal remass must remain within the earned 0..250 t allowance")
    if protected_water_kg != PROTECTED_WATER_KG:
        raise ValueError("protected water is a protected 50 t reserve, not normal remass")


def evaluate_torch_interface(
    *,
    mode: Optional[str],
    vehicle_mass_kg: Fraction,
    normal_remass_kg: Fraction,
    protected_water_kg: Fraction,
    torch_state: E1TorchState,
    high_metric_active: bool,
    physical_closure: Optional[OpenPhysicalClosure] = None,
) -> E1TorchInterfaceResult:
    """Evaluate the earned E1 torch card interface without closing reactor/nozzle physics."""
    vehicle_mass_kg = Fraction(vehicle_mass_kg)
    normal_remass_kg = Fraction(normal_remass_kg)
    protected_water_kg = Fraction(protected_water_kg)
    _validate_inventory(normal_remass_kg, protected_water_kg)

    if vehicle_mass_kg <= 0:
        raise ValueError("vehicle mass must be positive")
    if torch_state is E1TorchState.ACTIVE and high_metric_active:
        raise ValueError("active torch and high-metric operation are mutually exclusive")

    closure = physical_closure if physical_closure is not None else OpenPhysicalClosure()

    if torch_state is not E1TorchState.ACTIVE:
        if mode is not None:
            raise ValueError("a performance mode may only be selected while the torch is ACTIVE")
        zero = Fraction(0)
        return E1TorchInterfaceResult(
            mode=None,
            torch_state=torch_state,
            vehicle_mass_kg=vehicle_mass_kg,
            normal_remass_kg=normal_remass_kg,
            protected_water_kg=protected_water_kg,
            mdot_kg_s=zero,
            exhaust_velocity_m_s=zero,
            thrust_n=zero,
            direct_kinetic_jet_power_w=zero,
            acceleration_m_s2=zero,
            physical_closure=closure,
        )

    if mode not in MODE_CARDS:
        raise ValueError(f"unknown E1 torch mode: {mode!r}")
    if normal_remass_kg <= 0:
        raise ValueError("active torch requires positive normal remass; protected water is unavailable")

    mdot, ve, thrust, jet_power = mode_outputs(mode)
    return E1TorchInterfaceResult(
        mode=mode,
        torch_state=torch_state,
        vehicle_mass_kg=vehicle_mass_kg,
        normal_remass_kg=normal_remass_kg,
        protected_water_kg=protected_water_kg,
        mdot_kg_s=mdot,
        exhaust_velocity_m_s=ve,
        thrust_n=thrust,
        direct_kinetic_jet_power_w=jet_power,
        acceleration_m_s2=thrust / vehicle_mass_kg,
        physical_closure=closure,
    )
