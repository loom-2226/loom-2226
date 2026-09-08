from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Sequence, Tuple


MANUFACTURING_CONTEXT_VERSION = "LOOM_MANUFACTURING_CAPABILITY_CONTEXT_v0.1"
FUNCTIONAL_REGION_VERSION = "LOOM_FUNCTIONAL_REGION_v0.1"
MANUFACTURING_CONTEXT_AUTHORITY = "MANUFACTURING_CONTEXT_ONLY"
FUNCTIONAL_REGION_AUTHORITY = "FUNCTIONAL_DECOMPOSITION_ONLY"

MANUFACTURING_CLASSES = frozenset({"BULK_CONSTRUCTION", "PRECISION_STRUCTURAL", "EXOTIC_FUNCTIONAL"})
CAPABILITY_STATUSES = frozenset({"AVAILABLE", "UNAVAILABLE", "OPEN"})


class ManufacturingRegionError(ValueError):
    """Fail-closed error for manufacturing-capability or functional-region contracts."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManufacturingRegionError(f"{label} must be a non-empty string")
    return value.strip()


def _tuple(values: Sequence[str], label: str, *, allow_empty: bool = True) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ManufacturingRegionError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if not allow_empty and not cleaned:
        raise ManufacturingRegionError(f"{label} must not be empty")
    if len(cleaned) != len(set(cleaned)):
        raise ManufacturingRegionError(f"{label} must contain unique values")
    return cleaned


def _positive_optional(value: float | None, label: str) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ManufacturingRegionError(f"{label} must be finite and positive")
    return number


def _optional_bool(value: bool | None, label: str) -> bool | None:
    if value is None or isinstance(value, bool):
        return value
    raise ManufacturingRegionError(f"{label} must be bool or None")


@dataclass(frozen=True)
class MaterialSystemCapability:
    material_system_id: str
    status: str
    manufacturing_class: str
    feedstock_classes: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]


@dataclass(frozen=True)
class ManufacturingProcessCapability:
    process_id: str
    status: str
    manufacturing_class: str
    max_build_envelope_m: Tuple[float, float, float] | None
    minimum_feature_m: float | None
    material_grading_supported: bool | None
    multimaterial_supported: bool | None
    embedded_channels_supported: bool | None
    embedded_sensing_supported: bool | None
    in_situ_heat_treatment_supported: bool | None
    inspection_resolution_m: float | None
    repair_processes: Tuple[str, ...]
    certified_process_families: Tuple[str, ...]
    precision_cost_class: str
    provenance_refs: Tuple[str, ...]


@dataclass(frozen=True)
class ManufacturingCapabilityContext:
    context_id: str
    context_date: str
    industrial_context_hash: str
    material_systems: Tuple[MaterialSystemCapability, ...]
    processes: Tuple[ManufacturingProcessCapability, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = MANUFACTURING_CONTEXT_AUTHORITY


@dataclass(frozen=True)
class FunctionalRegion:
    region_id: str
    required_functions: Tuple[str, ...]
    load_interfaces: Tuple[str, ...]
    thermal_interfaces: Tuple[str, ...]
    fluid_interfaces: Tuple[str, ...]
    electrical_interfaces: Tuple[str, ...]
    pressure_boundary_role: str
    material_system_candidates: Tuple[str, ...]
    manufacturing_process_candidates: Tuple[str, ...]
    repairability_requirement: str
    inspection_requirement: str
    replaceable_interfaces: Tuple[str, ...]
    embedded_sensor_requirement: str
    provenance_refs: Tuple[str, ...]
    authority_status: str = FUNCTIONAL_REGION_AUTHORITY


def validate_material_system(row: MaterialSystemCapability) -> None:
    _text(row.material_system_id, "material_system_id")
    if row.status not in CAPABILITY_STATUSES:
        raise ManufacturingRegionError(f"unsupported material-system status {row.status}")
    if row.manufacturing_class not in MANUFACTURING_CLASSES:
        raise ManufacturingRegionError(f"unsupported manufacturing_class {row.manufacturing_class}")
    _tuple(row.feedstock_classes, "feedstock_classes", allow_empty=False)
    _tuple(row.provenance_refs, "provenance_refs", allow_empty=False)


def validate_process(row: ManufacturingProcessCapability) -> None:
    _text(row.process_id, "process_id")
    if row.status not in CAPABILITY_STATUSES:
        raise ManufacturingRegionError(f"unsupported process status {row.status}")
    if row.manufacturing_class not in MANUFACTURING_CLASSES:
        raise ManufacturingRegionError(f"unsupported manufacturing_class {row.manufacturing_class}")
    if row.max_build_envelope_m is not None:
        if len(row.max_build_envelope_m) != 3:
            raise ManufacturingRegionError("max_build_envelope_m must have exactly 3 values")
        for value in row.max_build_envelope_m:
            _positive_optional(value, "max_build_envelope_m value")
    _positive_optional(row.minimum_feature_m, "minimum_feature_m")
    _optional_bool(row.material_grading_supported, "material_grading_supported")
    _optional_bool(row.multimaterial_supported, "multimaterial_supported")
    _optional_bool(row.embedded_channels_supported, "embedded_channels_supported")
    _optional_bool(row.embedded_sensing_supported, "embedded_sensing_supported")
    _optional_bool(row.in_situ_heat_treatment_supported, "in_situ_heat_treatment_supported")
    _positive_optional(row.inspection_resolution_m, "inspection_resolution_m")
    _tuple(row.repair_processes, "repair_processes")
    _tuple(row.certified_process_families, "certified_process_families")
    _text(row.precision_cost_class, "precision_cost_class")
    _tuple(row.provenance_refs, "provenance_refs", allow_empty=False)


def validate_context(context: ManufacturingCapabilityContext) -> None:
    _text(context.context_id, "context_id")
    _text(context.context_date, "context_date")
    digest = _text(context.industrial_context_hash, "industrial_context_hash")
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest.lower()):
        raise ManufacturingRegionError("industrial_context_hash must be a 64-character hex digest")
    if context.authority_status != MANUFACTURING_CONTEXT_AUTHORITY:
        raise ManufacturingRegionError("manufacturing context may not claim engineering or canon authority")
    _tuple(context.provenance_refs, "provenance_refs", allow_empty=False)

    material_ids = set()
    for row in context.material_systems:
        validate_material_system(row)
        if row.material_system_id in material_ids:
            raise ManufacturingRegionError(f"duplicate material_system_id {row.material_system_id}")
        material_ids.add(row.material_system_id)

    process_ids = set()
    for row in context.processes:
        validate_process(row)
        if row.process_id in process_ids:
            raise ManufacturingRegionError(f"duplicate process_id {row.process_id}")
        process_ids.add(row.process_id)


def validate_region(region: FunctionalRegion, context: ManufacturingCapabilityContext) -> None:
    validate_context(context)
    _text(region.region_id, "region_id")
    if region.authority_status != FUNCTIONAL_REGION_AUTHORITY:
        raise ManufacturingRegionError("functional region may not claim engineering or canon authority")
    for field, required in (
        ("required_functions", True),
        ("load_interfaces", False),
        ("thermal_interfaces", False),
        ("fluid_interfaces", False),
        ("electrical_interfaces", False),
        ("material_system_candidates", False),
        ("manufacturing_process_candidates", False),
        ("replaceable_interfaces", False),
        ("provenance_refs", True),
    ):
        _tuple(getattr(region, field), field, allow_empty=not required)
    for field in (
        "pressure_boundary_role",
        "repairability_requirement",
        "inspection_requirement",
        "embedded_sensor_requirement",
    ):
        _text(getattr(region, field), field)

    known_materials = {row.material_system_id for row in context.material_systems}
    unknown_materials = sorted(set(region.material_system_candidates) - known_materials)
    if unknown_materials:
        raise ManufacturingRegionError(
            f"functional region references unknown material systems: {', '.join(unknown_materials)}"
        )

    known_processes = {row.process_id for row in context.processes}
    unknown_processes = sorted(set(region.manufacturing_process_candidates) - known_processes)
    if unknown_processes:
        raise ManufacturingRegionError(
            f"functional region references unknown manufacturing processes: {', '.join(unknown_processes)}"
        )


def canonical_json(row: object) -> str:
    return json.dumps(asdict(row), sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(row: object) -> str:
    return hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
