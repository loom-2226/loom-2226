import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "engineering" / "experience_one" / "qualification" / "e1_compound_ga_decision_rule.py"
spec = importlib.util.spec_from_file_location("e1_compound_ga_decision_rule", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompoundGADecisionRuleTests(unittest.TestCase):
    def test_hard_fail_has_precedence(self):
        result = module.evaluate_ga({
            "a": {"decision_state": "SATISFIED"},
            "b": {"decision_state": "HARD_FAIL"},
            "c": {"decision_state": "UNRESOLVED_REQUIRED"},
        })
        self.assertEqual(result["decision"], "INADMISSIBLE")
        self.assertEqual(result["blocking_axes"], ["b"])

    def test_unresolved_required_is_indeterminate_not_failure(self):
        result = module.evaluate_ga({
            "a": {"decision_state": "SATISFIED"},
            "b": {"decision_state": "UNRESOLVED_REQUIRED"},
        })
        self.assertEqual(result["decision"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(result["unresolved_required_axes"], ["b"])

    def test_all_satisfied_is_admissible(self):
        result = module.evaluate_ga({
            "a": {"decision_state": "SATISFIED"},
            "b": {"decision_state": "SATISFIED_NON_MATERIAL"},
        })
        self.assertEqual(result["decision"], "ADMISSIBLE")

    def test_cross_axis_compensation_is_forbidden(self):
        result = module.qualify_compound_ga_decision_rule()
        self.assertFalse(result["decision_rule"]["cross_axis_compensation_allowed"])
        self.assertFalse(result["decision_rule"]["weights_defined"])
        self.assertFalse(result["decision_rule"]["scalar_score_defined"])

    def test_current_e1_state_is_indeterminate(self):
        result = module.qualify_compound_ga_decision_rule()
        current = result["current_e1_evaluation"]
        self.assertEqual(current["decision"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("local_geometry", current["unresolved_required_axes"])
        self.assertIn("causal_structure", current["unresolved_required_axes"])
        self.assertIn("domain_size", current["unresolved_required_axes"])
        self.assertIn("loom_coherence", current["unresolved_required_axes"])
        self.assertIn("lattice_coherence", current["unresolved_required_axes"])

    def test_unknown_is_never_treated_as_zero_or_pass(self):
        result = module.qualify_compound_ga_decision_rule()
        self.assertFalse(result["uncertainty_policy"]["unknown_treated_as_zero"])
        self.assertFalse(result["uncertainty_policy"]["unknown_treated_as_satisfied"])
        self.assertTrue(result["uncertainty_policy"]["unknown_blocks_certification"])

    def test_no_runtime_or_campaign_binding(self):
        result = module.qualify_compound_ga_decision_rule()
        self.assertFalse(result["runtime_policy_bound"])
        self.assertEqual(result["runtime_policy_mutation"], "ZERO")
        self.assertEqual(result["campaign_state_mutation"], "ZERO")
        self.assertEqual(result["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
