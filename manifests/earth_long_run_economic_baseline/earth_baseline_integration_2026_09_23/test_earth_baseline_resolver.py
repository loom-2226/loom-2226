"""Focused non-mutating tests for the designated Earth baseline."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

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
        self.assertEqual(self.current["model_version"], "v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1")
        self.assertEqual(self.current["policy"], "WDI_NATIONAL_GFCF_GDP_LATEST_2024_2025_MEDIAN_2024_FALLBACK_v1")
        self.assertEqual(self.current["verified_registered_files"], 59)
        self.assertEqual(sha(self.current["manifest"]), self.pointer["active_manifest_sha256"])
        self.assertTrue(all(path.is_file() for path in self.current["artifacts"].values()))

    def test_downstream_endpoint_loader_uses_current_result(self):
        countries = load_endpoint_countries()
        self.assertEqual(len(countries), 80)
        self.assertEqual({row["year"] for row in countries}, {2226})
        self.assertEqual(sha(self.current["artifacts"]["endpoint_countries"]),
                         "bf4e9c59123ddd40f5361b53b051b69d0e1229a3b329711c257320f31006151a")

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
            run = json.loads(Path(manifest["qualified_successor_run_manifest"]["path"]).read_text())
            run["inputs"][0]["sha256"] = "0" * 64
            run_path = directory / "run.json"
            run_path.write_text(json.dumps(run))
            manifest["qualified_successor_run_manifest"].update(path=str(run_path), sha256=sha(run_path))
            manifest_path = directory / "manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            pointer = dict(self.pointer, active_manifest=str(manifest_path), active_manifest_sha256=sha(manifest_path))
            pointer.pop("active_decision_sha256", None)
            pointer_path = directory / "pointer.json"
            pointer_path.write_text(json.dumps(pointer))
            with self.assertRaisesRegex(BaselineResolutionError, "SHA-256 mismatch"):
                resolve(pointer_path)

    def test_pointer_only_rollback_uses_preserved_v1_result(self):
        with tempfile.TemporaryDirectory() as directory:
            pointer = dict(self.pointer)
            pointer["active_manifest"] = pointer["rollback_manifest"]
            pointer["active_manifest_sha256"] = pointer["rollback_manifest_sha256"]
            pointer["active_designation"] = pointer["previous_formal_designation"]
            pointer.pop("active_decision_sha256", None)
            path = Path(directory) / "pointer.json"
            path.write_text(json.dumps(pointer))
            rollback = resolve(path)
            self.assertEqual(rollback["policy"], "UNTREATED_FROZEN_2060_EXPLICIT_v1")
            self.assertEqual(rollback["verified_registered_files"], 75)
            self.assertNotEqual(rollback["artifacts"]["endpoint_countries"],
                                self.current["artifacts"]["endpoint_countries"])
            self.assertEqual(len(load_endpoint_countries(path)), 80)
        self.assertEqual(json.loads(CURRENT_POINTER.read_text()), self.pointer)


if __name__ == "__main__":
    unittest.main()
