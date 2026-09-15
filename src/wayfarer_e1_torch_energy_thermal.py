"""Wayfarer E1 torch source/energy/thermal hold envelope.

ENGINEERING INTERFACE / NON-CANON / NON-HARDWARE-CERTIFICATION.

Radiator area is only computed when a vehicle heat load and radiator emissivity are
explicitly supplied. No archived torch deposition ppm, historical radiator area,
source directed fraction, Q, specific power, or emissivity is silently promoted.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Tuple

from src.wayfarer_torch_mode_cards import MODE_CARDS, mode_outputs

# Current authority from the E1 primary-propulsion thermal interface.
HIGH_DRIVE_REJECT_INTERFACE_K = Fraction(900)
RADIATOR_COUNT = 4

# Exact decimal representation of the SI Stefan-Boltzmann constant since the 2019 SI.
STEFAN_BOLTZMANN_W_M2_K4 = Fraction(5670374419, 100_000_000_000_000_000)


@dataclass(frozen=True)
class TorchEnergyThermalResult:
    mode: str
    direct_kinetic_jet_power_w: Fraction
    source_directed_fraction: Optional[Fraction]
    source_output_w: Optional[Fraction]
    fusion_gain_q: Optional[Fraction]
    external_driver_power_w: Optional[Fraction]
    source_specific_power_w_per_kg: Optional[Fraction]
    source_mass_kg: Optional[Fraction]
    vehicle_deposition_fraction: Optional[Fraction]
    vehicle_deposition_w: Optional[Fraction]
    radiator_temperature_k: Fraction
    radiator_emissivity: Optional[Fraction]
    required_radiator_area_m2: Optional[Fraction]
    required_area_per_radiator_m2: Optional[Fraction]
    holds: Tuple[str, ...]


def _unit_fraction(name: str, value: Optional[Fraction], *, positive=False) -> Optional[Fraction]:
    if value is None:
        return None
    value = Fraction(value)
    if positive:
        if value <= 0 or value > 1:
            raise ValueError(f"{name} must be in (0, 1]")
    elif value < 0 or value > 1:
        raise ValueError(f"{name} must be in [0, 1]")
    return value


def radiator_area_m2(*, heat_rejection_w: Fraction, temperature_k: Fraction, emissivity: Fraction) -> Fraction:
    """Ideal emitting area from P = epsilon sigma A T^4; geometry/view factors remain separate."""
    heat_rejection_w = Fraction(heat_rejection_w)
    temperature_k = Fraction(temperature_k)
    emissivity = Fraction(emissivity)
    if heat_rejection_w < 0:
        raise ValueError("heat rejection must be non-negative")
    if temperature_k <= 0:
        raise ValueError("radiator temperature must be positive")
    if emissivity <= 0 or emissivity > 1:
        raise ValueError("radiator emissivity must be in (0, 1]")
    return heat_rejection_w / (emissivity * STEFAN_BOLTZMANN_W_M2_K4 * temperature_k**4)


def source_thermal_envelope(
    *,
    mode: str,
    source_directed_fraction: Optional[Fraction] = None,
    fusion_gain_q: Optional[Fraction] = None,
    source_specific_power_w_per_kg: Optional[Fraction] = None,
    vehicle_deposition_fraction: Optional[Fraction] = None,
    radiator_emissivity: Optional[Fraction] = None,
    radiator_temperature_k: Fraction = HIGH_DRIVE_REJECT_INTERFACE_K,
) -> TorchEnergyThermalResult:
    if mode not in MODE_CARDS:
        raise ValueError(f"unknown E1 torch mode: {mode!r}")

    source_directed_fraction = _unit_fraction("source directed fraction", source_directed_fraction, positive=True)
    vehicle_deposition_fraction = _unit_fraction("vehicle deposition fraction", vehicle_deposition_fraction)
    radiator_emissivity = _unit_fraction("radiator emissivity", radiator_emissivity, positive=True)
    radiator_temperature_k = Fraction(radiator_temperature_k)
    if radiator_temperature_k <= 0:
        raise ValueError("radiator temperature must be positive")
    if fusion_gain_q is not None and Fraction(fusion_gain_q) <= 0:
        raise ValueError("fusion gain Q must be positive")
    if source_specific_power_w_per_kg is not None and Fraction(source_specific_power_w_per_kg) <= 0:
        raise ValueError("source specific power must be positive")

    _, _, _, jet_power = mode_outputs(mode)
    source_output = None if source_directed_fraction is None else jet_power / source_directed_fraction
    driver_power = None
    if source_output is not None and fusion_gain_q is not None:
        driver_power = source_output / Fraction(fusion_gain_q)
    source_mass = None
    if source_output is not None and source_specific_power_w_per_kg is not None:
        source_mass = source_output / Fraction(source_specific_power_w_per_kg)
    deposition_w = None
    if source_output is not None and vehicle_deposition_fraction is not None:
        deposition_w = source_output * vehicle_deposition_fraction

    area = None
    per_radiator = None
    if deposition_w is not None and radiator_emissivity is not None:
        area = radiator_area_m2(
            heat_rejection_w=deposition_w,
            temperature_k=radiator_temperature_k,
            emissivity=radiator_emissivity,
        )
        per_radiator = area / RADIATOR_COUNT

    holds = []
    if source_directed_fraction is None:
        holds.append("SOURCE_DIRECTED_FRACTION_OPEN")
    if fusion_gain_q is None:
        holds.append("FUSION_GAIN_Q_OPEN")
    if source_specific_power_w_per_kg is None:
        holds.append("SOURCE_SPECIFIC_POWER_OPEN")
    if vehicle_deposition_fraction is None:
        holds.append("VEHICLE_DEPOSITION_FRACTION_OPEN")
    if radiator_emissivity is None:
        holds.append("RADIATOR_EMISSIVITY_OPEN")
    holds.extend((
        "DEPOSITION_PARTITION_OPEN",
        "THERMAL_TRANSPORT_AND_PLUMBING_OPEN",
        "RADIATOR_GEOMETRY_VIEW_FACTOR_AND_CLEARANCE_OPEN",
        "TRANSIENT_BUFFER_CREDIT_OPEN",
    ))

    return TorchEnergyThermalResult(
        mode=mode,
        direct_kinetic_jet_power_w=jet_power,
        source_directed_fraction=source_directed_fraction,
        source_output_w=source_output,
        fusion_gain_q=None if fusion_gain_q is None else Fraction(fusion_gain_q),
        external_driver_power_w=driver_power,
        source_specific_power_w_per_kg=None if source_specific_power_w_per_kg is None else Fraction(source_specific_power_w_per_kg),
        source_mass_kg=source_mass,
        vehicle_deposition_fraction=vehicle_deposition_fraction,
        vehicle_deposition_w=deposition_w,
        radiator_temperature_k=radiator_temperature_k,
        radiator_emissivity=radiator_emissivity,
        required_radiator_area_m2=area,
        required_area_per_radiator_m2=per_radiator,
        holds=tuple(holds),
    )
