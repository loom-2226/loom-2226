"""Focused Solar Phase-4B direct/propagated seam qualification."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import unittest

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError
from src.loom_spice_ephemeris_adapter import registry_from_manifest, service_from_manifest


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
MANIFEST = ROOT / "manifests/solar/SOLAR_PHASE4B_AUTHORITY_V1.json"
MIGRATION = ROOT / "data/postgres/migrations/013_solar_phase4b_closure.sql"
REQUIRED = {
    "CERES": "20000001", "SATURN": "699", "JUPITER": "599", "IO": "501",
    "EUROPA": "502", "GANYMEDE": "503", "CALLISTO": "504",
    "PLUTO": "999", "CHARON": "901",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
EPOCHS = (
    "2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z",
    "2250-01-01T00:00:00Z", "2250-12-31T23:59:59Z",
)


class Phase4BContractTests(unittest.TestCase):
    def test_manifest_is_hash_pinned_and_epistemically_explicit(self):
        document = json.loads(MANIFEST.read_text())
        self.assertEqual(document["manifest_id"], "SOLAR_PHASE4B_AUTHORITY_V1")
        self.assertTrue(document["horizon_contract"]["propagation_is_not_direct_authority"])
        self.assertEqual(document["propagation_model"]["algorithm_version"], "LOOM_SOLAR_PHASE4B_RK4_NBODY_V1")
        for asset in document["assets"]:
            path = ASSET_ROOT / asset["local_path"]
            if path.is_file():
                self.assertEqual(_sha256(path), asset["sha256"])
                self.assertEqual(path.stat().st_size, asset["byte_count"])

    def test_migration_records_direct_and_propagated_classes(self):
        sql = MIGRATION.read_text()
        self.assertIn("state_capability", sql)
        self.assertIn("EMPIRICAL_PROPAGATED_2250", sql)
        self.assertIn("navigation_grade, uncertainty_km, source_lineage", sql)
        self.assertIn("coverage_class, status", sql)
        self.assertIn("2251-01-01T00:00:00.816Z", sql)
        self.assertIn("JUPITER_SYSTEM_BARYCENTER", (ROOT / "data/postgres/migrations/012_solar_phase4_earned_authority.sql").read_text())


@unittest.skipUnless(
    MANIFEST.is_file()
    and all((ASSET_ROOT / a["local_path"]).is_file()
            for a in json.loads(MANIFEST.read_text())["assets"]),
    "Phase-4B governed assets are not installed",
)
class Phase4BQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import spiceypy  # noqa: F401
        except ImportError as exc:
            raise unittest.SkipTest("spiceypy is not installed") from exc
        cls.registry = registry_from_manifest(MANIFEST, ASSET_ROOT)
        cls.service = service_from_manifest(MANIFEST, ASSET_ROOT)

    def test_all_required_targets_resolve_at_full_horizon_checkpoints(self):
        for body, naif_id in REQUIRED.items():
            for epoch in EPOCHS:
                state = self.service.resolve(body, epoch)
                replay = self.service.resolve(body, epoch)
                self.assertEqual(state, replay)
                self.assertEqual(state.provenance["naif_identifier"], naif_id)
                self.assertEqual(state.reference_frame, CANONICAL_FRAME)
                self.assertEqual(state.provenance["units"], "km,km/s")
                self.assertTrue(all(math.isfinite(v) for v in (*state.position_km, *state.velocity_km_s)))
                self.assertEqual(len(state.position_km), 3)
                self.assertEqual(len(state.velocity_km_s), 3)

    def test_direct_and_propagated_sources_are_distinguished(self):
        for body in ("JUPITER", "IO", "EUROPA", "GANYMEDE", "CALLISTO"):
            direct = self.service.resolve(body, "2026-01-01T00:00:00Z")
            derived = self.service.resolve(body, "2250-12-31T23:59:59Z")
            self.assertTrue(direct.provenance["state_capability"].startswith("DIRECT_"))
            self.assertTrue(derived.provenance["state_capability"].startswith("EMPIRICAL_PROPAGATED_"))
            self.assertTrue(direct.navigation_grade)
            self.assertFalse(derived.navigation_grade)
            self.assertIsNotNone(derived.provenance["uncertainty_km"])
            self.assertIn("JPL_", derived.provenance["source_lineage"])
        for body in ("PLUTO", "CHARON"):
            direct = self.service.resolve(body, "2026-01-01T00:00:00Z")
            derived = self.service.resolve(body, "2250-12-31T23:59:59Z")
            self.assertTrue(direct.provenance["state_capability"].startswith("DIRECT_"))
            self.assertTrue(derived.provenance["state_capability"].startswith("EMPIRICAL_PROPAGATED_"))
            self.assertFalse(derived.navigation_grade)

    def test_physical_centers_never_collapse_to_barycenters(self):
        pairs = (
            ("JUPITER", "JUPITER_SYSTEM_BARYCENTER", "599", "5"),
            ("PLUTO", "PLUTO_SYSTEM_BARYCENTER", "999", "9"),
        )
        for body, barycenter, body_id, bary_id in pairs:
            state = self.service.resolve(body, "2250-12-31T23:59:59Z")
            bary = self.service.resolve(barycenter, "2250-12-31T23:59:59Z")
            self.assertEqual(state.provenance["naif_identifier"], body_id)
            self.assertEqual(bary.provenance["naif_identifier"], bary_id)
            self.assertNotEqual(state.provenance["naif_identifier"], bary.provenance["naif_identifier"])
            self.assertGreater(math.dist(state.position_km, bary.position_km), 1e-8)

    def test_outside_propagated_coverage_fails_closed(self):
        for body in ("JUPITER", "IO", "EUROPA", "GANYMEDE", "CALLISTO", "PLUTO", "CHARON"):
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, "2251-01-01T00:00:01Z")


@unittest.skipUnless(
    os.environ.get("SOLAR_PG_INTEGRATION") == "1",
    "Requires disposable PostgreSQL integration database",
)
class Phase4BPostgresTests(unittest.TestCase):
    database = os.environ.get("SOLAR_PG_TEST_DB", "loom_solar_phase4b_test")
    migration_009 = ROOT / "data/postgres/migrations/009_solar_ephemeris_foundation.sql"
    migration_012 = ROOT / "data/postgres/migrations/012_solar_phase4_earned_authority.sql"

    def psql(self, sql: str, check: bool = True) -> str:
        result = subprocess.run(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", self.database, "-Atqc", sql],
            check=check, capture_output=True, text=True,
        )
        return result.stdout.strip()

    @classmethod
    def setUpClass(cls):
        cls.psql(cls, cls.migration_009.read_text())
        cls.psql(cls, cls.migration_012.read_text())
        cls.psql(cls, MIGRATION.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.psql(cls, "DROP SCHEMA IF EXISTS loom_solar CASCADE;")

    def test_phase4b_counts_and_classes(self):
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body WHERE status='ACTIVE'"), "26")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.body_identifier WHERE status='ACTIVE'"), "26")
        self.assertEqual(self.psql("SELECT count(*) FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED'"), "33")
        self.assertEqual(self.psql("SELECT state_capability FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='PROP_IO_501_PHASE4B'"), "EMPIRICAL_PROPAGATED_2250")
        self.assertEqual(self.psql("SELECT navigation_grade::text FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='PROP_IO_501_PHASE4B'"), "false")
        self.assertEqual(self.psql("SELECT identifier_value FROM loom_solar.body_identifier WHERE body_id='PLUTO_SYSTEM_BARYCENTER'"), "9")


if __name__ == "__main__":
    unittest.main()
