"""CIVPROP Project Economics V1.

A typed parameter-set boundary separating qualified references, scenario assumptions,
uncertainty, scale behavior and technology-year adjustments from the runtime project
decision model.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import json
from typing import Any, Mapping


FORMAT = "CIVPROP_PROJECT_ECONOMICS_V1"
CONTRACT_VERSION = "1.0.0"
QUANTITY_STATUS = {"QUALIFIED_REFERENCE", "SCENARIO_ASSUMPTION"}
PROJECT_STATUS = {
    "SCENARIO_ASSUMPTION",
    "HYBRID_SCENARIO_WITH_QUALIFIED_COMPONENT",
}


def _finite_positive(value: Any, name: str, *, allow_zero: bool = False) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    if allow_zero:
        if out < 0:
            raise ValueError(f"{name} must be nonnegative")
    elif out <= 0:
        raise ValueError(f"{name} must be positive")
    return out


@dataclass(frozen=True)
class QuantityRange:
    low: float
    nominal: float
    high: float
    unit: str
    status: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class LagRange:
    low: int
    nominal: int
    high: int
    unit: str
    status: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ScaleModel:
    reference_scale: float
    capital_exponent: float
    output_exponent: float
    lag_exponent: float


@dataclass(frozen=True)
class EpochAdjustment:
    year: int
    cost_multiplier: float
    capacity_multiplier: float
    lag_multiplier: float
    status: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ProjectParameter:
    project_archetype_id: str
    project_kind: str
    parameter_status: str
    capital_cost: QuantityRange
    construction_lag: LagRange
    outputs: Mapping[str, QuantityRange]
    prerequisites: Mapping[str, QuantityRange]
    scale_model: ScaleModel
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ProjectEconomicsPackage:
    format: str
    contract_version: str
    parameter_set_id: str
    scope: str
    capital_unit: str
    dimension_units: Mapping[str, str]
    epoch_adjustments: tuple[EpochAdjustment, ...]
    projects: tuple[ProjectParameter, ...]
    domain_model_boundaries: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class ResolvedProjectEconomics:
    project_archetype_id: str
    project_kind: str
    year: int
    scale: float
    capital_cost: float
    capital_unit: str
    construction_lag_years: int
    output_capacities: Mapping[str, float]
    minimum_input_capacities: Mapping[str, float]
    parameter_status: str


def _quantity(
    data: Mapping[str, Any],
    *,
    expected_unit: str | None = None,
    name: str,
) -> QuantityRange:
    low = _finite_positive(data["low"], f"{name}.low", allow_zero=True)
    nominal = _finite_positive(data["nominal"], f"{name}.nominal", allow_zero=True)
    high = _finite_positive(data["high"], f"{name}.high", allow_zero=True)
    if not low <= nominal <= high:
        raise ValueError(f"{name}: expected low <= nominal <= high")
    unit = str(data.get("unit") or "")
    if not unit:
        raise ValueError(f"{name}: unit required")
    if expected_unit is not None and unit != expected_unit:
        raise ValueError(f"{name}: unit mismatch")
    status = str(data["status"])
    if status not in QUANTITY_STATUS:
        raise ValueError(f"{name}: invalid quantity status")
    refs = tuple(data.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name}: provenance required")
    return QuantityRange(low, nominal, high, unit, status, refs)


def _lag(data: Mapping[str, Any], name: str) -> LagRange:
    low = int(data["low"])
    nominal = int(data["nominal"])
    high = int(data["high"])
    if not 1 <= low <= nominal <= high:
        raise ValueError(f"{name}: invalid construction-lag range")
    if data.get("unit") != "year":
        raise ValueError(f"{name}: lag unit must be year")
    status = str(data["status"])
    if status not in QUANTITY_STATUS:
        raise ValueError(f"{name}: invalid lag status")
    refs = tuple(data.get("provenance_refs", ()))
    if not refs:
        raise ValueError(f"{name}: provenance required")
    return LagRange(low, nominal, high, "year", status, refs)


def load_project_economics_package(
    data: Mapping[str, Any],
) -> ProjectEconomicsPackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected project-economics contract")
    capital_unit = str(data.get("capital_unit") or "")
    if not capital_unit:
        raise ValueError("capital_unit required")
    dimension_units = {
        str(k): str(v) for k, v in data.get("dimension_units", {}).items()
    }
    if not dimension_units:
        raise ValueError("dimension_units required")

    epochs: list[EpochAdjustment] = []
    for row in data.get("epoch_adjustments", ()):
        status = str(row["status"])
        if status not in QUANTITY_STATUS:
            raise ValueError("invalid epoch-adjustment status")
        refs = tuple(row.get("provenance_refs", ()))
        if not refs:
            raise ValueError("epoch adjustment requires provenance")
        epochs.append(
            EpochAdjustment(
                year=int(row["year"]),
                cost_multiplier=_finite_positive(
                    row["cost_multiplier"], "cost multiplier"
                ),
                capacity_multiplier=_finite_positive(
                    row["capacity_multiplier"], "capacity multiplier"
                ),
                lag_multiplier=_finite_positive(
                    row["lag_multiplier"], "lag multiplier"
                ),
                status=status,
                provenance_refs=refs,
            )
        )
    if not epochs or [x.year for x in epochs] != sorted({x.year for x in epochs}):
        raise ValueError("epoch adjustments must be unique and sorted")

    projects: list[ProjectParameter] = []
    for row in data.get("projects", ()):
        project_id = str(row["project_archetype_id"])
        status = str(row["parameter_status"])
        if status not in PROJECT_STATUS:
            raise ValueError(f"{project_id}: invalid parameter status")
        refs = tuple(row.get("provenance_refs", ()))
        if not refs:
            raise ValueError(f"{project_id}: provenance required")
        outputs = {
            str(dim): _quantity(
                q,
                expected_unit=dimension_units.get(str(dim)),
                name=f"{project_id}.outputs.{dim}",
            )
            for dim, q in row.get("outputs", {}).items()
        }
        prereqs = {
            str(dim): _quantity(
                q,
                expected_unit=dimension_units.get(str(dim)),
                name=f"{project_id}.prerequisites.{dim}",
            )
            for dim, q in row.get("prerequisites", {}).items()
        }
        for dim in (*outputs.keys(), *prereqs.keys()):
            if dim not in dimension_units:
                raise ValueError(f"{project_id}: unknown capacity dimension {dim}")
        scale = row["scale_model"]
        scale_model = ScaleModel(
            reference_scale=_finite_positive(
                scale["reference_scale"], f"{project_id}.reference_scale"
            ),
            capital_exponent=_finite_positive(
                scale["capital_exponent"], f"{project_id}.capital_exponent"
            ),
            output_exponent=_finite_positive(
                scale["output_exponent"], f"{project_id}.output_exponent"
            ),
            lag_exponent=_finite_positive(
                scale["lag_exponent"],
                f"{project_id}.lag_exponent",
                allow_zero=True,
            ),
        )
        projects.append(
            ProjectParameter(
                project_archetype_id=project_id,
                project_kind=str(row["project_kind"]),
                parameter_status=status,
                capital_cost=_quantity(
                    row["capital_cost"],
                    expected_unit=capital_unit,
                    name=f"{project_id}.capital_cost",
                ),
                construction_lag=_lag(
                    row["construction_lag"],
                    f"{project_id}.construction_lag",
                ),
                outputs=outputs,
                prerequisites=prereqs,
                scale_model=scale_model,
                provenance_refs=refs,
            )
        )

    ids = [x.project_archetype_id for x in projects]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("project parameter ids must be nonempty and unique")

    return ProjectEconomicsPackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        parameter_set_id=str(data["parameter_set_id"]),
        scope=str(data["scope"]),
        capital_unit=capital_unit,
        dimension_units=dimension_units,
        epoch_adjustments=tuple(epochs),
        projects=tuple(projects),
        domain_model_boundaries=tuple(data.get("domain_model_boundaries", ())),
    )


def load_project_economics_path(path: Path) -> ProjectEconomicsPackage:
    return load_project_economics_package(json.loads(Path(path).read_text()))


class ProjectEconomicsRuntime:
    def __init__(self, package: ProjectEconomicsPackage):
        self.package = package
        self._projects = {x.project_archetype_id: x for x in package.projects}

    def _epoch(self, year: int) -> tuple[float, float, float]:
        points = self.package.epoch_adjustments
        if year <= points[0].year:
            p = points[0]
            return p.cost_multiplier, p.capacity_multiplier, p.lag_multiplier
        if year >= points[-1].year:
            p = points[-1]
            return p.cost_multiplier, p.capacity_multiplier, p.lag_multiplier
        left = points[0]
        right = points[-1]
        for a, b in zip(points, points[1:]):
            if a.year <= year <= b.year:
                left, right = a, b
                break
        fraction = (year - left.year) / (right.year - left.year)
        lerp = lambda x, y: x + fraction * (y - x)
        return (
            lerp(left.cost_multiplier, right.cost_multiplier),
            lerp(left.capacity_multiplier, right.capacity_multiplier),
            lerp(left.lag_multiplier, right.lag_multiplier),
        )

    def resolve(
        self,
        project_archetype_id: str,
        *,
        year: int,
        scale: float = 1.0,
    ) -> ResolvedProjectEconomics:
        if project_archetype_id not in self._projects:
            raise KeyError(project_archetype_id)
        project = self._projects[project_archetype_id]
        scale = _finite_positive(scale, "project scale")
        relative_scale = scale / project.scale_model.reference_scale
        cost_mult, capacity_mult, lag_mult = self._epoch(int(year))
        capital = (
            project.capital_cost.nominal
            * cost_mult
            * relative_scale ** project.scale_model.capital_exponent
        )
        lag = max(
            1,
            math.ceil(
                project.construction_lag.nominal
                * lag_mult
                * relative_scale ** project.scale_model.lag_exponent
            ),
        )
        outputs = {
            dim: q.nominal
            * capacity_mult
            * relative_scale ** project.scale_model.output_exponent
            for dim, q in project.outputs.items()
        }
        prereqs = {
            dim: q.nominal
            * capacity_mult
            * relative_scale ** project.scale_model.output_exponent
            for dim, q in project.prerequisites.items()
        }
        return ResolvedProjectEconomics(
            project_archetype_id=project.project_archetype_id,
            project_kind=project.project_kind,
            year=int(year),
            scale=scale,
            capital_cost=capital,
            capital_unit=self.package.capital_unit,
            construction_lag_years=lag,
            output_capacities=outputs,
            minimum_input_capacities=prereqs,
            parameter_status=project.parameter_status,
        )


__all__ = [
    "CONTRACT_VERSION",
    "FORMAT",
    "EpochAdjustment",
    "LagRange",
    "ProjectEconomicsPackage",
    "ProjectEconomicsRuntime",
    "ProjectParameter",
    "QuantityRange",
    "ResolvedProjectEconomics",
    "ScaleModel",
    "load_project_economics_package",
    "load_project_economics_path",
]
