import unittest

from engineering.civstate.hel_texture_upstream_provenance import summarize_upstream_rows


class HelTextureUpstreamProvenanceTests(unittest.TestCase):
    def test_duplicate_texture_pairs_are_compared_without_declaring_defect(self):
        rows = [
            {
                "node_subject_id": "NODE:HEL-03",
                "resident_population": 10.0,
                "transient_daily_population": 2.0,
                "workforce_assigned": 100.0,
                "cargo_throughput_tonnes_year": 1000.0,
                "passenger_movements_year": 50.0,
                "ship_calls_year": 4.0,
                "strategic_centrality": 0.5,
                "economic_centrality": 0.6,
                "transport_centrality": 0.7,
                "influence_actor_count": 4,
                "influence_domain_count": 3,
                "influence_weight_sum": 2.0,
                "influence_weight_max": 0.8,
            },
            {
                "node_subject_id": "NODE:HEL-10",
                "resident_population": 10.0,
                "transient_daily_population": 2.0,
                "workforce_assigned": 100.0,
                "cargo_throughput_tonnes_year": 1000.0,
                "passenger_movements_year": 50.0,
                "ship_calls_year": 4.0,
                "strategic_centrality": 0.5,
                "economic_centrality": 0.6,
                "transport_centrality": 0.7,
                "influence_actor_count": 4,
                "influence_domain_count": 3,
                "influence_weight_sum": 2.0,
                "influence_weight_max": 0.8,
            },
        ]
        report = summarize_upstream_rows(rows, [("NODE:HEL-03", "NODE:HEL-10")])
        self.assertEqual(report["pair_results"][0]["identical_upstream_fields"], report["compared_fields"])
        self.assertEqual(report["interpretation_authority"], "DIAGNOSTIC_ONLY_NO_DEFECT_DECLARATION")
        self.assertEqual(report["mutation_authority"], "ZERO")

    def test_differences_are_reported_field_by_field(self):
        rows = [
            {
                "node_subject_id": "NODE:HEL-04",
                "resident_population": 10.0,
                "transient_daily_population": 2.0,
                "workforce_assigned": 100.0,
                "cargo_throughput_tonnes_year": 1000.0,
                "passenger_movements_year": 50.0,
                "ship_calls_year": 4.0,
                "strategic_centrality": 0.5,
                "economic_centrality": 0.6,
                "transport_centrality": 0.7,
                "influence_actor_count": 4,
                "influence_domain_count": 3,
                "influence_weight_sum": 2.0,
                "influence_weight_max": 0.8,
            },
            {
                "node_subject_id": "NODE:HEL-06",
                "resident_population": 10.0,
                "transient_daily_population": 2.0,
                "workforce_assigned": 100.0,
                "cargo_throughput_tonnes_year": 900.0,
                "passenger_movements_year": 50.0,
                "ship_calls_year": 4.0,
                "strategic_centrality": 0.5,
                "economic_centrality": 0.6,
                "transport_centrality": 0.7,
                "influence_actor_count": 4,
                "influence_domain_count": 3,
                "influence_weight_sum": 2.0,
                "influence_weight_max": 0.8,
            },
        ]
        report = summarize_upstream_rows(rows, [("NODE:HEL-04", "NODE:HEL-06")])
        self.assertEqual(report["pair_results"][0]["different_upstream_fields"], ["cargo_throughput_tonnes_year"])


if __name__ == "__main__":
    unittest.main()
