import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).parents[1] / "engineering" / "experience_one" / "qualification" / "e1_compound_ga_coherence_model_form.py"
spec = importlib.util.spec_from_file_location("e1_compound_ga_coherence_model_form", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompoundGACoherenceModelFormTests(unittest.TestCase):
    def setUp(self):
        self.result = module.qualify_compound_ga_coherence_model_form()

    def test_passes_as_model_form_only(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(self.result["decision"], "LOOM_AND_LATTICE_COHERENCE_MODEL_FORM_QUALIFIED_NO_UNIVERSAL_NUMERIC_THRESHOLD")

    def test_axes_are_distinct(self):
        loom = self.result["coherence_axes"]["loom_coherence"]
        lattice = self.result["coherence_axes"]["lattice_coherence"]
        self.assertEqual(loom["role"], "ROUTE_TOPOLOGY_RELATIONAL_ACCESS_EVIDENCE")
        self.assertEqual(lattice["role"], "VESSEL_DOMAIN_FORMATION_AND_HARDWARE_STATE")
        self.assertNotEqual(loom["role"], lattice["role"])

    def test_no_scalar_threshold_is_invented(self):
        self.assertFalse(self.result["universal_coherence_threshold_defined"])
        self.assertFalse(self.result["loom_coherence_scalar_defined"])
        self.assertFalse(self.result["lattice_coherence_scalar_defined"])
        self.assertFalse(self.result["rf_research_promoted_to_engineering_authority"])

    def test_existing_operational_observables_are_preserved_as_inputs_not_ga_thresholds(self):
        loom = self.result["coherence_axes"]["loom_coherence"]
        lattice = self.result["coherence_axes"]["lattice_coherence"]
        self.assertIn("route_burden", loom["existing_operational_inputs"])
        self.assertIn("route_evidence", loom["existing_operational_inputs"])
        self.assertIn("integrity_class", lattice["existing_operational_inputs"])
        self.assertIn("formation_state", lattice["existing_operational_inputs"])
        self.assertTrue(loom["existing_inputs_are_not_universal_ga_thresholds"])
        self.assertTrue(lattice["existing_inputs_are_not_universal_ga_thresholds"])

    def test_unknowns_are_not_treated_as_zero(self):
        self.assertFalse(self.result["uncertainty_ledger"]["unknown_coherence_terms_treated_as_zero"])
        self.assertFalse(self.result["uncertainty_ledger"]["missing_topology_evidence_treated_as_absence"])
        self.assertFalse(self.result["uncertainty_ledger"]["excellent_formation_roll_overrides_hardware_limits"])

    def test_no_runtime_or_campaign_authority(self):
        self.assertFalse(self.result["admissibility_boolean_defined"])
        self.assertFalse(self.result["runtime_policy_bound"])
        self.assertEqual(self.result["runtime_policy_mutation"], "ZERO")
        self.assertEqual(self.result["campaign_state_mutation"], "ZERO")
        self.assertEqual(self.result["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
