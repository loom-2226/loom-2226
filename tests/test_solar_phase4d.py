"""Focused Phase-4D strategic-body identity and horizon qualification."""
from __future__ import annotations

from datetime import timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import unittest

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError
from src.loom_spice_ephemeris_adapter import _epoch, registry_from_manifest, service_from_manifest

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
MANIFEST = ROOT / "manifests/solar/SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json"
MIGRATION = ROOT / "data/postgres/migrations/015_solar_phase4d_strategic_bodies.sql"
TARGETS = {record["body_id"]: record for record in json.loads(MANIFEST.read_text())["identities"]}
EPOCHS = ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z", "2250-01-01T00:00:00Z", "2250-12-31T23:59:59Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@unittest.skipUnless(MANIFEST.is_file(), "Phase-4D manifest is not installed")
class Phase4DQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(MANIFEST.read_text())
        cls.registry = registry_from_manifest(MANIFEST, ASSET_ROOT)
        cls.service = service_from_manifest(MANIFEST, ASSET_ROOT)

    def test_manifest_assets_and_identity_are_hash_pinned(self):
        self.assertEqual(len(TARGETS), 20)
        for asset in self.document["assets"]:
            path = ASSET_ROOT / asset["local_path"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(_sha256(path), asset["sha256"])
            self.assertEqual(path.stat().st_size, asset["byte_count"])
        for body, record in TARGETS.items():
            self.assertEqual(self.registry.body_identifier(body).identifier_value, record["naif_id"])

    def test_all_required_targets_resolve_through_end_2250(self):
        for body, record in TARGETS.items():
            _, coverage = self.registry.source_for(body, EPOCHS[-1])
            self.assertGreaterEqual(_epoch(coverage.valid_until), _epoch("2251-01-01T00:00:00Z"))
            for epoch in EPOCHS:
                source, _ = self.registry.source_for(body, epoch)
                state = self.service.resolve(body, epoch)
                replay = self.service.resolve(body, epoch)
                self.assertEqual(state, replay)
                self.assertEqual(state.provenance["naif_identifier"], record["naif_id"])
                self.assertEqual(state.provenance["ephemeris_source_id"], source.ephemeris_source_id)
                self.assertEqual(state.reference_frame, CANONICAL_FRAME)
                self.assertEqual(state.provenance["spice_frame"], "ECLIPJ2000")
                self.assertEqual(state.provenance["units"], "km,km/s")
                self.assertTrue(all(math.isfinite(v) for v in (*state.position_km, *state.velocity_km_s)))
                self.assertEqual(len(state.position_km), 3)
                self.assertEqual(len(state.velocity_km_s), 3)

    def test_bennu_direct_to_propagated_seam_is_explicit(self):
        direct = self.service.resolve("BENNU", "2026-01-01T00:00:00Z")
        propagated = self.service.resolve("BENNU", "2250-12-31T23:59:59Z")
        self.assertEqual(direct.provenance["ephemeris_source_id"], "JPL_BENNU_SB441")
        self.assertEqual(direct.provenance["state_capability"], "DIRECT_SPICE_PARTIAL_2135")
        self.assertEqual(propagated.provenance["ephemeris_source_id"], "PROP_BENNU_2101955_PHASE4D")
        self.assertEqual(propagated.provenance["state_capability"], "EMPIRICAL_PROPAGATED_2250")
        self.assertFalse(propagated.navigation_grade)
        self.assertEqual(propagated.provenance["uncertainty_km"], 1_000_000_000.0)
        self.assertIn("RK4_NBODY_V2_SMALL_BODY", propagated.provenance["source_lineage"])

    def test_binary_component_semantics_are_not_silently_collapsed(self):
        semantics = self.document["binary_semantics"]
        for body in ("KLEOPATRA", "PATROCLUS", "DIDYMOS"):
            self.assertTrue(semantics[body]["components"])
            self.assertFalse(semantics[body]["component_state_promoted"])
        self.assertEqual(self.registry.body_identifier("DIDYMOS").identifier_value, "20065803")

    def test_outside_source_coverage_fails_closed(self):
        for body in TARGETS:
            _, coverage = self.registry.source_for(body, EPOCHS[-1])
            after = (_epoch(coverage.valid_until) + timedelta(seconds=1)).isoformat()
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, after)


@unittest.skipUnless(os.environ.get("SOLAR_PG_INTEGRATION") == "1", "Requires disposable PostgreSQL integration database")
class Phase4DPostgresTests(unittest.TestCase):
    database = os.environ.get("SOLAR_PG_TEST_DB", "loom_solar_phase4d_test")
    migrations = [ROOT / "data/postgres/migrations/009_solar_ephemeris_foundation.sql", ROOT / "data/postgres/migrations/012_solar_phase4_earned_authority.sql", ROOT / "data/postgres/migrations/013_solar_phase4b_closure.sql", ROOT / "data/postgres/migrations/014_solar_phase4c_major_moons.sql", MIGRATION]

    def psql(self, sql: str) -> str:
        return subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", self.database, "-Atqc", sql], check=True, capture_output=True, text=True).stdout.strip()

    @classmethod
    def setUpClass(cls):
        for migration in cls.migrations:
            cls.psql(cls, migration.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.psql(cls, "DROP SCHEMA IF EXISTS loom_solar CASCADE;")

    def test_counts_identity_and_propagation_metadata(self):
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body WHERE status='ACTIVE'"), "63")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body_identifier WHERE status='ACTIVE'"), "63")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED'"), "71")
        self.assertEqual(self.psql("SELECT state_capability FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='PROP_BENNU_2101955_PHASE4D'"), "EMPIRICAL_PROPAGATED_2250")
        self.assertEqual(self.psql("SELECT navigation_grade::text FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='PROP_BENNU_2101955_PHASE4D'"), "false")
        self.assertEqual(self.psql("SELECT identifier_value FROM loom_solar.body_identifier WHERE body_id='COMET_HALLEY'"), "1000036")


if __name__ == "__main__":
    unittest.main()
