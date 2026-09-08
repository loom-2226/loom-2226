from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple


class ComponentSelectionError(ValueError):
    """Fail-closed error for invalid component catalogs or selections."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ComponentSelectionError(f"{label} must be a non-empty string")
    return value.strip()


def _unique(values: Sequence[str], label: str) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ComponentSelectionError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if len(set(cleaned)) != len(cleaned):
        raise ComponentSelectionError(f"{label} must contain unique values")
    return cleaned


@dataclass(frozen=True)
class ComponentCatalogEntry:
    component_id: str
    component_type: str
    capabilities: Tuple[str, ...]
    technology_rule_refs: Tuple[str, ...]
    manufacturing_capability_refs: Tuple[str, ...]
    material_refs: Tuple[str, ...]
    authority_status: str
    provenance_ref: str


@dataclass(frozen=True)
class CapabilitySatisfaction:
    capability_id: str
    status: str
    selected_component_ids: Tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ComponentSelectionResult:
    selected_component_ids: Tuple[str, ...]
    capability_satisfaction: Tuple[CapabilitySatisfaction, ...]
    infeasibility_reasons: Tuple[str, ...]
    selection_status: str


def validate_entry(row: ComponentCatalogEntry) -> None:
    _text(row.component_id, "component_id")
    _text(row.component_type, "component_type")
    _unique(row.capabilities, "capabilities")
    _unique(row.technology_rule_refs, "technology_rule_refs")
    _unique(row.manufacturing_capability_refs, "manufacturing_capability_refs")
    _unique(row.material_refs, "material_refs")
    _text(row.authority_status, "authority_status")
    _text(row.provenance_ref, "provenance_ref")


def select_components(
    *,
    required_capabilities: Sequence[str],
    catalog: Sequence[ComponentCatalogEntry],
    available_component_ids: Sequence[str],
    prohibited_component_ids: Sequence[str] = (),
) -> ComponentSelectionResult:
    required = _unique(required_capabilities, "required_capabilities")
    available = set(_unique(available_component_ids, "available_component_ids"))
    prohibited = set(_unique(prohibited_component_ids, "prohibited_component_ids"))
    if available & prohibited:
        raise ComponentSelectionError("available/prohibited component sets overlap")

    entries: Dict[str, ComponentCatalogEntry] = {}
    for row in catalog:
        validate_entry(row)
        if row.component_id in entries:
            raise ComponentSelectionError(f"duplicate component_id {row.component_id}")
        entries[row.component_id] = row

    unknown_available = sorted(available - set(entries))
    if unknown_available:
        raise ComponentSelectionError(f"available component IDs missing from catalog: {unknown_available}")

    satisfaction = []
    selected = set()
    infeasible = []
    for capability_id in sorted(required):
        candidates = sorted(
            row.component_id
            for row in entries.values()
            if capability_id in row.capabilities
            and row.component_id in available
            and row.component_id not in prohibited
            and row.authority_status.upper() != "OPEN"
        )
        if candidates:
            chosen = candidates[0]
            selected.add(chosen)
            satisfaction.append(
                CapabilitySatisfaction(
                    capability_id=capability_id,
                    status="SATISFIED",
                    selected_component_ids=(chosen,),
                    reason="DETERMINISTIC_LEXICOGRAPHIC_v0.1",
                )
            )
        else:
            reason = f"NO_ADMITTED_AVAILABLE_COMPONENT:{capability_id}"
            infeasible.append(reason)
            satisfaction.append(
                CapabilitySatisfaction(
                    capability_id=capability_id,
                    status="UNSATISFIED",
                    selected_component_ids=(),
                    reason=reason,
                )
            )

    return ComponentSelectionResult(
        selected_component_ids=tuple(sorted(selected)),
        capability_satisfaction=tuple(sorted(satisfaction, key=lambda x: x.capability_id)),
        infeasibility_reasons=tuple(sorted(infeasible)),
        selection_status="PASS" if not infeasible else "INFEASIBLE",
    )
