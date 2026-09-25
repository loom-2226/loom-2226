from __future__ import annotations

from datetime import timedelta
import hashlib
import json
import math
from pathlib import Path
import unittest

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError
from src.loom_spice_ephemeris_adapter import (
    EphemerisCoverage,
    EphemerisSource,
    KernelAsset,
    SolarBody,
    SolarEphemerisRegistry,
    SpiceEphemerisAdapter,
    _epoch,
    registry_from_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
MANIFEST = ROOT / "manifests/solar/OFFICIAL_PLANET_CENTER_KERNELS_V1.json"
MIGRATION = ROOT / "data/postgres/migrations/012_solar_phase4_earned_authority.sql"
EVIDENCE = ROOT / "docs/qualification/OFFICIAL_PLANET_CENTERS_V1_evidence.json"
REPORT = ROOT / "docs/qualification/OFFICIAL_PLANET_CENTERS_V1_qualification_report.md"

CENTERS = {
    "MARS": ("499", "JPL_MAR099", "MARS_SYSTEM_BARYCENTER", "4"),
    "SATURN": ("699", "JPL_SAT441", "SATURN_SYSTEM_BARYCENTER", "6"),
    "URANUS": ("799", "JPL_URA184_PART_3", "URANUS_SYSTEM_BARYCENTER", "7"),
    "NEPTUNE": ("899", "JPL_NEP097", "NEPTUNE_SYSTEM_BARYCENTER", "8"),
}
EPOCHS = ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z", "2250-01-01T00:00:00Z")


class OfficialPlanetCenterManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(MANIFEST.read_text())
        cls.registry = registry_from_manifest(MANIFEST, ASSET_ROOT)

    def test_manifest_maps_physical_centers_and_barycenters_explicitly(self):
        for center, (center_id, _, barycenter, barycenter_id) in CENTERS.items():
            self.assertEqual(self.registry.body_identifier(center).identifier_value, center_id)
            self.assertEqual(self.registry.body_identifier(barycenter).identifier_value, barycenter_id)
            self.assertNotEqual(center_id, barycenter_id)

    def test_selected_source_and_actual_inventory_are_explicit(self):
        inventory = {
            record["selected_target"]["naif_id"]: record
            for record in self.document["selected_kernel_inventory"]
        }
        for center_id, _, _, barycenter_id in CENTERS.values():
            selected = inventory[int(center_id)]
            self.assertIn(int(center_id), selected["spk_target_ids"])
            self.assertEqual(selected["selected_target"]["center_naif_id"], int(barycenter_id))
            self.assertEqual(selected["selected_target"]["segment_frame_id"], 1)
            self.assertEqual(selected["selected_target"]["segment_frame"], "J2000")

    def test_supplementary_sources_pin_de440_last(self):
        for source in self.document["registry"]["sources"]:
            if source["ephemeris_source_id"] != "DE440":
                self.assertEqual(source["kernel_asset_ids"][-1], "DE440")

    def test_qualification_evidence_and_report_pin_current_manifest(self):
        evidence = json.loads(EVIDENCE.read_text())
        manifest_hash = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
        evidence_hash = hashlib.sha256(EVIDENCE.read_bytes()).hexdigest()
        self.assertEqual(evidence["result"], "PASS")
        self.assertEqual(evidence["manifest_sha256"], manifest_hash)
        report = REPORT.read_text()
        self.assertIn(manifest_hash, report)
        self.assertIn(evidence_hash, report)

    def test_migration_is_additive_data_only_and_has_no_derived_authority(self):
        sql = MIGRATION.read_text()
        self.assertNotIn("CREATE TABLE", sql)
        self.assertNotIn("ALTER TABLE", sql)
        self.assertNotIn("DERIVED", sql)
        for center, (center_id, source_id, barycenter, barycenter_id) in CENTERS.items():
            compact = sql.replace(' ', '')
            self.assertIn(f"('{center}','NAIF','NAIF_ID','{center_id}','ACTIVE')", compact)
            self.assertIn(f"('{barycenter}','NAIF','NAIF_ID','{barycenter_id}','ACTIVE')", compact)
            self.assertIn(source_id, sql)


@unittest.skipUnless(
    all((ASSET_ROOT / asset["local_path"]).is_file()
        for asset in json.loads(MANIFEST.read_text())["assets"]),
    "official Solar kernel assets are not installed",
)
class OfficialPlanetCenterQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import spiceypy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("spiceypy is not installed")
        cls.registry = registry_from_manifest(MANIFEST, ASSET_ROOT)
        cls.adapter = SpiceEphemerisAdapter(cls.registry)
        cls.service = cls.adapter.service()

    def test_2026_2226_2250_states_preserve_source_and_semantics(self):
        for body, (naif_id, source_id, barycenter, barycenter_id) in CENTERS.items():
            for epoch in EPOCHS:
                state = self.service.resolve(body, epoch)
                bary = self.service.resolve(barycenter, epoch)
                replay = self.service.resolve(body, epoch)
                self.assertEqual(state, replay)
                self.assertEqual(state.provenance["naif_identifier"], naif_id)
                self.assertNotEqual(state.provenance["naif_identifier"], barycenter_id)
                self.assertEqual(state.provenance["ephemeris_source_id"], source_id)
                self.assertEqual(bary.provenance["naif_identifier"], barycenter_id)
                self.assertEqual(bary.provenance["ephemeris_source_id"], "DE440")
                self.assertEqual(state.reference_frame, CANONICAL_FRAME)
                self.assertEqual(state.provenance["spice_frame"], "ECLIPJ2000")
                self.assertEqual(state.provenance["units"], "km,km/s")
                self.assertEqual(state.provenance["aberration_correction"], "NONE")
                self.assertEqual(state.provenance["request_time_scale"], "UTC")
                self.assertEqual(state.provenance["time_scale_internal"], "SPICE ET/TDB")
                self.assertTrue(all(math.isfinite(value) for value in (*state.position_km, *state.velocity_km_s)))
                separation = math.sqrt(sum(
                    (state.position_km[index] - bary.position_km[index]) ** 2
                    for index in range(3)
                ))
                self.assertGreater(separation, 1e-8)

    def test_exact_coverage_boundaries_resolve_and_outside_fails_closed(self):
        for body in CENTERS:
            source, coverage = self.registry.source_for(body, "2250-01-01T00:00:00Z")
            for boundary in (coverage.valid_from, coverage.valid_until):
                state = self.service.resolve(body, boundary)
                self.assertEqual(state.provenance["ephemeris_source_id"], source.ephemeris_source_id)
            before = (_epoch(coverage.valid_from) - timedelta(microseconds=1)).isoformat()
            after = (_epoch(coverage.valid_until) + timedelta(microseconds=1)).isoformat()
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, before)
            with self.assertRaises(CelestialStateError):
                self.service.resolve(body, after)

    def test_metadata_cannot_claim_an_object_missing_from_primary_source(self):
        de440 = ASSET_ROOT / "kernels/spk/de440.bsp"
        lsk = ASSET_ROOT / "kernels/lsk/naif0012.tls"
        false_source = EphemerisSource(
            "FALSE_899", "TEST", "DE440", "440", "de440.bsp",
            "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5",
            119799808, "test://false-coverage", "2026-09-25T00:00:00Z", "QUALIFIED",
            (
                KernelAsset(lsk, "678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b", 5257),
                KernelAsset(de440, "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5", 119799808),
            ),
        )
        registry = SolarEphemerisRegistry(
            [SolarBody("NEPTUNE", "Neptune", "PLANET")],
            [self.registry.body_identifier("NEPTUNE")],
            [false_source],
            [EphemerisCoverage(
                "FALSE_899", "NEPTUNE", "2026-01-01T00:00:00Z", "2250-01-01T00:00:00Z",
            )],
        )
        with self.assertRaisesRegex(CelestialStateError, "SPICE state unavailable"):
            SpiceEphemerisAdapter(registry).resolve("NEPTUNE", "2226-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
