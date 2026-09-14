import unittest

from engineering.experience_one.qualification import e1_ga_evidence_adapter as adapter


class E1GaEvidenceAdapterTests(unittest.TestCase):
    def test_report_schema_and_authority(self):
        report = adapter.build_static_evidence_report()
        self.assertEqual(report["schema"], "LOOM_E1_GA_EVIDENCE_ADAPTER_V1")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["authority"]["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["authority"]["llm_calculation_authority"], "ZERO")
        self.assertFalse(report["authority"]["certifies_ga_outcome"])

    def test_two_packages_and_five_blocked_axes_are_preserved(self):
        report = adapter.build_static_evidence_report()
        self.assertEqual(set(report["packages"]), {
            "endpoint_domain_physical_compatibility",
            "route_vessel_coherence",
        })
        self.assertEqual(report["blocked_axes"], [
            "causal_structure",
            "domain_size",
            "lattice_coherence",
            "local_geometry",
            "loom_coherence",
        ])
        self.assertFalse(report["evidence_policy"]["cross_axis_compensation_allowed"])
        self.assertFalse(report["evidence_policy"]["package_level_shortcut_to_admissible_allowed"])

    def test_package_a_does_not_promote_reference_results_to_acceptance(self):
        package = adapter.build_static_evidence_report()["packages"]["endpoint_domain_physical_compatibility"]
        fields = package["fields"]
        self.assertEqual(fields["translation_domain_geometry_or_certification_envelope"]["state"], "MISSING")
        self.assertEqual(fields["qualified_local_geometry_compatibility_result"]["state"], "PRESENT_BUT_NOT_ACCEPTANCE_AUTHORITY")
        self.assertEqual(fields["qualified_causal_compatibility_result_or_equivalent_invariant"]["state"], "PRESENT_BUT_NOT_ACCEPTANCE_AUTHORITY")

    def test_package_b_distinguishes_operational_form_from_certification(self):
        package = adapter.build_static_evidence_report()["packages"]["route_vessel_coherence"]
        fields = package["fields"]
        self.assertEqual(fields["route_solution_identity_and_direction"]["state"], "PRESENT_OPERATIONAL_EVIDENCE")
        self.assertEqual(fields["route_evidence_destination_state_and_momentum_mapping"]["state"], "RUNTIME_INSPECTION_REQUIRED")
        self.assertEqual(fields["route_burden_and_uncertainty"]["state"], "RUNTIME_INSPECTION_REQUIRED")
        self.assertEqual(fields["formation_and_integrity_state"]["state"], "RUNTIME_INSPECTION_REQUIRED")
        self.assertEqual(fields["hardware_thermal_and_bank_margins"]["state"], "RUNTIME_INSPECTION_REQUIRED")
        self.assertEqual(fields["certification_disposition"]["state"], "MISSING")

    def test_runtime_payload_inventory_is_generic_and_non_mutating(self):
        payload = {
            "candidate_id": "F000001",
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "leg": {
                "arrival": {"epoch_utc": "2226-08-22T09:45:17.864616Z"},
                "metric_segment": {"semantics": "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY"},
                "momentum_mapping": {"kind": "example"},
            },
        }
        inventory = adapter.inventory_payload(payload)
        self.assertIn("leg.arrival.epoch_utc", inventory["paths"])
        self.assertIn("leg.momentum_mapping.kind", inventory["paths"])
        self.assertEqual(payload["candidate_id"], "F000001")


if __name__ == "__main__":
    unittest.main()
