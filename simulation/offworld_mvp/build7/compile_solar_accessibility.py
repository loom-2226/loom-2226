"""Offline Build 7 preliminary transfer screen from qualified Solar SPK authority.

This compiler is deliberately outside the runtime path. Its output is a pinned,
public, actor-visible engineering input, not an operational mission design.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from src.loom_spice_ephemeris_adapter import (
    BodyIdentifier, EphemerisCoverage, SolarBody, SolarEphemerisRegistry,
    SpiceEphemerisAdapter, registry_from_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
INPUT = Path(__file__).resolve().parent / 'inputs/BUILD7_SOLAR_ACCESSIBILITY_REFERENCE_V1.json'
OUTPUT = Path(__file__).resolve().parent / 'inputs/BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1.json'
OFFLINE_REQUIREMENTS = Path(__file__).resolve().parent / 'inputs/BUILD7_ACCESSIBILITY_COMPILER_REQUIREMENTS_V1.txt'
MANIFESTS = (
    'manifests/solar/SOLAR_PHASE4B_AUTHORITY_V1.json',
    'manifests/solar/SOLAR_PHASE4C_MAJOR_MOONS_V1.json',
    'manifests/solar/SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json',
    'manifests/solar/SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json',
    'manifests/solar/OFFICIAL_PLANET_CENTER_KERNELS_V1.json',
)
PROMOTED_SQL = 'data/postgres/migrations/012_solar_phase4_earned_authority.sql'
SUN_GM_SOURCE = 'src/loom_solar_gis.py'
SUN_GM_KM3_S2 = 132712440018.0
DE440_FROM = '1549-12-30T23:59:18.815889Z'
DE440_UNTIL = '2650-01-24T23:58:50.815708Z'
DEPARTURE_MONTHS = (1, 7)
DEPARTURE_DAY = 15
TOF_DAYS = (30, 180, 365, 730, 1460, 2920)
METHOD = 'SUN_CENTRED_ZERO_REV_LAMBERT_GRID_V1'


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _iso(day: datetime) -> str:
    return day.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def _source_index(asset_root: Path):
    sources = {}
    manifests = []
    for relative in MANIFESTS:
        path = ROOT / relative
        registry = registry_from_manifest(path, asset_root)
        manifests.append({'path': relative, 'sha256': _digest(path)})
        for sid, source in registry.sources.items():
            if sid in sources:
                previous, coverage = sources[sid]
                if (previous.sha256, previous.kernel_assets) != (source.sha256, source.kernel_assets):
                    raise ValueError('conflicting qualified source asset: ' + sid)
                sources[sid] = (previous, (*coverage, *registry.coverage))
            else:
                sources[sid] = (source, registry.coverage)
    return sources, manifests


def _registry_for(record: dict, sources: dict) -> SolarEphemerisRegistry:
    bodies = [SolarBody('EARTH', 'Earth', 'PLANET')]
    identifiers = [BodyIdentifier('EARTH', 'NAIF', 'NAIF_ID', '399')]
    if record['body_id'] != 'EARTH':
        bodies.append(SolarBody(record['body_id'], record['canonical_name'], record['body_class']))
        identifiers.append(BodyIdentifier(record['body_id'], 'NAIF', 'NAIF_ID', record['active_naif_ids'][0]))
    selected = {'DE440'}
    for sid in record['ephemeris_sources']:
        source = sources[sid][0]
        # The NAV readiness map names the source active at its 2226 reference
        # epoch. Some are propagated successors; their lineage names the
        # qualified direct SPK still valid throughout the Build 7 horizon.
        if not source.navigation_grade:
            sid = (source.source_lineage or '').split(';')[0]
        if sid not in sources:
            raise ValueError('direct lineage source missing: ' + sid)
        selected.add(sid)
    records = []
    coverage = []
    for sid in sorted(selected):
        source, rows = sources[sid]
        if not source.navigation_grade or source.status != 'QUALIFIED':
            raise ValueError('unqualified source: ' + sid)
        records.append(source)
        coverage.extend(row for row in rows if row.ephemeris_source_id == sid
                        and row.body_id in (record['body_id'], 'EARTH') and row not in coverage)
    # These four exact body/DE440 rows are promoted by migration 012. The JSON
    # manifests contain the qualified DE440 asset but omit these older rows.
    for body in ('EARTH', 'MERCURY', 'MOON', 'VENUS'):
        if body == 'EARTH' or body == record['body_id']:
            if not any(row.body_id == body and row.ephemeris_source_id == 'DE440' for row in coverage):
                coverage.append(EphemerisCoverage('DE440', body, DE440_FROM, DE440_UNTIL))
    for body in bodies:
        if not any(row.body_id == body.body_id for row in coverage):
            raise ValueError('qualified coverage missing: ' + body.body_id)
    return SolarEphemerisRegistry(bodies, identifiers, records, coverage)


def _screen(body_id: str, year: int, adapter: SpiceEphemerisAdapter) -> dict:
    import numpy as np
    from lamberthub import izzo2015

    options = []
    source_ids = set()
    for month in DEPARTURE_MONTHS:
        departure = datetime(year, month, DEPARTURE_DAY, tzinfo=timezone.utc)
        depart_state = adapter.resolve('EARTH', _iso(departure))
        r1 = np.asarray(depart_state.position_km)
        earth_velocity = np.asarray(depart_state.velocity_km_s)
        for tof_days in TOF_DAYS:
            arrival = departure + timedelta(days=tof_days)
            arrive_state = adapter.resolve(body_id, _iso(arrival))
            source_ids.add(arrive_state.provenance['ephemeris_source_id'])
            r2 = np.asarray(arrive_state.position_km)
            target_velocity = np.asarray(arrive_state.velocity_km_s)
            try:
                v1, v2 = izzo2015(SUN_GM_KM3_S2, r1, r2, float(tof_days * 86400), M=0,
                                   prograde=True, low_path=True)
            except (ValueError, RuntimeError):
                continue
            departure_vinf = float(np.linalg.norm(v1 - earth_velocity))
            arrival_vinf = float(np.linalg.norm(v2 - target_velocity))
            burden = departure_vinf + arrival_vinf
            if all(isfinite(value) for value in (departure_vinf, arrival_vinf, burden)):
                options.append((burden, _iso(departure), tof_days, departure_vinf, arrival_vinf))
    if not options:
        raise ValueError(f'no numerical Lambert screen for {body_id} in {year}')
    burden, departure, tof_days, departure_vinf, arrival_vinf = min(options)
    return {'accessibility_status': 'SCREENED', 'sampled_departure_utc': departure,
            'sampled_time_of_flight_days': tof_days,
            'departure_vinf_km_s': round(departure_vinf, 6),
            'arrival_vinf_km_s': round(arrival_vinf, 6),
            'transfer_burden_km_s': round(burden, 6),
            'ephemeris_source_ids': sorted(source_ids), 'method_id': METHOD}


def compile_screen(asset_root: Path) -> dict:
    import importlib.metadata as metadata
    import lamberthub
    import numpy
    import spiceypy

    expected_versions = {'lamberthub': '1.0.0', 'spiceypy': '6.0.3',
                         'numpy': '2.5.3', 'scipy': '1.18.1',
                         'numba': '0.68.0', 'llvmlite': '0.50.0'}
    if any(metadata.version(name) != version for name, version in expected_versions.items()):
        raise ValueError('offline accessibility dependency version drift')

    authority = json.loads(INPUT.read_text())
    for ref in authority['source_artifacts']:
        if _digest(ROOT / ref['path']) != ref['sha256']:
            raise ValueError('accessibility authority drift: ' + ref['path'])
    if (authority['counts'] != {'derivable': 83, 'eligible_bodies': 90, 'unknown': 7}
            or authority['horizon'] != {'start_year': 2026, 'end_year': 2035}):
        raise ValueError('accessibility authority coverage drift')
    sources, manifests = _source_index(asset_root)
    rows = []
    for record in authority['records']:
        body_id = record['body_id']
        if record['accessibility_status'] == 'UNKNOWN':
            for year in range(2026, 2036):
                rows.append({'body_id': body_id, 'year': year, 'accessibility_status': 'UNKNOWN',
                             'unknown_reason': record['unknown_reason'], 'method_id': METHOD})
            continue
        if record['accessibility_status'] != 'DERIVABLE' or len(record['active_naif_ids']) != 1:
            raise ValueError('unsupported reference record: ' + body_id)
        registry = _registry_for(record, sources)
        spiceypy.kclear()
        adapter = SpiceEphemerisAdapter(registry)
        for year in range(2026, 2036):
            rows.append({'body_id': body_id, 'year': year, **_screen(body_id, year, adapter)})
    spiceypy.kclear()
    return {
        'schema': 'BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1',
        'classification': 'ENGINEERING_PRELIMINARY_TRANSFER_SCREEN_NOT_MISSION_DESIGN',
        'origin_body_id': 'EARTH',
        'authority_map_sha256': _digest(INPUT),
        'source_manifests': manifests,
        'promoted_de440_coverage': {'path': PROMOTED_SQL, 'sha256': _digest(ROOT / PROMOTED_SQL)},
        'sun_gm_engineering_parameter': {'km3_s2': SUN_GM_KM3_S2, 'path': SUN_GM_SOURCE,
                                         'sha256': _digest(ROOT / SUN_GM_SOURCE)},
        'method': {'id': METHOD, 'departure_months': list(DEPARTURE_MONTHS),
                   'departure_day': DEPARTURE_DAY, 'time_of_flight_days': list(TOF_DAYS),
                   'revolutions': 0, 'direction': 'PROGRADE',
                   'burden_definition': 'departure_vinf_km_s + arrival_vinf_km_s',
                   'solver': 'lamberthub.izzo2015', 'lamberthub_version': lamberthub.__version__,
                   'spiceypy_version': spiceypy.__version__, 'numpy_version': numpy.__version__,
                   'interpretation': 'Preliminary heliocentric geometry only; no launch, capture, service, capability, or operational mission feasibility claim.'},
        'counts': {'eligible_bodies': 90, 'screened': 83, 'unknown': 7, 'years': 10},
        'rows': sorted(rows, key=lambda row: (row['year'], row['body_id'])),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--asset-root', required=True, type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    result = json.dumps(compile_screen(args.asset_root), sort_keys=True, indent=2) + '\n'
    if args.check:
        if OUTPUT.read_text() != result:
            raise SystemExit('compiled accessibility artifact differs')
    else:
        OUTPUT.write_text(result)


if __name__ == '__main__':
    main()
