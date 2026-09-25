"""Targeted Phase-4E residual closure qualification."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import service_from_manifest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path("/home/ubuntu/loom_solar_assets")
MANIFEST = ROOT / "manifests/solar/SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json"
VALIDATION = ROOT / "docs/qualification/SOLAR_PHASE4E_TARGETED_RESIDUAL_PROPAGATION_VALIDATION.json"
RESIDUAL = ("NIX", "HYDRA", "KERBEROS", "STYX", "PIONEER10", "PIONEER11", "VOYAGER1", "VOYAGER2", "NEWHORIZONS", "PROTEUS", "DACTYL", "SELAM")


class Phase4EResidualClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.service = service_from_manifest(MANIFEST, ASSETS)
        cls.rows = {row["body_id"]: row for row in cls.manifest["qualification"]}

    def test_exactly_twelve_residuals_are_accounted(self):
        residual = tuple(self.manifest["targeted_residual_closure"]["initial_residual_body_ids"])
        self.assertEqual(set(residual), set(RESIDUAL))
        self.assertEqual(len(residual), 12)
        self.assertEqual(sum(self.rows[x]["object_type"] == "SPACECRAFT" for x in residual), 5)

    def test_spacecraft_2250_seam_is_explicit_and_deterministic(self):
        for body in ("PIONEER10", "PIONEER11", "VOYAGER1", "VOYAGER2", "NEWHORIZONS"):
            state = self.service.resolve(body, "2250-12-31T23:59:59Z")
            self.assertEqual(state.provenance["state_capability"], "EMPIRICAL_PROPAGATED_2250")
            self.assertFalse(state.navigation_grade)
            self.assertEqual(state, self.service.resolve(body, "2250-12-31T23:59:59Z"))

    def test_new_horizons_direct_authority_precedes_propagated_seam(self):
        state = self.service.resolve("NEWHORIZONS", "2026-01-01T00:00:00Z")
        self.assertEqual(state.provenance["ephemeris_source_id"], "NAIF_NH_OD164")
        self.assertEqual(state.provenance["state_capability"], "DIRECT_SPICE_PARTIAL_2033")

    def test_unclosed_natural_satellites_remain_fail_closed(self):
        for body in ("DACTYL", "SELAM"):
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, "2026-01-01T00:00:00Z")
        for body in ("NIX", "HYDRA", "KERBEROS", "STYX"):
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, "2250-12-31T23:59:59Z")

    def test_proteus_nep098_direct_partial_is_explicit_and_fail_closed(self):
        state = self.service.resolve("PROTEUS", "2026-01-01T00:00:00Z")
        self.assertEqual(state.provenance["naif_identifier"], "808")
        self.assertEqual(state.provenance["ephemeris_source_id"], "NAIF_NEP098_808")
        self.assertEqual(state.provenance["state_capability"], "EPHEMERIS_PARTIAL")
        self.assertEqual(state.provenance["units"], "km,km/s")
        self.assertEqual(state.reference_frame, "J2000/ECLIPTIC")
        terminal = self.service.resolve("PROTEUS", "2199-12-30T23:58:50Z")
        self.assertEqual(terminal, self.service.resolve("PROTEUS", "2199-12-30T23:58:50Z"))
        with self.assertRaises(CelestialStateError):
            self.service.resolve("PROTEUS", "2250-12-31T23:59:59Z")

    def test_held_out_validation_artifact_is_complete(self):
        validation = json.loads(VALIDATION.read_text())
        self.assertEqual(len(validation["held_out_validation"]), 5)
        for record in validation["held_out_validation"]:
            self.assertTrue(record["epochs"])
            self.assertGreater(max(v["position_error_km"] for v in record["epochs"].values()), 0.0)

    def test_migration_is_residual_only(self):
        migration = (ROOT / "data/postgres/migrations/017_solar_phase4e_targeted_residual_closure.sql").read_text()
        for source_id in ("NAIF_NH_OD164", "PROP_4E_PIONEER10", "PROP_4E_PIONEER11", "PROP_4E_VOYAGER1", "PROP_4E_VOYAGER2", "PROP_4E_NEWHORIZONS"):
            self.assertIn(source_id, migration)
        self.assertIn("WHERE body_id IN ('PIONEER10','PIONEER11','VOYAGER1','VOYAGER2','NEWHORIZONS')", migration)
        self.assertNotIn("INSERT INTO loom_solar.body", migration)

    def test_proteus_migration_records_direct_808_only(self):
        migration = (ROOT / "data/postgres/migrations/018_solar_proteus_nep098_partial.sql").read_text()
        self.assertIn("NAIF_NEP098_808", migration)
        self.assertIn("'PROTEUS'", migration)
        self.assertIn("'EPHEMERIS_PARTIAL'", migration)
        self.assertNotIn("INSERT INTO loom_solar.body", migration)


if __name__ == "__main__":
    unittest.main()
