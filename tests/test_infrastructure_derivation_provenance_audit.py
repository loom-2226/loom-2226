from __future__ import annotations

from pathlib import Path
import json
import unittest

from loom.infrastructure_derivation_provenance_audit import (
    CONTRACT,
    infrastructure_derivation_provenance_audit,
)


class InfrastructureDerivationProvenanceAuditTests(unittest.TestCase):
    def test_exact_repo_derivation_provenance_matrix(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = infrastructure_derivation_provenance_audit(root)
        summary = result["summary"]
        rows = result["rows"]

        self.assertEqual(result["contract"], CONTRACT)
        self.assertEqual(summary["row_count"], 127)
        self.assertEqual(len(rows), 127)
        self.assertTrue(all(row["PRIMARY_STRUCTURED_SOURCE"] == "WORLD_SQL" for row in rows))
        self.assertTrue(all(row["SPATIAL_DERIVABILITY"] == "CONSTRAINED_DESIGN_REQUIRED" for row in rows))
        self.assertTrue(all(row["QUALIFICATION_STATUS"] == "NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED" for row in rows))
        self.assertTrue(all(row["PROMOTION_TARGET"] == "WORLD_QUALIFIED_PHYSICAL_AUTHORITY" for row in rows))
        self.assertEqual(
            summary["source_conflict_status"],
            {"NO_CONFLICT_DEMONSTRATED_AUDIT_ONLY_NO_PROMOTION": 127},
        )
        self.assertEqual(
            summary["provenance_chain_status"],
            {"COMPLETE_STRUCTURED_REFERENCE_CHAIN": 127},
        )
        self.assertEqual(summary["node_source"], {"CANON I v2.4": 127})
        self.assertEqual(summary["state_source"], {"DERIVED_PLACEMENT_MODEL": 127})

        print("F_PA_INFRA_PROVENANCE_SUMMARY=" + json.dumps(summary, sort_keys=True))
        compact = [
            {
                "node_id": row["node_id"],
                "node_name": row["node_name"],
                "node_source": row["node_source"],
                "location_model_id": row["location_model_id"],
                "placement_model_status": row["placement_model_status"],
                "orbit_source_id": row["orbit_source_id"],
                "orbit_source_authority_status": row["orbit_source_authority_status"],
                "derivation_model_id": row["derivation_model_id"],
                "derivation_model_status": row["derivation_model_status"],
                "derivation_source_authority_status": row["derivation_source_authority_status"],
                "state_source": row["state_source"],
                "state_model_id": row["state_model_id"],
                "TEXT_CANON_CONSTRAINT": row["TEXT_CANON_CONSTRAINT"],
                "canon_i_mention": row["canon_i_mention"],
                "atlas_mention": row["atlas_mention"],
                "SOURCE_CONFLICT_STATUS": row["SOURCE_CONFLICT_STATUS"],
                "provenance_chain_status": row["provenance_chain_status"],
            }
            for row in rows
        ]
        print("F_PA_INFRA_PROVENANCE_ROWS=" + json.dumps(compact, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
