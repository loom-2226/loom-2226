"""CIVPROP Demand/Pressure V1 causal stock-flow boundary.

Demand is derived from explicit civilization state and declared strategic
requirements. Pressure retains unmet demand with channel-specific decay and gain.
No annual author-written demand curve is consumed by this contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Optional


FORMAT = "CIVPROP_DEMAND_PRESSURE_V1"
CONTRACT_VERSION = "1.0.0"
PARAMETER_STATUS = "UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1"
_ALLOWED_STATE_FIELDS = {
    "biological_population",
    "transient_population",
    "workforce",
    "capital",
    "power",
    "resource",
    "industrial",
    "habitat",
    "shipyard",
    "transport",
}


def _nonnegative(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return out


def _unit(value: Any, name: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{name} requires unit")
    return out


@dataclass(frozen=True)
class DemandDriver:
    field: str
    coefficient: float
    coefficient_unit: str


@dataclass(frozen=True)
class DemandChannel:
    channel_id: str
    unit: str
    available_field: str
    decay: float
    gain: float
    drivers: tuple[DemandDriver, ...]


@dataclass(frozen=True)
class StrategicRequirement:
    requirement_id: str
    actor_id: str
    location_id: str
    channel_id: str
    amount: float
    unit: str
    valid_from_year: int
    valid_to_year: Optional[int]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class DemandPressurePackage:
    format: str
    contract_version: str
    scope: str
    excluded_location_ids: tuple[str, ...]
    channels: tuple[DemandChannel, ...]
    strategic_requirements: tuple[StrategicRequirement, ...]
    parameter_status: str


@dataclass(frozen=True)
class DemandComponent:
    component_type: str
    source_id: str
    quantity: float
    unit: str


@dataclass(frozen=True)
class DemandObservation:
    year: int
    location_id: str
    channel_id: str
    unit: str
    required: float
    available: float
    unmet: float
    driver_components: tuple[str, ...]
    quantified_components: tuple[DemandComponent, ...] = ()
    available_component_type: str = "INSTALLED_CAPACITY"
    available_source_id: str | None = None


def _driver(data: Mapping[str, Any]) -> DemandDriver:
    field = str(data["field"])
    if field not in _ALLOWED_STATE_FIELDS:
        raise ValueError(f"unsupported demand driver field: {field}")
    return DemandDriver(
        field=field,
        coefficient=_nonnegative(data["coefficient"], "demand coefficient"),
        coefficient_unit=_unit(data.get("coefficient_unit"), "demand coefficient"),
    )


def _channel(data: Mapping[str, Any]) -> DemandChannel:
    channel_id = str(data["channel_id"])
    available_field = str(data["available_field"])
    if available_field not in _ALLOWED_STATE_FIELDS:
        raise ValueError(f"unsupported available field: {available_field}")
    decay = float(data["decay"])
    gain = float(data["gain"])
    if not math.isfinite(decay) or not 0 <= decay < 1:
        raise ValueError("pressure decay must be in [0,1)")
    if not math.isfinite(gain) or gain <= 0:
        raise ValueError("pressure gain must be positive")
    drivers = tuple(_driver(x) for x in data.get("drivers", ()))
    driver_fields = [x.field for x in drivers]
    if len(driver_fields) != len(set(driver_fields)):
        raise ValueError("duplicate demand driver field")
    return DemandChannel(
        channel_id=channel_id,
        unit=_unit(data.get("unit"), "demand channel"),
        available_field=available_field,
        decay=decay,
        gain=gain,
        drivers=drivers,
    )


def load_demand_pressure_package(data: Mapping[str, Any]) -> DemandPressurePackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected demand/pressure contract")
    if data.get("parameter_status") != PARAMETER_STATUS:
        raise ValueError("unexpected demand/pressure parameter status")

    channels = tuple(_channel(x) for x in data.get("channels", ()))
    ids = [x.channel_id for x in channels]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("demand channels must be nonempty and unique")
    channel_by_id = {x.channel_id: x for x in channels}

    requirements = []
    seen = set()
    for data_row in data.get("strategic_requirements", ()):
        requirement_id = str(data_row["requirement_id"])
        if requirement_id in seen:
            raise ValueError("duplicate strategic requirement")
        seen.add(requirement_id)
        channel_id = str(data_row["channel_id"])
        if channel_id not in channel_by_id:
            raise ValueError("strategic requirement references unknown channel")
        unit = _unit(data_row.get("unit"), "strategic requirement")
        if unit != channel_by_id[channel_id].unit:
            raise ValueError("strategic requirement unit does not match channel")
        valid_from = int(data_row["valid_from_year"])
        valid_to = (
            None
            if data_row.get("valid_to_year") is None
            else int(data_row["valid_to_year"])
        )
        if valid_to is not None and valid_to < valid_from:
            raise ValueError("invalid strategic requirement validity")
        requirements.append(
            StrategicRequirement(
                requirement_id=requirement_id,
                actor_id=str(data_row["actor_id"]),
                location_id=str(data_row["location_id"]),
                channel_id=channel_id,
                amount=_nonnegative(data_row["amount"], "strategic requirement"),
                unit=unit,
                valid_from_year=valid_from,
                valid_to_year=valid_to,
                provenance_refs=tuple(data_row.get("provenance_refs", ())),
            )
        )

    return DemandPressurePackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        scope=str(data["scope"]),
        excluded_location_ids=tuple(data.get("excluded_location_ids", ())),
        channels=channels,
        strategic_requirements=tuple(requirements),
        parameter_status=PARAMETER_STATUS,
    )


class DemandPressureRuntime:
    """Pure deterministic demand derivation and pressure-memory update."""

    def __init__(self, package: DemandPressurePackage):
        self.package = package
        self.channels = {x.channel_id: x for x in package.channels}

    def derive(
        self,
        states: Mapping[str, Any],
        *,
        year: int,
        additional_requirements: Mapping[tuple[str, str], float] | None = None,
    ) -> tuple[DemandObservation, ...]:
        additional = additional_requirements or {}
        excluded = set(self.package.excluded_location_ids)
        rows: list[DemandObservation] = []
        for location_id in sorted(states):
            if location_id in excluded:
                continue
            state = states[location_id]
            for channel in self.package.channels:
                required = 0.0
                components: list[str] = []
                quantified: list[DemandComponent] = []
                for driver in channel.drivers:
                    value = _nonnegative(
                        getattr(state, driver.field),
                        f"state driver {driver.field}",
                    )
                    contribution = value * driver.coefficient
                    if contribution:
                        required += contribution
                        source_id = f"state:{driver.field}"
                        components.append(source_id)
                        quantified.append(
                            DemandComponent(
                                component_type="STATE_DRIVER",
                                source_id=source_id,
                                quantity=contribution,
                                unit=channel.unit,
                            )
                        )

                for strategic in self.package.strategic_requirements:
                    if strategic.location_id != location_id:
                        continue
                    if strategic.channel_id != channel.channel_id:
                        continue
                    if year < strategic.valid_from_year:
                        continue
                    if (
                        strategic.valid_to_year is not None
                        and year > strategic.valid_to_year
                    ):
                        continue
                    required += strategic.amount
                    source_id = f"strategic:{strategic.requirement_id}"
                    components.append(source_id)
                    quantified.append(
                        DemandComponent(
                            component_type="STRATEGIC_REQUIREMENT",
                            source_id=source_id,
                            quantity=strategic.amount,
                            unit=channel.unit,
                        )
                    )

                extra = _nonnegative(
                    additional.get((location_id, channel.channel_id), 0.0),
                    "additional requirement",
                )
                if extra:
                    required += extra
                    source_id = "pending_project_minimum_input"
                    components.append(source_id)
                    quantified.append(
                        DemandComponent(
                            component_type="PENDING_PROJECT_REQUIREMENT",
                            source_id=source_id,
                            quantity=extra,
                            unit=channel.unit,
                        )
                    )

                available = _nonnegative(
                    getattr(state, channel.available_field),
                    f"available state {channel.available_field}",
                )
                rows.append(
                    DemandObservation(
                        year=int(year),
                        location_id=location_id,
                        channel_id=channel.channel_id,
                        unit=channel.unit,
                        required=required,
                        available=available,
                        unmet=max(0.0, required - available),
                        driver_components=tuple(components),
                        quantified_components=tuple(quantified),
                    )
                )
        return tuple(rows)

    def advance_pressure(
        self,
        previous: Mapping[tuple[str, str], float],
        observations: tuple[DemandObservation, ...],
    ) -> dict[tuple[str, str], float]:
        result: dict[tuple[str, str], float] = {}
        observed_keys = set()
        for row in observations:
            key = (row.location_id, row.channel_id)
            observed_keys.add(key)
            channel = self.channels[row.channel_id]
            prior = _nonnegative(previous.get(key, 0.0), "previous pressure")
            result[key] = prior * channel.decay + row.unmet * channel.gain

        for key, value in previous.items():
            if key in observed_keys:
                continue
            channel_id = key[1]
            if channel_id not in self.channels:
                continue
            result[key] = _nonnegative(value, "previous pressure") * self.channels[
                channel_id
            ].decay
        return result


__all__ = [
    "CONTRACT_VERSION",
    "FORMAT",
    "PARAMETER_STATUS",
    "DemandChannel",
    "DemandComponent",
    "DemandDriver",
    "DemandObservation",
    "DemandPressurePackage",
    "DemandPressureRuntime",
    "StrategicRequirement",
    "load_demand_pressure_package",
]
