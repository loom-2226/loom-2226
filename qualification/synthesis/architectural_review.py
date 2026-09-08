from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Sequence, Tuple


ARCHITECTURAL_REVIEW_VERSION = "LOOM_SOL_ARCHITECTURAL_REVIEW_v0.1"
ARCHITECTURAL_REVIEW_AUTHORITY = "ARCHITECTURAL_REVIEW_ONLY"

SEVERITIES = frozenset({"NOTE", "WARN", "REJECT"})
RECOMMENDATIONS = frozenset({"ACCEPT", "REVISE", "REJECT"})
CRITERION_FAMILIES = frozenset({
    "LEGIBILITY",
    "STRUCTURAL_HONESTY",
    "PURPOSEFUL_SYMMETRY",
    "MEANINGFUL_ASYMMETRY",
    "HIERARCHY",
    "PROPORTION",
    "RHYTHM",
    "ECONOMY_OF_FORM",
    "MAINTAINABILITY_EXPRESSION",
    "IDENTITY_FROM_FUNCTION",
})


class ArchitecturalReviewError(ValueError):
    """Fail-closed error for malformed architectural review records."""


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArchitecturalReviewError(f"{label} must be a non-empty string")
    return value.strip()


def _unique(values: Sequence[str], label: str, *, allow_empty: bool = True) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ArchitecturalReviewError(f"{label} must be a sequence, not a string")
    cleaned = tuple(_text(v, label) for v in values)
    if not allow_empty and not cleaned:
        raise ArchitecturalReviewError(f"{label} must not be empty")
    if len(cleaned) != len(set(cleaned)):
        raise ArchitecturalReviewError(f"{label} must contain unique values")
    return cleaned


@dataclass(frozen=True)
class DesignReviewCriterion:
    criterion_id: str
    family: str
    question: str
    positive_signals: Tuple[str, ...]
    failure_signals: Tuple[str, ...]
    evidence_expectations: Tuple[str, ...]
    authority_status: str = ARCHITECTURAL_REVIEW_AUTHORITY


@dataclass(frozen=True)
class ArchitecturalDoctrine:
    doctrine_id: str
    name: str
    principles: Tuple[str, ...]
    forbidden_shortcuts: Tuple[str, ...]
    criteria: Tuple[DesignReviewCriterion, ...]
    provenance_refs: Tuple[str, ...]
    authority_status: str = ARCHITECTURAL_REVIEW_AUTHORITY


@dataclass(frozen=True)
class DesignReviewFinding:
    finding_id: str
    criterion_id: str
    severity: str
    claim: str
    evidence_refs: Tuple[str, ...]
    experiment_request: str
    authority_status: str = ARCHITECTURAL_REVIEW_AUTHORITY


@dataclass(frozen=True)
class DesignReviewReport:
    report_id: str
    candidate_id: str
    evidence_package_hash: str
    doctrine_hash: str
    reviewer_id: str
    reviewer_model: str
    findings: Tuple[DesignReviewFinding, ...]
    overall_recommendation: str
    architectural_summary: str
    physical_feasibility_claimed: bool = False
    flight_dynamics_authority_claimed: bool = False
    canon_change_claimed: bool = False
    production_shipclass_change_claimed: bool = False
    authority_status: str = ARCHITECTURAL_REVIEW_AUTHORITY


def validate_criterion(row: DesignReviewCriterion) -> None:
    for value, label in (
        (row.criterion_id, "criterion_id"),
        (row.family, "family"),
        (row.question, "question"),
    ):
        _text(value, label)
    if row.family not in CRITERION_FAMILIES:
        raise ArchitecturalReviewError(f"unsupported criterion family {row.family}")
    if row.authority_status != ARCHITECTURAL_REVIEW_AUTHORITY:
        raise ArchitecturalReviewError("criterion may not claim engineering or canon authority")
    _unique(row.positive_signals, "positive_signals", allow_empty=False)
    _unique(row.failure_signals, "failure_signals", allow_empty=False)
    _unique(row.evidence_expectations, "evidence_expectations", allow_empty=False)


