"""Promotion-scope and rollback checks for the governed Earth v4 pointer."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from earth_baseline_resolver import BaselineResolutionError, load_endpoint_countries, resolve


BASE = Path(__file__).resolve().parents[1]
V4 = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24")
V3 = Path("/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pointer():
    return {"schema": "loom-earth-local-economic-baseline-pointer-v1",
            "active_designation": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24",
            "active_manifest": str(V4 / "BASELINE_MANIFEST.json"),
            "active_manifest_sha256": digest(V4 / "BASELINE_MANIFEST.json"),
            "active_decision_sha256": digest(V4 / "BASELINE_DECISION.md"),
            "previous_formal_designation": "EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23",
            "rollback_manifest": str(V3 / "BASELINE_MANIFEST.json"),
            "rollback_manifest_sha256": digest(V3 / "BASELINE_MANIFEST.json")}


class V4PromotionResolverTests(unittest.TestCase):
    def test_promoted_scope_resolves_as_80_economic_plus_237_demographic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pointer.json"
            path.write_text(json.dumps(pointer()))
            resolved = resolve(path)
            self.assertEqual(resolved["designation"], "EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24")
            self.assertEqual(resolved["coverage"]["economic_economies"], 80)
            self.assertEqual(resolved["coverage"]["identity_demographic_areas"], 237)
            self.assertEqual(resolved["coverage"]["demographic_only_areas"], 157)
            self.assertEqual(len(load_endpoint_countries(path)), 80)

    def test_false_coverage_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = json.loads((V4 / "BASELINE_MANIFEST.json").read_text())
            manifest["promotion_scope"]["sha256"] = "0" * 64
            (folder / "BASELINE_DECISION.md").write_bytes((V4 / "BASELINE_DECISION.md").read_bytes())
            manifest_path = folder / "BASELINE_MANIFEST.json"
            manifest_path.write_text(json.dumps(manifest))
            declared = pointer()
            declared.update(active_manifest=str(manifest_path), active_manifest_sha256=digest(manifest_path))
            pointer_path = folder / "pointer.json"
            pointer_path.write_text(json.dumps(declared))
            with self.assertRaisesRegex(BaselineResolutionError, "V4 designation/run records disagree"):
                resolve(pointer_path)

    def test_pointer_only_rollback_resolves_preserved_v3(self):
        with tempfile.TemporaryDirectory() as directory:
            declared = pointer()
            declared.update(active_designation=declared["previous_formal_designation"],
                            active_manifest=declared["rollback_manifest"],
                            active_manifest_sha256=declared["rollback_manifest_sha256"],
                            active_decision_sha256=digest(V3 / "BASELINE_DECISION.md"))
            path = Path(directory) / "pointer.json"
            path.write_text(json.dumps(declared))
            self.assertEqual(resolve(path)["designation"], declared["active_designation"])
            self.assertEqual(len(load_endpoint_countries(path)), 80)


if __name__ == "__main__":
    unittest.main()
