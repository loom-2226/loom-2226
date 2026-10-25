"""Live governed satellite-path reference regression; no generated ephemerides."""
import json
import math
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = os.environ.get('SOLAR_INSPECTOR_URL', 'http://127.0.0.1:8765')
EVIDENCE = Path(os.environ.get('SOLAR_LOCAL_PATH_AUTHORITY_EVIDENCE', '/tmp/solar-local-path-authority.json'))
ET = 836354165.1840523
PAIRS = {
    'MOON': ('EARTH', 'EARTH'),
    'PHOBOS': ('MARS', 'MARS_SYSTEM_BARYCENTER'),
    'DEIMOS': ('MARS', 'MARS_SYSTEM_BARYCENTER'),
    'IO': ('JUPITER', 'JUPITER'),
    'TITAN': ('SATURN', 'SATURN_SYSTEM_BARYCENTER'),
    'TRITON': ('NEPTUNE', 'NEPTUNE_SYSTEM_BARYCENTER'),
    'CHARON': ('PLUTO', 'PLUTO'),
}


def get(route, **query):
    with urlopen(BASE + route + '?' + urlencode(query), timeout=180) as response:
        assert response.status == 200
        return json.load(response)


def norm(vector):
    return math.dist(vector, (0, 0, 0))


def residual(a, b, expected):
    return math.dist([x-y for x, y in zip(a, b)], expected)


