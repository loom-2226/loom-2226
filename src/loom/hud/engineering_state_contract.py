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
class AttitudeEnergyCandidateHudState:
    exhaust_velocity: StateDatum[float]
    jet_power: StateDatum[float]
    jet_energy: StateDatum[float]
    equivalent_expelled_mass: StateDatum[float]
    waste_heat_power: StateDatum[float]
    waste_heat_energy: StateDatum[float]
    heat_fraction_of_50GJ_buffer: StateDatum[float]
    radiator_transient_credit_applied: StateDatum[bool]


@dataclass(frozen=True)
class AttitudeEnergyManeuverHudState:
    control_case: StateDatum[str]
    maneuver: StateDatum[str]
    axis: StateDatum[str]
    angle_deg: StateDatum[int]
    qualified_transition_time: StateDatum[float]
    powered_rcs_time: StateDatum[float]
    settle_margin_time: StateDatum[float]
    worst_failed_cluster: StateDatum[str | None]
    total_resultant_mount_thrust: StateDatum[float]
    max_physical_mount_utilization: StateDatum[float]
    candidates: Mapping[str, AttitudeEnergyCandidateHudState]


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
    attitude_energy_status: StateDatum[str]
    attitude_energy_buffer_screen_pass: StateDatum[bool]
    attitude_energy_detail_available: StateDatum[bool]
    attitude_energy_max_jet_energy: StateDatum[float]
    attitude_energy_max_waste_heat_energy: StateDatum[float]
    attitude_energy_max_equivalent_expelled_mass: StateDatum[float]
    combined_maneuver_energy_available: StateDatum[bool]
    translation_maneuver_energy_available: StateDatum[bool]
    attitude_energy_maneuvers: Mapping[str, AttitudeEnergyManeuverHudState]
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


def _optional_datum(
    value,
    *,
    unit: str | None,
    epoch: str,
    source_path: str,
    quality: str,
    unavailable_quality: str,
    derivation: str = "pinned PR #96 engineering handoff adapter",
):
    if value is not None:
        return _datum(
            value,
            unit=unit,
            epoch=epoch,
            source_path=source_path,
            quality=quality,
            derivation=derivation,
        )
    return StateDatum(
        value=None,
        unit=unit,
        epoch=epoch,
        frame=FRAME,
        source=f"PR96:{ENGINEERING_SOURCE_COMMIT}:{source_path}",
        authority=AuthorityClass.UNAVAILABLE,
        derivation=derivation,
        freshness_seconds=None,
        availability=Availability.UNAVAILABLE,
        quality=unavailable_quality,
    )


