"""Read-only PostgreSQL ledger -> existing SolarEphemerisRegistry.

PostgreSQL owns membership and authority metadata. Versioned manifests supply
only local asset recipes; their immutable source identities must agree.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import (
    BodyIdentifier, EphemerisCoverage, EphemerisSource, SolarBody,
    SolarEphemerisRegistry, registry_from_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    'OFFICIAL_PLANET_CENTER_KERNELS_V1.json',
    'SOLAR_PHASE4B_AUTHORITY_V1.json',
    'SOLAR_PHASE4C_MAJOR_MOONS_V1.json',
    'SOLAR_PHASE4D_STRATEGIC_BODIES_V1.json',
    'SOLAR_PHASE4E_CURATED_42_PLUS_5_V1.json',
    'SOLAR_PHASE4F_ESTIMATED_RELATIVE_V1.json',
)
ET_OVERLAY = ROOT / 'manifests/solar/SOLAR_NATIVE_ET_COVERAGE_V1.json'
SOURCE_IDENTITY = ('provider', 'product_version', 'asset_filename', 'sha256', 'byte_count')


def read_ledger(database):
    # Fixed SQL; no user input is interpolated. psql is the repository's existing
    # PostgreSQL access dependency. One repeatable read snapshot, no writes.
    tables = ('body', 'body_identifier', 'ephemeris_source', 'ephemeris_coverage',
              'object_metadata', 'curated_cohort_member')
    pairs = ','.join(f"'{t}',(SELECT coalesce(json_agg(r ORDER BY to_jsonb(r)::text),'[]'::json) FROM loom_solar.{t} r)"
                     for t in tables)
    sql = ('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY; '
           "SET LOCAL statement_timeout='15s'; "
           f'SELECT json_build_object({pairs}); COMMIT;')
    result = subprocess.run(['psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1',
                             '-d', database, '-c', sql],
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise CelestialStateError(f'PostgreSQL ledger read failed: {result.stderr.strip()}')
    return json.loads(result.stdout)


def asset_recipes(asset_root, manifest_dir=ROOT / 'manifests/solar'):
    sources, identifiers, hashes = {}, {}, {}
    for filename in MANIFESTS:
        path = Path(manifest_dir) / filename
        registry = registry_from_manifest(path, asset_root)
        hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
        for key, source in registry.sources.items():
            previous = sources.get(key)
            if previous and any(getattr(previous, k) != getattr(source, k)
                                for k in (*SOURCE_IDENTITY, 'kernel_assets')):
                raise CelestialStateError(f'conflicting manifest asset recipes: {key}')
            sources[key] = source
        for ident in registry.identifiers:
            key = (ident.body_id, ident.authority, ident.identifier_type)
            if key in identifiers and identifiers[key] != ident.identifier_value:
                raise CelestialStateError(f'conflicting manifest identifier: {key}')
            identifiers[key] = ident.identifier_value
    if ET_OVERLAY.is_file():
        hashes[ET_OVERLAY.name] = hashlib.sha256(ET_OVERLAY.read_bytes()).hexdigest()
    return sources, identifiers, hashes


def registry_from_ledger(ledger, recipes, manifest_identifiers, *, verify_et=True):
    bodies = [SolarBody(**{k: row[k] for k in ('body_id', 'canonical_name', 'body_class')})
              for row in ledger['body']]
    if len({b.body_id for b in bodies}) != len(bodies):
        raise CelestialStateError('duplicate PostgreSQL body identity')
    identifiers = [BodyIdentifier(**row) for row in ledger['body_identifier']]
    for ident in identifiers:
        key = (ident.body_id, ident.authority, ident.identifier_type)
        if ident.status == 'ACTIVE' and key in manifest_identifiers:
            if manifest_identifiers[key] != ident.identifier_value:
                raise CelestialStateError(f'PostgreSQL/manifest identifier mismatch: {key}')
    sources = []
    for row in ledger['ephemeris_source']:
        key = row['ephemeris_source_id']
        recipe = recipes.get(key)
        if recipe is None and row['status'] == 'QUALIFIED':
            raise CelestialStateError(f'no governed local asset recipe for qualified source: {key}')
        if recipe:
            for field in SOURCE_IDENTITY:
                if row[field] != getattr(recipe, field):
                    raise CelestialStateError(f'PostgreSQL/manifest source mismatch: {key}.{field}')
        # Display labels, lifecycle, capability, uncertainty and acquisition time
        # are read from the current ledger, not historical manifest defaults.
        sources.append(EphemerisSource(**row, kernel_assets=recipe.kernel_assets if recipe else ()))
    sources_by_id = {s.ephemeris_source_id: s for s in sources}
    coverage = [EphemerisCoverage(**row) for row in ledger['ephemeris_coverage']]
    if verify_et:
        overlay = json.loads(ET_OVERLAY.read_text())
        expected = {(r['ephemeris_source_id'], r['body_id'], r['status']): r for r in overlay['rows']}
        if len(expected) != len(overlay['rows']) or len(coverage) != len(expected):
            raise CelestialStateError('Solar ET coverage overlay/ledger row count mismatch')
    for row in coverage:
        if row.reference_frame != 'ECLIPJ2000' or row.units != 'km,km/s':
            raise CelestialStateError('noncanonical PostgreSQL coverage frame/units')
        if (row.body_id is None) != (row.coverage_class == 'PRODUCT'):
            raise CelestialStateError('invalid PostgreSQL coverage specificity')
        if verify_et:
            evidence = expected.get((row.ephemeris_source_id, row.body_id, row.status))
            if evidence is None or row.coverage_start_et != evidence['coverage_start_et'] or row.coverage_end_et != evidence['coverage_end_et']:
                raise CelestialStateError('PostgreSQL/native SPK ET coverage mismatch')
            if sources_by_id[row.ephemeris_source_id].sha256 != evidence['primary_spk_sha256']:
                raise CelestialStateError('PostgreSQL/ET overlay SPK hash mismatch')
            if _same_label(row.valid_from, evidence['valid_from']) is False or _same_label(row.valid_until, evidence['valid_until']) is False:
                raise CelestialStateError('PostgreSQL/ET overlay historical label mismatch')
    return SolarEphemerisRegistry(bodies, identifiers, sources, coverage)


def _same_label(a, b):
    from src.loom_spatial_state_authority import _epoch
    return _epoch(a) == _epoch(b)


def load_authority(database, asset_root):
    ledger = read_ledger(database)
    recipes, identifiers, hashes = asset_recipes(asset_root)
    registry = registry_from_ledger(ledger, recipes, identifiers)
    return ledger, registry, hashes