def validate_doctrine(row: ArchitecturalDoctrine) -> None:
    _text(row.doctrine_id, "doctrine_id")
    _text(row.name, "name")
    if row.authority_status != ARCHITECTURAL_REVIEW_AUTHORITY:
        raise ArchitecturalReviewError("doctrine may not claim engineering or canon authority")
    _unique(row.principles, "principles", allow_empty=False)
    _unique(row.forbidden_shortcuts, "forbidden_shortcuts", allow_empty=False)
    _unique(row.provenance_refs, "provenance_refs", allow_empty=False)
    if not row.criteria:
        raise ArchitecturalReviewError("doctrine requires at least one criterion")
    ids = set()
    families = set()
    for criterion in row.criteria:
        validate_criterion(criterion)
        if criterion.criterion_id in ids:
            raise ArchitecturalReviewError(f"duplicate criterion_id {criterion.criterion_id}")
        ids.add(criterion.criterion_id)
        if criterion.family in families:
            raise ArchitecturalReviewError(f"duplicate criterion family {criterion.family}")
        families.add(criterion.family)


def validate_finding(row: DesignReviewFinding, criterion_ids: set[str]) -> None:
    for value, label in (
        (row.finding_id, "finding_id"),
        (row.criterion_id, "criterion_id"),
        (row.severity, "severity"),
        (row.claim, "claim"),
        (row.experiment_request, "experiment_request"),
    ):
        _text(value, label)
    if row.criterion_id not in criterion_ids:
        raise ArchitecturalReviewError(f"finding references unknown criterion {row.criterion_id}")
    if row.severity not in SEVERITIES:
        raise ArchitecturalReviewError(f"unsupported severity {row.severity}")
    if row.authority_status != ARCHITECTURAL_REVIEW_AUTHORITY:
        raise ArchitecturalReviewError("finding may not claim engineering or canon authority")
    _unique(row.evidence_refs, "evidence_refs", allow_empty=False)


def validate_report(row: DesignReviewReport, doctrine: ArchitecturalDoctrine) -> None:
    validate_doctrine(doctrine)
    for value, label in (
        (row.report_id, "report_id"),
        (row.candidate_id, "candidate_id"),
        (row.evidence_package_hash, "evidence_package_hash"),
        (row.doctrine_hash, "doctrine_hash"),
        (row.reviewer_id, "reviewer_id"),
        (row.reviewer_model, "reviewer_model"),
        (row.overall_recommendation, "overall_recommendation"),
        (row.architectural_summary, "architectural_summary"),
    ):
        _text(value, label)
    if row.authority_status != ARCHITECTURAL_REVIEW_AUTHORITY:
        raise ArchitecturalReviewError("report may not claim engineering or canon authority")
    if row.doctrine_hash != content_hash(doctrine):
        raise ArchitecturalReviewError("report doctrine_hash does not match doctrine")
    if row.overall_recommendation not in RECOMMENDATIONS:
        raise ArchitecturalReviewError(f"unsupported recommendation {row.overall_recommendation}")
    if (
        row.physical_feasibility_claimed
        or row.flight_dynamics_authority_claimed
        or row.canon_change_claimed
        or row.production_shipclass_change_claimed
    ):
        raise ArchitecturalReviewError("architectural review may not claim physical, flight, canon, or production authority")

    criterion_ids = {criterion.criterion_id for criterion in doctrine.criteria}
    finding_ids = set()
    for finding in row.findings:
        validate_finding(finding, criterion_ids)
        if finding.finding_id in finding_ids:
            raise ArchitecturalReviewError(f"duplicate finding_id {finding.finding_id}")
        finding_ids.add(finding.finding_id)

    severities = {finding.severity for finding in row.findings}
    if "REJECT" in severities and row.overall_recommendation != "REJECT":
        raise ArchitecturalReviewError("REJECT finding requires overall REJECT")
    if "REJECT" not in severities and "WARN" in severities and row.overall_recommendation == "ACCEPT":
        raise ArchitecturalReviewError("WARN finding requires REVISE or REJECT")


