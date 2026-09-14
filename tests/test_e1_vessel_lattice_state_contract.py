import unittest

from engineering.experience_one.qualification import e1_vessel_lattice_state_contract as lattice


class E1VesselLatticeStateContractTests(unittest.TestCase):
    def test_unknown_state_is_explicit_and_non_certifying(self):
        report = lattice.build_unknown_state()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(
            sorted(report["missing_required_evidence"]),
            sorted([
                "bank_margin",
                "domain_membership_and_attachment_state",
                "formation_and_integrity_state",
                "hardware_condition",
            ]),
        )
        self.assertFalse(report["authority"]["certifies_lattice_coherence"])
        self.assertEqual(report["authority"]["llm_calculation_authority"], "ZERO")

    def test_contract_does_not_invent_thresholds_or_numeric_margins(self):
        contract = lattice.build_contract()
        self.assertFalse(contract["policy"]["invent_numeric_thresholds"])
        self.assertFalse(contract["policy"]["infer_unknown_as_nominal"])
        self.assertTrue(contract["policy"]["explicit_unknown_allowed"])

    def test_all_required_groups_must_be_known_before_satisfied(self):
        state = lattice.build_unknown_state()
        state["state"].update({
            "domain_membership_and_attachment_state": "ATTACHED_CONFIRMED",
            "formation_and_integrity_state": "FORMED_INTEGRITY_CONFIRMED",
            "hardware_condition": "NOMINAL_CONFIRMED",
            "thermal_margin": "POSITIVE_CONFIRMED",
            "bank_margin": "POSITIVE_CONFIRMED",
        })
        report = lattice.evaluate_state(state["state"])
        self.assertEqual(report["disposition"], "SATISFIED")
        self.assertEqual(report["missing_required_evidence"], [])


if __name__ == "__main__":
    unittest.main()
