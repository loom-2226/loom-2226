import unittest

from engineering.experience_one.qualification.e1_domain_membership_attachment_state import (
    evaluate_runtime_configuration_state,
    build_current_e1_runtime_inventory,
)


class DomainMembershipAttachmentStateTests(unittest.TestCase):
    def test_unknown_runtime_state_remains_non_certifying(self):
        report = evaluate_runtime_configuration_state({
            "configuration_identity": "WAYFARER_REFERENCE_SCHEMATIC_V2_4A",
        })
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(
            report["missing_required_evidence"],
            [
                "deployable_structure_state",
                "domain_membership_state",
                "external_attachment_state",
                "launch_attachment_state",
            ],
        )

    def test_complete_runtime_state_can_be_present_without_certifying_domain_geometry(self):
        report = evaluate_runtime_configuration_state({
            "configuration_identity": "WAYFARER_REFERENCE_SCHEMATIC_V2_4A",
            "launch_attachment_state": "DOCKED",
            "external_attachment_state": "FREE",
            "deployable_structure_state": "STOWED",
            "domain_membership_state": "MEMBER",
        })
        self.assertEqual(report["disposition"], "RUNTIME_CONFIGURATION_STATE_PRESENT")
        self.assertEqual(report["missing_required_evidence"], [])
        self.assertFalse(report["authority"]["certifies_domain_geometry"])
        self.assertFalse(report["authority"]["certifies_domain_size"])
        self.assertFalse(report["authority"]["certifies_lattice_coherence"])

    def test_runtime_state_is_not_inferred_from_baseline_identity(self):
        report = build_current_e1_runtime_inventory()
        self.assertEqual(report["configuration_identity"], "WAYFARER_REFERENCE_SCHEMATIC_V2_4A")
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertFalse(report["policy"]["infer_launch_docked_from_baseline"])
        self.assertFalse(report["policy"]["infer_radiators_stowed_from_mode"])
        self.assertFalse(report["policy"]["infer_domain_membership_from_configuration_identity"])


if __name__ == "__main__":
    unittest.main()