def functional_expressionism_doctrine() -> ArchitecturalDoctrine:
    def criterion(
        criterion_id: str,
        family: str,
        question: str,
        positive: Sequence[str],
        failures: Sequence[str],
        evidence: Sequence[str],
    ) -> DesignReviewCriterion:
        return DesignReviewCriterion(
            criterion_id=criterion_id,
            family=family,
            question=question,
            positive_signals=tuple(positive),
            failure_signals=tuple(failures),
            evidence_expectations=tuple(evidence),
        )

    return ArchitecturalDoctrine(
        doctrine_id="SOL-FUNCTIONAL-EXPRESSIONISM-v0.1",
        name="Functional Expressionism",
        principles=(
            "major form should arise from function",
            "force paths and system hierarchy should be legible",
            "symmetry and asymmetry require engineering reasons",
            "maintainability should be visible in architecture",
            "identity should emerge from repeated engineering decisions rather than decoration",
        ),
        forbidden_shortcuts=(
            "styling-first geometry",
            "fake aerodynamic features",
            "random fins or windows",
            "greeble density used as complexity",
            "glowing strips used as identity",
            "naval bridge cosplay",
            "radiators treated as afterthoughts",
            "obscured primary load paths",
        ),
        criteria=(
            criterion("SOL-LEGIBILITY", "LEGIBILITY", "Can a reviewer infer major ship functions from the architecture?", ("major systems have readable placement logic",), ("component collection lacks a readable whole",), ("geometry or topology evidence", "system-location evidence")),
            criterion("SOL-STRUCTURE", "STRUCTURAL_HONESTY", "Does the visible architecture agree with major load paths and structural hierarchy?", ("primary load path is visually and topologically coherent",), ("major masses appear unsupported or structurally unrelated",), ("load-path evidence", "mass-location evidence")),
            criterion("SOL-SYMMETRY", "PURPOSEFUL_SYMMETRY", "Where symmetry exists, is it justified by function, loads, operations, or production?", ("symmetry follows repeated functional demand",), ("symmetry appears ornamental or forces bad access",), ("symmetry rationale", "maintenance or load evidence")),
            criterion("SOL-ASYMMETRY", "MEANINGFUL_ASYMMETRY", "Where asymmetry exists, is it attributable to a real requirement or system?", ("asymmetry traces to a named system or operational need",), ("asymmetry appears accidental or decorative",), ("asymmetry rationale", "system-location evidence")),
            criterion("SOL-HIERARCHY", "HIERARCHY", "Do primary, secondary, and tertiary forms reflect engineering importance?", ("propulsion, habitation, payload, thermal, and service systems read at appropriate scales",), ("minor systems dominate form while primary systems disappear",), ("system hierarchy evidence",)),
            criterion("SOL-PROPORTION", "PROPORTION", "Do major dimensions and volumes have explainable relationships to their functions?", ("proportions track payload, tankage, structure, access, or thermal needs",), ("large formal gestures lack requirement linkage",), ("dimensional evidence", "requirement provenance")),
            criterion("SOL-RHYTHM", "RHYTHM", "Do repeated modules and spacing reflect fabrication, structure, access, or system repetition?", ("repetition corresponds to real modules or frame spacing",), ("surface repetition is decorative noise",), ("module evidence", "fabrication evidence")),
            criterion("SOL-ECONOMY", "ECONOMY_OF_FORM", "Has unnecessary form been avoided without hiding necessary complexity?", ("geometry does multiple engineering jobs",), ("gratuitous appendages or surface languages proliferate",), ("component purpose evidence",)),
            criterion("SOL-MAINT", "MAINTAINABILITY_EXPRESSION", "Does architecture expose believable service, replacement, inspection, and access logic?", ("service zones and replaceable modules are accessible",), ("critical systems are trapped behind unrelated structure",), ("maintenance evidence", "access evidence")),
            criterion("SOL-IDENTITY", "IDENTITY_FROM_FUNCTION", "Would recognizable identity survive removal of logos, paint, and decorative styling?", ("identity follows architecture family and repeated engineering decisions",), ("identity depends on markings or arbitrary ornament",), ("lineage evidence", "institution-context evidence")),
        ),
        provenance_refs=("docs:LOOM_2226_Computational_Shipyard_Agent_Architecture_v0.1",),
    )


def canonical_json(row: object) -> str:
    return json.dumps(asdict(row), sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_hash(row: object) -> str:
    return hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()
