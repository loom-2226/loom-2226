"""CIVPROP Production Accounting V1.

Explicitly separates physical production feasibility, monetary valuation, and gross
productive-capital accounting.

Earth sector authority contributes transferable accounting vocabulary/identities.
It does not supply off-world prices, operating costs, utilization, or productivity.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


FORMAT = "CIVPROP_PRODUCTION_ACCOUNTING_V1"
CONTRACT_VERSION = "1.2.0"

VALUE_STATUS = {"KNOWN", "UNKNOWN"}
CONSTRAINT_STATUS = {"KNOWN", "UNKNOWN", "NOT_APPLICABLE"}
OUTPUT_SOURCE = {
    "CAPACITY_FIELD",
    "RESOURCE_RECOVERED_PRODUCT",
    "POWER_GENERATION",
    "DEFERRED",
}
STATE_STATUS = {"KNOWN", "UNKNOWN", "DEFERRED"}
VALUATION_STATUS = {"KNOWN", "UNKNOWN", "PARTIAL", "DEFERRED"}

CONSTRAINT_IDS = {
    "POWER",
    "LABOR_AUTOMATION",
    "MATERIALS",
    "TRANSPORT",
}


def _stable_id(prefix: str, *parts: object) -> str:
    payload = json.dumps(parts, separators=(",", ":"), allow_nan=False).encode()
    return f"{prefix}-" + hashlib.sha256(payload).hexdigest()[:20]


def _finite_nonnegative(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out) or out < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return out


def _ratio(value: Any, name: str) -> float:
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
class ValuationParameters:
    unit_output_value: ValueParameter
    intermediate_consumption_per_output: ValueParameter
    operating_cost_per_output: ValueParameter


@dataclass(frozen=True)
class FacilityProductionModel:
    production_model_id: str
    project_archetype_id: str
    sector_id: str
    output_source: str
    output_field: Optional[str]
    output_unit: Optional[str]
    resource_id: Optional[str]
    downstream_gap: Optional[str]
    required_constraints: tuple[str, ...]
    valuation: ValuationParameters
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ProductionAccountingPackage:
    format: str
    contract_version: str
    package_id: str
    monetary_stock_unit: str
    monetary_flow_unit: str
    facility_models: tuple[FacilityProductionModel, ...]


@dataclass(frozen=True)
class ConstraintObservationV1:
    constraint_id: str
    status: str
    utilization_ratio: Optional[float]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.constraint_id not in CONSTRAINT_IDS:
            raise ValueError("unknown production constraint")
        if self.status not in CONSTRAINT_STATUS:
            raise ValueError("invalid production constraint status")
        if not self.provenance_refs:
            raise ValueError("production constraint requires provenance")
        if self.status == "KNOWN":
            if self.utilization_ratio is None:
                raise ValueError("KNOWN constraint requires utilization ratio")
            _ratio(self.utilization_ratio, "constraint utilization ratio")
        elif self.utilization_ratio is not None:
            raise ValueError(
                "UNKNOWN/NOT_APPLICABLE constraint cannot carry utilization ratio"
            )


@dataclass(frozen=True)
class FacilityProductionStateV1:
    production_state_id: str
    year: int
    facility_id: str
    project_archetype_id: str
    production_model_id: str
    sector_id: str
    location_id: str
    owner_actor_id: str
    output_source: str
    physical_output_unit: Optional[str]
    installed_output_capacity: Optional[float]
    physical_output_ceiling: Optional[float]
    constraint_observations: tuple[ConstraintObservationV1, ...]
    utilization_status: str
    realized_utilization: Optional[float]
    controlling_constraint_id: Optional[str]
    physical_output_status: str
    physical_output_quantity: Optional[float]
    valuation_status: str
    unit_output_value: Optional[float]
    gross_output: Optional[float]
    intermediate_consumption: Optional[float]
    operating_cost: Optional[float]
    value_added: Optional[float]
    monetary_flow_unit: str
    opening_gross_productive_capital: float
    commissioned_investment: float
    closing_gross_productive_capital: float
    monetary_stock_unit: str


@dataclass(frozen=True)
class SectorProductionStateV1:
    aggregate_id: str
    year: int
    location_id: str
    sector_id: str
    facility_count: int
    physical_output_status: str
    physical_output_unit: Optional[str]
    physical_output_quantity: Optional[float]
    valuation_status: str
    gross_output: Optional[float]
    intermediate_consumption: Optional[float]
    operating_cost: Optional[float]
    value_added: Optional[float]
    commissioned_investment: float
    opening_gross_productive_capital: float
    closing_gross_productive_capital: float
    monetary_flow_unit: str
    monetary_stock_unit: str


@dataclass(frozen=True)
class LocationProductionStateV1:
    aggregate_id: str
    year: int
    location_id: str
    sector_count: int
    facility_count: int
    valuation_status: str
    gross_output: Optional[float]
    intermediate_consumption: Optional[float]
    operating_cost: Optional[float]
    value_added: Optional[float]
    commissioned_investment: float
    opening_gross_productive_capital: float
    closing_gross_productive_capital: float
    monetary_flow_unit: str
    monetary_stock_unit: str


@dataclass(frozen=True)
class BodyProductionStateV1:
    aggregate_id: str
    year: int
    body_id: str
    location_count: int
    facility_count: int
    valuation_status: str
    gross_output: Optional[float]
    intermediate_consumption: Optional[float]
    operating_cost: Optional[float]
    value_added: Optional[float]
    commissioned_investment: float
    opening_gross_productive_capital: float
    closing_gross_productive_capital: float
    monetary_flow_unit: str
    monetary_stock_unit: str


def _value_parameter(
    raw: Mapping[str, Any],
    name: str,
) -> ValueParameter:
    status = str(raw.get("status"))
    if status not in VALUE_STATUS:
        raise ValueError(f"{name}: invalid status")
    unit = str(raw.get("unit") or "")
    if not unit:
        raise ValueError(f"{name}: unit required")
    value = raw.get("value")
    if status == "UNKNOWN":
        if value is not None:
            raise ValueError(f"{name}: UNKNOWN cannot carry value")
        numeric = None
    else:
        if value is None:
            raise ValueError(f"{name}: KNOWN requires value")
        numeric = _finite_nonnegative(value, name)
    return ValueParameter(
        status=status,
        value=numeric,
        unit=unit,
        provenance_refs=_refs(raw, name),
    )


def load_production_accounting_package(
    data: Mapping[str, Any],
) -> ProductionAccountingPackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected production-accounting contract")
    if data.get("monetary_stock_unit") != "USD_2026_billion":
        raise ValueError("production capital must use USD_2026_billion")
    if data.get("monetary_flow_unit") != "USD_2026_billion/year":
        raise ValueError("production monetary flows must use USD_2026_billion/year")

    models = []
    for raw in data.get("facility_models", ()):
        source = str(raw["output_source"])
        if source not in OUTPUT_SOURCE:
            raise ValueError("invalid production output source")
        constraints = tuple(str(x) for x in raw.get("required_constraints", ()))
        if len(constraints) != len(set(constraints)):
            raise ValueError("duplicate required production constraint")
        if any(x not in CONSTRAINT_IDS for x in constraints):
            raise ValueError("unknown required production constraint")

        output_field = raw.get("output_field")
        output_unit = raw.get("output_unit")
        resource_id = raw.get("resource_id")
        downstream_gap = raw.get("downstream_gap")
        if source == "DEFERRED":
            if downstream_gap is None:
                raise ValueError("deferred production model requires downstream gap")
        else:
            if output_field is None or output_unit is None:
                raise ValueError("production model requires output field/unit")
        if source == "RESOURCE_RECOVERED_PRODUCT" and resource_id is None:
            raise ValueError("resource production requires resource_id")

        valuation = raw["valuation"]
        models.append(
            FacilityProductionModel(
                production_model_id=str(raw["production_model_id"]),
                project_archetype_id=str(raw["project_archetype_id"]),
                sector_id=str(raw["sector_id"]),
                output_source=source,
                output_field=None if output_field is None else str(output_field),
                output_unit=None if output_unit is None else str(output_unit),
                resource_id=None if resource_id is None else str(resource_id),
                downstream_gap=(
                    None if downstream_gap is None else str(downstream_gap)
                ),
                required_constraints=constraints,
                valuation=ValuationParameters(
                    unit_output_value=_value_parameter(
                        valuation["unit_output_value"],
                        "unit output value",
                    ),
                    intermediate_consumption_per_output=_value_parameter(
                        valuation["intermediate_consumption_per_output"],
                        "intermediate consumption per output",
                    ),
                    operating_cost_per_output=_value_parameter(
                        valuation["operating_cost_per_output"],
                        "operating cost per output",
                    ),
                ),
                provenance_refs=_refs(raw, "facility production model"),
            )
        )
    if not models:
        raise ValueError("production-accounting package requires facility models")
    ids = [x.production_model_id for x in models]
    archetypes = [x.project_archetype_id for x in models]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate production model id")
    if len(archetypes) != len(set(archetypes)):
        raise ValueError("duplicate project archetype production model")

    return ProductionAccountingPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        monetary_stock_unit="USD_2026_billion",
        monetary_flow_unit="USD_2026_billion/year",
        facility_models=tuple(models),
    )


def load_production_accounting_path(path: Path) -> ProductionAccountingPackage:
    return load_production_accounting_package(json.loads(Path(path).read_text()))


class ProductionAccountingRuntime:
    def __init__(self, package: ProductionAccountingPackage):
        self.package = package
        self._models = {
            x.project_archetype_id: x for x in package.facility_models
        }

    @staticmethod
    def _state_id(year: int, facility_id: str) -> str:
        return _stable_id("prod", int(year), facility_id)

    @staticmethod
    def _aggregate_id(level: str, year: int, *scope: str) -> str:
        return _stable_id("pa", level, int(year), *scope)

    def _constraints(
        self,
        model: FacilityProductionModel,
        supplied: Mapping[str, ConstraintObservationV1],
    ) -> tuple[
        tuple[ConstraintObservationV1, ...],
        str,
        Optional[float],
        Optional[str],
    ]:
        rows = []
        for constraint_id in model.required_constraints:
            row = supplied.get(constraint_id)
            if row is None:
                row = ConstraintObservationV1(
                    constraint_id=constraint_id,
                    status="UNKNOWN",
                    utilization_ratio=None,
                    provenance_refs=("MISSING_CONSTRAINT_OBSERVATION",),
                )
            if row.constraint_id != constraint_id:
                raise ValueError("constraint mapping/id mismatch")
            rows.append(row)

        unknown = [x for x in rows if x.status == "UNKNOWN"]
        if unknown:
            return tuple(rows), "UNKNOWN", None, unknown[0].constraint_id

        known = [x for x in rows if x.status == "KNOWN"]
        if not known:
            return tuple(rows), "KNOWN", 1.0, None
        controlling = min(
            known,
            key=lambda x: (float(x.utilization_ratio), x.constraint_id),
        )
        return (
            tuple(rows),
            "KNOWN",
            float(controlling.utilization_ratio),
            controlling.constraint_id,
        )

    def evaluate_facility(
        self,
        *,
        year: int,
        facility: Any,
        constraint_observations: Mapping[str, ConstraintObservationV1],
        resource_states: Sequence[Any],
        peer_facilities: Sequence[Any] = (),
        power_states: Sequence[Any] = (),
    ) -> FacilityProductionStateV1:
        model = self._models.get(facility.project_archetype_id)
        if model is None:
            raise ValueError("active facility lacks production-accounting model")
        if facility.status != "ACTIVE":
            raise ValueError("production accounting requires active facility")
        if int(facility.commissioned_year) > int(year):
            raise ValueError("cannot produce before facility commissioning")

        capital = _finite_nonnegative(facility.capital, "facility capital")
        commissioned_investment = (
            capital if int(year) == int(facility.commissioned_year) else 0.0
        )
        opening_capital = (
            0.0 if int(year) == int(facility.commissioned_year) else capital
        )
        closing_capital = opening_capital + commissioned_investment

        constraints, utilization_status, utilization, controlling = self._constraints(
            model,
            constraint_observations,
        )

        installed_capacity: Optional[float] = None
        ceiling: Optional[float] = None
        output_status = "UNKNOWN"
        output_quantity: Optional[float] = None

        if model.output_source == "DEFERRED":
            utilization_status = "DEFERRED"
            utilization = None
            controlling = model.downstream_gap
            output_status = "DEFERRED"
        else:
            assert model.output_field is not None
            installed_capacity = _finite_nonnegative(
                getattr(facility.capacities, model.output_field),
                "installed output capacity",
            )
            if model.output_source == "CAPACITY_FIELD":
                ceiling = installed_capacity
            elif model.output_source == "POWER_GENERATION":
                power_matches = [
                    x
                    for x in power_states
                    if int(x.year) == int(year)
                    and x.location_id == facility.location_id
                ]
                if len(power_matches) != 1:
                    ceiling = None
                else:
                    power_state = power_matches[0]
                    installed_capacity = (
                        installed_capacity * power_state.interval_hours
                    )
                    components = [
                        x
                        for x in power_state.generation_components
                        if x.source_type == "FACILITY_GENERATOR"
                        and x.source_id == facility.facility_id
                    ]
                    if len(components) != 1:
                        ceiling = None
                    else:
                        average_generation = (
                            components[0].average_generation_mw
                        )
                        ceiling = (
                            None
                            if average_generation is None
                            else average_generation
                            * power_state.interval_hours
                        )
            else:
                matches = [
                    x
                    for x in resource_states
                    if int(x.year) == int(year)
                    and x.location_id == facility.location_id
                    and x.resource_id == model.resource_id
                ]
                if len(matches) != 1:
                    ceiling = None
                else:
                    recovered = matches[0].recovered_product_tonnes
                    if recovered is None:
                        ceiling = None
                    else:
                        recovered_value = _finite_nonnegative(
                            recovered,
                            "resource recovered product",
                        )
                        peers = tuple(peer_facilities) or (facility,)
                        eligible = tuple(
                            x
                            for x in peers
                            if getattr(x, "status", None) == "ACTIVE"
                            and getattr(
                                x,
                                "project_archetype_id",
                                None,
                            )
                            == facility.project_archetype_id
                            and getattr(x, "location_id", None)
                            == facility.location_id
                            and int(
                                getattr(x, "commissioned_year")
                            )
                            <= int(year)
                        )
                        if not any(
                            getattr(x, "facility_id", None)
                            == facility.facility_id
                            for x in eligible
                        ):
                            raise ValueError(
                                "resource production peer set omits facility"
                            )
                        total_capacity = sum(
                            _finite_nonnegative(
                                getattr(
                                    x.capacities,
                                    model.output_field,
                                ),
                                "peer resource capacity",
                            )
                            for x in eligible
                        )
                        if total_capacity <= 0:
                            ceiling = 0.0
                        else:
                            allocated_product = (
                                recovered_value
                                * installed_capacity
                                / total_capacity
                            )
                            ceiling = min(
                                installed_capacity,
                                allocated_product,
                            )
            if ceiling is not None and utilization_status == "KNOWN":
                assert utilization is not None
                output_quantity = ceiling * utilization
                output_status = "KNOWN"
            else:
                output_status = "UNKNOWN"

        valuation = model.valuation
        unit_value = valuation.unit_output_value.value
        ic_per_output = valuation.intermediate_consumption_per_output.value
        operating_per_output = valuation.operating_cost_per_output.value

        gross_output = None
        intermediate = None
        operating_cost = None
        value_added = None
        if output_status == "DEFERRED":
            valuation_status = "DEFERRED"
        elif output_quantity is None:
            valuation_status = "UNKNOWN"
        else:
            if unit_value is not None:
                gross_output = output_quantity * unit_value
            if ic_per_output is not None:
                intermediate = output_quantity * ic_per_output
            if operating_per_output is not None:
                operating_cost = output_quantity * operating_per_output
            if gross_output is not None and intermediate is not None:
                value_added = gross_output - intermediate
            known_count = sum(
                x is not None
                for x in (gross_output, intermediate, operating_cost, value_added)
            )
            valuation_status = (
                "KNOWN"
                if known_count == 4
                else ("UNKNOWN" if known_count == 0 else "PARTIAL")
            )

        state = FacilityProductionStateV1(
            production_state_id=self._state_id(year, facility.facility_id),
            year=int(year),
            facility_id=str(facility.facility_id),
            project_archetype_id=str(facility.project_archetype_id),
            production_model_id=model.production_model_id,
            sector_id=model.sector_id,
            location_id=str(facility.location_id),
            owner_actor_id=str(facility.owner_actor_id),
            output_source=model.output_source,
            physical_output_unit=model.output_unit,
            installed_output_capacity=installed_capacity,
            physical_output_ceiling=ceiling,
            constraint_observations=constraints,
            utilization_status=utilization_status,
            realized_utilization=utilization,
            controlling_constraint_id=controlling,
            physical_output_status=output_status,
            physical_output_quantity=output_quantity,
            valuation_status=valuation_status,
            unit_output_value=unit_value,
            gross_output=gross_output,
            intermediate_consumption=intermediate,
            operating_cost=operating_cost,
            value_added=value_added,
            monetary_flow_unit=self.package.monetary_flow_unit,
            opening_gross_productive_capital=opening_capital,
            commissioned_investment=commissioned_investment,
            closing_gross_productive_capital=closing_capital,
            monetary_stock_unit=self.package.monetary_stock_unit,
        )
        self.validate_facility_state(state)
        return state

    @staticmethod
    def validate_facility_state(state: FacilityProductionStateV1) -> None:
        if state.utilization_status not in STATE_STATUS:
            raise ValueError("invalid utilization status")
        if state.physical_output_status not in STATE_STATUS:
            raise ValueError("invalid physical output status")
        if state.valuation_status not in VALUATION_STATUS:
            raise ValueError("invalid valuation status")
        if state.realized_utilization is not None:
            _ratio(state.realized_utilization, "realized utilization")
        for value, name in (
            (state.installed_output_capacity, "installed output capacity"),
            (state.physical_output_ceiling, "physical output ceiling"),
            (state.physical_output_quantity, "physical output quantity"),
            (state.unit_output_value, "unit output value"),
            (state.gross_output, "gross output"),
            (state.intermediate_consumption, "intermediate consumption"),
            (state.operating_cost, "operating cost"),
            (state.opening_gross_productive_capital, "opening gross capital"),
            (state.commissioned_investment, "commissioned investment"),
            (state.closing_gross_productive_capital, "closing gross capital"),
        ):
            if value is not None:
                _finite_nonnegative(value, name)
        if state.value_added is not None and not math.isfinite(state.value_added):
            raise ValueError("value added must be finite")
        if (
            state.physical_output_quantity is not None
            and state.physical_output_ceiling is not None
            and state.physical_output_quantity
            > state.physical_output_ceiling + 1e-12
        ):
            raise ValueError("physical output exceeds admitted ceiling")
        if (
            state.gross_output is not None
            and state.intermediate_consumption is not None
        ):
            expected = state.gross_output - state.intermediate_consumption
            if state.value_added is None or not math.isclose(
                state.value_added,
                expected,
                rel_tol=0,
                abs_tol=1e-12,
            ):
                raise ValueError("value-added identity does not close")
        expected_capital = (
            state.opening_gross_productive_capital
            + state.commissioned_investment
        )
        if not math.isclose(
            state.closing_gross_productive_capital,
            expected_capital,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("gross productive capital identity does not close")

    @staticmethod
    def _sum_optional(rows: Sequence[Any], field: str) -> Optional[float]:
        values = [getattr(x, field) for x in rows]
        if any(x is None for x in values):
            return None
        return sum(float(x) for x in values)

    @staticmethod
    def _valuation_status_from_values(
        gross: Optional[float],
        intermediate: Optional[float],
        operating: Optional[float],
        value_added: Optional[float],
    ) -> str:
        values = (gross, intermediate, operating, value_added)
        count = sum(x is not None for x in values)
        if count == len(values):
            return "KNOWN"
        return "UNKNOWN" if count == 0 else "PARTIAL"

    def aggregate(
        self,
        *,
        year: int,
        facility_states: Sequence[FacilityProductionStateV1],
        location_to_body: Mapping[str, Optional[str]],
    ) -> tuple[
        tuple[SectorProductionStateV1, ...],
        tuple[LocationProductionStateV1, ...],
        tuple[BodyProductionStateV1, ...],
    ]:
        rows = tuple(x for x in facility_states if x.year == int(year))

        by_sector: dict[tuple[str, str], list[FacilityProductionStateV1]] = {}
        for row in rows:
            by_sector.setdefault((row.location_id, row.sector_id), []).append(row)

        sectors = []
        for (location_id, sector_id), members in sorted(by_sector.items()):
            units = {x.physical_output_unit for x in members}
            output_status = (
                "KNOWN"
                if all(x.physical_output_status == "KNOWN" for x in members)
                else (
                    "DEFERRED"
                    if all(x.physical_output_status == "DEFERRED" for x in members)
                    else "UNKNOWN"
                )
            )
            output_unit = next(iter(units)) if len(units) == 1 else None
            output_quantity = (
                sum(float(x.physical_output_quantity) for x in members)
                if output_status == "KNOWN"
                and output_unit is not None
                and all(x.physical_output_quantity is not None for x in members)
                else None
            )
            gross = self._sum_optional(members, "gross_output")
            intermediate = self._sum_optional(members, "intermediate_consumption")
            operating = self._sum_optional(members, "operating_cost")
            value_added = self._sum_optional(members, "value_added")
            sectors.append(
                SectorProductionStateV1(
                    aggregate_id=self._aggregate_id(
                        "SECTOR",
                        year,
                        location_id,
                        sector_id,
                    ),
                    year=int(year),
                    location_id=location_id,
                    sector_id=sector_id,
                    facility_count=len(members),
                    physical_output_status=output_status,
                    physical_output_unit=output_unit,
                    physical_output_quantity=output_quantity,
                    valuation_status=self._valuation_status_from_values(
                        gross,
                        intermediate,
                        operating,
                        value_added,
                    ),
                    gross_output=gross,
                    intermediate_consumption=intermediate,
                    operating_cost=operating,
                    value_added=value_added,
                    commissioned_investment=sum(
                        x.commissioned_investment for x in members
                    ),
                    opening_gross_productive_capital=sum(
                        x.opening_gross_productive_capital for x in members
                    ),
                    closing_gross_productive_capital=sum(
                        x.closing_gross_productive_capital for x in members
                    ),
                    monetary_flow_unit=self.package.monetary_flow_unit,
                    monetary_stock_unit=self.package.monetary_stock_unit,
                )
            )

        by_location: dict[str, list[SectorProductionStateV1]] = {}
        for row in sectors:
            by_location.setdefault(row.location_id, []).append(row)
        locations = []
        for location_id, members in sorted(by_location.items()):
            gross = self._sum_optional(members, "gross_output")
            intermediate = self._sum_optional(members, "intermediate_consumption")
            operating = self._sum_optional(members, "operating_cost")
            value_added = self._sum_optional(members, "value_added")
            locations.append(
                LocationProductionStateV1(
                    aggregate_id=self._aggregate_id(
                        "LOCATION",
                        year,
                        location_id,
                    ),
                    year=int(year),
                    location_id=location_id,
                    sector_count=len(members),
                    facility_count=sum(x.facility_count for x in members),
                    valuation_status=self._valuation_status_from_values(
                        gross,
                        intermediate,
                        operating,
                        value_added,
                    ),
                    gross_output=gross,
                    intermediate_consumption=intermediate,
                    operating_cost=operating,
                    value_added=value_added,
                    commissioned_investment=sum(
                        x.commissioned_investment for x in members
                    ),
                    opening_gross_productive_capital=sum(
                        x.opening_gross_productive_capital for x in members
                    ),
                    closing_gross_productive_capital=sum(
                        x.closing_gross_productive_capital for x in members
                    ),
                    monetary_flow_unit=self.package.monetary_flow_unit,
                    monetary_stock_unit=self.package.monetary_stock_unit,
                )
            )

        by_body: dict[str, list[LocationProductionStateV1]] = {}
        for row in locations:
            body_id = location_to_body.get(row.location_id)
            if body_id is None:
                continue
            by_body.setdefault(str(body_id), []).append(row)
        bodies = []
        for body_id, members in sorted(by_body.items()):
            gross = self._sum_optional(members, "gross_output")
            intermediate = self._sum_optional(members, "intermediate_consumption")
            operating = self._sum_optional(members, "operating_cost")
            value_added = self._sum_optional(members, "value_added")
            bodies.append(
                BodyProductionStateV1(
                    aggregate_id=self._aggregate_id(
                        "BODY",
                        year,
                        body_id,
                    ),
                    year=int(year),
                    body_id=body_id,
                    location_count=len(members),
                    facility_count=sum(x.facility_count for x in members),
                    valuation_status=self._valuation_status_from_values(
                        gross,
                        intermediate,
                        operating,
                        value_added,
                    ),
                    gross_output=gross,
                    intermediate_consumption=intermediate,
                    operating_cost=operating,
                    value_added=value_added,
                    commissioned_investment=sum(
                        x.commissioned_investment for x in members
                    ),
                    opening_gross_productive_capital=sum(
                        x.opening_gross_productive_capital for x in members
                    ),
                    closing_gross_productive_capital=sum(
                        x.closing_gross_productive_capital for x in members
                    ),
                    monetary_flow_unit=self.package.monetary_flow_unit,
                    monetary_stock_unit=self.package.monetary_stock_unit,
                )
            )

        return tuple(sectors), tuple(locations), tuple(bodies)


__all__ = [
    "BodyProductionStateV1",
    "CONTRACT_VERSION",
    "ConstraintObservationV1",
    "FORMAT",
    "FacilityProductionModel",
    "FacilityProductionStateV1",
    "LocationProductionStateV1",
    "ProductionAccountingPackage",
    "ProductionAccountingRuntime",
    "SectorProductionStateV1",
    "ValueParameter",
    "ValuationParameters",
    "load_production_accounting_package",
    "load_production_accounting_path",
]
