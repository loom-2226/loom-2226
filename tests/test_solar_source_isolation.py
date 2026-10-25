"""Regression for source/provenance contamination across requests and instances."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import unittest
from unittest.mock import patch

from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import SpiceEphemerisAdapter, registry_from_manifest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path('/home/ubuntu/loom_solar_assets')


@unittest.skipUnless(ASSETS.is_dir(), 'requires qualified local Solar assets')
class SourceIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import spiceypy
        cls.spice = spiceypy
        cls.space = SpiceEphemerisAdapter(registry_from_manifest(
            ROOT / 'manifests/solar/SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json', ASSETS))
        cls.planets = SpiceEphemerisAdapter(registry_from_manifest(
            ROOT / 'manifests/solar/OFFICIAL_PLANET_CENTER_KERNELS_V1.json', ASSETS))

    def setUp(self):
        self.spice.kclear()

    def tearDown(self):
        self.spice.kclear()

    def test_revisited_direct_epoch_uses_actual_direct_segment(self):
        epoch = '2033-01-01T06:00:00Z'
        original = self.space.resolve('NEWHORIZONS', epoch)
        self.space.resolve('NEWHORIZONS', '2250-01-01T00:00:00Z')
        actual = []
        evaluate = self.spice.spkgeo

        def observe(target, et, frame, observer):
            handle, _, _ = self.spice.spksfs(target, et, 256)
            actual.extend(Path(self.spice.kdata(i, 'SPK')[0]).name
                          for i in range(self.spice.ktotal('SPK'))
                          if self.spice.kdata(i, 'SPK')[3] == handle)
            return evaluate(target, et, frame, observer)

        with patch.object(self.spice, 'spkgeo', side_effect=observe):
            replay = self.space.resolve('NEWHORIZONS', epoch)
        self.assertEqual(original, replay)
        self.assertEqual(set(actual), {replay.provenance['asset_filename']})
        self.assertEqual(replay.provenance['ephemeris_source_id'], 'NAIF_NH_OD164')

    def test_cross_adapter_neptune_proteus_order_is_irrelevant(self):
        epoch = '2026-01-01T00:00:00Z'
        original = self.planets.resolve('NEPTUNE', epoch)
        self.space.resolve('PROTEUS', epoch)
        self.assertEqual(original, self.planets.resolve('NEPTUNE', epoch))

    def test_external_pool_is_restored_after_success_and_failure(self):
        source = self.space.registry.sources['PROP_4E_NEWHORIZONS']
        for asset in source.kernel_assets:
            self.spice.furnsh(str(asset.path))
        def pool():
            return [self.spice.kdata(i, 'ALL')[:3] for i in range(self.spice.ktotal('ALL'))]
        before = pool()
        self.space.resolve('NEWHORIZONS', '2033-01-01T06:00:00Z')
        self.assertEqual(before, pool())
        with patch.object(self.spice, 'spkgeo', side_effect=RuntimeError('injected')):
            with self.assertRaises(CelestialStateError):
                self.space.resolve('NEWHORIZONS', '2033-01-01T06:00:00Z')
        self.assertEqual(before, pool())

    def test_concurrent_governed_requests_are_serialized(self):
        epochs = ['2033-01-01T06:00:00Z', '2250-01-01T00:00:00Z'] * 4
        expected = [self.space.resolve('NEWHORIZONS', t) for t in epochs]
        with ThreadPoolExecutor(max_workers=3) as executor:
            actual = list(executor.map(lambda t: self.space.resolve('NEWHORIZONS', t), epochs))
        self.assertEqual(expected, actual)
