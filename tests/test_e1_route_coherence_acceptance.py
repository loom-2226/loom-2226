import unittest

from engineering.experience_one.qualification import e1_route_coherence_acceptance as route_accept


class E1RouteCoherenceAcceptanceTests(unittest.TestCase):
    def test_missing_uncertainty_blocks_certification_without_hard_fail(self):
        payload = {
            "mission": {"route": ["CERES", "NEPTUNE_SYSTEM"], "ship": "WAYFARER_BASELINE"},
            "candidate": {"candidate_id": "F000001", "total_duration_s": 100.0, "total_remass_t": 1.0},
            "leg": {
                "arrival": {"epoch_utc": "2226-08-22T09:45:17.864616Z"},
                "metric_segment": {
                    "beta_c": 0.5,
                    "distance_km": 123.0,
                    "collapse_position_km_j2000_ecliptic": [1.0, 2.0, 3.0],
                    "semantics": "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY",
                },
                "ordinary_velocity_memory": {"collapse_velocity_km_s": [7.0, 8.0, 9.0]},
            },
            "source_authority": "SOURCE-010",
        }
        report = route_accept.classify_route_evidence(payload)
        self.assertEqual(report["axis"], "loom_coherence")
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("route_uncertainty", report["missing_required_evidence"])
        self.assertNotIn("route_identity_and_direction", report["missing_required_evidence"])
        self.assertFalse(report["hard_fail"])

    def test_explicit_uncertainty_can_close_route_axis_when_all_other_groups_present(self):
        payload = {
            "mission": {"route": ["CERES", "NEPTUNE_SYSTEM"], "ship": "WAYFARER_BASELINE"},
            "candidate": {
                "candidate_id": "F000001",
                "total_duration_s": 100.0,
                "total_remass_t": 1.0,
                "uncertainty": {"arrival_position_km_1sigma": 2.0},
            },
            "leg": {
                "arrival": {"epoch_utc": "2226-08-22T09:45:17.864616Z"},
                "metric_segment": {
                    "beta_c": 0.5,
                    "distance_km": 123.0,
                    "collapse_position_km_j2000_ecliptic": [1.0, 2.0, 3.0],
                    "semantics": "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY",
                },
                "ordinary_velocity_memory": {"collapse_velocity_km_s": [7.0, 8.0, 9.0]},
            },
            "source_authority": "SOURCE-010",
        }
        report = route_accept.classify_route_evidence(payload)
        self.assertEqual(report["disposition"], "SATISFIED")
        self.assertEqual(report["missing_required_evidence"], [])
        self.assertFalse(report["hard_fail"])

    def test_governed_summary_lines_expose_axis_disposition_and_missing_evidence(self):
        report = {
            "axis": "loom_coherence",
            "disposition": "INDETERMINATE_NOT_CERTIFIABLE",
            "missing_required_evidence": ["route_uncertainty"],
        }
        lines = route_accept.governed_summary_lines(report)
        self.assertEqual(lines[0], "QUALIFICATION_AXIS=loom_coherence")
        self.assertEqual(lines[1], "QUALIFICATION_DISPOSITION=INDETERMINATE_NOT_CERTIFIABLE")
        self.assertEqual(lines[2], "QUALIFICATION_MISSING_REQUIRED_EVIDENCE=route_uncertainty")

    def test_no_cross_axis_or_runtime_authority_is_created(self):
        report = route_accept.build_static_contract()
        self.assertFalse(report["authority"]["certifies_lattice_coherence"])
        self.assertEqual(report["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["authority"]["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["authority"]["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
