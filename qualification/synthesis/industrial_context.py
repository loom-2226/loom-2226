from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Mapping, Sequence, Tuple


CONTEXT_VERSION = "LOOM_INDUSTRIAL_CONTEXT_v0.1"


class IndustrialContextError(ValueError):
    """Fail-closed error for invalid technology/industrial contexts."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IndustrialContextError(f"{label} must be a non-empty string")
    return value.strip()


def _unique(values: Sequence[str], label: str) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise IndustrialContextError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if len(set(cleaned)) != len(cleaned):
        raise IndustrialContextError(f"{label} must contain unique values")
    return cleaned


@dataclass(frozen=True)
class TechnologyRuleRef:
    rule_id: str
    status: str
    provenance_ref: str


@dataclass(frozen=True)
class MaterialAvailability:
    material_id: str
    status: str
    max_quantity: float | None
    quantity_unit: str | None
    provenance_ref: str


@dataclass(frozen=True)
class ManufacturingCapability:
    capability_id: str
    status: str
    max_envelope_m: Tuple[float, float, float] | None
    provenance_ref: str


@dataclass(frozen=True)
class IndustrialContext:
    context_id: str
    context_date: str
    technology_rules: Tuple[TechnologyRuleRef, ...]
    materials: Tuple[MaterialAvailability, ...]
    manufacturing_capabilities: Tuple[ManufacturingCapability, ...]
    supplier_component_ids: Tuple[str, ...]
    prohibited_component_ids: Tuple[str, ...]
    economic_constraints: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str
    context_hash: str


def build_industrial_context(
    *,
    context_id: str,
    context_date: str,
    technology_rules: Sequence[TechnologyRuleRef] = (),
    materials: Sequence[MaterialAvailability] = (),
    manufacturing_capabilities: Sequence[ManufacturingCapability] = (),
    supplier_component_ids: Sequence[str] = (),
    prohibited_component_ids: Sequence[str] = (),
    economic_constraints: Sequence[str] = (),
    provenance_refs: Sequence[str] = (),
    authority_status: str = "QUALIFICATION_ONLY",
) -> IndustrialContext:
    context_id = _text(context_id, "context_id")
    context_date = _text(context_date, "context_date")
    authority_status = _text(authority_status, "authority_status")
    suppliers = _unique(supplier_component_ids, "supplier_component_ids")
    prohibited = _unique(prohibited_component_ids, "prohibited_component_ids")
    if set(suppliers) & set(prohibited):
        raise IndustrialContextError("component cannot be both supplied and prohibited")
    economics = _unique(economic_constraints, "economic_constraints")
    provenance = _unique(provenance_refs, "provenance_refs")

    seen_rules = set()
    clean_rules = []
    for row in technology_rules:
        rid = _text(row.rule_id, "rule_id")
        _text(row.status, "technology rule status")
        _text(row.provenance_ref, "technology rule provenance_ref")
        if rid in seen_rules:
            raise IndustrialContextError(f"duplicate technology rule {rid}")
        seen_rules.add(rid)
        clean_rules.append(row)

    seen_materials = set()
    clean_materials = []
    for row in materials:
        mid = _text(row.material_id, "material_id")
        _text(row.status, "material status")
        _text(row.provenance_ref, "material provenance_ref")
        if row.max_quantity is None:
            if row.quantity_unit is not None:
                raise IndustrialContextError(f"material {mid} has unit without quantity")
        else:
            q = float(row.max_quantity)
            if not math.isfinite(q) or q < 0.0:
                raise IndustrialContextError(f"material {mid} max_quantity must be finite and non-negative")
            _text(row.quantity_unit, "material quantity_unit")
        if mid in seen_materials:
            raise IndustrialContextError(f"duplicate material {mid}")
        seen_materials.add(mid)
        clean_materials.append(row)

    seen_caps = set()
    clean_caps = []
    for row in manufacturing_capabilities:
        cid = _text(row.capability_id, "manufacturing capability_id")
        _text(row.status, "manufacturing capability status")
        _text(row.provenance_ref, "manufacturing capability provenance_ref")
        if row.max_envelope_m is not None:
            if len(row.max_envelope_m) != 3:
                raise IndustrialContextError(f"capability {cid} max_envelope_m must have 3 values")
            dims = tuple(float(v) for v in row.max_envelope_m)
            if any((not math.isfinite(v) or v <= 0.0) for v in dims):
                raise IndustrialContextError(f"capability {cid} envelope must be finite and positive")
        if cid in seen_caps:
            raise IndustrialContextError(f"duplicate manufacturing capability {cid}")
        seen_caps.add(cid)
        clean_caps.append(row)

    payload = {
        "version": CONTEXT_VERSION,
        "context_id": context_id,
        "context_date": context_date,
        "technology_rules": [asdict(v) for v in sorted(clean_rules, key=lambda x: x.rule_id)],
        "materials": [asdict(v) for v in sorted(clean_materials, key=lambda x: x.material_id)],
        "manufacturing_capabilities": [asdict(v) for v in sorted(clean_caps, key=lambda x: x.capability_id)],
        "supplier_component_ids": sorted(suppliers),
        "prohibited_component_ids": sorted(prohibited),
        "economic_constraints": sorted(economics),
        "provenance_refs": sorted(provenance),
        "authority_status": authority_status,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return IndustrialContext(
        context_id=context_id,
        context_date=context_date,
        technology_rules=tuple(sorted(clean_rules, key=lambda x: x.rule_id)),
        materials=tuple(sorted(clean_materials, key=lambda x: x.material_id)),
        manufacturing_capabilities=tuple(sorted(clean_caps, key=lambda x: x.capability_id)),
        supplier_component_ids=tuple(sorted(suppliers)),
        prohibited_component_ids=tuple(sorted(prohibited)),
        economic_constraints=tuple(sorted(economics)),
        provenance_refs=tuple(sorted(provenance)),
        authority_status=authority_status,
        context_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )
