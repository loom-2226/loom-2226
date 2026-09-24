import hashlib
import json
import os
import unittest
from pathlib import Path

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError
from src.loom_spice_ephemeris_adapter import (
    BodyIdentifier,
    EphemerisCoverage,
    EphemerisSource,
    KernelAsset,
    SolarBody,
    SolarEphemerisRegistry,
    SpiceEphemerisAdapter,
)


ASSET_ROOT = Path("/home/ubuntu/loom_solar_assets")
EVIDENCE = ASSET_ROOT / "qualification/EPHEMERIS_FOUNDATION_V1/qualification_evidence.json"


def _asset(path: Path, digest: str) -> KernelAsset:
    return KernelAsset(path, digest, path.stat().st_size)


@unittest.skipUnless(EVIDENCE.is_file(), "qualification assets are not installed")
class SpiceEphemerisQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with EVIDENCE.open() as handle:
            cls.evidence = json.load(handle)
        cls.de440 = Path(cls.evidence["assets"]["de440"]["path"])
        cls.lsk = Path(cls.evidence["assets"]["lsk"]["path"])
        cls.ceres = Path(cls.evidence["assets"]["ceres"]["path"])
        try:
            import spiceypy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("spiceypy is not installed")

    def _registry(self, include_ceres=True):
        bodies = [
            SolarBody("EARTH", "Earth", "PLANET"),
            SolarBody("NEPTUNE_SYSTEM_BARYCENTER", "Neptune system barycenter", "BARYCENTER"),
            SolarBody("NEPTUNE_CENTER", "Neptune center", "SATELLITE"),
            SolarBody("CERES", "Ceres", "DWARF_PLANET"),
        ]
        identifiers = [
            BodyIdentifier("EARTH", "NAIF", "NAIF_ID", "399"),
            BodyIdentifier("NEPTUNE_SYSTEM_BARYCENTER", "NAIF", "NAIF_ID", "8"),
            BodyIdentifier("NEPTUNE_CENTER", "NAIF", "NAIF_ID", "899"),
            BodyIdentifier("CERES", "NAIF", "NAIF_ID", "20000001"),
            # A non-NAIF alias cannot change the SPICE target identity.
            BodyIdentifier("CERES", "IAU", "DESIGNATION", "1 Ceres"),
        ]
        de_source = EphemerisSource(
            "DE440", "JPL/NAIF", "DE440", "440", "de440.bsp",
            self.evidence["assets"]["de440"]["sha256"], self.de440.stat().st_size,
            "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440.bsp", "2026-01-01T00:00:00Z", "QUALIFIED",
            (_asset(self.lsk, self.evidence["assets"]["lsk"]["sha256"]),
             _asset(self.de440, self.evidence["assets"]["de440"]["sha256"])),
        )
        sources = [de_source]
        coverage = [
            EphemerisCoverage("DE440", "EARTH", "1550-01-01T00:00:00Z", "2650-01-01T00:00:00Z"),
            EphemerisCoverage("DE440", "NEPTUNE_SYSTEM_BARYCENTER", "1550-01-01T00:00:00Z", "2650-01-01T00:00:00Z"),
        ]
        if include_ceres:
            ceres_source = EphemerisSource(
                "CERES_SPK_2025_2227", "JPL/Horizons", "Ceres supplementary SPK", "2025-2227",
                "2000001_ceres_2025_2227.bsp", self.evidence["assets"]["ceres"]["sha256"], self.ceres.stat().st_size,
                "qualification evidence artifact", "2026-01-01T00:00:00Z", "QUALIFIED",
                (_asset(self.lsk, self.evidence["assets"]["lsk"]["sha256"]),
                 _asset(self.ceres, self.evidence["assets"]["ceres"]["sha256"])),
            )
            sources.append(ceres_source)
            coverage.append(EphemerisCoverage(
                "CERES_SPK_2025_2227", "CERES", "2024-12-31T23:58:50.816Z", "2226-12-31T23:58:50.816Z",
            ))
        return SolarEphemerisRegistry(bodies, identifiers, sources, coverage)

    def test_earth_2026_and_2226_match_frozen_evidence(self):
        service = SpiceEphemerisAdapter(self._registry()).service()
        for case_name in ("earth_2026", "earth_2226"):
            case = next(c for c in self.evidence["cases"] if c["case"] == case_name)
            state = service.resolve("EARTH", case["epoch_utc"])
            for actual, expected in zip((*state.position_km, *state.velocity_km_s), case["reference"]):
                self.assertAlmostEqual(actual, expected, delta=0.001 if abs(expected) > 100 else 1e-8)
            self.assertEqual(state.reference_frame, CANONICAL_FRAME)
            self.assertTrue(state.navigation_grade)

    def test_neptune_barycenter_is_exact_target(self):
        state = SpiceEphemerisAdapter(self._registry()).resolve(
            "NEPTUNE_SYSTEM_BARYCENTER", "2226-01-01T00:00:00Z"
        )
        self.assertEqual(state.provenance["naif_identifier"], "8")
        self.assertNotEqual(state.provenance["naif_identifier"], "899")

    def test_ceres_2026_and_2226_use_supplementary_spk(self):
        service = SpiceEphemerisAdapter(self._registry()).service()
        for epoch in ("2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z"):
            state = service.resolve("CERES", epoch)
            self.assertEqual(state.provenance["naif_identifier"], "20000001")
            self.assertEqual(state.provenance["ephemeris_source_id"], "CERES_SPK_2025_2227")
            self.assertEqual(state.reference_frame, CANONICAL_FRAME)
            self.assertEqual(state.provenance["units"], "km,km/s")

    def test_de440_only_ceres_and_neptune_center_fail_closed(self):
        service = SpiceEphemerisAdapter(self._registry(include_ceres=False)).service()
        for body in ("CERES", "NEPTUNE_CENTER"):
            with self.assertRaises(CelestialStateError):
                service.resolve(body, "2226-01-01T00:00:00Z")

    def test_coverage_and_time_normalization_are_explicit(self):
        service = SpiceEphemerisAdapter(self._registry()).service()
        state = service.resolve("EARTH", "2026-01-01T01:00:00+01:00")
        self.assertEqual(state.epoch_utc, "2026-01-01T00:00:00Z")
        for epoch in ("1549-12-31T23:59:59Z", "2227-01-01T00:00:00Z"):
            with self.assertRaises(CelestialStateError):
                service.resolve("CERES", epoch)

    def test_source_provenance_contract_is_exact(self):
        state = SpiceEphemerisAdapter(self._registry()).resolve("EARTH", "2026-01-01T00:00:00Z")
        self.assertEqual(state.provenance["asset_sha256"], self.evidence["assets"]["de440"]["sha256"])
        self.assertEqual(state.provenance["spice_frame"], "ECLIPJ2000")
        self.assertEqual(state.provenance["aberration_correction"], "NONE")
        self.assertEqual(state.provenance["time_scale_internal"], "SPICE ET/TDB")


class SolarEphemerisContractTests(unittest.TestCase):
    def _source(self, source_id, status="QUALIFIED"):
        return EphemerisSource(
            source_id, "TEST", "TEST", "1", f"{source_id}.bsp", "a" * 64, 1,
            "test://source", "2026-01-01T00:00:00Z", status, (),
        )

    def _coverage(self, source_id, body_id):
        return EphemerisCoverage(
            source_id, body_id, "2026-01-01T00:00:00Z", "2226-01-01T00:00:00Z",
        )

    def _registry(self, sources, coverage):
        return SolarEphemerisRegistry(
            [SolarBody("EARTH", "Earth", "PLANET")], [], sources, coverage,
        )

    def test_qualification_evidence_hash_is_pinned(self):
        self.assertEqual(
            hashlib.sha256(EVIDENCE.read_bytes()).hexdigest(),
            "294890bc0ad5624d0bc2f0bf0ec850a7f19322093685adbb427c50c2dac9e56a",
        )

    def test_duplicate_nonexact_body_identity_does_not_control_spice(self):
        body = SolarBody("CERES", "Ceres", "DWARF_PLANET")
        with self.assertRaises(CelestialStateError):
            SolarEphemerisRegistry(
                [body], [BodyIdentifier("CERES", "MPC", "NUMBER", "1")], [], []
            ).body_identifier("CERES")

    def test_body_coverage_outranks_product_coverage(self):
        product = self._source("PRODUCT")
        body = self._source("BODY")
        registry = self._registry(
            [product, body], [self._coverage("PRODUCT", None), self._coverage("BODY", "EARTH")],
        )
        source, record = registry.source_for("EARTH", "2026-01-01T00:00:00Z")
        self.assertEqual(source.ephemeris_source_id, "BODY")
        self.assertEqual(record.body_id, "EARTH")

    def test_coverage_on_nonqualified_source_is_ineligible(self):
        registry = self._registry(
            [self._source("CANDIDATE", "CANDIDATE")], [self._coverage("CANDIDATE", "EARTH")],
        )
        with self.assertRaisesRegex(CelestialStateError, "no qualified source coverage"):
            registry.source_for("EARTH", "2026-01-01T00:00:00Z")

    def test_equally_preferred_body_sources_fail_closed(self):
        registry = self._registry(
            [self._source("BODY_A"), self._source("BODY_B")],
            [self._coverage("BODY_A", "EARTH"), self._coverage("BODY_B", "EARTH")],
        )
        with self.assertRaisesRegex(CelestialStateError, "ambiguous qualified ephemeris authority"):
            registry.source_for("EARTH", "2026-01-01T00:00:00Z")

    def test_equally_preferred_product_sources_fail_closed(self):
        registry = self._registry(
            [self._source("PRODUCT_A"), self._source("PRODUCT_B")],
            [self._coverage("PRODUCT_A", None), self._coverage("PRODUCT_B", None)],
        )
        with self.assertRaisesRegex(CelestialStateError, "ambiguous qualified ephemeris authority"):
            registry.source_for("EARTH", "2026-01-01T00:00:00Z")

    def test_candidate_order_does_not_tiebreak_authority(self):
        sources = [self._source("PRODUCT_A"), self._source("PRODUCT_B")]
        coverage = [self._coverage("PRODUCT_A", None), self._coverage("PRODUCT_B", None)]
        for ordered_sources, ordered_coverage in ((sources, coverage), (sources[::-1], coverage[::-1])):
            registry = self._registry(ordered_sources, ordered_coverage)
            with self.assertRaisesRegex(CelestialStateError, "ambiguous qualified ephemeris authority"):
                registry.source_for("EARTH", "2026-01-01T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
