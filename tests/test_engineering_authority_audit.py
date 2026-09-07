from __future__ import annotations

import unittest
from pathlib import Path

from loom.engineering_authority_audit import engineering_authority_audit


class EngineeringAuthorityAuditTests(unittest.TestCase):
    def test_exact_repo_engineering_authority_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report = engineering_authority_audit(root)
        self.assertEqual(report["contract"], "LOOM_F_PA_ENGINEERING_AUTHORITY_AUDIT_V1")
        self.assertEqual(report["engineering_canon_git_blob"], "618ee985f395414e0acbb583fa82e1b297745aba")
        self.assertGreaterEqual(report["locked_or_governing_count"], 7)
        self.assertEqual(report["diagnostic_shadow_count"], 2)
        self.assertGreaterEqual(report["missing_runtime_domain_count"], 10)
        domains = report["authority_domains"]
        self.assertEqual(domains["PROPULSION_REGIME_SEPARATION"], "GOVERNING_CANON")
        self.assertEqual(domains["TORCH_THRUST_MAGNITUDE_RUNTIME_CHECK"], "DIAGNOSTIC_SHADOW_ONLY")
        self.assertEqual(domains["CERTIFIED_THRUST_VECTOR_GIMBAL_ENVELOPE"], "MISSING")
        self.assertEqual(domains["VEHICLE_TRUE_6DOF_DYNAMICS"], "MISSING")
        self.assertEqual(domains["SENSOR_SUITE_MEASUREMENT_MODELS"], "MISSING")


if __name__ == "__main__":
    unittest.main()
