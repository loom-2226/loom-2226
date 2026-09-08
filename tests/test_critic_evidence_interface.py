import dataclasses
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "qualification" / "synthesis"))

from architectural_review import DesignReviewFinding, DesignReviewReport, content_hash, functional_expressionism_doctrine
from critic_evidence_interface import CriticEvidenceInterfaceError, architectural_review_to_design_critique
from design_evidence import build_evidence_package


class TestCriticEvidenceInterface(unittest.TestCase):
    def setUp(self):
        self.doctrine = functional_expressionism_doctrine()
        self.evidence = build_evidence_package(
            candidate_id="CAND-1",
            requirements_hash="req-hash",
            institution_context_hash="inst-hash",
            industrial_context_hash="industrial-hash",
            evaluation_hash="eval-hash",
            open_items=("OPEN: radiator service envelope",),
            provenance_refs=("prov:evaluator",),
        )
        self.finding = DesignReviewFinding(
            finding_id="SOL-F1",
            criterion_id="SOL-MAINT",
            severity="WARN",
            claim="Service access is not architecturally legible.",
            evidence_refs=("evidence:maintenance-access",),
            experiment_request="Expose two alternative service-corridor topologies to the same evaluator.",
        )
        self.report = DesignReviewReport(
            report_id="SOL-R1",
            candidate_id=self.evidence.candidate_id,
            evidence_package_hash=self.evidence.package_hash,
            doctrine_hash=content_hash(self.doctrine),
            reviewer_id="SOL",
            reviewer_model="gpt-5.6-sol",
            findings=(self.finding,),
            overall_recommendation="REVISE",
            architectural_summary="Physically evaluated candidate needs architectural revision.",
        )

    def test_adapter_preserves_traceability_and_critic_only_authority(self):
        critique = architectural_review_to_design_critique(
            evidence=self.evidence,
            report=self.report,
            doctrine=self.doctrine,
        )
        self.assertEqual(critique.candidate_id, self.evidence.candidate_id)
        self.assertEqual(critique.evaluation_hash, self.evidence.evaluation_hash)
        self.assertEqual(critique.institution_context_hash, self.evidence.institution_context_hash)
        self.assertEqual(critique.authority_claim, "CRITIQUE_ONLY")
        self.assertEqual(len(critique.issues), 1)
        self.assertEqual(critique.issues[0].evidence_refs, self.finding.evidence_refs)
        self.assertEqual(critique.issues[0].category, "ARCHITECTURE/SOL-MAINT")

    def test_candidate_mismatch_fails_closed(self):
        bad = dataclasses.replace(self.report, candidate_id="OTHER")
        with self.assertRaisesRegex(CriticEvidenceInterfaceError, "candidate_id"):
            architectural_review_to_design_critique(evidence=self.evidence, report=bad, doctrine=self.doctrine)

    def test_evidence_hash_mismatch_fails_closed(self):
        bad = dataclasses.replace(self.report, evidence_package_hash="wrong")
        with self.assertRaisesRegex(CriticEvidenceInterfaceError, "evidence_package_hash"):
            architectural_review_to_design_critique(evidence=self.evidence, report=bad, doctrine=self.doctrine)

    def test_open_engineering_items_remain_open_and_are_not_converted_to_critic_issues(self):
        critique = architectural_review_to_design_critique(
            evidence=self.evidence,
            report=self.report,
            doctrine=self.doctrine,
        )
        issue_text = " ".join(issue.claim for issue in critique.issues)
        self.assertNotIn("radiator service envelope", issue_text)
        self.assertIn("OPEN: radiator service envelope", self.evidence.open_items)

    def test_architectural_reject_remains_critique_not_engineering_authority(self):
        reject_finding = dataclasses.replace(self.finding, severity="REJECT", finding_id="SOL-F2")
        report = dataclasses.replace(self.report, findings=(reject_finding,), overall_recommendation="REJECT")
        critique = architectural_review_to_design_critique(
            evidence=self.evidence,
            report=report,
            doctrine=self.doctrine,
        )
        self.assertEqual(critique.overall_recommendation, "REJECT")
        self.assertEqual(critique.authority_claim, "CRITIQUE_ONLY")
        self.assertEqual(critique.issues[0].authority_claim, "CRITIQUE_ONLY")


if __name__ == "__main__":
    unittest.main()
