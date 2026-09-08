from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import Dict, Sequence, Tuple

from shipyard_agent_contracts import ShipyardInstitutionContext

INSTITUTION_CONTRACT_VERSION = "LOOM_SHIPBUILDING_INSTITUTION_v0.1"
INSTITUTION_AUTHORITY = "INSTITUTIONAL_CONTEXT_ONLY"
DESIGN_AUTHORITY = "HISTORICAL_EVIDENCE_ONLY"
MEMORY_AUTHORITY = "YARD_MEMORY_ONLY"

LINEAGE_MECHANISMS = frozenset({
    "TOOLING_CONTINUITY", "MODULE_REUSE", "SUPPLIER_CONTINUITY",
    "CERTIFICATION_PRECEDENT", "MANUFACTURING_PROCESS_CONTINUITY",
    "FIELD_LESSON", "OPERATOR_FAMILIARITY", "ARCHITECTURAL_PRECEDENT",
})
MEMORY_KINDS = frozenset({
    "DESIGN_SUCCESS", "DESIGN_FAILURE", "FIELD_REPORT", "SUPPLIER_HISTORY",
    "MANUFACTURING_PROCESS", "MODULE_REUSE", "CERTIFICATION_HISTORY",
    "MAINTENANCE_EXPERIENCE",
})


