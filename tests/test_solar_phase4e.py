"""Focused qualification and locked-membership tests for Solar Phase 4E."""
from __future__ import annotations

from datetime import timedelta
import hashlib
import json
from pathlib import Path
import unittest

from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import _epoch, registry_from_manifest, service_from_manifest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path("/home/ubuntu/loom_solar_assets")
MANIFEST = ROOT / "manifests/solar/SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json"
EVIDENCE = ROOT / "docs/qualification/SOLAR_PHASE4E_CURATED_42_PLUS_5_evidence.json"
EPOCHS = ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z", "2250-01-01T00:00:00Z", "2250-12-31T23:59:59Z")


class Phase4EQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(MANIFEST.read_text())
        cls.evidence = json.loads(EVIDENCE.read_text())
        cls.registry = registry_from_manifest(MANIFEST, ASSETS)
        cls.service = service_from_manifest(MANIFEST, ASSETS)

    def test_locked_accounting_is_exact_and_complete(self):
        self.assertEqual(self.document["locked_cohort"], {"natural_count": 42, "spacecraft_count": 5, "total_count": 47})
        self.assertEqual(len(self.document["identities"]), 47)
        self.assertEqual(len(self.evidence["rows"]), 47)
        self.assertEqual(self.evidence["counts"]["accounted_outcomes"], 47)
        self.assertEqual(sum(row["cohort"] == "NATURAL" for row in self.evidence["rows"]), 42)
        self.assertEqual(sum(row["cohort"] == "SPACECRAFT" for row in self.evidence["rows"]), 5)
        self.assertEqual({row["outcome"] for row in self.evidence["rows"]}, {"QUALIFIED_HORIZONS", "QUALIFIED_DIRECT", "QUALIFIED_PROPAGATED", "PARTIAL", "CATALOG_ONLY"})

    def test_all_manifest_assets_are_hash_pinned(self):
        for asset in self.document["assets"]:
            path = ASSETS / asset["local_path"]
            self.assertTrue(path.is_file(), path)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, asset["sha256"], path)
            self.assertEqual(path.stat().st_size, asset["byte_count"], path)

    def test_direct_targets_resolve_at_required_epochs(self):
        direct = [row for row in self.evidence["rows"] if row["outcome"] in ("QUALIFIED_DIRECT", "QUALIFIED_HORIZONS")]
        for row in direct:
            for epoch in EPOCHS:
                state = self.service.resolve(row["body_id"], epoch)
                self.assertEqual(state.provenance["naif_identifier"], str(row["naif_id"]))
                self.assertEqual(state.reference_frame, "J2000/ECLIPTIC")
                self.assertEqual(state.provenance["units"], "km,km/s")
                self.assertEqual(state, self.service.resolve(row["body_id"], epoch))
                self.assertEqual(len(state.position_km), 3)
                self.assertEqual(len(state.velocity_km_s), 3)

    def test_partial_and_catalog_only_states_are_explicit(self):
        for row in self.evidence["rows"]:
            if row["outcome"] == "CATALOG_ONLY":
                with self.assertRaises(CelestialStateError):
                    self.service.resolve(row["body_id"], EPOCHS[0])
        for body in ("NIX", "HYDRA", "KERBEROS", "STYX"):
            self.assertEqual(self.service.resolve(body, EPOCHS[0]).provenance["state_capability"], "EPHEMERIS_PARTIAL")
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, EPOCHS[-1])

    def test_spacecraft_are_distinct_and_fail_closed_outside_mission_coverage(self):
        for body, epoch in (("PIONEER10", "1973-01-01T00:00:00Z"), ("PIONEER11", "1974-01-01T00:00:00Z"), ("VOYAGER1", "1981-01-01T00:00:00Z"), ("VOYAGER2", "1990-01-01T00:00:00Z")):
            state = self.service.resolve(body, epoch)
            self.assertFalse(state.navigation_grade)
            self.assertTrue(state.provenance["state_capability"].startswith("DIRECT_SPICE_PARTIAL") or state.provenance["state_capability"] == "EPHEMERIS_PARTIAL")
        self.assertEqual(self.service.resolve("PIONEER10", "2026-01-01T00:00:00Z").provenance["state_capability"], "EMPIRICAL_PROPAGATED_2250")
        self.assertEqual(self.service.resolve("NEWHORIZONS", EPOCHS[0]).provenance["state_capability"], "DIRECT_SPICE_PARTIAL_2033")


if __name__ == "__main__":
    unittest.main()