def _attitude_energy_maneuvers(attitude_energy: dict, *, epoch: str) -> dict[str, AttitudeEnergyManeuverHudState]:
    result: dict[str, AttitudeEnergyManeuverHudState] = {}
    quality = str(attitude_energy["status"])
    for index, row in enumerate(attitude_energy["maneuvers"]):
        key = f'{row["control_case"]}:{row["maneuver"]}'
        base = f"q5_attitude_energy.maneuvers.{index}"
        candidates: dict[str, AttitudeEnergyCandidateHudState] = {}
        for candidate_name, screen in row["candidates"].items():
            source = f"{base}.candidates.{candidate_name}"
            candidates[str(candidate_name)] = AttitudeEnergyCandidateHudState(
                exhaust_velocity=_datum(float(screen["exhaust_velocity_km_s"]), unit="km/s", epoch=epoch, source_path=f"{source}.exhaust_velocity_km_s", quality="CANDIDATE_SCREEN_ONLY"),
                jet_power=_datum(float(screen["jet_power_GW"]), unit="GW", epoch=epoch, source_path=f"{source}.jet_power_GW", quality=quality),
                jet_energy=_datum(float(screen["jet_energy_GJ"]), unit="GJ", epoch=epoch, source_path=f"{source}.jet_energy_GJ", quality=quality),
                equivalent_expelled_mass=_datum(float(screen["equivalent_expelled_mass_kg"]), unit="kg", epoch=epoch, source_path=f"{source}.equivalent_expelled_mass_kg", quality="EQUIVALENT_MASS_CANDIDATE_VE"),
                waste_heat_power=_datum(float(screen["worst_conversion_waste_heat_power_MW"]), unit="MW", epoch=epoch, source_path=f"{source}.worst_conversion_waste_heat_power_MW", quality="WORST_SCREENED_CONVERSION_EFFICIENCY"),
                waste_heat_energy=_datum(float(screen["worst_conversion_waste_heat_energy_GJ"]), unit="GJ", epoch=epoch, source_path=f"{source}.worst_conversion_waste_heat_energy_GJ", quality="WORST_SCREENED_CONVERSION_EFFICIENCY"),
                heat_fraction_of_50GJ_buffer=_datum(float(screen["worst_heat_fraction_of_50GJ_buffer"]), unit="fraction", epoch=epoch, source_path=f"{source}.worst_heat_fraction_of_50GJ_buffer", quality="NO_RADIATOR_TRANSIENT_CREDIT"),
                radiator_transient_credit_applied=_datum(bool(screen["radiator_transient_credit_applied"]), unit=None, epoch=epoch, source_path=f"{source}.radiator_transient_credit_applied", quality="HARD_BOUNDARY"),
            )
        result[key] = AttitudeEnergyManeuverHudState(
            control_case=_datum(str(row["control_case"]), unit=None, epoch=epoch, source_path=f"{base}.control_case", quality=quality),
            maneuver=_datum(str(row["maneuver"]), unit=None, epoch=epoch, source_path=f"{base}.maneuver", quality=quality),
            axis=_datum(str(row["axis"]), unit=None, epoch=epoch, source_path=f"{base}.axis", quality=quality),
            angle_deg=_datum(int(row["angle_deg"]), unit="deg", epoch=epoch, source_path=f"{base}.angle_deg", quality=quality),
            qualified_transition_time=_datum(float(row["qualified_transition_time_s"]), unit="s", epoch=epoch, source_path=f"{base}.qualified_transition_time_s", quality="Q4_QUALIFIED_TIMING"),
            powered_rcs_time=_datum(float(row["powered_rcs_time_s"]), unit="s", epoch=epoch, source_path=f"{base}.powered_rcs_time_s", quality="DERIVED_FROM_Q4_SETTLE_MODEL"),
            settle_margin_time=_datum(float(row["settle_margin_time_s"]), unit="s", epoch=epoch, source_path=f"{base}.settle_margin_time_s", quality="Q4_SETTLE_MARGIN"),
            worst_failed_cluster=_optional_datum(
                row["worst_failed_cluster"],
                unit=None,
                epoch=epoch,
                source_path=f"{base}.worst_failed_cluster",
                quality="WORST_SCREENED_Q4_ALLOCATION_CASE",
                unavailable_quality="NOT_APPLICABLE_NOMINAL_CONTROL_CASE",
            ),
            total_resultant_mount_thrust=_datum(float(row["total_resultant_mount_thrust_kN"]), unit="kN", epoch=epoch, source_path=f"{base}.total_resultant_mount_thrust_kN", quality="PHYSICAL_RESULTANT_MOUNT_THRUST"),
            max_physical_mount_utilization=_datum(float(row["max_physical_mount_utilization_fraction"]), unit="fraction", epoch=epoch, source_path=f"{base}.max_physical_mount_utilization_fraction", quality="Q4_BOUNDED_ALLOCATION_SCREEN"),
            candidates=candidates,
        )
    return result


