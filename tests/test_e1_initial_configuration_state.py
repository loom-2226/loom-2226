import unittest

from engineering.experience_one.qualification.e1_initial_configuration_state import (
    build_e1_initial_configuration_state,
)


class E1InitialConfigurationStateTests(unittest.TestCase):
    def test_initial_configuration_is_explicit_and_complete(self):
        state = build_e1_initial_configuration_state()
        evidence = state.to_evidence()
        self.assertEqual(evidence["disposition"], "AUTHORED_RUNTIME_INPUT_PRESENT")
        self.assertEqual(evidence["missing_authored_scenario_inputs"], [])
        self.assertEqual(evidence["authored_state"]["launch_attachment_state"], "DOCKED")
        self.assertEqual(evidence["authored_state"]["external_attachment_state"], "FREE")
        self.assertEqual(evidence["authored_state"]["deployable_structure_state"], "STOWED")

    def test_domain_membership_remains_derived_only(self):
        evidence = build_e1_initial_configuration_state().to_evidence()
        self.assertEqual(evidence["derived_state"]["domain_membership_state"], "UNKNOWN")
        self.assertTrue(evidence["policy"]["domain_membership_is_derived_only"])
        self.assertFalse(evidence["policy"]["manual_domain_membership_override_allowed"])
        self.assertFalse(evidence["authority"]["certifies_domain_membership"])

    def test_scenario_lock_is_identified_as_authored_not_recovered_fact(self):
        evidence = build_e1_initial_configuration_state().to_evidence()
        self.assertEqual(evidence["scenario_lock"]["kind"], "E1_AUTHORED_INITIAL_CONDITION")
        self.assertEqual(evidence["scenario_lock"]["epoch_utc"], "2226-08-22T01:32:00Z")
        self.assertEqual(evidence["scenario_lock"]["route"], ["CERES", "NEPTUNE_SYSTEM"])


if __name__ == "__main__":
    unittest.main()
