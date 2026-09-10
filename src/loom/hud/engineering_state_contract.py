from __future__ import annotations

"""Typed HUD-facing view of the pinned Wayfarer engineering handoff.

This adapter deliberately does not create engineering authority. It converts the
verified PR #96 handoff into the existing HUD StateDatum vocabulary so downstream
presentation can consume value/unit/source/authority/availability/status without
re-reading raw engineering JSON or embedding constants in UI code.
"""

from dataclasses import dataclass
from typing import Mapping

from loom.hud.contracts import AuthorityClass, Availability, StateDatum
from loom.hud.wayfarer_engineering_state import (
    ENGINEERING_SOURCE_COMMIT,
    load_wayfarer_engineering_state,
)

CONTRACT = "LOOM_HUD_WAYFARER_ENGINEERING_TYPED_STATE_V1"
FRAME = "WAYFARER_ENGINEERING"


@dataclass(frozen=True)
class TorchModeHudState:
    acceleration_g: StateDatum[float]
    exhaust_velocity: StateDatum[float]
    status: StateDatum[str]
    authorization: StateDatum[str]


@dataclass(frozen=True)
class WayfarerEngineeringHudState:
    contract: str
    epoch: str
    source_commit: str
    reference_wet_mass: StateDatum[float]
    dry_mass: StateDatum[float]
    normal_remass: StateDatum[float]
    protected_water_reserve: StateDatum[float]
    normal_dispatch_remass: StateDatum[float]
    operational_remass_floor: StateDatum[float]
    protected_optimizer_reserve: StateDatum[float]
    routine_optimizer_may_consume_protected_water: StateDatum[bool]
    attitude_status: StateDatum[str]
    power_thermal_status: StateDatum[str]
    radiator_effective_area_range: StateDatum[tuple[float, float]]
    thermal_buffer_range: StateDatum[tuple[float, float]]
    torch_coupled_heat_ceiling: StateDatum[float]
    dispatch_status: StateDatum[str]
    feedstock_primary: StateDatum[str]
    feedstock_certified_species: StateDatum[tuple[str, ...]]
    torch_jet_power_is_electrical_bus_power: StateDatum[bool]
    metric_velocity_reset_allowed: StateDatum[bool]
    torch_modes: Mapping[str, TorchModeHudState]


def _datum(
    value,
    *,
    unit: str | None,
    epoch: str,
    source_path: str,
    quality: str,
    derivation: str = "pinned PR #96 engineering handoff adapter",
):
    return StateDatum(
        value=value,
        unit=unit,
        epoch=epoch,
        frame=FRAME,
        source=f"PR96:{ENGINEERING_SOURCE_COMMIT}:{source_path}",
        authority=AuthorityClass.QUALIFICATION_ONLY,
        derivation=derivation,
        freshness_seconds=None,
        availability=Availability.AVAILABLE,
        quality=quality,
    )


