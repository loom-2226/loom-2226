"""Focused non-mutating tests for the designated Earth authority."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import earth_baseline_resolver as resolver_module
from earth_baseline_resolver import (
    BASELINE_ROOT,
    BaselineResolutionError,
    CURRENT_POINTER,
    load_endpoint_countries,
    resolve,
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class EarthBaselineResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pointer = json.loads(CURRENT_POINTER.read_text())
        cls.current = resolve()

    def test_current_pointer_resolves_to_qualified_coupled_successor(self):
        self.assertEqual(
            self.current["designation"],
            "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24",
        )
        self.assertEqual(self.current["policy"], "MED_CENTRAL__SYNTH_CENTRAL")
        self.assertGreater(self.current["verified_registered_files"], 60)
        self.assertEqual(
            self.current["coverage"],
            {"economic_economies": 80, "identity_demographic_areas": 237,
             "demographic_only_areas": 157},
        )
        self.assertEqual(sha(self.current["manifest"]), self.pointer["active_manifest_sha256"])
        self.assertTrue(all(path.is_file() for path in self.current["artifacts"].values()))

    def test_downstream_endpoint_loader_uses_selected_80_economy_result(self):
        countries = load_endpoint_countries()
        self.assertEqual(len(countries), 80)
        self.assertEqual({row["year"] for row in countries}, {2226})
        self.assertEqual(len({row["iso3"] for row in countries}), 80)

    def test_post_2100_authority_is_annual_and_wpp_boundary_is_preserved(self):
        authority = self.current["demographic_authority"]
        self.assertEqual(authority["wpp_authority_through_year"], 2100)
        self.assertEqual(authority["post_2100_selected_state"],
                         "EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR")
        self.assertEqual(authority["post_2100_status"],
                         "SELECTED_ANNUAL_COHORT_TRAJECTORY_2101_2226")
        self.assertEqual(authority["selected_scenario"], "MED_CENTRAL__SYNTH_CENTRAL")
        self.assertAlmostEqual(authority["earth_biological_population_2226"],
                               7163281708.265873, places=6)
        self.assertAlmostEqual(authority["earth_synthetic_person_population_2226"],
                               9672505.78986048, places=6)
        self.assertAlmostEqual(authority["earth_recognized_person_population_2226"],
                               7172954214.055734, places=6)
        self.assertEqual(authority["selected_country_area_count"], 237)

    def test_workforce_and_personhood_categories_resolve_separately(self):
        labor = self.current["labor_authority"]
        self.assertEqual(labor["workforce_invariant_passed"], 80)
        self.assertEqual(labor["workforce_invariant_failed"], 0)
        self.assertNotEqual(labor["synthetic_labor_2226"], labor["machine_task_capacity_2226"])
        self.assertAlmostEqual(
            labor["total_effective_labor_2226"],
            labor["biological_labor_2226"] + labor["synthetic_labor_2226"] +
            labor["machine_task_capacity_2226"],
            places=5,
        )

    def test_demographic_pointer_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_pointer = json.loads(resolver_module.DEMOGRAPHIC_POINTER.read_text())
            fake_pointer["selected_endpoint_sha256"] = "0" * 64
            path = Path(directory) / "demographic_pointer.json"
            path.write_text(json.dumps(fake_pointer))
            with patch.object(resolver_module, "DEMOGRAPHIC_POINTER", path):
                with self.assertRaisesRegex(BaselineResolutionError, "SHA-256 mismatch"):
                    resolve()

    def test_invalid_active_manifest_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            pointer = dict(self.pointer, active_manifest=str(Path(directory) / "missing.json"))
            path = Path(directory) / "pointer.json"
            path.write_text(json.dumps(pointer))
            with self.assertRaises(BaselineResolutionError):
                resolve(path)

    def test_registered_artifact_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest = json.loads(self.current["manifest"].read_text())
            manifest["files"][0]["sha256"] = "0" * 64
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            pointer = dict(self.pointer, active_manifest=str(manifest_path),
                           active_manifest_sha256=sha(manifest_path))
            pointer_path = directory / "pointer.json"
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(BaselineResolutionError, "SHA-256 mismatch"):
                resolve(pointer_path)

    def test_v4_and_bridge_remain_hash_pinned_rollback_provenance(self):
        v4 = resolver_module._authority_path(self.pointer["rollback_manifest"])
        bridge = resolver_module._authority_path(self.pointer["rollback_demographic_manifest"])
        self.assertEqual(sha(v4), self.pointer["rollback_manifest_sha256"])
        self.assertEqual(sha(bridge), self.pointer["rollback_demographic_manifest_sha256"])
        self.assertTrue((BASELINE_ROOT / "earth_long_run_economic_baseline_v3_repaired_2026_09_23").is_dir())


if __name__ == "__main__":
    unittest.main()
