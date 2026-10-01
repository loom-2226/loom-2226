"""ET authority regression against a migrated disposable Solar ledger."""
import json
import os
import math
from copy import deepcopy
from pathlib import Path
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread
import unittest
from unittest.mock import patch

from src.loom_solar_inspector import Inspector, relative_state
from src.loom_solar_postgres import asset_recipes, read_ledger, registry_from_ledger
from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import SPICE_FRAME
from src.solar_inspector_server import handler_for

ASSETS = Path('/home/ubuntu/loom_solar_assets')
DB = os.environ.get('SOLAR_INSPECTOR_DB')


@unittest.skipUnless(DB and ASSETS.is_dir(), 'requires migrated disposable Solar database and local kernels')
class SolarNativeEtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inspector = Inspector.connect(DB, ASSETS)
        cls.registry = cls.inspector.registry
        cls.service = cls.inspector.service

    def test_pinned_native_et_coverage_and_boundaries(self):
        rows = read_ledger(DB)['ephemeris_coverage']
        self.assertEqual((len(rows), sum(r['status'] == 'QUALIFIED' for r in rows)), (123, 121))
        earth = next(c for c in self.registry.coverage if c.body_id == 'EARTH' and c.status == 'QUALIFIED')
        self.assertEqual((earth.coverage_start_et, earth.coverage_end_et), (-14200747200.0, 20514081600.0))
        for et in (earth.coverage_start_et, earth.coverage_end_et):
            self.assertEqual(self.registry.source_for('EARTH', et)[0].ephemeris_source_id, 'DE440')
        for et in (math.nextafter(earth.coverage_start_et, -math.inf),
                   math.nextafter(earth.coverage_end_et, math.inf),
                   earth.coverage_start_et - 1, earth.coverage_end_et + 1):
            with self.assertRaisesRegex(CelestialStateError, 'no qualified source coverage'):
                self.registry.source_for('EARTH', et)
            with self.assertRaises(CelestialStateError):
                self.service.resolve_et('EARTH', et)

    def test_postgres_and_overlay_disagreement_fails_closed(self):
        ledger = read_ledger(DB)
        recipes, identifiers, _ = asset_recipes(ASSETS)
        changed = deepcopy(ledger)
        row = next(r for r in changed['ephemeris_coverage'] if r['body_id'] == 'EARTH' and r['status'] == 'QUALIFIED')
        row['coverage_end_et'] += 1
        with self.assertRaisesRegex(CelestialStateError, 'ET coverage mismatch'):
            registry_from_ledger(changed, recipes, identifiers)

    def test_every_promoted_et_interval_is_within_pinned_native_spk_window(self):
        overlay = json.loads(Path('manifests/solar/SOLAR_NATIVE_ET_COVERAGE_V1.json').read_text())
        self.assertEqual(len(overlay['rows']), 123)
        narrowed = []
        for row in overlay['rows']:
            self.assertLessEqual(row['native_start_et'], row['coverage_start_et'])
            self.assertLess(row['coverage_start_et'], row['coverage_end_et'])
            self.assertLessEqual(row['coverage_end_et'], row['native_end_et'])
            if row['method'] != 'NATIVE_SPK_ENDPOINTS':
                narrowed.append(row['ephemeris_source_id'])
        self.assertEqual(set(narrowed), {'NAIF_NEP101XL_802', 'NAIF_NH_OD164',
                                         'PROP_4E_NEWHORIZONS', 'PROP_4E_PIONEER10',
                                         'PROP_4E_PIONEER11'})

    def test_numeric_et_reaches_spkgeo_without_utc_roundtrip(self):
        import spiceypy as spice
        et = 7131844800.0
        original = spice.spkgeo
        calls = []
        evaluated = []
        def observed(target, epoch, frame, observer):
            calls.append((target, epoch, frame, observer))
            result = original(target, epoch, frame, observer)
            evaluated.append(result[0])
            return result
        with (patch.object(spice, 'str2et', side_effect=AssertionError('UTC conversion in physical evaluator')),
              patch.object(spice, 'spkgeo', side_effect=observed)):
            state = self.service.resolve_et('EARTH', et)
        self.assertEqual(calls, [(399, et, 'ECLIPJ2000', 10)])
        self.assertEqual(state.epoch_et, et)
        self.assertIsNone(state.epoch_utc)
        self.assertEqual(state.reference_frame, SPICE_FRAME)
        self.assertEqual(state.provenance['units'], 'km,km/s')
        self.assertEqual(state.position_km, tuple(evaluated[0][:3]))
        self.assertEqual(state.velocity_km_s, tuple(evaluated[0][3:]))

    def test_2026_2226_2250_tdb_states_and_relative_epoch(self):
        for label, et in [('2026-01-01T00:00:00 TDB', 820497600.0),
                          ('2226-01-01T00:00:00 TDB', 7131844800.0),
                          ('2250-01-01T00:00:00 TDB', 7889227200.0)]:
            with self.subTest(label=label):
                self.assertEqual(self.inspector.time.parse(label), et)
                earth = self.inspector.at('EARTH', et, 'SUN')
                sun = self.inspector.record('SUN', et)
                self.assertEqual(earth['resolution'], 'RESOLVED')
                self.assertEqual(earth['state']['epoch_et'], sun['state']['epoch_et'])
                self.assertEqual(earth['state']['reference_frame'], 'ECLIPJ2000')
                self.assertEqual(earth['state']['provenance']['ephemeris_source_id'], 'DE440')
                self.assertEqual(earth['relative']['position_km'],
                                 [a-b for a,b in zip(earth['state']['position_km'], sun['state']['position_km'])])

    def test_display_label_cannot_change_defined_et(self):
        et = 7131844800.123456
        state = self.service.resolve_et('EARTH', et)
        label = self.inspector.time.label(et)
        self.assertIn('TDB', label)
        self.assertEqual(state.epoch_et, et)
        self.assertEqual(self.service.resolve_et('EARTH', state.epoch_et).position_km, state.position_km)
        altered = dict(state.__dict__, epoch_utc='2250-01-01T00:00:00Z')
        self.assertEqual(relative_state(altered, dict(altered, epoch_utc='2026-01-01T00:00:00Z'))['position_km'], [0.0]*3)
        with self.assertRaises(CelestialStateError):
            relative_state(altered, dict(altered, epoch_et=et+1))

    def test_explicit_future_utc_is_lsk_projection_not_tdb_identity(self):
        projected = self.inspector.at('EARTH', '2226-01-01T00:00:00Z', 'SUN')
        self.assertEqual(projected['input_representation'], 'UTC_LSK_PROJECTION')
        self.assertAlmostEqual(projected['epoch_et'], 7131844869.183806, places=5)
        self.assertNotEqual(projected['epoch_et'], self.inspector.time.parse('2226-01-01T00:00:00 TDB'))
        self.assertEqual(self.inspector.authority['utc_projection_lsk_sha256'],
                         '678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b')

    def test_trajectory_samples_et_and_preserves_gaps(self):
        start, end = 7131844800.0, 7131844800.0 + 86400*10
        result = self.inspector.trajectory('EARTH', start, end, 'SUN', samples=12)
        self.assertEqual((result['start_et'], result['end_et']), (start, end))
        self.assertEqual((result['points'][0]['epoch_et'], result['points'][-1]['epoch_et']), (start, end))
        self.assertTrue(all(p['state']['epoch_et'] == p['epoch_et'] for p in result['points']))
        self.assertFalse(result['closed_by_renderer'])
        self.assertEqual(result['gap_indices'], [])

    def test_future_direct_and_derived_authority_and_seam(self):
        for et in (7131844800.0, 7889227200.0):
            for body, source_id, capability in (
                ('EARTH', 'DE440', 'DIRECT_'),
                ('JUPITER', 'PROP_JUPITER_599_PHASE4B', 'EMPIRICAL_PROPAGATED'),
                ('NEWHORIZONS', 'PROP_4E_NEWHORIZONS', 'EMPIRICAL_PROPAGATED'),
                ('OUMUAMUA', 'HORIZONS_4E_OUMUAMUA', 'HORIZONS_'),
            ):
                with self.subTest(et=et, body=body):
                    state = self.service.resolve_et(body, et)
                    self.assertEqual(state.epoch_et, et)
                    self.assertEqual(state.provenance['ephemeris_source_id'], source_id)
                    self.assertTrue(state.provenance['state_capability'].startswith(capability))
        direct_end = next(c.coverage_end_et for c in self.registry.coverage
                          if c.ephemeris_source_id == 'NAIF_NH_OD164' and c.status == 'QUALIFIED')
        self.assertEqual(self.registry.source_for('NEWHORIZONS', direct_end)[0].ephemeris_source_id,
                         'NAIF_NH_OD164')
        self.assertEqual(self.registry.source_for('NEWHORIZONS', direct_end + .001)[0].ephemeris_source_id,
                         'PROP_4E_NEWHORIZONS')

    def test_real_http_automatic_path(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(self.inspector, Path('web/three/three.min.js')))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = HTTPConnection('127.0.0.1', server.server_port, timeout=90)
            conn.request('GET', '/api/trajectory?body=EARTH&center=SUN&start=2026-09-27T00:00:00%20TDB&view=auto')
            response = conn.getresponse()
            data = json.loads(response.read())
            self.assertEqual(response.status, 200, data)
            self.assertEqual(data['horizon']['status'], 'REVOLUTION_COMPLETE')
            self.assertEqual(data['start_et'], 843739200.0)
            self.assertTrue(data['points'])
            self.assertTrue(all(p['authority_class'] == 'DIRECT' for p in data['points']))
            self.assertEqual(data['gap_indices'], [])
            self.assertFalse(data['closed_by_renderer'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_browser_is_display_only_and_local(self):
        script = Path('web/solar-inspector/inspector.js').read_text()
        self.assertNotIn('Date.parse', script)
        self.assertNotIn('toISOString', script)
        self.assertNotIn('spiceypy', script)
        self.assertNotIn('LOOM_Solar_GIS', script)
        self.assertNotIn('https://', script)

    def test_j2000_zero_et_is_a_real_catalog_selection_epoch(self):
        earth = next(row for row in self.inspector.catalog(0.0)['objects'] if row['body_id'] == 'EARTH')
        self.assertGreater(earth['source_asset_bytes'], 0)


if __name__ == '__main__':
    unittest.main()

def test_v1_tdb_start_boundary_is_resolvable_for_corrected_rows():
    from src.loom_solar_inspector import Inspector
    inspector = Inspector.connect('loom_dev', '/home/ubuntu/loom_solar_assets')
    assert inspector.time.parse('2026 JAN 01 TDB') == 820497600.0
    for body_id in ('NEREID', 'PIONEER10', 'PIONEER11'):
        row = inspector.record(body_id, 820497600.0)
        assert row['resolution'] == 'RESOLVED'
        assert row['state']['provenance']['coverage']['coverage_start_et'] == 820497600.0
