"""CIVPROP Power Balance V1.

Separates installed generation capacity, average generation, peak/average load,
annual electrical energy, firm capacity, reserve, and modeled storage.

The LOOM Technology Timeline is context and provenance only. Threshold years never
auto-create generation, availability, storage, or actor/site access.
"""
from __future__ import annotations

from dataclasses import dataclass
import calendar
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .demand_pressure_v1 import DemandPressurePackage


FORMAT = "CIVPROP_POWER_BALANCE_V1"
CONTRACT_VERSION = "1.0.0"
VALUE_STATUS = {"KNOWN", "UNKNOWN"}
ENERGY_STATUS = {"CLOSED", "UNKNOWN"}
FLOW_TYPES = {
    "GENERATION",
    "SERVED_LOAD",
    "UNSERVED_LOAD",
    "CURTAILMENT",
}


def _stable_id(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, separators=(",", ":"), allow_nan=False).encode()
    return f"{prefix}-" + hashlib.sha256(payload).hexdigest()[:20]


def _nonnegative(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return out


def _fraction(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or not 0 <= out <= 1:
        raise ValueError(f"{name} must be finite and in [0,1]")
    return out


def _refs(data: Mapping[str, Any], name: str) -> tuple[str, ...]:
    refs = tuple(str(x) for x in data.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name} requires provenance")
    return refs


@dataclass(frozen=True)
class ValueParameter:
    status: str
    value: Optional[float]
    unit: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class GenerationModel:
    project_archetype_id: str
    availability_factor: ValueParameter
    firm_capacity_fraction: ValueParameter
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class FacilityLoadModel:
    project_archetype_id: str
    peak_load_mw_per_facility: ValueParameter
    average_to_peak_factor: ValueParameter
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class TimelineContext:
    demonstrator_reference_id: str
    industrial_milestone_id: str
    industrial_threshold_year: int
    auto_unlock: bool
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class PowerBalancePackage:
    format: str
    contract_version: str
    package_id: str
    scope: str
    excluded_location_ids: tuple[str, ...]
    hours_basis: str
    population_peak_source: str
    population_average_to_peak_factor: ValueParameter
    initial_compatibility_generation: GenerationModel
    generation_models: tuple[GenerationModel, ...]
    facility_load_models: tuple[FacilityLoadModel, ...]
    reserve_margin_fraction: ValueParameter
    storage_model_status: str
    storage_power_capacity_mw: float
    storage_energy_capacity_mwh: float
    timeline_context: TimelineContext


@dataclass(frozen=True)
class PowerLoadComponentV1:
    component_id: str
    source_type: str
    source_id: str
    peak_load_status: str
    peak_load_mw: Optional[float]
    average_load_status: str
    average_load_mw: Optional[float]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class PowerGenerationComponentV1:
    component_id: str
    source_type: str
    source_id: str
    installed_capacity_mw: float
    availability_status: str
    availability_factor: Optional[float]
    average_generation_mw: Optional[float]
    firm_capacity_status: str
    firm_capacity_fraction: Optional[float]
    firm_generation_capacity_mw: Optional[float]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class PowerFlowV1:
    power_flow_id: str
    power_state_id: str
    year: int
    location_id: str
    flow_type: str
    amount_mwh: float


@dataclass(frozen=True)
class PowerStateV1:
    power_state_id: str
    year: int
    location_id: str
    interval_hours: int
    installed_generation_capacity_mw: float
    generation_components: tuple[PowerGenerationComponentV1, ...]
    average_generation_mw: Optional[float]
    firm_generation_capacity_mw: Optional[float]
    load_components: tuple[PowerLoadComponentV1, ...]
    population_peak_load_mw: float
    facility_peak_load_mw: Optional[float]
    peak_demand_mw: Optional[float]
    average_demand_mw: Optional[float]
    reserve_margin_status: str
    reserve_margin_fraction: Optional[float]
    required_firm_capacity_mw: Optional[float]
    reserve_adequacy_ratio: Optional[float]
    peak_service_ratio: Optional[float]
    storage_model_status: str
    storage_power_capacity_mw: float
    storage_energy_capacity_mwh: float
    demanded_energy_mwh: Optional[float]
    generated_energy_mwh: Optional[float]
    consumed_energy_mwh: Optional[float]
    unserved_energy_mwh: Optional[float]
    curtailed_energy_mwh: Optional[float]
    energy_service_ratio: Optional[float]
    power_service_ratio: Optional[float]
    energy_closure_residual_mwh: Optional[float]
    energy_balance_status: str
    atlas_power_average_mw: Optional[float]
    atlas_power_peak_mw: Optional[float]


def _value(
    raw: Mapping[str, Any],
    *,
    name: str,
    expected_unit: str,
    fraction: bool = False,
) -> ValueParameter:
    status = str(raw.get("status"))
    if status not in VALUE_STATUS:
        raise ValueError(f"{name}: invalid status")
    unit = str(raw.get("unit") or "")
    if unit != expected_unit:
        raise ValueError(f"{name}: expected unit {expected_unit}")
    raw_value = raw.get("value")
    if status == "UNKNOWN":
        if raw_value is not None:
            raise ValueError(f"{name}: UNKNOWN cannot carry value")
        value = None
    else:
        if raw_value is None:
            raise ValueError(f"{name}: KNOWN requires value")
        value = (
            _fraction(raw_value, name)
            if fraction
            else _nonnegative(raw_value, name)
        )
    return ValueParameter(
        status=status,
        value=value,
        unit=unit,
        provenance_refs=_refs(raw, name),
    )


def _generation_model(
    raw: Mapping[str, Any],
    *,
    name: str,
) -> GenerationModel:
    return GenerationModel(
        project_archetype_id=str(raw["project_archetype_id"]),
        availability_factor=_value(
            raw["availability_factor"],
            name=f"{name} availability",
            expected_unit="fraction",
            fraction=True,
        ),
        firm_capacity_fraction=_value(
            raw["firm_capacity_fraction"],
            name=f"{name} firm capacity",
            expected_unit="fraction",
            fraction=True,
        ),
        provenance_refs=_refs(raw, name),
    )


def load_power_balance_package(
    data: Mapping[str, Any],
) -> PowerBalancePackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected power-balance contract")
    if data.get("hours_basis") != "GREGORIAN_CALENDAR_YEAR":
        raise ValueError("Power Balance V1 requires Gregorian calendar-year hours")
    if data.get("population_peak_source") != "DEMAND_PRESSURE_POWER_STATE_DRIVERS":
        raise ValueError("unexpected population peak-load source")

    initial_raw = data["initial_compatibility_generation"]
    initial = _generation_model(
        {
            **initial_raw,
            "project_archetype_id": "INITIAL_COMPATIBILITY_CAPACITY",
        },
        name="initial compatibility generation",
    )
    generation_models = tuple(
        _generation_model(x, name="facility generation model")
        for x in data.get("generation_models", ())
    )
    generation_ids = [x.project_archetype_id for x in generation_models]
    if len(generation_ids) != len(set(generation_ids)):
        raise ValueError("duplicate generation model")

    load_models = []
    for raw in data.get("facility_load_models", ()):
        load_models.append(
            FacilityLoadModel(
                project_archetype_id=str(raw["project_archetype_id"]),
                peak_load_mw_per_facility=_value(
                    raw["peak_load_mw_per_facility"],
                    name="facility peak load",
                    expected_unit="MW/facility",
                ),
                average_to_peak_factor=_value(
                    raw["average_to_peak_factor"],
                    name="facility average-to-peak factor",
                    expected_unit="fraction",
                    fraction=True,
                ),
                provenance_refs=_refs(raw, "facility load model"),
            )
        )
    load_ids = [x.project_archetype_id for x in load_models]
    if len(load_ids) != len(set(load_ids)):
        raise ValueError("duplicate facility load model")

    storage = data["storage_model"]
    if storage.get("status") != "NOT_MODELED_V1":
        raise ValueError(
            "Power Balance V1 currently admits only explicit NOT_MODELED storage"
        )
    storage_power = _nonnegative(
        storage.get("modeled_power_capacity_mw", 0),
        "modeled storage power capacity",
    )
    storage_energy = _nonnegative(
        storage.get("modeled_energy_capacity_mwh", 0),
        "modeled storage energy capacity",
    )
    if storage_power != 0 or storage_energy != 0:
        raise ValueError("NOT_MODELED storage capacities must be zero")

    timeline = data["timeline_context"]
    if bool(timeline.get("auto_unlock")):
        raise ValueError("technology timeline may not auto-unlock power capability")

    package = PowerBalancePackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        scope=str(data["scope"]),
        excluded_location_ids=tuple(data.get("excluded_location_ids", ())),
        hours_basis="GREGORIAN_CALENDAR_YEAR",
        population_peak_source="DEMAND_PRESSURE_POWER_STATE_DRIVERS",
        population_average_to_peak_factor=_value(
            data["population_average_to_peak_factor"],
            name="population average-to-peak factor",
            expected_unit="fraction",
            fraction=True,
        ),
        initial_compatibility_generation=initial,
        generation_models=generation_models,
        facility_load_models=tuple(load_models),
        reserve_margin_fraction=_value(
            data["reserve_margin_fraction"],
            name="reserve margin",
            expected_unit="fraction",
            fraction=True,
        ),
        storage_model_status="NOT_MODELED_V1",
        storage_power_capacity_mw=storage_power,
        storage_energy_capacity_mwh=storage_energy,
        timeline_context=TimelineContext(
            demonstrator_reference_id=str(
                timeline["demonstrator_reference_id"]
            ),
            industrial_milestone_id=str(
                timeline["industrial_milestone_id"]
            ),
            industrial_threshold_year=int(
                timeline["industrial_threshold_year"]
            ),
            auto_unlock=False,
            provenance_refs=_refs(timeline, "power timeline context"),
        ),
    )
    return package


def load_power_balance_path(path: Path) -> PowerBalancePackage:
    return load_power_balance_package(json.loads(Path(path).read_text()))


class PowerBalanceRuntime:
    def __init__(
        self,
        package: PowerBalancePackage,
        demand_pressure: DemandPressurePackage,
    ):
        self.package = package
        channels = {
            x.channel_id: x for x in demand_pressure.channels
        }
        if "POWER" not in channels:
            raise ValueError("Power Balance V1 requires POWER demand channel")
        self.power_channel = channels["POWER"]
        if self.power_channel.unit != "MW":
            raise ValueError("POWER demand channel must use MW")
        if set(package.excluded_location_ids) != set(
            demand_pressure.excluded_location_ids
        ):
            raise ValueError(
                "power-balance scope must match demand-pressure exclusions"
            )
        self.generation_models = {
            x.project_archetype_id: x for x in package.generation_models
        }
        self.facility_load_models = {
            x.project_archetype_id: x for x in package.facility_load_models
        }

    def is_excluded(self, location_id: str) -> bool:
        return location_id in set(self.package.excluded_location_ids)

    @staticmethod
    def _hours(year: int) -> int:
        return 8784 if calendar.isleap(int(year)) else 8760

    @staticmethod
    def _component_total(
        values: Sequence[Optional[float]],
    ) -> Optional[float]:
        if not values:
            return 0.0
        if any(x is None for x in values):
            return None
        return sum(float(x) for x in values)

    def _load_component(
        self,
        *,
        year: int,
        location_id: str,
        source_type: str,
        source_id: str,
        peak_status: str,
        peak_mw: Optional[float],
        average_status: str,
        average_mw: Optional[float],
        provenance_refs: Sequence[str],
    ) -> PowerLoadComponentV1:
        return PowerLoadComponentV1(
            component_id=_stable_id(
                "pl",
                year,
                location_id,
                source_type,
                source_id,
            ),
            source_type=source_type,
            source_id=source_id,
            peak_load_status=peak_status,
            peak_load_mw=peak_mw,
            average_load_status=average_status,
            average_load_mw=average_mw,
            provenance_refs=tuple(provenance_refs),
        )

    def _generation_component(
        self,
        *,
        year: int,
        location_id: str,
        source_type: str,
        source_id: str,
        installed_mw: float,
        model: GenerationModel,
    ) -> PowerGenerationComponentV1:
        installed_mw = _nonnegative(installed_mw, "installed generation")
        availability = model.availability_factor.value
        firm = model.firm_capacity_fraction.value
        return PowerGenerationComponentV1(
            component_id=_stable_id(
                "pg",
                year,
                location_id,
                source_type,
                source_id,
            ),
            source_type=source_type,
            source_id=source_id,
            installed_capacity_mw=installed_mw,
            availability_status=model.availability_factor.status,
            availability_factor=availability,
            average_generation_mw=(
                0.0
                if installed_mw == 0
                else (
                    None
                    if availability is None
                    else installed_mw * availability
                )
            ),
            firm_capacity_status=model.firm_capacity_fraction.status,
            firm_capacity_fraction=firm,
            firm_generation_capacity_mw=(
                0.0
                if installed_mw == 0
                else None if firm is None else installed_mw * firm
            ),
            provenance_refs=model.provenance_refs,
        )

    def step_location(
        self,
        *,
        year: int,
        location_id: str,
        state: Any,
        facilities: Sequence[Any],
    ) -> tuple[PowerStateV1, tuple[PowerFlowV1, ...]]:
        if self.is_excluded(location_id):
            raise ValueError("excluded location cannot produce PowerStateV1")
        hours = self._hours(year)

        load_components = []
        population_peak = 0.0
        population_average_values = []
        avg_factor = self.package.population_average_to_peak_factor
        for driver in self.power_channel.drivers:
            value = _nonnegative(
                getattr(state, driver.field),
                f"power driver {driver.field}",
            )
            peak = value * driver.coefficient
            population_peak += peak
            if peak == 0:
                average = 0.0
                average_status = "KNOWN"
            elif avg_factor.value is None:
                average = None
                average_status = "UNKNOWN"
            else:
                average = peak * avg_factor.value
                average_status = "KNOWN"
            population_average_values.append(average)
            load_components.append(
                self._load_component(
                    year=year,
                    location_id=location_id,
                    source_type="POPULATION_DRIVER",
                    source_id=f"state:{driver.field}",
                    peak_status="KNOWN",
                    peak_mw=peak,
                    average_status=average_status,
                    average_mw=average,
                    provenance_refs=(
                        "engineering/civprop/contracts/demand_pressure_v1.json#POWER",
                    ),
                )
            )

        active = tuple(
            x
            for x in facilities
            if x.status == "ACTIVE"
            and x.location_id == location_id
            and x.commissioned_year <= year
        )
        facility_peak_values = []
        facility_average_values = []
        for facility in sorted(active, key=lambda x: x.facility_id):
            model = self.facility_load_models.get(
                facility.project_archetype_id
            )
            if model is None:
                raise ValueError("active facility lacks power-load model")
            peak = model.peak_load_mw_per_facility.value
            peak_status = model.peak_load_mw_per_facility.status
            avg_ratio = model.average_to_peak_factor.value
            if peak is None:
                average = None
                average_status = "UNKNOWN"
            elif peak == 0:
                average = 0.0
                average_status = "KNOWN"
            elif avg_ratio is None:
                average = None
                average_status = "UNKNOWN"
            else:
                average = peak * avg_ratio
                average_status = "KNOWN"
            facility_peak_values.append(peak)
            facility_average_values.append(average)
            load_components.append(
                self._load_component(
                    year=year,
                    location_id=location_id,
                    source_type="FACILITY_LOAD",
                    source_id=facility.facility_id,
                    peak_status=peak_status,
                    peak_mw=peak,
                    average_status=average_status,
                    average_mw=average,
                    provenance_refs=model.provenance_refs,
                )
            )

        facility_peak = self._component_total(facility_peak_values)
        population_average = self._component_total(
            population_average_values
        )
        facility_average = self._component_total(
            facility_average_values
        )
        peak_demand = (
            None
            if facility_peak is None
            else population_peak + facility_peak
        )
        average_demand = (
            None
            if population_average is None or facility_average is None
            else population_average + facility_average
        )

        generation_components = []
        active_power_capacity = sum(
            _nonnegative(x.capacities.power, "facility power capacity")
            for x in active
        )
        state_power = (
            getattr(state, "power")
            if hasattr(state, "power")
            else getattr(state.capacities, "power")
        )
        total_installed = _nonnegative(
            state_power,
            "location installed power capacity",
        )
        initial_capacity = total_installed - active_power_capacity
        if initial_capacity < -1e-9:
            raise ValueError(
                "facility power capacity exceeds location installed capacity"
            )
        initial_capacity = max(0.0, initial_capacity)
        if initial_capacity > 0:
            generation_components.append(
                self._generation_component(
                    year=year,
                    location_id=location_id,
                    source_type="INITIAL_COMPATIBILITY_CAPACITY",
                    source_id=f"{location_id}:initial",
                    installed_mw=initial_capacity,
                    model=self.package.initial_compatibility_generation,
                )
            )

        for facility in sorted(active, key=lambda x: x.facility_id):
            installed = _nonnegative(
                facility.capacities.power,
                "facility power capacity",
            )
            if installed == 0:
                continue
            model = self.generation_models.get(
                facility.project_archetype_id
            )
            if model is None:
                raise ValueError(
                    "power-producing facility lacks generation model"
                )
            generation_components.append(
                self._generation_component(
                    year=year,
                    location_id=location_id,
                    source_type="FACILITY_GENERATOR",
                    source_id=facility.facility_id,
                    installed_mw=installed,
                    model=model,
                )
            )

        component_installed = sum(
            x.installed_capacity_mw for x in generation_components
        )
        if not math.isclose(
            component_installed,
            total_installed,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError(
                "generation components do not reconcile installed capacity"
            )

        if total_installed == 0:
            average_generation = 0.0
            firm_generation = 0.0
        else:
            average_generation = self._component_total(
                [x.average_generation_mw for x in generation_components]
            )
            firm_generation = self._component_total(
                [x.firm_generation_capacity_mw for x in generation_components]
            )

        reserve = self.package.reserve_margin_fraction
        if peak_demand == 0:
            required_firm = 0.0
            reserve_adequacy = 1.0
            peak_service = 1.0
        else:
            required_firm = (
                None
                if reserve.value is None or peak_demand is None
                else peak_demand * (1.0 + reserve.value)
            )
            reserve_adequacy = (
                None
                if required_firm is None
                or firm_generation is None
                or required_firm == 0
                else min(1.0, firm_generation / required_firm)
            )
            peak_service = (
                None
                if peak_demand is None or firm_generation is None
                else min(1.0, firm_generation / peak_demand)
            )

        flows = []
        state_id = _stable_id("power", year, location_id)
        if average_generation is None or average_demand is None:
            demanded_energy = None
            generated_energy = None
            consumed_energy = None
            unserved_energy = None
            curtailed_energy = None
            energy_service = None
            residual = None
            energy_status = "UNKNOWN"
        else:
            demanded_energy = average_demand * hours
            generated_energy = average_generation * hours
            consumed_energy = min(demanded_energy, generated_energy)
            unserved_energy = max(0.0, demanded_energy - generated_energy)
            curtailed_energy = max(0.0, generated_energy - demanded_energy)
            energy_service = (
                1.0
                if demanded_energy == 0
                else min(1.0, consumed_energy / demanded_energy)
            )
            generation_residual = (
                generated_energy - consumed_energy - curtailed_energy
            )
            demand_residual = (
                demanded_energy - consumed_energy - unserved_energy
            )
            residual = max(
                abs(generation_residual),
                abs(demand_residual),
            )
            energy_status = "CLOSED"
            amounts = (
                ("GENERATION", generated_energy),
                ("SERVED_LOAD", consumed_energy),
                ("UNSERVED_LOAD", unserved_energy),
                ("CURTAILMENT", curtailed_energy),
            )
            for flow_type, amount in amounts:
                if amount <= 0:
                    continue
                flows.append(
                    PowerFlowV1(
                        power_flow_id=_stable_id(
                            "pf",
                            year,
                            location_id,
                            flow_type,
                        ),
                        power_state_id=state_id,
                        year=int(year),
                        location_id=location_id,
                        flow_type=flow_type,
                        amount_mwh=amount,
                    )
                )

        if energy_service is None or peak_service is None:
            power_service = None
        else:
            power_service = min(energy_service, peak_service)

        result = PowerStateV1(
            power_state_id=state_id,
            year=int(year),
            location_id=location_id,
            interval_hours=hours,
            installed_generation_capacity_mw=total_installed,
            generation_components=tuple(generation_components),
            average_generation_mw=average_generation,
            firm_generation_capacity_mw=firm_generation,
            load_components=tuple(load_components),
            population_peak_load_mw=population_peak,
            facility_peak_load_mw=facility_peak,
            peak_demand_mw=peak_demand,
            average_demand_mw=average_demand,
            reserve_margin_status=reserve.status,
            reserve_margin_fraction=reserve.value,
            required_firm_capacity_mw=required_firm,
            reserve_adequacy_ratio=reserve_adequacy,
            peak_service_ratio=peak_service,
            storage_model_status=self.package.storage_model_status,
            storage_power_capacity_mw=self.package.storage_power_capacity_mw,
            storage_energy_capacity_mwh=self.package.storage_energy_capacity_mwh,
            demanded_energy_mwh=demanded_energy,
            generated_energy_mwh=generated_energy,
            consumed_energy_mwh=consumed_energy,
            unserved_energy_mwh=unserved_energy,
            curtailed_energy_mwh=curtailed_energy,
            energy_service_ratio=energy_service,
            power_service_ratio=power_service,
            energy_closure_residual_mwh=residual,
            energy_balance_status=energy_status,
            atlas_power_average_mw=average_demand,
            atlas_power_peak_mw=peak_demand,
        )
        self.validate_state(result)
        return result, tuple(flows)

    @staticmethod
    def validate_state(state: PowerStateV1) -> None:
        _nonnegative(
            state.installed_generation_capacity_mw,
            "installed generation capacity",
        )
        for value, name in (
            (state.average_generation_mw, "average generation"),
            (state.firm_generation_capacity_mw, "firm generation"),
            (state.population_peak_load_mw, "population peak load"),
            (state.facility_peak_load_mw, "facility peak load"),
            (state.peak_demand_mw, "peak demand"),
            (state.average_demand_mw, "average demand"),
            (state.required_firm_capacity_mw, "required firm capacity"),
            (state.demanded_energy_mwh, "demanded energy"),
            (state.generated_energy_mwh, "generated energy"),
            (state.consumed_energy_mwh, "consumed energy"),
            (state.unserved_energy_mwh, "unserved energy"),
            (state.curtailed_energy_mwh, "curtailed energy"),
            (state.energy_closure_residual_mwh, "energy closure residual"),
        ):
            if value is not None:
                _nonnegative(value, name)
        for value, name in (
            (state.reserve_adequacy_ratio, "reserve adequacy"),
            (state.peak_service_ratio, "peak service"),
            (state.energy_service_ratio, "energy service"),
            (state.power_service_ratio, "power service"),
        ):
            if value is not None:
                _fraction(value, name)
        if state.energy_balance_status not in ENERGY_STATUS:
            raise ValueError("invalid energy balance status")
        if (
            state.energy_balance_status == "CLOSED"
            and (
                state.energy_closure_residual_mwh is None
                or state.energy_closure_residual_mwh > 1e-9
            )
        ):
            raise ValueError("power energy balance does not close")
        if (
            state.atlas_power_average_mw
            != state.average_demand_mw
            or state.atlas_power_peak_mw != state.peak_demand_mw
        ):
            raise ValueError("Atlas power metrics must derive from runtime load")


__all__ = [
    "CONTRACT_VERSION",
    "FORMAT",
    "FacilityLoadModel",
    "GenerationModel",
    "PowerBalancePackage",
    "PowerBalanceRuntime",
    "PowerFlowV1",
    "PowerGenerationComponentV1",
    "PowerLoadComponentV1",
    "PowerStateV1",
    "TimelineContext",
    "ValueParameter",
    "load_power_balance_package",
    "load_power_balance_path",
]