def check():
    catalog_response = get('/api/catalog', epoch=ET)
    catalog = {row['body_id']: row for row in catalog_response['objects']}
    rows = []
    for body, (primary, orbital_reference) in PAIRS.items():
        heliocentric = get('/api/trajectory', body=body, start=ET, center='SUN', view='auto')
        local = get('/api/trajectory', body=body, start=ET, center=primary, view='auto')
        assert heliocentric['body_id'] == local['body_id'] == body
        assert heliocentric['reference_center'] == 'SUN'
        assert local['reference_center'] == primary
        assert heliocentric['reference_frame'] == local['reference_frame'] == 'ECLIPJ2000'
        assert heliocentric['horizon']['orbital_reference_center'] == orbital_reference
        assert local['horizon']['orbital_reference_center'] == orbital_reference
        assert heliocentric['horizon']['status'] == local['horizon']['status'] == 'REVOLUTION_COMPLETE'
        assert heliocentric['start_et'] == local['start_et'] == ET
        assert heliocentric['end_et'] == local['end_et']
        assert not heliocentric['gap_indices'] and not local['gap_indices']
        assert not heliocentric['closed_by_renderer'] and not local['closed_by_renderer']
        assert all(point.get('relative', {}).get('reference_center') == 'SUN' for point in heliocentric['points'])
        assert all(point.get('relative', {}).get('reference_center') == primary for point in local['points'])
        assert all(len(segment['indices']) >= 2 for segment in local['segments'])
        checks, primary_positions = [], []
        for index in sorted({0, len(local['points'])//2, len(local['points'])-1}):
            point = local['points'][index]
            et = point['epoch_et']
            sun_rows = get('/api/state', epoch=et, center='SUN', view='scene',
                           bodies=','.join(dict.fromkeys((body, primary, orbital_reference))))
            sun = {row['body_id']: row['relative'] for row in sun_rows['objects']}
            primary_positions.append(sun[primary]['position_km'])
            local_row = get('/api/state', epoch=et, center=primary, view='scene', bodies=body)['objects'][0]
            assert local_row['relative'] == point['relative']
            position_error = residual(sun[body]['position_km'], sun[primary]['position_km'],
                                      point['relative']['position_km'])
            velocity_error = residual(sun[body]['velocity_km_s'], sun[primary]['velocity_km_s'],
                                      point['relative']['velocity_km_s'])
            assert position_error < 1e-6 and velocity_error < 1e-9, (body, et, position_error, velocity_error)
            reference_row = (local_row if orbital_reference == primary else
                             get('/api/state', epoch=et, center=orbital_reference,
                                 view='scene', bodies=body)['objects'][0])
            reference_position_error = residual(sun[body]['position_km'], sun[orbital_reference]['position_km'],
                                                reference_row['relative']['position_km'])
            reference_velocity_error = residual(sun[body]['velocity_km_s'], sun[orbital_reference]['velocity_km_s'],
                                                reference_row['relative']['velocity_km_s'])
            assert reference_position_error < 1e-6 and reference_velocity_error < 1e-9
            checks.append({'index': index, 'epoch_et': et,
                           'position_residual_km': position_error,
                           'velocity_residual_km_s': velocity_error,
                           'orbital_reference_position_residual_km': reference_position_error,
                           'orbital_reference_velocity_residual_km_s': reference_velocity_error})
        for index in (0, len(heliocentric['points'])-1):
            point = heliocentric['points'][index]
            row = get('/api/state', epoch=point['epoch_et'], center='SUN', view='scene', bodies=body)['objects'][0]
            assert row['relative'] == point['relative']
        local_positions = [point['relative']['position_km'] for point in local['points']]
        sun_positions = [point['relative']['position_km'] for point in heliocentric['points']]
        exhaustive = None
        if body == 'PHOBOS':
            max_position_error = max_velocity_error = 0.0
            for point in local['points']:
                states = get('/api/state', epoch=point['epoch_et'], center='SUN', view='scene',
                             bodies='PHOBOS,MARS')['objects']
                states = {row['body_id']: row['relative'] for row in states}
                max_position_error = max(max_position_error,
                    residual(states['PHOBOS']['position_km'], states['MARS']['position_km'],
                             point['relative']['position_km']))
                max_velocity_error = max(max_velocity_error,
                    residual(states['PHOBOS']['velocity_km_s'], states['MARS']['velocity_km_s'],
                             point['relative']['velocity_km_s']))
            assert max_position_error < 1e-6 and max_velocity_error < 1e-9
            exhaustive = {'samples': len(local['points']), 'max_position_residual_km': max_position_error,
                          'max_velocity_residual_km_s': max_velocity_error}
        rows.append({'body_id': body, 'catalog_parent': catalog[body]['parent_body_id'],
                     'local_center': primary, 'horizon_reference': orbital_reference,
                     'frame': local['reference_frame'], 'horizon_status': local['horizon']['status'],
                     'start_et': ET, 'end_et': local['end_et'],
                     'sun_points': len(heliocentric['points']), 'local_points': len(local['points']),
                     'sun_segments': heliocentric['segments'], 'local_segments': local['segments'],
                     'sun_first_last_displacement_km': math.dist(sun_positions[0],sun_positions[-1]),
                     'primary_sun_first_last_displacement_km': math.dist(primary_positions[0],primary_positions[-1]),
                     'local_first_last_displacement_km': math.dist(local_positions[0],local_positions[-1]),
                     'local_radius_min_km': min(map(norm,local_positions)),
                     'local_radius_max_km': max(map(norm,local_positions)),
                     'local_max_displacement_from_first_km': max(math.dist(p,local_positions[0]) for p in local_positions),
                     'sampled_identity_checks': checks, 'all_local_samples_identity': exhaustive})
    evidence = {'epoch_et': ET, 'authority_ledger_sha256': catalog_response['authority']['ledger_sha256'],
                'objects': rows, 'checks': 'same-ET, same-frame governed position and velocity subtraction'}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'result': 'PASS', 'objects': len(rows),
                      'max_position_residual_km': max(check['position_residual_km']
                           for row in rows for check in row['sampled_identity_checks']),
                      'max_velocity_residual_km_s': max(check['velocity_residual_km_s']
                           for row in rows for check in row['sampled_identity_checks']),
                      'evidence': str(EVIDENCE)}, indent=2))


if __name__ == '__main__':
    check()
