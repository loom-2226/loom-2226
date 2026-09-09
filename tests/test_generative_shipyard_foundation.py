from __future__ import annotations

import unittest

from qualification.synthesis.generative_shipyard_foundation import (
    FOUNDATION_AUTHORITY,
    GenerativeShipyardError,
    ModelAdequacyContract,
    canonical_result_json,
    run_wayfarer_config_experiment,
    validate_adequacy,
    wayfarer_config_domain,
)


class GenerativeShipyardFoundationTests(unittest.TestCase):
    def test_wayfarer_experiment_is_deterministic_and_fail_closed(self):
        a = run_wayfarer_config_experiment(2226)
        b = run_wayfarer_config_experiment(2226)
        self.assertEqual(a.experiment_hash, b.experiment_hash)
        self.assertEqual(canonical_result_json(a), canonical_result_json(b))
        self.assertFalse(a.flight_dynamics_authority)
        self.assertFalse(a.canon_changed)
        self.assertFalse(a.production_shipclasses_changed)
        self.assertEqual(len(a.outcomes), 10)

        legal = [x for x in a.outcomes if x.status == "SURVIVED_SCREEN"]
        rejected = [x for x in a.outcomes if x.status == "REJECTED_BY_ADEQUATE_MODEL"]
        self.assertGreaterEqual(len(legal), 2)
        self.assertGreaterEqual(len(rejected), 2)
        self.assertTrue(all(not x.flight_dynamics_authority for x in a.outcomes))
        self.assertTrue(all(x.failed_constraint_ids for x in rejected))
        self.assertTrue(all(x.rejection_reason for x in rejected))
        self.assertTrue(a.pareto_frontier)
        legal_ids = {x.candidate_id for x in legal}
        self.assertTrue(all(x.candidate_id in legal_ids for x in a.pareto_frontier))

    def test_probe_rejections_are_traceable_to_current_s1_contract(self):
        result = run_wayfarer_config_experiment()
        by_id = {row.candidate_id.split("::")[1]: row for row in result.outcomes}
        self.assertIn("LAUNCH_WITHIN_BAY", by_id["P04"].failed_constraint_ids)
        self.assertIn("LAUNCH_WITHIN_BAY", by_id["P05"].failed_constraint_ids)
        self.assertIn("TANK_QUADRATURE_MASS_STATION", by_id["P06"].failed_constraint_ids)
        self.assertIn("TANK_QUADRATURE_MASS_STATION", by_id["P07"].failed_constraint_ids)

    def test_domain_keeps_open_geometry_open(self):
        domain = wayfarer_config_domain()
        self.assertEqual(domain.authority_status, FOUNDATION_AUTHORITY)
        choices = {row.choice_id: row for row in domain.choices}
        self.assertEqual(choices["tank_axial_geometry"].status, "OPEN_NOT_ADMITTED")
        self.assertEqual(choices["tank_axial_geometry"].allowed_values, ())
        self.assertEqual(choices["radiator_panel_geometry"].status, "OPEN_NOT_ADMITTED")

    def test_model_cannot_claim_selection_adequacy_by_accident(self):
        bad = ModelAdequacyContract(
            model_id="BAD",
            fidelity="L0",
            validity_domain="test",
            known_omissions=("everything",),
            calibration_basis="none",
            adequate_for_screening=False,
            adequate_for_rejection=False,
            adequate_for_selection=True,
            admissible_rejection_reasons=(),
        )
        with self.assertRaises(GenerativeShipyardError):
            validate_adequacy(bad)


if __name__ == "__main__":
    unittest.main()
