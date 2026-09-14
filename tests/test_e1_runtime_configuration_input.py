import unittest

from engineering.experience_one.qualification.e1_runtime_configuration_input import (
    DeployableStructureState,
    ExternalAttachmentState,
    LaunchAttachmentState,
    RuntimeConfigurationInput,
    build_default_e1_runtime_configuration,
)


class RuntimeConfigurationInputTests(unittest.TestCase):
    def test_default_authored_states_are_unknown(self):
        state = build_default_e1_runtime_configuration()
        self.assertEqual(state.launch_attachment_state, LaunchAttachmentState.UNKNOWN)
        self.assertEqual(state.external_attachment_state, ExternalAttachmentState.UNKNOWN)
        self.assertEqual(state.deployable_structure_state, DeployableStructureState.UNKNOWN)

    def test_domain_membership_is_not_an_authored_input(self):
        fields = RuntimeConfigurationInput.__dataclass_fields__
        self.assertNotIn("domain_membership_state", fields)

    def test_explicit_scenario_inputs_serialize_without_certifying_membership(self):
        state = RuntimeConfigurationInput(
            configuration_identity="WAYFARER_REFERENCE_SCHEMATIC_V2_4A",
            launch_attachment_state=LaunchAttachmentState.DOCKED,
            external_attachment_state=ExternalAttachmentState.FREE,
            deployable_structure_state=DeployableStructureState.STOWED,
        )
        evidence = state.to_evidence()
        self.assertEqual(evidence["authored_state"]["launch_attachment_state"], "DOCKED")
        self.assertEqual(evidence["authored_state"]["external_attachment_state"], "FREE")
        self.assertEqual(evidence["authored_state"]["deployable_structure_state"], "STOWED")
        self.assertEqual(evidence["derived_state"]["domain_membership_state"], "UNKNOWN")
        self.assertTrue(evidence["policy"]["domain_membership_is_derived_only"])
        self.assertFalse(evidence["authority"]["certifies_domain_membership"])


if __name__ == "__main__":
    unittest.main()