class InstitutionContractError(ValueError):
    """Fail-closed error for malformed institutional memory or genealogy."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InstitutionContractError(f"{label} must be a non-empty string")
    return value.strip()


def _tuple(values: Sequence[str], label: str, *, allow_empty: bool = True) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise InstitutionContractError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if not allow_empty and not cleaned:
        raise InstitutionContractError(f"{label} must not be empty")
    if len(cleaned) != len(set(cleaned)):
        raise InstitutionContractError(f"{label} must contain unique values")
    return cleaned


def _date(value: str, label: str) -> date:
    _text(value, label)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InstitutionContractError(f"{label} must be ISO YYYY-MM-DD") from exc


@dataclass(frozen=True)
class ShipbuildingInstitution:
    institution_id: str
    founded_date: str
    founding_lineage: Tuple[str, ...]
    cultural_progenitors: Tuple[str, ...]
    engineering_lineage: Tuple[str, ...]
    design_doctrine: Tuple[str, ...]
    preferred_architectures: Tuple[str, ...]
    manufacturing_capabilities: Tuple[str, ...]
    material_access: Tuple[str, ...]
    material_constraints: Tuple[str, ...]
    economic_constraints: Tuple[str, ...]
    automation_profile: Tuple[str, ...]
    component_ecosystem: Tuple[str, ...]
    risk_tolerance: str
    maintainability_doctrine: Tuple[str, ...]
    aesthetic_principles: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = INSTITUTION_AUTHORITY


@dataclass(frozen=True)
class HistoricalDesign:
    design_id: str
    institution_id: str
    service_date: str
    architecture_family: str
    mission_roles: Tuple[str, ...]
    successful_modules: Tuple[str, ...]
    manufacturing_processes: Tuple[str, ...]
    supplier_refs: Tuple[str, ...]
    certification_refs: Tuple[str, ...]
    field_evidence_refs: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = DESIGN_AUTHORITY


@dataclass(frozen=True)
class DesignLineageEdge:
    parent_design_id: str
    child_design_id: str
    mechanisms: Tuple[str, ...]
    rationale: str
    provenance_refs: Tuple[str, ...]


@dataclass(frozen=True)
class YardMemoryEvent:
    event_id: str
    institution_id: str
    event_date: str
    memory_kind: str
    design_refs: Tuple[str, ...]
    lesson: str
    evidence_refs: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = MEMORY_AUTHORITY


@dataclass(frozen=True)
class InstitutionalMemorySnapshot:
    institution: ShipbuildingInstitution
    as_of_date: str
    historical_designs: Tuple[HistoricalDesign, ...]
    lineage_edges: Tuple[DesignLineageEdge, ...]
    memory_events: Tuple[YardMemoryEvent, ...]
    authority_status: str = INSTITUTION_AUTHORITY


def validate_institution(row: ShipbuildingInstitution) -> None:
    _text(row.institution_id, "institution_id")
    _date(row.founded_date, "founded_date")
    if row.authority_status != INSTITUTION_AUTHORITY:
        raise InstitutionContractError("institution may not claim engineering or canon authority")
    for field, required in (
        ("founding_lineage", True), ("cultural_progenitors", False),
        ("engineering_lineage", True), ("design_doctrine", True),
        ("preferred_architectures", False), ("manufacturing_capabilities", True),
        ("material_access", False), ("material_constraints", False),
        ("economic_constraints", False), ("automation_profile", False),
        ("component_ecosystem", False), ("maintainability_doctrine", True),
        ("aesthetic_principles", False), ("provenance_refs", True),
    ):
        _tuple(getattr(row, field), field, allow_empty=not required)
    _text(row.risk_tolerance, "risk_tolerance")


def validate_historical_design(row: HistoricalDesign) -> None:
    for field in ("design_id", "institution_id", "architecture_family"):
        _text(getattr(row, field), field)
    _date(row.service_date, "service_date")
    if row.authority_status != DESIGN_AUTHORITY:
        raise InstitutionContractError("historical design record may not claim engineering or canon authority")
    for field, required in (
        ("mission_roles", True), ("successful_modules", False),
        ("manufacturing_processes", False), ("supplier_refs", False),
        ("certification_refs", False), ("field_evidence_refs", False),
        ("provenance_refs", True),
    ):
        _tuple(getattr(row, field), field, allow_empty=not required)


def validate_memory_event(row: YardMemoryEvent) -> None:
    for field in ("event_id", "institution_id", "memory_kind", "lesson"):
        _text(getattr(row, field), field)
    _date(row.event_date, "event_date")
    if row.memory_kind not in MEMORY_KINDS:
        raise InstitutionContractError(f"unsupported memory_kind {row.memory_kind}")
    if row.authority_status != MEMORY_AUTHORITY:
        raise InstitutionContractError("yard memory may not claim engineering or canon authority")
    _tuple(row.design_refs, "design_refs")
    _tuple(row.evidence_refs, "evidence_refs", allow_empty=False)
    _tuple(row.provenance_refs, "provenance_refs", allow_empty=False)


def validate_snapshot(snapshot: InstitutionalMemorySnapshot) -> None:
    validate_institution(snapshot.institution)
    as_of = _date(snapshot.as_of_date, "as_of_date")
    if snapshot.authority_status != INSTITUTION_AUTHORITY:
        raise InstitutionContractError("snapshot may not claim engineering or canon authority")
    if _date(snapshot.institution.founded_date, "founded_date") > as_of:
        raise InstitutionContractError("institution founding date is after snapshot date")

    designs: Dict[str, HistoricalDesign] = {}
    for row in snapshot.historical_designs:
        validate_historical_design(row)
        if row.institution_id != snapshot.institution.institution_id:
            raise InstitutionContractError("historical design belongs to a different institution")
        if row.design_id in designs:
            raise InstitutionContractError(f"duplicate design_id {row.design_id}")
        if _date(row.service_date, "service_date") > as_of:
            raise InstitutionContractError(f"design {row.design_id} is after snapshot date")
        designs[row.design_id] = row

    adjacency: Dict[str, list[str]] = {design_id: [] for design_id in designs}
    seen_edges = set()
    for edge in snapshot.lineage_edges:
        key = (edge.parent_design_id, edge.child_design_id)
        if key in seen_edges:
            raise InstitutionContractError(f"duplicate lineage edge {key}")
        seen_edges.add(key)
        if edge.parent_design_id == edge.child_design_id:
            raise InstitutionContractError("lineage self-loop is forbidden")
        if edge.parent_design_id not in designs or edge.child_design_id not in designs:
            raise InstitutionContractError("lineage edge references unknown design")
        mechanisms = _tuple(edge.mechanisms, "mechanisms", allow_empty=False)
        bad = sorted(set(mechanisms) - LINEAGE_MECHANISMS)
        if bad:
            raise InstitutionContractError(f"unsupported lineage mechanism(s): {', '.join(bad)}")
        _text(edge.rationale, "rationale")
        _tuple(edge.provenance_refs, "provenance_refs", allow_empty=False)
        if _date(designs[edge.parent_design_id].service_date, "parent service_date") > _date(designs[edge.child_design_id].service_date, "child service_date"):
            raise InstitutionContractError("lineage parent may not post-date child")
        adjacency[edge.parent_design_id].append(edge.child_design_id)

    state: Dict[str, int] = {key: 0 for key in designs}

    def visit(node: str) -> None:
        if state[node] == 1:
            raise InstitutionContractError("design lineage graph contains a cycle")
        if state[node] == 2:
            return
        state[node] = 1
        for child in sorted(adjacency[node]):
            visit(child)
        state[node] = 2

    for node in sorted(designs):
        visit(node)

    event_ids = set()
    for event in snapshot.memory_events:
        validate_memory_event(event)
        if event.institution_id != snapshot.institution.institution_id:
            raise InstitutionContractError("yard memory belongs to a different institution")
        if event.event_id in event_ids:
            raise InstitutionContractError(f"duplicate event_id {event.event_id}")
        event_ids.add(event.event_id)
        if _date(event.event_date, "event_date") > as_of:
            raise InstitutionContractError(f"memory event {event.event_id} is after snapshot date")
        unknown = sorted(set(event.design_refs) - set(designs))
        if unknown:
            raise InstitutionContractError(f"memory event references unknown designs: {', '.join(unknown)}")


def institutional_context(snapshot: InstitutionalMemorySnapshot) -> ShipyardInstitutionContext:
    """Project persistent yard state into the existing model-neutral agent context contract.

    Only semantically identical fields are projected. Material access remains a distinct
    persistent-yard fact and is not silently converted into a material constraint.
    """
    validate_snapshot(snapshot)
    inst = snapshot.institution
    ordered_designs = tuple(
        row.design_id
        for row in sorted(snapshot.historical_designs, key=lambda row: (row.service_date, row.design_id))
    )
    provenance = tuple(dict.fromkeys(
        inst.provenance_refs
        + tuple(ref for row in snapshot.historical_designs for ref in row.provenance_refs)
        + tuple(ref for event in snapshot.memory_events for ref in event.provenance_refs)
    ))
    return ShipyardInstitutionContext(
        institution_id=inst.institution_id,
        context_date=snapshot.as_of_date,
        progenitor_cultures=inst.cultural_progenitors,
        engineering_lineage=inst.engineering_lineage,
        design_doctrine=inst.design_doctrine,
        aesthetic_principles=inst.aesthetic_principles,
        manufacturing_capabilities=inst.manufacturing_capabilities,
        material_constraints=inst.material_constraints,
        economic_constraints=inst.economic_constraints,
        historical_design_refs=ordered_designs,
        provenance_refs=provenance,
        authority_status=INSTITUTION_AUTHORITY,
    )


def canonical_json(row: object) -> str:
    return json.dumps(asdict(row), sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(row: object) -> str:
    return hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
