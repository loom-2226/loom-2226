"""Focused non-mutating tests for the designated Earth baseline."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import earth_baseline_resolver as resolver_module
from earth_baseline_resolver import (
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

    def test_current_pointer_resolves_to_qualified_successor(self):
        self.assertEqual(self.current["designation"], "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24")
        self.assertEqual(self.current["model_version"], "v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1+earth-v4-seed")
        self.assertEqual(self.current["policy"], "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1")
        self.assertGreater(self.current["verified_registered_files"], 40)
        self.assertEqual(self.current["coverage"], {"economic_economies": 80,
                                                     "identity_demographic_areas": 237,
                                                     "demographic_only_areas": 157})
        self.assertEqual(sha(self.current["manifest"]), self.pointer["active_manifest_sha256"])
        self.assertTrue(all(path.is_file() for path in self.current["artifacts"].values()))

    def test_downstream_endpoint_loader_uses_current_result(self):
        countries = load_endpoint_countries()
        self.assertEqual(len(countries), 80)
        self.assertEqual({row["year"] for row in countries}, {2226})
        self.assertEqual(sha(self.current["artifacts"]["endpoint_countries"]),
                         json.loads(Path(self.pointer["active_manifest"]).read_text())["selected_outputs"]["successor_80_2226/results/countries_2226.ndjson"]["sha256"])

    def test_2226_demographic_endpoint_is_selected_without_fake_annual_tail(self):
        authority = self.current["demographic_authority"]
        self.assertEqual(authority["wpp_authority_through_year"], 2100)
        self.assertEqual(authority["post_2100_selected_state"],
                         "EARTH_2226_CANON_CONSTRAINED_COUNTRY_ALLOCATION")
        self.assertEqual(authority["post_2100_status"],
                         "SELECTED_ENDPOINT_ONLY_NO_ANNUAL_COHORT_TRAJECTORY")
        self.assertEqual(authority["selected_year"], 2226)
        self.assertAlmostEqual(authority["earth_biological_population_2226"],
                               8312538895.185726, places=6)
        self.assertEqual(authority["selected_country_area_count"], 237)
        self.assertEqual(authority["cohort_detail_status"],
                         "NOT_REPROMOTED_BY_THIS_CORRECTION")
        self.assertEqual(authority["recovered_cohort_control_2226"], 8442000000)
        self.assertEqual(authority["recovered_control_status"],
                         "PROVISIONAL_PROPAGATION_DEPENDENT_NOT_GOVERNING")
        self.assertIn("demographic_sensitivity", self.current["artifacts"])
        self.assertIn("demographic_authority_2226", self.current["artifacts"])
        self.assertIn("demographic_country_population_2226", self.current["artifacts"])

    def test_demographic_correction_manifest_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fake_pointer = json.loads(resolver_module.DEMOGRAPHIC_POINTER.read_text())
            fake_pointer["active_manifest_sha256"] = "0" * 64
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
            manifest = json.loads(Path(self.pointer["active_manifest"]).read_text())
            run = json.loads(Path(manifest["run_manifest"]["path"]).read_text())
            run["candidate_local_artifacts"]["successor_80_2226/results/countries_2226.ndjson"]["sha256"] = "0" * 64
            run_path = directory / "run.json"
            run_path.write_text(json.dumps(run))
            manifest["run_manifest"].update(path=str(run_path), sha256=sha(run_path), bytes=run_path.stat().st_size)
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            (directory / "BASELINE_DECISION.md").write_bytes(
                (Path(self.pointer["active_manifest"]).parent / "BASELINE_DECISION.md").read_bytes()
            )
            pointer = dict(self.pointer, active_manifest=str(manifest_path), active_manifest_sha256=sha(manifest_path))
            pointer_path = directory / "pointer.json"
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(BaselineResolutionError, "SHA-256 mismatch"):
                resolve(pointer_path)

    def test_pointer_only_rollback_uses_preserved_v3_result(self):
        with tempfile.TemporaryDirectory() as directory:
            pointer = dict(self.pointer)
            pointer["active_manifest"] = pointer["rollback_manifest"]
            pointer["active_manifest_sha256"] = pointer["rollback_manifest_sha256"]
            pointer["active_designation"] = pointer["previous_formal_designation"]
            pointer["active_decision_sha256"] = sha(Path(pointer["active_manifest"]).parent / "BASELINE_DECISION.md")
            path = Path(directory) / "pointer.json"
            path.write_text(json.dumps(pointer))
            rollback = resolve(path)
            self.assertEqual(rollback["policy"], "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1")
            self.assertGreater(rollback["verified_registered_files"], 40)
            self.assertNotEqual(rollback["artifacts"]["endpoint_countries"],
                                self.current["artifacts"]["endpoint_countries"])
            self.assertEqual(len(load_endpoint_countries(path)), 80)
        self.assertEqual(json.loads(CURRENT_POINTER.read_text()), self.pointer)


if __name__ == "__main__":
    unittest.main()
