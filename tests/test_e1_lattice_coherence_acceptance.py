import unittest

from engineering.experience_one.qualification import e1_lattice_coherence_acceptance as lattice


class E1LatticeCoherenceAcceptanceTests(unittest.TestCase):
    def test_ship_identity_alone_does_not_close_lattice_axis(self):
        payload = {
            "mission": {"ship": "WAYFARER_BASELINE"},
            "candidate": {"candidate_id": "F000001"},
            "source_authority": "SOURCE-010",
        }
        report = lattice.classify_lattice_evidence(payload)
        self.assertEqual(report["axis"], "lattice_coherence")
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("domain_membership_and_attachment_state", report["missing_required_evidence"])
        self.assertIn("formation_and_integrity_state", report["missing_required_evidence"])
        self.assertIn("hardware_condition", report["missing_required_evidence"])
        self.assertIn("thermal_margin", report["missing_required_evidence"])
        self.assertIn("bank_margin", report["missing_required_evidence"])
        self.assertFalse(report["hard_fail"])

    def test_complete_governed_lattice_evidence_can_satisfy_axis(self):
        payload = {
            "mission": {"ship": "WAYFARER_BASELINE"},
            "candidate": {
                "candidate_id": "F000001",
                "lattice_state": {
                    "configuration_id": "WAYFARER_BASELINE",
                    "domain_membership": "BOUND",
                    "attachment_state": "ATTACHED",
                    "formation_state": "FORMED",
                    "integrity_state": "NOMINAL",
                    "hardware_condition": "NOMINAL",
                    "thermal_margin": {"qualified": True},
                    "bank_margin": {"qualified": True},
                },
            },
            "source_authority": "SOURCE-010",
        }
        report = lattice.classify_lattice_evidence(payload)
        self.assertEqual(report["disposition"], "SATISFIED")
        self.assertEqual(report["missing_required_evidence"], [])

    def test_governed_summary_lines_expose_axis_and_missing_groups(self):
        report = {
            "axis": "lattice_coherence",
            "disposition": "INDETERMINATE_NOT_CERTIFIABLE",
            "missing_required_evidence": ["thermal_margin", "bank_margin"],
        }
        lines = lattice.governed_summary_lines(report)
        self.assertEqual(lines[0], "QUALIFICATION_AXIS=lattice_coherence")
        self.assertEqual(lines[1], "QUALIFICATION_DISPOSITION=INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(lines[2], "QUALIFICATION_MISSING_REQUIRED_EVIDENCE=bank_margin,thermal_margin")

    def test_axis_local_authority_only(self):
        report = lattice.build_static_contract()
        self.assertTrue(report["authority"]["certifies_lattice_coherence_only"])
        self.assertFalse(report["authority"]["certifies_overall_ga"])
        self.assertEqual(report["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["authority"]["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["authority"]["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
