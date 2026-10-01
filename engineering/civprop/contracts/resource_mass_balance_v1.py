"""CIVPROP Resource Mass Balance V1.

Physical stock-flow accounting for extractive resources.

This contract deliberately separates:
- evidence / actor-visible belief;
- evaluator-only physical realization;
- process-model capability;
- annual stock / extraction / recovery / inventory state.

UNKNOWN is never coerced to zero. Existing Method Lab present/grade compatibility
truth is not a Resource Mass Balance physical realization.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


FORMAT = "CIVPROP_RESOURCE_MASS_BALANCE_V1"
CONTRACT_VERSION = "1.0.0"
PHYSICAL_FORMAT = "CIVPROP_RESOURCE_PHYSICAL_REALIZATION_V1"
PHYSICAL_CONTRACT_VERSION = "1.0.0"

VALUE_STATUS = {"KNOWN", "UNKNOWN"}
REALIZATION_STATUS = {"KNOWN", "UNKNOWN", "ABSENT"}
PRODUCTION_STATUS = {
    "NO_ACTIVE_PROCESS_CAPACITY",
    "PHYSICAL_STATE_UNKNOWN",
    "PROCESS_MODEL_UNKNOWN",
    "PRODUCED",
    "DEPLETED",
}
FLOW_TYPES = {
    "EXTRACTED_FEED",
    "RECOVERED_PRODUCT",
    "PROCESS_TAILINGS",
    "INVENTORY_CONSUMPTION",
    "INVENTORY_OUTBOUND",
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
class ModelValue:
    status: str
    value: Optional[float]
    unit: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResourceDefinition:
    resource_id: str
    location_id: str
    region_id: Optional[str]
    material_family: str
    evidence_state: str
    evidence_scope: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResourceProcessModel:
    process_model_id: str
    project_archetype_id: str
    resource_id: str
    location_id: str
    extraction_feed_capacity_per_facility: ModelValue
    recovery_fraction: ModelValue
    processing_product_capacity_field: str
    parameter_status: str
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResourceMassBalancePackage:
    format: str
    contract_version: str
    package_id: str
    mass_unit: str
    rate_unit: str
    resources: tuple[ResourceDefinition, ...]
    process_models: tuple[ResourceProcessModel, ...]


@dataclass(frozen=True)
class ResourcePhysicalRealization:
    resource_id: str
    location_id: str
    realization_status: str
    stock_status: str
    opening_stock_tonnes: Optional[float]
    grade_status: str
    grade_mass_fraction: Optional[float]
    inventory_status: str
    opening_inventory_tonnes: Optional[float]
    provenance_refs: tuple[str, ...]


@dataclass(frozen=True)
class ResourcePhysicalRealizationPackage:
    format: str
    contract_version: str
    resources: tuple[ResourcePhysicalRealization, ...]


@dataclass(frozen=True)
class ResourceStateV1:
    resource_state_id: str
    year: int
    location_id: str
    resource_id: str
    material_family: str
    region_id: Optional[str]
    authority_class: str
    actor_visible: bool
    production_status: str
    opening_stock_tonnes: Optional[float]
    grade_mass_fraction: Optional[float]
    active_process_facilities: int
    extraction_feed_capacity_tpy: Optional[float]
    processing_product_capacity_tpy: float
    extracted_feed_tonnes: Optional[float]
    contained_resource_tonnes: Optional[float]
    recovered_product_tonnes: Optional[float]
    unrecovered_contained_tonnes: Optional[float]
    process_tailings_tonnes: Optional[float]
    opening_inventory_tonnes: Optional[float]
    consumption_tonnes: Optional[float]
    outbound_tonnes: Optional[float]
    closing_inventory_tonnes: Optional[float]
    closing_stock_tonnes: Optional[float]


@dataclass(frozen=True)
class ResourceFlowV1:
    resource_flow_id: str
    resource_state_id: str
    year: int
    location_id: str
    resource_id: str
    flow_type: str
    amount_tonnes: float
    facility_ids: tuple[str, ...]
    authority_class: str = "SIMULATED_PHYSICAL_FLOW"


@dataclass
class _MutablePhysical:
    realization_status: str
    stock_status: str
    stock_tonnes: Optional[float]
    grade_status: str
    grade_mass_fraction: Optional[float]
    inventory_status: str
    inventory_tonnes: Optional[float]


def _model_value(
    data: Mapping[str, Any],
    *,
    expected_unit: str,
    name: str,
    fraction: bool = False,
) -> ModelValue:
    status = str(data.get("status"))
    if status not in VALUE_STATUS:
        raise ValueError(f"{name}: invalid status")
    unit = str(data.get("unit") or "")
    if unit != expected_unit:
        raise ValueError(f"{name}: expected unit {expected_unit}")
    raw = data.get("value")
    if status == "UNKNOWN":
        if raw is not None:
            raise ValueError(f"{name}: UNKNOWN cannot carry value")
        value = None
    else:
        if raw is None:
            raise ValueError(f"{name}: KNOWN requires value")
        value = _fraction(raw, name) if fraction else _nonnegative(raw, name)
    return ModelValue(
        status=status,
        value=value,
        unit=unit,
        provenance_refs=_refs(data, name),
    )


def load_resource_mass_balance_package(
    data: Mapping[str, Any],
) -> ResourceMassBalancePackage:
    if data.get("format") != FORMAT or data.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("unexpected resource mass-balance contract")
    mass_unit = str(data.get("mass_unit") or "")
    rate_unit = str(data.get("rate_unit") or "")
    if mass_unit != "tonne" or rate_unit != "tonnes/year":
        raise ValueError("Resource Mass Balance V1 requires tonne and tonnes/year")

    resources = tuple(
        ResourceDefinition(
            resource_id=str(row["resource_id"]),
            location_id=str(row["location_id"]),
            region_id=(
                None if row.get("region_id") is None else str(row["region_id"])
            ),
            material_family=str(row["material_family"]),
            evidence_state=str(row["evidence_state"]),
            evidence_scope=str(row["evidence_scope"]),
            provenance_refs=_refs(row, "resource definition"),
        )
        for row in data.get("resources", ())
    )
    if not resources:
        raise ValueError("resource mass-balance package requires resources")

    process_models = tuple(
        ResourceProcessModel(
            process_model_id=str(row["process_model_id"]),
            project_archetype_id=str(row["project_archetype_id"]),
            resource_id=str(row["resource_id"]),
            location_id=str(row["location_id"]),
            extraction_feed_capacity_per_facility=_model_value(
                row["extraction_feed_capacity_per_facility"],
                expected_unit=rate_unit,
                name="extraction feed capacity",
            ),
            recovery_fraction=_model_value(
                row["recovery_fraction"],
                expected_unit="fraction",
                name="recovery fraction",
                fraction=True,
            ),
            processing_product_capacity_field=str(
                row["processing_product_capacity_field"]
            ),
            parameter_status=str(row["parameter_status"]),
            provenance_refs=_refs(row, "resource process model"),
        )
        for row in data.get("process_models", ())
    )
    if not process_models:
        raise ValueError("resource mass-balance package requires process models")

    resource_keys = [(x.resource_id, x.location_id) for x in resources]
    if len(resource_keys) != len(set(resource_keys)):
        raise ValueError("duplicate resource/location definition")
    process_ids = [x.process_model_id for x in process_models]
    if len(process_ids) != len(set(process_ids)):
        raise ValueError("duplicate resource process model")
    process_keys = [
        (x.resource_id, x.location_id) for x in process_models
    ]
    if len(process_keys) != len(set(process_keys)):
        raise ValueError("duplicate resource/location process model")
    defined = set(resource_keys)
    for process in process_models:
        if (process.resource_id, process.location_id) not in defined:
            raise ValueError("process model references undefined resource/location")
        if process.processing_product_capacity_field != "resource":
            raise ValueError("V1 only admits facility resource capacity as product capacity")

    return ResourceMassBalancePackage(
        format=FORMAT,
        contract_version=CONTRACT_VERSION,
        package_id=str(data["package_id"]),
        mass_unit=mass_unit,
        rate_unit=rate_unit,
        resources=resources,
        process_models=process_models,
    )


def load_resource_mass_balance_path(path: Path) -> ResourceMassBalancePackage:
    return load_resource_mass_balance_package(json.loads(Path(path).read_text()))


def load_resource_physical_realization(
    data: Mapping[str, Any],
) -> ResourcePhysicalRealizationPackage:
    if (
        data.get("format") != PHYSICAL_FORMAT
        or data.get("contract_version") != PHYSICAL_CONTRACT_VERSION
    ):
        raise ValueError("unexpected resource physical-realization contract")

    rows = []
    for row in data.get("resources", ()):
        realization_status = str(row["realization_status"])
        stock_status = str(row["stock_status"])
        grade_status = str(row["grade_status"])
        inventory_status = str(row["inventory_status"])
        if realization_status not in REALIZATION_STATUS:
            raise ValueError("invalid resource realization status")
        if stock_status not in VALUE_STATUS:
            raise ValueError("invalid resource stock status")
        if grade_status not in VALUE_STATUS:
            raise ValueError("invalid resource grade status")
        if inventory_status not in VALUE_STATUS:
            raise ValueError("invalid resource inventory status")

        raw_stock = row.get("opening_stock_tonnes")
        raw_grade = row.get("grade_mass_fraction")
        raw_inventory = row.get("opening_inventory_tonnes")
        if stock_status == "UNKNOWN":
            if raw_stock is not None:
                raise ValueError("UNKNOWN stock cannot carry quantity")
            stock = None
        else:
            if raw_stock is None:
                raise ValueError("KNOWN stock requires quantity")
            stock = _nonnegative(raw_stock, "opening stock")

        if grade_status == "UNKNOWN":
            if raw_grade is not None:
                raise ValueError("UNKNOWN grade cannot carry value")
            grade = None
        else:
            if raw_grade is None:
                raise ValueError("KNOWN grade requires value")
            grade = _fraction(raw_grade, "grade mass fraction")

        if inventory_status == "UNKNOWN":
            if raw_inventory is not None:
                raise ValueError("UNKNOWN inventory cannot carry quantity")
            inventory = None
        else:
            if raw_inventory is None:
                raise ValueError("KNOWN inventory requires quantity")
            inventory = _nonnegative(raw_inventory, "opening inventory")

        if realization_status == "ABSENT":
            if stock_status != "KNOWN" or stock != 0:
                raise ValueError("ABSENT realization requires known zero stock")
        if realization_status == "KNOWN":
            if stock_status != "KNOWN" or grade_status != "KNOWN":
                raise ValueError("KNOWN realization requires known stock and grade")

        rows.append(
            ResourcePhysicalRealization(
                resource_id=str(row["resource_id"]),
                location_id=str(row["location_id"]),
                realization_status=realization_status,
                stock_status=stock_status,
                opening_stock_tonnes=stock,
                grade_status=grade_status,
                grade_mass_fraction=grade,
                inventory_status=inventory_status,
                opening_inventory_tonnes=inventory,
                provenance_refs=_refs(row, "resource physical realization"),
            )
        )

    keys = [(x.resource_id, x.location_id) for x in rows]
    if not rows or len(keys) != len(set(keys)):
        raise ValueError("physical realization resources must be nonempty and unique")
    return ResourcePhysicalRealizationPackage(
        format=PHYSICAL_FORMAT,
        contract_version=PHYSICAL_CONTRACT_VERSION,
        resources=tuple(rows),
    )


class ResourceMassBalanceRuntime:
    def __init__(
        self,
        package: ResourceMassBalancePackage,
        physical: ResourcePhysicalRealizationPackage,
    ):
        self.package = package
        self.physical = physical
        definitions = {(x.resource_id, x.location_id) for x in package.resources}
        realizations = {(x.resource_id, x.location_id) for x in physical.resources}
        if definitions != realizations:
            raise ValueError("resource definitions and physical realization do not match")

        self._resource = {
            (x.resource_id, x.location_id): x for x in package.resources
        }
        self._process = {
            (x.resource_id, x.location_id): x for x in package.process_models
        }
        self._state = {
            (x.resource_id, x.location_id): _MutablePhysical(
                realization_status=x.realization_status,
                stock_status=x.stock_status,
                stock_tonnes=x.opening_stock_tonnes,
                grade_status=x.grade_status,
                grade_mass_fraction=x.grade_mass_fraction,
                inventory_status=x.inventory_status,
                inventory_tonnes=x.opening_inventory_tonnes,
            )
            for x in physical.resources
        }

    @staticmethod
    def state_id(year: int, resource_id: str, location_id: str) -> str:
        return _stable_id("rs", int(year), resource_id, location_id)

    @staticmethod
    def flow_id(
        year: int,
        resource_id: str,
        location_id: str,
        flow_type: str,
    ) -> str:
        return _stable_id(
            "rf",
            int(year),
            resource_id,
            location_id,
            flow_type,
        )

    def _flow(
        self,
        *,
        state: ResourceStateV1,
        flow_type: str,
        amount: float,
        facility_ids: Sequence[str],
    ) -> ResourceFlowV1:
        if flow_type not in FLOW_TYPES:
            raise ValueError("invalid resource flow type")
        return ResourceFlowV1(
            resource_flow_id=self.flow_id(
                state.year,
                state.resource_id,
                state.location_id,
                flow_type,
            ),
            resource_state_id=state.resource_state_id,
            year=state.year,
            location_id=state.location_id,
            resource_id=state.resource_id,
            flow_type=flow_type,
            amount_tonnes=_nonnegative(amount, "resource flow amount"),
            facility_ids=tuple(sorted(str(x) for x in facility_ids)),
        )

    def step(
        self,
        *,
        year: int,
        facilities: Sequence[Any],
        consumption_tonnes: Optional[Mapping[tuple[str, str], float]] = None,
        outbound_tonnes: Optional[Mapping[tuple[str, str], float]] = None,
    ) -> tuple[tuple[ResourceStateV1, ...], tuple[ResourceFlowV1, ...]]:
        consumption_tonnes = consumption_tonnes or {}
        outbound_tonnes = outbound_tonnes or {}
        states = []
        flows = []

        for key in sorted(self._resource):
            resource = self._resource[key]
            process = self._process[key]
            physical = self._state[key]
            active = tuple(
                facility
                for facility in facilities
                if getattr(facility, "status", None) == "ACTIVE"
                and getattr(facility, "project_archetype_id", None)
                == process.project_archetype_id
                and getattr(facility, "location_id", None) == process.location_id
            )
            facility_ids = tuple(
                sorted(str(getattr(x, "facility_id")) for x in active)
            )
            product_capacity = sum(
                float(
                    getattr(
                        getattr(facility, "capacities"),
                        process.processing_product_capacity_field,
                    )
                )
                for facility in active
            )
            opening_stock = physical.stock_tonnes
            opening_inventory = physical.inventory_tonnes

            extraction_capacity: Optional[float]
            if not active:
                extraction_capacity = 0.0
            elif process.extraction_feed_capacity_per_facility.status == "KNOWN":
                assert process.extraction_feed_capacity_per_facility.value is not None
                extraction_capacity = (
                    len(active)
                    * process.extraction_feed_capacity_per_facility.value
                )
            else:
                extraction_capacity = None

            known_physics = (
                physical.stock_status == "KNOWN"
                and physical.grade_status == "KNOWN"
                and physical.inventory_status == "KNOWN"
                and opening_stock is not None
                and physical.grade_mass_fraction is not None
                and opening_inventory is not None
            )
            known_process = (
                process.recovery_fraction.status == "KNOWN"
                and process.recovery_fraction.value is not None
                and extraction_capacity is not None
            )

            if not active or product_capacity <= 0:
                extracted = 0.0
                contained = 0.0
                recovered = 0.0
                unrecovered = 0.0
                tailings = 0.0
                consumed = (
                    0.0
                    if physical.inventory_status == "KNOWN"
                    else None
                )
                outbound = (
                    0.0
                    if physical.inventory_status == "KNOWN"
                    else None
                )
                closing_stock = opening_stock
                closing_inventory = opening_inventory
                status = "NO_ACTIVE_PROCESS_CAPACITY"
            elif not known_physics:
                extracted = contained = recovered = unrecovered = tailings = None
                consumed = outbound = None
                closing_stock = None
                closing_inventory = None
                status = "PHYSICAL_STATE_UNKNOWN"
                # Once an active process exists but physical quantities are unresolved,
                # later numeric stock/inventory cannot honestly remain known.
                physical.stock_status = "UNKNOWN"
                physical.stock_tonnes = None
                physical.inventory_status = "UNKNOWN"
                physical.inventory_tonnes = None
            elif not known_process:
                extracted = contained = recovered = unrecovered = tailings = None
                consumed = outbound = None
                closing_stock = None
                closing_inventory = None
                status = "PROCESS_MODEL_UNKNOWN"
                physical.stock_status = "UNKNOWN"
                physical.stock_tonnes = None
                physical.inventory_status = "UNKNOWN"
                physical.inventory_tonnes = None
            else:
                assert opening_stock is not None
                assert opening_inventory is not None
                assert physical.grade_mass_fraction is not None
                assert extraction_capacity is not None
                assert process.recovery_fraction.value is not None

                grade = physical.grade_mass_fraction
                recovery = process.recovery_fraction.value
                yield_fraction = grade * recovery
                if yield_fraction > 0:
                    process_feed_limit = product_capacity / yield_fraction
                    extracted = min(
                        opening_stock,
                        extraction_capacity,
                        process_feed_limit,
                    )
                else:
                    extracted = 0.0
                contained = extracted * grade
                recovered = contained * recovery
                unrecovered = contained - recovered
                tailings = extracted - recovered
                requested_consumption = _nonnegative(
                    consumption_tonnes.get(key, 0.0),
                    "resource consumption",
                )
                requested_outbound = _nonnegative(
                    outbound_tonnes.get(key, 0.0),
                    "resource outbound",
                )
                available_inventory = opening_inventory + recovered
                if requested_consumption + requested_outbound > available_inventory + 1e-12:
                    raise ValueError("resource inventory sink exceeds available inventory")
                consumed = requested_consumption
                outbound = requested_outbound
                closing_stock = opening_stock - extracted
                closing_inventory = (
                    available_inventory - consumed - outbound
                )
                physical.stock_tonnes = closing_stock
                physical.inventory_tonnes = closing_inventory
                status = "DEPLETED" if closing_stock <= 1e-12 else "PRODUCED"

            state = ResourceStateV1(
                resource_state_id=self.state_id(
                    year,
                    resource.resource_id,
                    resource.location_id,
                ),
                year=int(year),
                location_id=resource.location_id,
                resource_id=resource.resource_id,
                material_family=resource.material_family,
                region_id=resource.region_id,
                authority_class="EVALUATOR_PHYSICAL_STATE",
                actor_visible=False,
                production_status=status,
                opening_stock_tonnes=opening_stock,
                grade_mass_fraction=physical.grade_mass_fraction,
                active_process_facilities=len(active),
                extraction_feed_capacity_tpy=extraction_capacity,
                processing_product_capacity_tpy=product_capacity,
                extracted_feed_tonnes=extracted,
                contained_resource_tonnes=contained,
                recovered_product_tonnes=recovered,
                unrecovered_contained_tonnes=unrecovered,
                process_tailings_tonnes=tailings,
                opening_inventory_tonnes=opening_inventory,
                consumption_tonnes=consumed,
                outbound_tonnes=outbound,
                closing_inventory_tonnes=closing_inventory,
                closing_stock_tonnes=closing_stock,
            )
            self.validate_state(state)
            states.append(state)

            if recovered is not None and extracted is not None and tailings is not None:
                if extracted > 0:
                    flows.append(
                        self._flow(
                            state=state,
                            flow_type="EXTRACTED_FEED",
                            amount=extracted,
                            facility_ids=facility_ids,
                        )
                    )
                if recovered > 0:
                    flows.append(
                        self._flow(
                            state=state,
                            flow_type="RECOVERED_PRODUCT",
                            amount=recovered,
                            facility_ids=facility_ids,
                        )
                    )
                if tailings > 0:
                    flows.append(
                        self._flow(
                            state=state,
                            flow_type="PROCESS_TAILINGS",
                            amount=tailings,
                            facility_ids=facility_ids,
                        )
                    )
                if consumed and consumed > 0:
                    flows.append(
                        self._flow(
                            state=state,
                            flow_type="INVENTORY_CONSUMPTION",
                            amount=consumed,
                            facility_ids=facility_ids,
                        )
                    )
                if outbound and outbound > 0:
                    flows.append(
                        self._flow(
                            state=state,
                            flow_type="INVENTORY_OUTBOUND",
                            amount=outbound,
                            facility_ids=facility_ids,
                        )
                    )

        return tuple(states), tuple(flows)

    @staticmethod
    def validate_state(state: ResourceStateV1) -> None:
        if state.authority_class != "EVALUATOR_PHYSICAL_STATE":
            raise ValueError("resource state must remain evaluator-only")
        if state.actor_visible:
            raise ValueError("physical resource state cannot be actor-visible")
        if state.production_status not in PRODUCTION_STATUS:
            raise ValueError("invalid resource production status")
        if state.active_process_facilities < 0:
            raise ValueError("negative active resource facilities")
        _nonnegative(
            state.processing_product_capacity_tpy,
            "processing product capacity",
        )
        if state.extraction_feed_capacity_tpy is not None:
            _nonnegative(
                state.extraction_feed_capacity_tpy,
                "extraction feed capacity",
            )
        if state.grade_mass_fraction is not None:
            _fraction(state.grade_mass_fraction, "resource grade")

        quantities = (
            state.opening_stock_tonnes,
            state.extracted_feed_tonnes,
            state.contained_resource_tonnes,
            state.recovered_product_tonnes,
            state.unrecovered_contained_tonnes,
            state.process_tailings_tonnes,
            state.opening_inventory_tonnes,
            state.consumption_tonnes,
            state.outbound_tonnes,
            state.closing_inventory_tonnes,
            state.closing_stock_tonnes,
        )
        for value in quantities:
            if value is not None:
                _nonnegative(value, "resource state quantity")

        known_chain = all(
            value is not None
            for value in (
                state.opening_stock_tonnes,
                state.grade_mass_fraction,
                state.extracted_feed_tonnes,
                state.contained_resource_tonnes,
                state.recovered_product_tonnes,
                state.unrecovered_contained_tonnes,
                state.process_tailings_tonnes,
                state.opening_inventory_tonnes,
                state.consumption_tonnes,
                state.outbound_tonnes,
                state.closing_inventory_tonnes,
                state.closing_stock_tonnes,
            )
        )
        if not known_chain:
            return

        assert state.opening_stock_tonnes is not None
        assert state.grade_mass_fraction is not None
        assert state.extracted_feed_tonnes is not None
        assert state.contained_resource_tonnes is not None
        assert state.recovered_product_tonnes is not None
        assert state.unrecovered_contained_tonnes is not None
        assert state.process_tailings_tonnes is not None
        assert state.opening_inventory_tonnes is not None
        assert state.consumption_tonnes is not None
        assert state.outbound_tonnes is not None
        assert state.closing_inventory_tonnes is not None
        assert state.closing_stock_tonnes is not None

        if not math.isclose(
            state.opening_stock_tonnes,
            state.extracted_feed_tonnes + state.closing_stock_tonnes,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("resource stock mass balance does not close")
        if not math.isclose(
            state.contained_resource_tonnes,
            state.extracted_feed_tonnes * state.grade_mass_fraction,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("contained resource does not match feed * grade")
        if not math.isclose(
            state.contained_resource_tonnes,
            state.recovered_product_tonnes
            + state.unrecovered_contained_tonnes,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("resource recovery mass balance does not close")
        if not math.isclose(
            state.process_tailings_tonnes,
            state.extracted_feed_tonnes - state.recovered_product_tonnes,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("resource tailings mass balance does not close")
        if not math.isclose(
            state.opening_inventory_tonnes + state.recovered_product_tonnes,
            state.consumption_tonnes
            + state.outbound_tonnes
            + state.closing_inventory_tonnes,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("resource inventory mass balance does not close")
        if (
            state.extraction_feed_capacity_tpy is not None
            and state.extracted_feed_tonnes
            > state.extraction_feed_capacity_tpy + 1e-9
        ):
            raise ValueError("resource extraction exceeds extraction capacity")
        if (
            state.recovered_product_tonnes
            > state.processing_product_capacity_tpy + 1e-9
        ):
            raise ValueError("resource product exceeds processing capacity")


__all__ = [
    "CONTRACT_VERSION",
    "FLOW_TYPES",
    "FORMAT",
    "PHYSICAL_CONTRACT_VERSION",
    "PHYSICAL_FORMAT",
    "ModelValue",
    "ResourceDefinition",
    "ResourceFlowV1",
    "ResourceMassBalancePackage",
    "ResourceMassBalanceRuntime",
    "ResourcePhysicalRealization",
    "ResourcePhysicalRealizationPackage",
    "ResourceProcessModel",
    "ResourceStateV1",
    "load_resource_mass_balance_package",
    "load_resource_mass_balance_path",
    "load_resource_physical_realization",
]
