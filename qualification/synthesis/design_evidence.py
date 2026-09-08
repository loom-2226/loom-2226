from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Sequence, Tuple


EVIDENCE_VERSION = "LOOM_DESIGN_EVIDENCE_PACKAGE_v0.1"


class EvidencePackageError(ValueError):
    """Fail-closed error for malformed critic-facing evidence packages."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidencePackageError(f"{label} must be a non-empty string")
    return value.strip()


def _unique(values: Sequence[str], label: str) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise EvidencePackageError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if len(set(cleaned)) != len(cleaned):
        raise EvidencePackageError(f"{label} must contain unique values")
    return cleaned


@dataclass(frozen=True)
class EvidenceFinding:
    finding_id: str
    category: str
    status: str
    value_text: str
    evidence_ref: str
    authority_status: str


@dataclass(frozen=True)
class DesignEvidencePackage:
    candidate_id: str
    requirements_hash: str
    institution_context_hash: str
    industrial_context_hash: str
    evaluation_hash: str
    selected_component_ids: Tuple[str, ...]
    hard_constraint_findings: Tuple[EvidenceFinding, ...]
    objective_findings: Tuple[EvidenceFinding, ...]
    open_items: Tuple[str, ...]
    provenance_refs: Tuple[str, ...]
    flight_dynamics_authority: bool
    canon_changed: bool
    production_shipclasses_changed: bool
    package_hash: str


def build_evidence_package(
    *,
    candidate_id: str,
    requirements_hash: str,
    institution_context_hash: str,
    industrial_context_hash: str,
    evaluation_hash: str,
    selected_component_ids: Sequence[str] = (),
    hard_constraint_findings: Sequence[EvidenceFinding] = (),
    objective_findings: Sequence[EvidenceFinding] = (),
    open_items: Sequence[str] = (),
    provenance_refs: Sequence[str] = (),
    flight_dynamics_authority: bool = False,
    canon_changed: bool = False,
    production_shipclasses_changed: bool = False,
) -> DesignEvidencePackage:
    for value, label in (
        (candidate_id, "candidate_id"),
        (requirements_hash, "requirements_hash"),
        (institution_context_hash, "institution_context_hash"),
        (industrial_context_hash, "industrial_context_hash"),
        (evaluation_hash, "evaluation_hash"),
    ):
        _text(value, label)

    selected = _unique(selected_component_ids, "selected_component_ids")
    opens = _unique(open_items, "open_items")
    provenance = _unique(provenance_refs, "provenance_refs")

    def clean_findings(rows: Sequence[EvidenceFinding], label: str) -> Tuple[EvidenceFinding, ...]:
        seen = set()
        cleaned = []
        for row in rows:
            for value, field in (
                (row.finding_id, "finding_id"),
                (row.category, "category"),
                (row.status, "status"),
                (row.value_text, "value_text"),
                (row.evidence_ref, "evidence_ref"),
                (row.authority_status, "authority_status"),
            ):
                _text(value, field)
            if row.finding_id in seen:
                raise EvidencePackageError(f"duplicate {label} finding_id {row.finding_id}")
            seen.add(row.finding_id)
            cleaned.append(row)
        return tuple(sorted(cleaned, key=lambda x: x.finding_id))

    hard = clean_findings(hard_constraint_findings, "hard_constraint")
    objectives = clean_findings(objective_findings, "objective")
    payload = {
        "version": EVIDENCE_VERSION,
        "candidate_id": candidate_id,
        "requirements_hash": requirements_hash,
        "institution_context_hash": institution_context_hash,
        "industrial_context_hash": industrial_context_hash,
        "evaluation_hash": evaluation_hash,
        "selected_component_ids": sorted(selected),
        "hard_constraint_findings": [asdict(v) for v in hard],
        "objective_findings": [asdict(v) for v in objectives],
        "open_items": sorted(opens),
        "provenance_refs": sorted(provenance),
        "flight_dynamics_authority": bool(flight_dynamics_authority),
        "canon_changed": bool(canon_changed),
        "production_shipclasses_changed": bool(production_shipclasses_changed),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return DesignEvidencePackage(
        candidate_id=candidate_id,
        requirements_hash=requirements_hash,
        institution_context_hash=institution_context_hash,
        industrial_context_hash=industrial_context_hash,
        evaluation_hash=evaluation_hash,
        selected_component_ids=tuple(sorted(selected)),
        hard_constraint_findings=hard,
        objective_findings=objectives,
        open_items=tuple(sorted(opens)),
        provenance_refs=tuple(sorted(provenance)),
        flight_dynamics_authority=bool(flight_dynamics_authority),
        canon_changed=bool(canon_changed),
        production_shipclasses_changed=bool(production_shipclasses_changed),
        package_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )
