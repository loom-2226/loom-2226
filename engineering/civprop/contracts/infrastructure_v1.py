"""CIVPROP Infrastructure Archetype Contract V1.

Separates stable infrastructure semantics from versioned numeric parameterizations.
The catalog is intentionally not a list of Atlas answers. Archetypes are reusable
capacity-bearing modules; final Atlas facility identities/types may aggregate or
co-locate several modules.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping


CATALOG_FORMAT = "CIVPROP_INFRASTRUCTURE_ARCHETYPE_CATALOG_V1"

ALLOWED_PLACEMENTS = frozenset({"SURFACE", "ORBITAL", "FREE_SPACE"})
CAPACITY_DIMENSIONS = frozenset(
    {"power", "resource", "industrial", "habitat", "shipyard", "transport"}
)
CAPABILITY_TAGS = frozenset(
    {
        "TRANSPORT",
        "POWER",
        "HABITATION",
        "RESOURCE_EXTRACTION",
        "RESOURCE_PROCESSING",
        "MANUFACTURING",
        "CONSTRUCTION",
    }
)

PARAMETER_STATUS_METHOD_LAB = "SYNTHETIC_METHOD_FIXTURE"
ALLOWED_PARAMETER_STATUS = frozenset(
    {
        PARAMETER_STATUS_METHOD_LAB,
        "QUALIFIED_MODEL",
        "SCENARIO_ASSUMPTION",
    }
)


@dataclass(frozen=True)
class InfrastructureArchetype:
    archetype_id: str
    family: str
    module_semantics: str
    allowed_placements: tuple[str, ...]
    required_capability_tags: tuple[str, ...]
    input_capacity_dimensions: tuple[str, ...]
    output_capacity_dimensions: tuple[str, ...]
    materialization_note: str


@dataclass(frozen=True)
class InfrastructureParameterization:
    parameter_set_id: str
    archetype_id: str
    parameter_status: str
    scope: str
    capital_cost: float
    capital_unit: str
    construction_lag_years: int
    minimum_input_capacities: Mapping[str, float]
    output_capacities: Mapping[str, float]
    provenance_ref: str


@dataclass(frozen=True)
class InfrastructureCatalog:
    format: str
    catalog_id: str
    assumptions: tuple[str, ...]
    archetypes: tuple[InfrastructureArchetype, ...]
    parameterizations: tuple[InfrastructureParameterization, ...]

    def by_id(self, archetype_id: str) -> InfrastructureArchetype:
        for archetype in self.archetypes:
            if archetype.archetype_id == archetype_id:
                return archetype
        raise KeyError(archetype_id)

    def parameterization(
        self,
        archetype_id: str,
        parameter_set_id: str,
    ) -> InfrastructureParameterization:
        for parameterization in self.parameterizations:
            if (
                parameterization.archetype_id == archetype_id
                and parameterization.parameter_set_id == parameter_set_id
            ):
                return parameterization
        raise KeyError((archetype_id, parameter_set_id))


def _number_map(value: Mapping[str, object]) -> dict[str, float]:
    return {str(key): float(number) for key, number in value.items()}


def load_infrastructure_catalog(path: Path) -> InfrastructureCatalog:
    raw = json.loads(Path(path).read_text())
    catalog = InfrastructureCatalog(
        format=raw["format"],
        catalog_id=raw["catalog_id"],
        assumptions=tuple(raw.get("assumptions", ())),
        archetypes=tuple(
            InfrastructureArchetype(
                archetype_id=x["archetype_id"],
                family=x["family"],
                module_semantics=x["module_semantics"],
                allowed_placements=tuple(x["allowed_placements"]),
                required_capability_tags=tuple(x["required_capability_tags"]),
                input_capacity_dimensions=tuple(x["input_capacity_dimensions"]),
                output_capacity_dimensions=tuple(x["output_capacity_dimensions"]),
                materialization_note=x["materialization_note"],
            )
            for x in raw["archetypes"]
        ),
        parameterizations=tuple(
            InfrastructureParameterization(
                parameter_set_id=x["parameter_set_id"],
                archetype_id=x["archetype_id"],
                parameter_status=x["parameter_status"],
                scope=x["scope"],
                capital_cost=float(x["capital_cost"]),
                capital_unit=x["capital_unit"],
                construction_lag_years=int(x["construction_lag_years"]),
                minimum_input_capacities=_number_map(
                    x.get("minimum_input_capacities", {})
                ),
                output_capacities=_number_map(x.get("output_capacities", {})),
                provenance_ref=x["provenance_ref"],
            )
            for x in raw["parameterizations"]
        ),
    )
    validate_infrastructure_catalog(catalog)
    return catalog


def validate_infrastructure_catalog(catalog: InfrastructureCatalog) -> None:
    if catalog.format != CATALOG_FORMAT:
        raise ValueError(f"unexpected catalog format: {catalog.format}")
    if not catalog.catalog_id:
        raise ValueError("catalog_id is required")
    if not catalog.assumptions:
        raise ValueError("catalog must preserve explicit assumptions")

    archetype_ids = [x.archetype_id for x in catalog.archetypes]
    if len(archetype_ids) != len(set(archetype_ids)):
        raise ValueError("duplicate infrastructure archetype_id")

    archetype_by_id = {x.archetype_id: x for x in catalog.archetypes}

    for archetype in catalog.archetypes:
        if not archetype.archetype_id or not archetype.family:
            raise ValueError("archetype identity/family is required")
        if archetype.module_semantics != "CAPACITY_BEARING_MODULE":
            raise ValueError("V1 archetypes must be capacity-bearing modules")
        if not archetype.allowed_placements:
            raise ValueError(f"{archetype.archetype_id}: no allowed placements")
        if not set(archetype.allowed_placements) <= ALLOWED_PLACEMENTS:
            raise ValueError(f"{archetype.archetype_id}: invalid placement")
        if not set(archetype.required_capability_tags) <= CAPABILITY_TAGS:
            raise ValueError(f"{archetype.archetype_id}: invalid capability tag")
        if not set(archetype.input_capacity_dimensions) <= CAPACITY_DIMENSIONS:
            raise ValueError(f"{archetype.archetype_id}: invalid input capacity dimension")
        if not archetype.output_capacity_dimensions:
            raise ValueError(f"{archetype.archetype_id}: no output capacity dimension")
        if not set(archetype.output_capacity_dimensions) <= CAPACITY_DIMENSIONS:
            raise ValueError(f"{archetype.archetype_id}: invalid output capacity dimension")
        if not archetype.materialization_note:
            raise ValueError(f"{archetype.archetype_id}: missing materialization note")

    parameter_keys = [
        (x.parameter_set_id, x.archetype_id) for x in catalog.parameterizations
    ]
    if len(parameter_keys) != len(set(parameter_keys)):
        raise ValueError("duplicate parameter-set/archetype pair")

    for parameterization in catalog.parameterizations:
        if parameterization.archetype_id not in archetype_by_id:
            raise ValueError(
                f"parameterization references unknown archetype: "
                f"{parameterization.archetype_id}"
            )
        if parameterization.parameter_status not in ALLOWED_PARAMETER_STATUS:
            raise ValueError("invalid parameter status")
        if not parameterization.parameter_set_id:
            raise ValueError("parameter_set_id is required")
        if not parameterization.scope:
            raise ValueError("parameterization scope is required")
        if parameterization.capital_cost <= 0:
            raise ValueError("capital_cost must be positive")
        if not parameterization.capital_unit:
            raise ValueError("capital_unit is required")
        if parameterization.construction_lag_years < 1:
            raise ValueError("construction lag must be >= 1")
        if not parameterization.provenance_ref:
            raise ValueError("provenance_ref is required")

        archetype = archetype_by_id[parameterization.archetype_id]
        input_keys = set(parameterization.minimum_input_capacities)
        output_keys = set(parameterization.output_capacities)
        if not input_keys <= CAPACITY_DIMENSIONS:
            raise ValueError("parameterization has invalid input capacity key")
        if not output_keys <= CAPACITY_DIMENSIONS:
            raise ValueError("parameterization has invalid output capacity key")
        if any(value < 0 for value in parameterization.minimum_input_capacities.values()):
            raise ValueError("negative minimum input capacity")
        if any(value < 0 for value in parameterization.output_capacities.values()):
            raise ValueError("negative output capacity")
        if not output_keys <= set(archetype.output_capacity_dimensions):
            raise ValueError(
                f"{parameterization.archetype_id}: parameterized output not declared "
                "by archetype semantics"
            )
        if not input_keys <= set(archetype.input_capacity_dimensions):
            raise ValueError(
                f"{parameterization.archetype_id}: parameterized input not declared "
                "by archetype semantics"
            )
