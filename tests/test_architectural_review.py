import dataclasses
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qualification" / "synthesis"))

from architectural_review import (
    ARCHITECTURAL_REVIEW_AUTHORITY,
    ArchitecturalReviewError,
    DesignReviewFinding,
    DesignReviewReport,
    content_hash,
    functional_expressionism_doctrine,
    validate_doctrine,
    validate_report,
)


class TestArchitecturalReview(unittest.TestCase):
    def setUp(self):
        self.doctrine = functional_expressionism_doctrine()
        self.doctrine_hash = content_hash(self.doctrine)

    def report(self, *, findings=(), recommendation="ACCEPT"):
        return DesignReviewReport(
            report_id="SOL-R1",
            candidate_id="CAND-1",
            evidence_package_hash="evidence-hash-1",
            doctrine_hash=self.doctrine_hash,
            reviewer_id="SOL",
            reviewer_model="gpt-5.6-sol",
            findings=tuple(findings),
            overall_recommendation=recommendation,
            architectural_summary="Architecture is reviewed separately from physical feasibility.",
        )

    def finding(self, *, severity="NOTE", criterion_id="SOL-LEGIBILITY"):
        return DesignReviewFinding(
            finding_id=f"F-{severity}-{criterion_id}",
            criterion_id=criterion_id,
            severity=severity,
            claim="The major-system relationship requires explicit architectural review.",
            evidence_refs=("evidence:geometry",),
            experiment_request="Compare topology alternatives while preserving hard engineering constraints.",
        )

    def test_default_doctrine_is_valid_and_deterministic(self):
        validate_doctrine(self.doctrine)
        self.assertEqual(content_hash(self.doctrine), content_hash(functional_expressionism_doctrine()))
        self.assertEqual(len(self.doctrine.criteria), 10)
        self.assertEqual(len({row.family for row in self.doctrine.criteria}), 10)

    def test_clean_report_can_accept_without_claiming_physical_authority(self):
        report = self.report()
        validate_report(report, self.doctrine)
        self.assertFalse(report.physical_feasibility_claimed)
        self.assertEqual(report.authority_status, ARCHITECTURAL_REVIEW_AUTHORITY)

    def test_reject_finding_requires_architectural_reject(self):
        report = self.report(findings=(self.finding(severity="REJECT"),), recommendation="REVISE")
        with self.assertRaisesRegex(ArchitecturalReviewError, "requires overall REJECT"):
            validate_report(report, self.doctrine)

    def test_warn_finding_cannot_be_silently_accepted(self):
        report = self.report(findings=(self.finding(severity="WARN"),), recommendation="ACCEPT")
        with self.assertRaisesRegex(ArchitecturalReviewError, "requires REVISE or REJECT"):
            validate_report(report, self.doctrine)

    def test_unknown_criterion_fails_closed(self):
        report = self.report(findings=(self.finding(criterion_id="SOL-NOT-REAL"),), recommendation="REVISE")
        with self.assertRaisesRegex(ArchitecturalReviewError, "unknown criterion"):
            validate_report(report, self.doctrine)

    def test_doctrine_hash_mismatch_fails_closed(self):
        report = dataclasses.replace(self.report(), doctrine_hash="wrong-hash")
        with self.assertRaisesRegex(ArchitecturalReviewError, "doctrine_hash"):
            validate_report(report, self.doctrine)

    def test_architectural_review_cannot_claim_physical_feasibility(self):
        report = dataclasses.replace(self.report(), physical_feasibility_claimed=True)
        with self.assertRaisesRegex(ArchitecturalReviewError, "may not claim physical"):
            validate_report(report, self.doctrine)

    def test_architectural_review_cannot_claim_flight_authority(self):
        report = dataclasses.replace(self.report(), flight_dynamics_authority_claimed=True)
        with self.assertRaisesRegex(ArchitecturalReviewError, "may not claim physical"):
            validate_report(report, self.doctrine)

    def test_architectural_review_cannot_change_canon_or_production(self):
        for field in ("canon_change_claimed", "production_shipclass_change_claimed"):
            with self.subTest(field=field):
                report = dataclasses.replace(self.report(), **{field: True})
                with self.assertRaisesRegex(ArchitecturalReviewError, "may not claim physical"):
                    validate_report(report, self.doctrine)

    def test_evidence_refs_are_required_for_findings(self):
        bad = dataclasses.replace(self.finding(), evidence_refs=())
        report = self.report(findings=(bad,), recommendation="ACCEPT")
        with self.assertRaisesRegex(ArchitecturalReviewError, "evidence_refs must not be empty"):
            validate_report(report, self.doctrine)

    def test_criterion_authority_escalation_fails_closed(self):
        criterion = dataclasses.replace(self.doctrine.criteria[0], authority_status="ENGINEERING_PASS")
        doctrine = dataclasses.replace(self.doctrine, criteria=(criterion,) + self.doctrine.criteria[1:])
        with self.assertRaisesRegex(ArchitecturalReviewError, "may not claim engineering"):
            validate_doctrine(doctrine)

    def test_duplicate_criterion_family_fails_closed(self):
        duplicate = dataclasses.replace(
            self.doctrine.criteria[1],
            criterion_id="SOL-DUP",
            family=self.doctrine.criteria[0].family,
        )
        doctrine = dataclasses.replace(self.doctrine, criteria=(self.doctrine.criteria[0], duplicate) + self.doctrine.criteria[2:])
        with self.assertRaisesRegex(ArchitecturalReviewError, "duplicate criterion family"):
            validate_doctrine(doctrine)

    def test_architectural_reject_does_not_assert_engineering_failure(self):
        report = self.report(findings=(self.finding(severity="REJECT"),), recommendation="REJECT")
        validate_report(report, self.doctrine)
        self.assertEqual(report.overall_recommendation, "REJECT")
        self.assertFalse(report.physical_feasibility_claimed)
        self.assertFalse(report.flight_dynamics_authority_claimed)


if __name__ == "__main__":
    unittest.main()