def build_wayfarer_engineering_hud_state(*, epoch: str) -> WayfarerEngineeringHudState:
    engineering = load_wayfarer_engineering_state()
    mass = engineering["mass"]
    dispatch = engineering["dispatch"]
    attitude = engineering["attitude"]
    attitude_energy = engineering["attitude_energy"]
    thermal = engineering["power_thermal"]
    feedstock = engineering["feedstock"]
    torch = engineering["torch"]
    firewall = engineering["mobility_firewall"]

    radiator_areas = tuple(float(x) for x in thermal["radiator"]["candidate_effective_area_m2"])
    buffer_values = tuple(float(x) for x in thermal["thermal_buffer"]["usable_energy_GJ_screening"])
    energy_summary = attitude_energy["summary"]

    torch_modes: dict[str, TorchModeHudState] = {}
    for mode, card in torch["mode_cards"].items():
        card_quality = str(card["status"])
        torch_modes[str(mode)] = TorchModeHudState(
            acceleration_g=_datum(float(card["acceleration_g"]), unit="g", epoch=epoch, source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.acceleration_g", quality=card_quality),
            exhaust_velocity=_datum(float(card["exhaust_velocity_km_s"]), unit="km/s", epoch=epoch, source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.exhaust_velocity_km_s", quality=card_quality),
            status=_datum(card_quality, unit=None, epoch=epoch, source_path=f"baseline.mobility_regimes.torch.mode_cards.{mode}.status", quality=card_quality),
            authorization=_datum(str(dispatch["torch_mode_authorization"][mode]), unit=None, epoch=epoch, source_path=f"dispatch.torch_mode_authorization.{mode}", quality=str(dispatch["status"])),
        )

    return WayfarerEngineeringHudState(
        contract=CONTRACT,
        epoch=epoch,
        source_commit=ENGINEERING_SOURCE_COMMIT,
        reference_wet_mass=_datum(float(mass["reference_wet_mass_t"]), unit="t", epoch=epoch, source_path="baseline.mass_states.reference_wet_mass_t", quality=str(mass["status"])),
        dry_mass=_datum(float(mass["dry_mass_t"]), unit="t", epoch=epoch, source_path="baseline.mass_states.dry_mass_t", quality=str(mass["status"])),
        normal_remass=_datum(float(mass["normal_remass_allowance_t"]), unit="t", epoch=epoch, source_path="baseline.mass_states.normal_remass_allowance_t", quality=str(mass["status"])),
        protected_water_reserve=_datum(float(mass["protected_water_reserve_t"]), unit="t", epoch=epoch, source_path="baseline.mass_states.protected_water_reserve_t", quality="PROTECTED_NOT_ROUTINE_PROPULSION"),
        normal_dispatch_remass=_datum(float(dispatch["normal_dispatch_remass_t"]), unit="t", epoch=epoch, source_path="dispatch.working_policy.normal_dispatch_remass_t", quality=str(dispatch["status"])),
        operational_remass_floor=_datum(float(dispatch["minimum_dispatch_remass_t"]), unit="t", epoch=epoch, source_path="dispatch.working_policy.minimum_dispatch_remass_t", quality=str(dispatch["status"])),
        protected_optimizer_reserve=_datum(float(dispatch["protected_optimizer_reserve_t"]), unit="t", epoch=epoch, source_path="dispatch.working_policy.protected_optimizer_reserve_t", quality=str(dispatch["status"])),
        routine_optimizer_may_consume_protected_water=_datum(bool(dispatch["routine_optimizer_may_consume_protected_water"]), unit=None, epoch=epoch, source_path="dispatch.routine_optimizer_may_consume_protected_water", quality="HARD_FIREWALL"),
        attitude_status=_datum(str(attitude["status"]), unit=None, epoch=epoch, source_path="q4_hud_attitude.status", quality=str(attitude["status"])),
        attitude_energy_status=_datum(str(attitude_energy["qualification_status"]), unit=None, epoch=epoch, source_path="q5_attitude_energy.qualification_status", quality=str(attitude_energy["status"])),
        attitude_energy_buffer_screen_pass=_datum(bool(energy_summary["all_checked_gross_conversion_heat_within_50GJ_buffer_screen"]), unit=None, epoch=epoch, source_path="q5_attitude_energy.summary.all_checked_gross_conversion_heat_within_50GJ_buffer_screen", quality="CHECKED_REFERENCE_WET_DOCKED_PURE_ATTITUDE_SET"),
        attitude_energy_detail_available=_datum(bool(attitude_energy["machine_readable_per_maneuver_detail_available"]), unit=None, epoch=epoch, source_path="q5_attitude_energy.machine_readable_per_maneuver_detail_available", quality=str(attitude_energy["detail_availability_reason"])),
        attitude_energy_max_jet_energy=_datum(float(energy_summary["max_checked_jet_energy_GJ"]), unit="GJ", epoch=epoch, source_path="q5_attitude_energy.summary.max_checked_jet_energy_GJ", quality="CHECKED_SET_MAXIMUM"),
        attitude_energy_max_waste_heat_energy=_datum(float(energy_summary["max_gross_conversion_waste_heat_energy_GJ"]), unit="GJ", epoch=epoch, source_path="q5_attitude_energy.summary.max_gross_conversion_waste_heat_energy_GJ", quality="CHECKED_SET_MAXIMUM_NO_RADIATOR_CREDIT"),
        attitude_energy_max_equivalent_expelled_mass=_datum(float(energy_summary["max_equivalent_expelled_mass_kg"]), unit="kg", epoch=epoch, source_path="q5_attitude_energy.summary.max_equivalent_expelled_mass_kg", quality="CHECKED_SET_MAXIMUM_CANDIDATE_VE"),
        combined_maneuver_energy_available=_datum(False, unit=None, epoch=epoch, source_path="q5_attitude_energy.unavailable.combined_maneuver_energy", quality=str(attitude_energy["combined_maneuver_duration"]), derivation="energy unavailable because duration remains unearned"),
        translation_maneuver_energy_available=_datum(False, unit=None, epoch=epoch, source_path="q5_attitude_energy.unavailable.translation_maneuver_energy", quality=str(attitude_energy["translation_maneuver_duration"]), derivation="energy unavailable because duration remains unearned"),
        attitude_energy_maneuvers=_attitude_energy_maneuvers(attitude_energy, epoch=epoch),
        power_thermal_status=_datum(str(thermal["qualification_status"]), unit=None, epoch=epoch, source_path="q5_power_thermal.qualification_status", quality=str(thermal["status"])),
        radiator_effective_area_range=_datum((min(radiator_areas), max(radiator_areas)), unit="m^2", epoch=epoch, source_path="q5_power_thermal.radiator.candidate_effective_area_m2", quality=str(thermal["radiator"]["physical_geometry_status"])),
        thermal_buffer_range=_datum((min(buffer_values), max(buffer_values)), unit="GJ", epoch=epoch, source_path="q5_power_thermal.thermal_buffer.usable_energy_GJ_screening", quality=str(thermal["thermal_buffer"]["medium_status"])),
        torch_coupled_heat_ceiling=_datum(float(thermal["torch"]["normal_ship_coupled_heat_ceiling_MW"]), unit="MW", epoch=epoch, source_path="q5_power_thermal.torch.normal_ship_coupled_heat_ceiling_MW", quality=str(thermal["qualification_status"])),
        dispatch_status=_datum(str(dispatch["status"]), unit=None, epoch=epoch, source_path="q7_dispatch.status", quality=str(dispatch["status"])),
        feedstock_primary=_datum(str(feedstock["primary_candidate"]), unit=None, epoch=epoch, source_path="q2_feedstock.provisional_doctrine.primary", quality="PRIMARY_CANDIDATE_NOT_CERTIFIED"),
        feedstock_certified_species=_datum(tuple(str(x) for x in feedstock["certified_species"]), unit=None, epoch=epoch, source_path="q2_feedstock.certified_species", quality="CERTIFIED_NONE" if not feedstock["certified_species"] else "CERTIFIED_SET"),
        torch_jet_power_is_electrical_bus_power=_datum(bool(torch["jet_power_is_electrical_bus_power"]), unit=None, epoch=epoch, source_path="baseline.power_thermal.torch_jet_power_is_electrical_bus_power", quality="HARD_FIREWALL"),
        metric_velocity_reset_allowed=_datum(bool(firewall["metric_ordinary_velocity_reset_allowed"]), unit=None, epoch=epoch, source_path="baseline.mobility_regimes.metric.ordinary_velocity_reset_allowed", quality="HARD_FIREWALL"),
        torch_modes=torch_modes,
    )
