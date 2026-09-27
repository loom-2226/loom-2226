"""Focused adapter, reconciliation, trajectory and live qualification checks."""
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import timedelta
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.loom_solar_postgres import read_ledger, registry_from_ledger, asset_recipes
from src.loom_solar_inspector import Inspector, relative_state
from src.solar_inspector_server import handler_for
from src.loom_spatial_state_authority import SpatialState, CelestialStateError, CANONICAL_FRAME, _epoch
from src.loom_spice_ephemeris_adapter import (
    EphemerisSource, EphemerisCoverage, KernelAsset, SpiceEphemerisAdapter,
    registry_from_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path('/home/ubuntu/loom_solar_assets')


def fixture():
    source = EphemerisSource('DIRECT', 'TEST', 'Test', '1', 'test.bsp', 'a'*64, 1,
                            'test://fixture', '2026-01-01T00:00:00Z', 'QUALIFIED',
                            (KernelAsset('test.bsp', 'a'*64, 1),))
    propagated = replace(source, ephemeris_source_id='PROP', state_capability='EMPIRICAL_PROPAGATED_2250', navigation_grade=False)
    records = [asdict(EphemerisCoverage('DIRECT', 'BODY', '2026-01-01T00:00:00Z', '2026-01-02T00:00:00Z')),
               asdict(EphemerisCoverage('PROP', 'BODY', '2026-01-02T00:00:00Z', '2026-01-03T00:00:00Z', coverage_class='DERIVED')),
               asdict(EphemerisCoverage('DIRECT', 'SUN', '2026-01-01T00:00:00Z', '2026-01-04T00:00:00Z'))]
    ledger = {'body': [{'body_id': b, 'canonical_name': b, 'body_class': 'TEST', 'parent_body_id': None, 'status': 'ACTIVE'}
                       for b in ('SUN', 'BODY', 'MISSING')],
              'body_identifier': [{'body_id': b, 'authority': 'NAIF', 'identifier_type': 'NAIF_ID', 'identifier_value': str(i), 'status': 'ACTIVE'}
                                  for i, b in enumerate(('SUN', 'BODY'))],
              'ephemeris_source': [{k: v for k, v in asdict(s).items() if k != 'kernel_assets'} for s in (source, propagated)],
              'ephemeris_coverage': records, 'object_metadata': [], 'curated_cohort_member': []}
    return ledger, {'DIRECT': source, 'PROP': propagated}


class AdapterTests(unittest.TestCase):
    def test_pg_identity_and_coverage_populate_existing_registry(self):
        ledger, recipes = fixture()
        registry = registry_from_ledger(ledger, recipes, {})
        self.assertEqual(set(registry.bodies), {r['body_id'] for r in ledger['body']})
        self.assertEqual(registry.body_identifier('BODY').identifier_value, '1')
        self.assertEqual(registry.source_for('BODY', '2026-01-02T00:00:00Z')[0].ephemeris_source_id, 'DIRECT')
        self.assertEqual(registry.source_for('BODY', '2026-01-02T01:00:00Z')[0].ephemeris_source_id, 'PROP')

    def test_fail_closed_source_identity_and_hash_mismatch(self):
        for field, value in [('sha256', 'b'*64), ('byte_count', 2), ('provider', 'OTHER'),
                             ('asset_filename', 'other.bsp'), ('product_version', '2')]:
            ledger, recipes = fixture()
            ledger['ephemeris_source'][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(CelestialStateError, 'source mismatch'):
                registry_from_ledger(ledger, recipes, {})

    def test_identifiers_missing_recipe_and_invalid_coverage_fail_closed(self):
        ledger, recipes = fixture()
        with self.assertRaisesRegex(CelestialStateError, 'identifier mismatch'):
            registry_from_ledger(ledger, recipes, {('BODY', 'NAIF', 'NAIF_ID'): '999'})
        with self.assertRaisesRegex(CelestialStateError, 'no governed'):
            registry_from_ledger(ledger, {}, {})
        for field, value in [('units', 'AU'), ('reference_frame', 'J2000'), ('valid_until', '2025-01-01T00:00:00Z'), ('body_id', 'ORPHAN')]:
            modified = deepcopy(ledger); modified['ephemeris_coverage'][0][field] = value
            with self.subTest(field=field), self.assertRaises(CelestialStateError):
                registry_from_ledger(modified, recipes, {})

    def test_pg_current_qualification_is_used_not_manifest_defaults(self):
        ledger, recipes = fixture()
        ledger['ephemeris_source'][0]['status'] = 'RETIRED'
        registry = registry_from_ledger(ledger, recipes, {})
        with self.assertRaises(CelestialStateError):
            registry.source_for('BODY', '2026-01-01T12:00:00Z')

    def test_postgres_read_uses_fixed_read_only_snapshot_and_no_shell(self):
        with patch('src.loom_solar_postgres.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='{}')) as run:
            self.assertEqual(read_ledger('database name'), {})
        args, kwargs = run.call_args
        self.assertIn('ISOLATION LEVEL REPEATABLE READ READ ONLY', args[0][-1])
        self.assertEqual(args[0][args[0].index('-d')+1], 'database name')
        self.assertNotIn('shell', kwargs)


class SamplingTests(unittest.TestCase):
    def setUp(self):
        ledger, recipes = fixture()
        registry = registry_from_ledger(ledger, recipes, {})
        self.calls = []
        def resolve(body, epoch):
            self.calls.append((body, epoch))
            source, coverage = registry.source_for(body, epoch)
            t = (_epoch(epoch)-_epoch('2026-01-01T00:00:00Z')).total_seconds()
            return SpatialState(body, epoch, CANONICAL_FRAME,
                                (t, 2, 3) if body == 'BODY' else (1, 1, 1), (4, 5, 6),
                                {'units': 'km,km/s', 'state_capability': source.state_capability,
                                 'ephemeris_source_id': source.ephemeris_source_id}, source.navigation_grade)
        self.inspector = Inspector(ledger, registry, SimpleNamespace(resolve=resolve))

    def test_catalog_reconciles_and_unresolved_has_no_coordinates(self):
        result = self.inspector.snapshot('2026-01-01T01:00:00+01:00')
        self.assertEqual(result['epoch_utc'], '2026-01-01T00:00:00Z')
        c = result['counts']
        self.assertEqual(c['resolved']+c['unresolved'], c['catalog'])
        self.assertEqual(c['direct']+c['propagated'], c['resolved'])
        missing = next(r for r in result['objects'] if r['body_id'] == 'MISSING')
        self.assertIn('reason', missing)
        self.assertNotIn('state', missing)
        self.assertNotIn('relative', missing)

    def test_compact_scene_and_catalog_preserve_exact_state_boundary(self):
        epoch = '2026-01-01T00:00:00Z'
        catalog = self.inspector.catalog()
        self.assertEqual(len(catalog['objects']), 3)
        self.assertFalse(self.calls, 'catalog identity must not evaluate ephemerides')
        with self.assertRaises(CelestialStateError):
            self.inspector.catalog('not an epoch')
        with self.assertRaises(CelestialStateError):
            self.inspector.preview_ids('not an epoch')
        self.inspector.bodies['BODY']['body_class'] = 'PLANET'
        self.assertEqual(self.inspector.preview_ids(epoch), ('SUN', 'BODY'))
        preview = self.inspector.scene_snapshot(epoch, 'SUN', ('SUN', 'BODY'))
        self.assertFalse(preview['complete'])
        self.assertEqual(preview['catalog_total'], 3)
        self.assertEqual(preview['counts']['catalog'], 2)
        full = self.inspector.scene_snapshot(epoch)
        exact = self.inspector.snapshot(epoch)
        self.assertTrue(full['complete'])
        self.assertEqual(full['counts'], exact['counts'])
        for compact, rich in zip(full['objects'], exact['objects']):
            self.assertEqual(compact['body_id'], rich['body_id'])
            self.assertEqual(compact.get('relative'), rich.get('relative'))
            self.assertNotIn('state', compact)
            self.assertNotIn('known_coverage', compact)

    def test_compact_path_uses_exact_trajectory_geometry(self):
        args = ('BODY', '2026-01-01T00:00:00Z', '2026-01-04T00:00:00Z')
        compact = self.inspector.path(*args, samples=7)
        exact = self.inspector.trajectory(*args, samples=7)
        self.assertEqual(compact['segments'], exact['segments'])
        self.assertEqual(compact['gap_indices'], exact['gap_indices'])
        self.assertEqual([p.get('relative') for p in compact['points']],
                         [p.get('relative') for p in exact['points']])
        self.assertTrue(all('state' not in p and 'known_coverage' not in p for p in compact['points']))

    def test_samples_use_resolver_and_split_seams_and_gaps(self):
        result = self.inspector.trajectory('BODY', '2026-01-01T00:00:00Z', '2026-01-04T00:00:00Z', samples=7)
        for p in result['points']:
            self.assertIn(('BODY', p['epoch_utc']), self.calls)
            self.assertIn(('SUN', p['epoch_utc']), self.calls)
        self.assertEqual(len(result['seams']), 1)
        self.assertEqual([s['authority_class'] for s in result['segments']], ['DIRECT', 'PROPAGATED'])
        seam = result['seams'][0]
        self.assertEqual(seam['time_bracket_utc'], ['2026-01-02T00:00:00Z', '2026-01-02T00:00:00.000001Z'])
        self.assertTrue(result['gap_indices'])
        self.assertFalse(result['closed_by_renderer'])
        indices = [i for segment in result['segments'] for i in segment['indices']]
        self.assertFalse(set(indices) & set(result['gap_indices']))
        self.assertNotEqual(result['points'][indices[0]]['relative']['position_km'], result['points'][indices[-1]]['relative']['position_km'])

    def test_relative_state_is_separate_and_unavailable_center_hides_geometry(self):
        row = self.inspector.at('BODY', '2026-01-01T00:00:00Z', 'SUN')
        self.assertEqual(row['state']['position_km'], (0, 2, 3))
        self.assertEqual(row['relative']['position_km'], [-1, 1, 2])
        self.assertEqual(row['relative']['velocity_km_s'], [0, 0, 0])
        self.assertNotIn('relative', self.inspector.at('BODY', '2026-01-01T00:00:00Z', 'MISSING'))
        with self.assertRaises(CelestialStateError):
            relative_state(row['state'], dict(row['state'], epoch_utc='2226-01-01T00:00:00Z'))

    def test_bad_epoch_and_unbounded_sampling_rejected(self):
        with self.assertRaises(CelestialStateError):
            self.inspector.snapshot('2026-01-01')
        with self.assertRaises(ValueError):
            self.inspector.trajectory('BODY', '2026-01-01T00:00:00Z', '2226-01-01T00:00:00Z', samples=513)

    def test_no_legacy_or_network_ephemeris_fallback(self):
        for name in ('loom_solar_inspector.py', 'loom_solar_postgres.py', 'solar_inspector_server.py'):
            text = (ROOT / 'src' / name).read_text()
            for forbidden in ('loom_solar_gis', 'sqlite3', 'urllib.request', 'requests.', 'spiceypy', 'propagate_parent_centric'):
                self.assertNotIn(forbidden, text)


@unittest.skipUnless(os.environ.get('SOLAR_INSPECTOR_DB'), 'requires read-only local Solar PostgreSQL and assets')
class LiveQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inspector = Inspector.connect(os.environ['SOLAR_INSPECTOR_DB'], ASSETS)
        cls.evidence = {'epochs': {}, 'local_systems': {}, 'trajectories': {}}

    def test_epoch_catalog_reconciliation_and_known_unresolved(self):
        for epoch in ('2026-01-01T00:00:00Z', '2226-01-01T00:00:00Z', '2250-01-01T00:00:00Z', '2250-12-31T23:59:59Z'):
            snapshot = self.inspector.snapshot(epoch)
            c = snapshot['counts']
            self.assertEqual(c['catalog'], len(self.inspector.ledger['body']))
            self.assertEqual(c['catalog'], c['resolved']+c['unresolved'])
            self.assertEqual(c['resolved'], c['direct']+c['propagated'])
            failures = [r['body_id'] for r in snapshot['objects'] if r['resolution'] == 'UNRESOLVED']
            self.assertIn('DACTYL', failures); self.assertIn('SELAM', failures)
            if epoch.startswith(('2226', '2250')):
                for body in ('PROTEUS', 'NIX', 'HYDRA', 'KERBEROS', 'STYX'):
                    self.assertIn(body, failures)
            self.evidence['epochs'][epoch] = {'counts': c, 'unresolved': failures}

    def test_local_systems_and_asteroid_companions(self):
        for body, center in [('MOON', 'EARTH'), ('PHOBOS', 'MARS'), ('IO', 'JUPITER'), ('TITAN', 'SATURN'),
                             ('TRITON', 'NEPTUNE'), ('CHARON', 'PLUTO'), ('DACTYL', 'IDA'), ('SELAM', 'DINKINESH')]:
            row = self.inspector.at(body, '2026-01-01T00:00:00Z', center)
            if body not in ('DACTYL', 'SELAM'):
                self.assertIn('relative', row)
                c = self.inspector.record(center, row['epoch_utc'])['state']
                self.assertEqual(row['relative'], relative_state(row['state'], c))
            else:
                self.assertNotIn('relative', row)
            self.evidence['local_systems'][body] = {'center': center, 'resolution': row['resolution']}

    def test_escape_interstellar_and_direct_propagated_seam(self):
        for body in ('NEWHORIZONS', 'VOYAGER1', 'OUMUAMUA'):
            result = self.inspector.trajectory(body, '2026-01-01T00:00:00Z', '2250-01-01T00:00:00Z', samples=16)
            # Boundary samples may expose declared-coverage/SPK endpoint gaps;
            # these remain explicit and must never be joined by rendering.
            rendered = {i for segment in result['segments'] for i in segment['indices']}
            self.assertFalse(rendered.intersection(result['gap_indices']))
            for i in result['gap_indices']:
                self.assertEqual(result['points'][i]['resolution'], 'UNRESOLVED')
                self.assertNotIn('relative', result['points'][i])
            self.assertNotEqual(result['points'][0]['state']['position_km'], result['points'][-1]['state']['position_km'])
            if body == 'NEWHORIZONS':
                self.assertTrue(result['seams'])
                self.assertEqual(result['segments'][0]['authority_class'], 'DIRECT')
                self.assertEqual(result['segments'][-1]['authority_class'], 'PROPAGATED')
            self.evidence['trajectories'][body] = {'samples': len(result['points']), 'seams': len(result['seams']), 'gaps': len(result['gap_indices'])}

    @classmethod
    def tearDownClass(cls):
        print('INSPECTOR_QUALIFICATION=' + json.dumps(cls.evidence, sort_keys=True))


class AutomaticHorizonTests(unittest.TestCase):
    def setUp(self):
        bodies = [('SUN', 'STAR'), ('BOUND', 'NATURAL_SATELLITE'),
                  ('LONG', 'TRANS_NEPTUNIAN_OBJECT'), ('CRAFT', 'SPACECRAFT'),
                  ('OPEN', 'INTERSTELLAR_OBJECT'), ('GAPPY', 'NATURAL_SATELLITE')]
        ledger = {'body': [{'body_id': body, 'canonical_name': body, 'body_class': kind,
                            'parent_body_id': 'SUN', 'status': 'ACTIVE'} for body, kind in bodies],
                  'object_metadata': [], 'curated_cohort_member': []}
        registry = SimpleNamespace(identifiers=[], coverage=[], sources={})
        origin = _epoch('2026-01-01T00:00:00Z')
        def resolve(body, epoch):
            days = (_epoch(epoch)-origin).total_seconds()/86400
            if body == 'GAPPY' and 8 < days < 12:
                raise CelestialStateError('governed gap')
            period = 365250 if body == 'LONG' else 27
            angle = 2*math.pi*days/period
            rate = 2*math.pi/period/86400
            position = (0,0,0) if body == 'SUN' else (math.cos(angle)*100000,math.sin(angle)*100000,0)
            velocity = (0,0,0) if body == 'SUN' else (-math.sin(angle)*100000*rate,math.cos(angle)*100000*rate,0)
            if body in ('CRAFT','OPEN'):
                position, velocity = (days*1000,100000,0), (1000/86400,0,0)
            propagated = body == 'BOUND' and days >= 15
            provenance = {'units':'km,km/s', 'state_capability':'EMPIRICAL_PROPAGATED_2250' if propagated else 'DIRECT',
                          'ephemeris_source_id':'PROP' if propagated else 'DIRECT'}
            return SpatialState(body, epoch, CANONICAL_FRAME, position, velocity, provenance, not propagated)
        self.inspector = Inspector(ledger, registry, SimpleNamespace(resolve=resolve), max_orbit_years=10)

    def test_http_auto_route_uses_start_as_governed_t0(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(self.inspector, ROOT / 'web/three/three.min.js'))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection('127.0.0.1', server.server_port, timeout=10)
            try:
                connection.request('GET', '/api/trajectory?body=BOUND&center=SUN&start=2026-01-01T00:00:00Z&view=auto')
                response = connection.getresponse()
                body = json.loads(response.read())
            finally:
                connection.close()
            self.assertEqual(response.status, 200, body)
            self.assertEqual(body['horizon']['start'], '2026-01-01T00:00:00Z')
            self.assertEqual(body['horizon']['status'], 'REVOLUTION_COMPLETE')
            self.assertEqual(body['reference_center'], 'SUN')
            self.assertTrue(body['segments'])
            self.assertTrue(body['seams'])
            self.assertFalse(body['closed_by_renderer'])
            self.assertFalse({index for segment in body['segments'] for index in segment['indices']}
                             & set(body['gap_indices']))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=10)

    def test_complete_bound_revolution_starts_at_t0_and_keeps_seam(self):
        path = self.inspector.automatic_path('BOUND','2026-01-01T00:00:00Z','SUN')
        self.assertEqual(path['horizon']['status'], 'REVOLUTION_COMPLETE')
        self.assertEqual(path['horizon']['start'], '2026-01-01T00:00:00Z')
        self.assertAlmostEqual((_epoch(path['horizon']['end'])-_epoch(path['horizon']['start'])).total_seconds()/86400,27,delta=.01)
        self.assertTrue(any(segment['authority_class'] == 'PROPAGATED' for segment in path['segments']))
        self.assertGreaterEqual(len(path['segments']),2)
        self.assertTrue(path['seams'])
        self.assertFalse(path['closed_by_renderer'])
        self.assertEqual(path['points'][0]['epoch_utc'],path['horizon']['start'])

    def test_open_year_and_maximum_horizon_are_explicit(self):
        for body in ('CRAFT','OPEN'):
            plan = self.inspector.automatic_plan(body,'2026-01-01T00:00:00Z')
            self.assertEqual(plan['horizon_kind'],'OPEN_ONE_EARTH_YEAR')
            self.assertAlmostEqual((_epoch(plan['end'])-_epoch(plan['start'])).total_seconds()/86400,365.25)
        plan = self.inspector.automatic_plan('LONG','2026-01-01T00:00:00Z')
        self.assertEqual(plan['status'],'MAX_HORIZON_TRUNCATED')
        self.assertFalse(plan['revolution_complete'])
        self.assertEqual(plan['max_orbit_years'],10)

    def test_unresolved_automatic_path_retains_gaps(self):
        path = self.inspector.automatic_path('GAPPY','2026-01-01T00:00:00Z','SUN')
        self.assertEqual(path['horizon']['status'],'UNRESOLVED_BEFORE_COMPLETION')
        self.assertTrue(path['gap_indices'])
        self.assertFalse(path['closed_by_renderer'])
        self.assertTrue(all('relative' not in path['points'][i] for i in path['gap_indices']))


if __name__ == '__main__':
    unittest.main()
