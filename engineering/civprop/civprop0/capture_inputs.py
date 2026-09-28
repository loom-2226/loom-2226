"""Optional read-only recapture. Requires psql and the existing Solar SPICE env.

Run from repository root. This script never runs migrations or writes databases.
The frozen JSON is a disposable experiment input, not an authority database.
"""
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import subprocess
from src.loom_spice_ephemeris_adapter import (
    SolarBody, BodyIdentifier, EphemerisSource, EphemerisCoverage,
    KernelAsset, SolarEphemerisRegistry, SpiceEphemerisAdapter,
)

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = 'b22703ab7ce5586fecfeda0998d19b7d1fbbfe30'


def capture(database='loom_dev', asset_root=Path('/home/ubuntu/loom_solar_assets')):
    # Fixed queries, one consistent read-only transaction; no SQL from user inputs.
    queries = {
        'earth_actor': "SELECT * FROM loom_earth.earth_area WHERE iso3='AUS'",
        'earth_snapshot': "SELECT * FROM loom_control.snapshot WHERE snapshot_id='earth-v0-1-9934d0ac-20260925'",
        'bodies': "SELECT * FROM loom_solar.body WHERE body_id IN ('EARTH','MOON') ORDER BY body_id",
        'identifiers': "SELECT * FROM loom_solar.body_identifier WHERE body_id IN ('EARTH','MOON') AND authority='NAIF' AND status='ACTIVE' ORDER BY body_id",
        'sources': "SELECT * FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='DE440'",
        'coverage': "SELECT * FROM loom_solar.ephemeris_coverage WHERE body_id IN ('EARTH','MOON') AND ephemeris_source_id='DE440' ORDER BY body_id",
        'timeline_rules': 'SELECT * FROM loom_timeline.interpretation_rule ORDER BY rule_key',
    }
    sql = 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n'
    sql += '\n'.join(f"SELECT json_build_object('key','{key}','rows',COALESCE(json_agg(t),'[]'))::jsonb::text FROM ({q}) t;" for key, q in queries.items())
    sql += '\nCOMMIT;'
    output = subprocess.check_output(['psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-d', database, '-c', sql], text=True)
    records = {x['key']: x['rows'] for x in map(json.loads, output.splitlines())}
    assert len(records['earth_actor']) == 1 and records['earth_snapshot'][0]['state'] == 'VALIDATED'
    manifest_path = 'manifests/solar/SOLAR_PHASE4B_AUTHORITY_V1.json'
    manifest = json.loads((ROOT / manifest_path).read_text())
    assets = tuple(KernelAsset(asset_root / a['local_path'], a['sha256'], a['byte_count'])
                   for a in manifest['assets'] if a['asset_id'] in ('LSK', 'DE440'))
    def typed(cls, row):
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in row.items() if k in names})
    source = records['sources'][0]
    expected = next(s for s in manifest['registry']['sources'] if s['ephemeris_source_id'] == 'DE440')
    assert source['sha256'] == expected['sha256'] and source['status'] == 'QUALIFIED'
    registry = SolarEphemerisRegistry(
        [typed(SolarBody, r) for r in records['bodies']],
        [typed(BodyIdentifier, r) for r in records['identifiers']],
        [typed(EphemerisSource, {**source, 'kernel_assets': assets})],
        [typed(EphemerisCoverage, r) for r in records['coverage']],
    )
    service = SpiceEphemerisAdapter(registry).service()
    states = [asdict(service.resolve(body, epoch))
              for epoch in ('2026-09-28T00:00:00Z', '2026-10-03T00:00:00Z')
              for body in ('EARTH', 'MOON')]
    campaign_path = 'dev/solar_civprop_m4b/campaign_assertions.json'
    campaign = json.loads((ROOT / campaign_path).read_text())
    assertion = next(r for r in campaign['evidence_assertions'] if r['key'] == 'MOON_POLAR_WATER_ICE')
    paths = [manifest_path, campaign_path, 'src/loom_spice_ephemeris_adapter.py',
             'src/loom_spatial_state_authority.py', 'data/postgres/earth_temporal_projection_manifest.json',
             'docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md',
             'reports/solar_civprop/DORRINGTON_OLSEN_M2_CIVPROP_ASSESSMENT.md',
             'dev/solar_civprop_m4b/reports/M4B_QUALIFICATION_REPORT.md']
    pins = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    document = dict(format='CIVPROP0_INPUT_V1', main_commit=BASE,
                    architecture_basis={'pr': 321, 'commit': 'bb117d933a863fab4dbedc2add3783c7cad004a1'},
                    acquisition='PostgreSQL repeatable-read READ ONLY + promoted SPICE adapter; 2026-09-28',
                    records=records, states=states, source_hashes=pins,
                    resource={'assertion': assertion, 'status': 'CANDIDATE',
                              'site_status': 'UNKNOWN', 'site_abundance': None,
                              'scope': 'POLAR_AND_SELECTED_SURFACE_FOOTPRINTS',
                              'admission': 'Scenario context only; no production promotion or site measurement'})
    payload = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + '\n'
    (HERE / 'inputs.json').write_text(payload)
    (HERE / 'inputs.sha256').write_text(hashlib.sha256(payload.encode()).hexdigest() + '\n')
    print('Captured Earth identity, timeline rules, four governed spatial states and candidate resource context.')


if __name__ == '__main__':
    capture()