def build_wayfarer_engineering_hud_state(*, epoch: str) -> WayfarerEngineeringHudState:
    engineering = load_wayfarer_engineering_state()
    mass = engineering["mass"]
    dispatch = engineering["dispatch"]
    attitude = engineering["attitude"]
    thermal = engineering["power_thermal"]
    feedstock = engineering["feedstock"]
    torch = engineering["torch"]
    firewall = engineering["mobility_firewall"]

    radiator_areas = tuple(float(x) for x in thermal["radiator"]["candidate_effective_area_m2"])
    buffer_values = tuple(float(x) for x in thermal["thermal_buffer"]["usable_energy_GJ_screening"])

    torch_modes: dict[str, TorchModeHudState] = {}
    for mode, card in torch["mode_cards"].items():
        card_quality = str(card["status"])
        torch_modes[str(mode)] = TorchModeHudState(
            acceleration_g=_datum(
                float(card["acceleration_g"]), unit="g", epoch=epoch,
                source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.acceleration_g",
                quality=card_quality,
            ),
            exhaust_velocity=_datum(
                float(card["exhaust_velocity_km_s"]), unit="km/s", epoch=epoch,
                source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.exhaust_velocity_km_s",
                quality=card_quality,
            ),
            status=_datum(
                card_quality, unit=None, epoch=epoch,
                source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.status",
                quality=card_quality,
            ),
            authorization=_datum(
                str(dispatch["torch_mode_authorization"][mode]), unit=None, epoch=epoch,
                source_path=f"dispatch.torch_mode_authorization.{mode}",
                quality=str(dispatch["status"]),
            ),
        )

    return WayfarerEngineeringHudState(
        contract=CONTRACT,
        epoch=epoch,
        source_commit=ENGINEERING_SOURCE_COMMIT,
        reference_wet_mass=_datum(
            float(mass["reference_wet_mass_t"]), unit="t", epoch=epoch,
            source_path="baseline.mass_states.reference_wet_mass_t",
            quality=str(mass["status"]),
        ),
        dry_mass=_datum(
            float(mass["dry_mass_t"]), unit="t", epoch=epoch,
            source_path="baseline.mass_states.dry_mass_t",
            quality=str(mass["status"]),
        ),
        normal_remass=_datum(
            float(mass["normal_remass_allowance_t"]), unit="t", epoch=epoch,
            source_path="baseline.mass_states.normal_remass_allowance_t",
            quality=str(mass["status"]),
        ),
        protected_water_reserve=_datum(
            float(mass["protected_water_reserve_t"]), unit="t", epoch=epoch,
            source_path="baseline.mass_states.protected_water_reserve_t",
            quality="PROTECTED_NOT_ROUTINE_PROPULSION",
        ),
        normal_dispatch_remass=_datum(
            float(dispatch["normal_dispatch_remass_t"]), unit="t", epoch=epoch,
            source_path="dispatch.working_policy.normal_dispatch_remass_t",
            quality=str(dispatch["status"]),
        ),
        operational_remass_floor=_datum(
            float(dispatch["minimum_dispatch_remass_t"]), unit="t", epoch=epoch,
            source_path="dispatch.working_policy.minimum_dispatch_remass_t",
            quality=str(dispatch["status"]),
        ),
        protected_optimizer_reserve=_datum(
            float(dispatch["protected_optimizer_reserve_t"]), unit="t", epoch=epoch,
            source_path="dispatch.working_policy.protected_optimizer_reserve_t",
            quality=str(dispatch["status"]),
        ),
        routine_optimizer_may_consume_protected_water=_datum(
            bool(dispatch["routine_optimizer_may_consume_protected_water"]), unit=None, epoch=epoch,
            source_path="dispatch.routine_optimizer_may_consume_protected_water",
            quality="HARD_FIREWALL",
        ),
        attitude_status=_datum(
            str(attitude["status"]), unit=None, epoch=epoch,
            source_path="q4_hud_attitude.status",
            quality=str(attitude["status"]),
        ),
        power_thermal_status=_datum(
            str(thermal["qualification_status"]), unit=None, epoch=epoch,
            source_path="q5_power_thermal.qualification_status",
            quality=str(thermal["status"]),
        ),
        radiator_effective_area_range=_datum(
            (min(radiator_areas), max(radiator_areas)), unit="m^2", epoch=epoch,
            source_path="q5_power_thermal.radiator.candidate_effective_area_m2",
            quality=str(thermal["radiator"]["physical_geometry_status"]),
        ),
        thermal_buffer_range=_datum(
            (min(buffer_values), max(buffer_values)), unit="GJ", epoch=epoch,
            source_path="q5_power_thermal.thermal_buffer.usable_energy_GJ_screening",
            quality=str(thermal["thermal_buffer"]["medium_status"]),
        ),
        torch_coupled_heat_ceiling=_datum(
            float(thermal["torch"]["normal_ship_coupled_heat_ceiling_MW"]), unit="MW", epoch=epoch,
            source_path="q5_power_thermal.torch.normal_ship_coupled_heat_ceiling_MW",
            quality=str(thermal["qualification_status"]),
        ),
        dispatch_status=_datum(
            str(dispatch["status"]), unit=None, epoch=epoch,
            source_path="q7_dispatch.status",
            quality=str(dispatch["status"]),
        ),
        feedstock_primary=_datum(
            str(feedstock["primary_candidate"]), unit=None, epoch=epoch,
            source_path="q2_feedstock.provisional_doctrine.primary",
            quality="PRIMARY_CANDIDATE_NOT_CERTIFIED",
        ),
        feedstock_certified_species=_datum(
            tuple(str(x) for x in feedstock["certified_species"]), unit=None, epoch=epoch,
            source_path="q2_feedstock.certified_species",
            quality="CERTIFIED_NONE" if not feedstock["certified_species"] else "CERTIFIED_SET",
        ),
        torch_jet_power_is_electrical_bus_power=_datum(
            bool(torch["jet_power_is_electrical_bus_power"]), unit=None, epoch=epoch,
            source_path="baseline.power_thermal.torch_jet_power_is_electrical_bus_power",
            quality="HARD_FIREWALL",
        ),
        metric_velocity_reset_allowed=_datum(
            bool(firewall["metric_ordinary_velocity_reset_allowed"]), unit=None, epoch=epoch,
            source_path="baseline.mobility_regimes.metric.ordinary_velocity_reset_allowed",
            quality="HARD_FIREWALL",
        ),
        torch_modes=torch_modes,
    )
