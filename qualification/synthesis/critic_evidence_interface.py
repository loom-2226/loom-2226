from __future__ import annotations

from architectural_review import ArchitecturalDoctrine, DesignReviewReport, validate_report
from design_evidence import DesignEvidencePackage
from shipyard_agent_contracts import CritiqueIssue, DesignCritique, validate_critique


class CriticEvidenceInterfaceError(ValueError):
    """Fail-closed error when critic output is not traceable to supplied evidence."""


def architectural_review_to_design_critique(
    *,
    evidence: DesignEvidencePackage,
    report: DesignReviewReport,
    doctrine: ArchitecturalDoctrine,
) -> DesignCritique:
    """Convert a validated SOL architectural review into the model-neutral critic contract.

    This adapter carries evidence and critique forward. It does not create engineering findings,
    close OPEN items, or grant any additional authority.
    """
    validate_report(report, doctrine)

    if report.candidate_id != evidence.candidate_id:
        raise CriticEvidenceInterfaceError("report candidate_id does not match evidence package")
    if report.evidence_package_hash != evidence.package_hash:
        raise CriticEvidenceInterfaceError("report evidence_package_hash does not match evidence package")

    issues = tuple(
        CritiqueIssue(
            issue_id=finding.finding_id,
            category=f"ARCHITECTURE/{finding.criterion_id}",
            severity=finding.severity,
            claim=finding.claim,
            evidence_refs=finding.evidence_refs,
            proposed_experiment=finding.experiment_request,
        )
        for finding in report.findings
    )

    critique = DesignCritique(
        critique_id=report.report_id,
        candidate_id=evidence.candidate_id,
        evaluation_hash=evidence.evaluation_hash,
        institution_context_hash=evidence.institution_context_hash,
        issues=issues,
        critic_id=report.reviewer_id,
        critic_model=report.reviewer_model,
        overall_recommendation=report.overall_recommendation,
    )
    validate_critique(critique)
    return critique
