"""Focused direct-authority qualification for Solar Phase 4C major moons."""
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
MANIFEST = ROOT / "manifests/solar/SOLAR_PHASE4C_MAJOR_MOONS_V1.json"
MIGRATION = ROOT / "data/postgres/migrations/014_solar_phase4c_major_moons.sql"
TARGETS = {
    "PHOBOS": "401", "DEIMOS": "402",
    "MIMAS": "601", "ENCELADUS": "602", "TETHYS": "603", "DIONE": "604",
    "RHEA": "605", "TITAN": "606", "HYPERION": "607", "IAPETUS": "608", "PHOEBE": "609",
    "ARIEL": "701", "UMBRIEL": "702", "TITANIA": "703", "OBERON": "704", "MIRANDA": "705",
    "TRITON": "801",
}
PARENTS = {
    "PHOBOS": ("MARS_SYSTEM_BARYCENTER", "4"), "DEIMOS": ("MARS_SYSTEM_BARYCENTER", "4"),
    "MIMAS": ("SATURN_SYSTEM_BARYCENTER", "6"), "ENCELADUS": ("SATURN_SYSTEM_BARYCENTER", "6"),
    "TETHYS": ("SATURN_SYSTEM_BARYCENTER", "6"), "DIONE": ("SATURN_SYSTEM_BARYCENTER", "6"),
    "RHEA": ("SATURN_SYSTEM_BARYCENTER", "6"), "TITAN": ("SATURN_SYSTEM_BARYCENTER", "6"),
    "HYPERION": ("SATURN_SYSTEM_BARYCENTER", "6"), "IAPETUS": ("SATURN_SYSTEM_BARYCENTER", "6"),
    "PHOEBE": ("SATURN_SYSTEM_BARYCENTER", "6"), "ARIEL": ("URANUS_SYSTEM_BARYCENTER", "7"),
    "UMBRIEL": ("URANUS_SYSTEM_BARYCENTER", "7"), "TITANIA": ("URANUS_SYSTEM_BARYCENTER", "7"),
    "OBERON": ("URANUS_SYSTEM_BARYCENTER", "7"), "MIRANDA": ("URANUS_SYSTEM_BARYCENTER", "7"),
    "TRITON": ("NEPTUNE_SYSTEM_BARYCENTER", "8"),
}
EPOCHS = ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z", "2250-01-01T00:00:00Z", "2250-12-31T23:59:59Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@unittest.skipUnless(MANIFEST.is_file(), "Phase-4C manifest is not installed")
class Phase4CQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(MANIFEST.read_text())
        cls.registry = registry_from_manifest(MANIFEST, ASSET_ROOT)
        cls.service = service_from_manifest(MANIFEST, ASSET_ROOT)

    def test_assets_hashes_and_direct_sources_are_pinned(self):
        for asset in self.document["assets"]:
            path = ASSET_ROOT / asset["local_path"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(_sha256(path), asset["sha256"])
            self.assertEqual(path.stat().st_size, asset["byte_count"])
        for body in TARGETS:
            source, _ = self.registry.source_for(body, EPOCHS[-1])
            self.assertEqual(source.state_capability, "DIRECT_SPICE_2250_QUALIFIED")
            self.assertTrue(source.provider.startswith("JPL/"))

    def test_all_required_targets_resolve_object_level_horizon(self):
        for body, naif_id in TARGETS.items():
            source, coverage = self.registry.source_for(body, EPOCHS[-1])
            self.assertLessEqual(_epoch(coverage.valid_from), _epoch(EPOCHS[0]))
            self.assertGreaterEqual(_epoch(coverage.valid_until), _epoch("2251-01-01T00:00:00Z"))
            for epoch in EPOCHS:
                state = self.service.resolve(body, epoch)
                replay = self.service.resolve(body, epoch)
                self.assertEqual(state, replay)
                self.assertEqual(state.provenance["naif_identifier"], naif_id)
                self.assertEqual(state.provenance["ephemeris_source_id"], source.ephemeris_source_id)
                self.assertEqual(state.reference_frame, CANONICAL_FRAME)
                self.assertEqual(state.provenance["spice_frame"], "ECLIPJ2000")
                self.assertEqual(state.provenance["units"], "km,km/s")
                self.assertTrue(all(math.isfinite(value) for value in (*state.position_km, *state.velocity_km_s)))
                self.assertEqual(len(state.position_km), 3)
                self.assertEqual(len(state.velocity_km_s), 3)

    def test_physical_satellites_remain_distinct_from_system_barycenters(self):
        for body, (parent, parent_id) in PARENTS.items():
            satellite = self.service.resolve(body, "2250-12-31T23:59:59Z")
            barycenter = self.service.resolve(parent, "2250-12-31T23:59:59Z")
            self.assertEqual(satellite.provenance["naif_identifier"], TARGETS[body])
            self.assertEqual(barycenter.provenance["naif_identifier"], parent_id)
            self.assertNotEqual(satellite.provenance["naif_identifier"], parent_id)
            self.assertGreater(math.dist(satellite.position_km, barycenter.position_km), 1e-8)

    def test_exact_boundary_and_outside_coverage_fail_closed(self):
        for body in TARGETS:
            _, coverage = self.registry.source_for(body, EPOCHS[-1])
            self.service.resolve(body, coverage.valid_from)
            # State qualification uses the modeled horizon checkpoints above.
            # The source endpoint itself may include a planetary-backbone guard
            # that cannot be evaluated relative to the Sun beyond DE440.
            after = (_epoch(coverage.valid_until) + timedelta(seconds=1)).isoformat()
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, after)


@unittest.skipUnless(os.environ.get("SOLAR_PG_INTEGRATION") == "1", "Requires disposable PostgreSQL integration database")
class Phase4CPostgresTests(unittest.TestCase):
    database = os.environ.get("SOLAR_PG_TEST_DB", "loom_solar_phase4c_test")
    migrations = [ROOT / "data/postgres/migrations/009_solar_ephemeris_foundation.sql", ROOT / "data/postgres/migrations/012_solar_phase4_earned_authority.sql", ROOT / "data/postgres/migrations/013_solar_phase4b_closure.sql", MIGRATION]

    def psql(self, sql: str) -> str:
        return subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", self.database, "-Atqc", sql], check=True, capture_output=True, text=True).stdout.strip()

    @classmethod
    def setUpClass(cls):
        for migration in cls.migrations:
            cls.psql(cls, migration.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.psql(cls, "DROP SCHEMA IF EXISTS loom_solar CASCADE;")

    def test_counts_hierarchy_and_required_ids(self):
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body WHERE status='ACTIVE'"), "43")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body_identifier WHERE status='ACTIVE'"), "43")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED'"), "50")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body WHERE body_id IN ('PHOBOS','DEIMOS','MIMAS','TRITON') AND parent_body_id IS NOT NULL"), "4")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body_identifier WHERE identifier_value IN ('401','402','601','801')"), "4")


if __name__ == "__main__":
    unittest.main()
