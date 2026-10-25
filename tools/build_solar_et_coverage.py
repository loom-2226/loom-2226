"""Build the additive ET coverage migration from read-only ledger + pinned SPKs.

Run only against the qualified Solar snapshot. Output is reviewed/static: the
server never performs migration or derives coverage from UTC at runtime.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import spiceypy as spice

from src.loom_solar_postgres import asset_recipes, read_ledger, registry_from_ledger
from src.loom_spatial_state_authority import _epoch, _iso

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'manifests/solar/SOLAR_NATIVE_ET_COVERAGE_V1.json'
MIGRATION = ROOT / 'data/postgres/migrations/020_solar_native_et_coverage.sql'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def build(database='loom_dev', asset_root='/home/ubuntu/loom_solar_assets'):
    ledger = read_ledger(database)
    recipes, identifiers, _ = asset_recipes(asset_root)
    registry = registry_from_ledger(ledger, recipes, identifiers, verify_et=False)
    if len(registry.coverage) != 123 or sum(c.status == 'QUALIFIED' for c in registry.coverage) != 121:
        raise ValueError('Solar coverage snapshot differs from the reviewed 123/121 ledger')
    lsk = next(a for a in registry.sources['DE440'].kernel_assets if str(a.path).endswith('.tls'))
    if sha256(lsk.path) != lsk.sha256:
        raise ValueError('pinned LSK hash mismatch')
    spice.furnsh(str(lsk.path))
    verified = set()
    rows = []
    for c in sorted(registry.coverage, key=lambda c: (c.ephemeris_source_id, c.body_id or '', c.valid_from)):
        source = registry.sources[c.ephemeris_source_id]
        matches = [a for a in source.kernel_assets if Path(a.path).name == source.asset_filename]
        if matches:
            path, expected_sha = Path(matches[0].path), matches[0].sha256
        elif c.status == 'RETIRED':
            historical = list(Path(asset_root).rglob(source.asset_filename))
            if len(historical) != 1:
                raise ValueError('retired source artifact must have one exact local match')
            path, expected_sha = historical[0], source.sha256
        else:
            raise ValueError(f'qualified source has no asset recipe: {source.ephemeris_source_id}')
        if path not in verified:
            if sha256(path) != expected_sha:
                raise ValueError(f'pinned SPK hash mismatch: {path}')
            verified.add(path)
        if c.body_id is None:
            raise ValueError('product coverage requires an explicit target set before ET promotion')
        target = int(registry.body_identifier(c.body_id).identifier_value)
        window = spice.spkcov(str(path), target)
        intervals = [spice.wnfetd(window, i) for i in range(spice.wncard(window))]
        if not intervals:
            raise ValueError(f'no native SPK coverage: {source.ephemeris_source_id}/{c.body_id}')
        # Old UTC labels are retained solely as a qualification-limiting guard.
        # Most labels are exact et2utc projections of the native endpoints.
        # Where qualification deliberately narrowed a wide SPK, intersect the
        # native window with that historical limit and record the exception.
        old_start = float(spice.str2et(_iso(_epoch(c.valid_from))))
        old_end = float(spice.str2et(_iso(_epoch(c.valid_until))))
        native_start, native_end = intervals[0][0], intervals[-1][1]
        start = max(native_start, old_start) if old_start > native_start + .02 else native_start
        end = min(native_end, old_end) if old_end < native_end - .02 else native_end
        if not native_start <= start < end <= native_end:
            raise ValueError(f'nonoverlapping qualified/native coverage: {c.ephemeris_source_id}/{c.body_id}')
        method = ('NATIVE_SPK_ENDPOINTS' if abs(start-native_start) <= .02 and abs(end-native_end) <= .02
                  else 'NATIVE_SPK_INTERSECT_HISTORICAL_QUALIFICATION_LIMIT')
        rows.append(dict(ephemeris_source_id=c.ephemeris_source_id, body_id=c.body_id,
                         valid_from=c.valid_from, valid_until=c.valid_until, status=c.status,
                         coverage_start_et=start, coverage_end_et=end, native_start_et=native_start,
                         native_end_et=native_end, primary_spk_sha256=expected_sha, method=method))
    spice.kclear()
    document = dict(schema='SOLAR_NATIVE_ET_COVERAGE_V1', time_scale='SPICE ET/TDB seconds past J2000',
                    historical_utc_projection_lsk_sha256=lsk.sha256, rows=rows)
    OVERLAY.write_text(json.dumps(document, indent=2) + '\n')
    quoted = lambda x: "'" + x.replace("'", "''") + "'"
    values = ',\n'.join('    (' + ', '.join((quoted(r['ephemeris_source_id']), quoted(r['body_id']),
                  quoted(r['valid_from'])+'::timestamptz', quoted(r['valid_until'])+'::timestamptz',
                  quoted(r['status']), repr(r['coverage_start_et'])+'::double precision',
                  repr(r['coverage_end_et'])+'::double precision')) + ')' for r in rows)
    MIGRATION.write_text(f'''-- Solar ET authority: generated by tools/build_solar_et_coverage.py.
-- Source: pinned SPK target windows; historical UTC labels only narrow prior qualifications.
-- Overlay SHA256: {hashlib.sha256(OVERLAY.read_bytes()).hexdigest()}
BEGIN;
ALTER TABLE loom_solar.ephemeris_coverage
    ADD COLUMN coverage_start_et double precision,
    ADD COLUMN coverage_end_et double precision;

DO $migration$
DECLARE updated_count integer;
BEGIN
    IF (SELECT count(*) FROM loom_solar.ephemeris_coverage) <> 123 OR
       (SELECT count(*) FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED') <> 121 THEN
        RAISE EXCEPTION 'Solar ET migration ledger preimage differs';
    END IF;
    WITH evidence(ephemeris_source_id,body_id,valid_from,valid_until,status,et_start,et_end) AS (
      VALUES
{values}
    )
    UPDATE loom_solar.ephemeris_coverage c
       SET coverage_start_et=e.et_start, coverage_end_et=e.et_end
      FROM evidence e
     WHERE c.ephemeris_source_id=e.ephemeris_source_id
       AND c.body_id IS NOT DISTINCT FROM e.body_id
       AND c.valid_from=e.valid_from AND c.valid_until=e.valid_until AND c.status=e.status;
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    IF updated_count <> 123 THEN
        RAISE EXCEPTION 'Solar ET migration matched % of 123 rows', updated_count;
    END IF;
END $migration$;
ALTER TABLE loom_solar.ephemeris_coverage
    ALTER COLUMN coverage_start_et SET NOT NULL,
    ALTER COLUMN coverage_end_et SET NOT NULL,
    ADD CONSTRAINT solar_et_coverage_order CHECK (
      coverage_start_et > '-Infinity'::double precision
      AND coverage_end_et < 'Infinity'::double precision
      AND coverage_start_et < coverage_end_et);
CREATE INDEX ephemeris_coverage_body_et_idx
    ON loom_solar.ephemeris_coverage(body_id, coverage_start_et, coverage_end_et);
COMMIT;
''')
    print(f'wrote {len(rows)} rows, {len(verified)} verified SPKs, {sum(r["method"] != "NATIVE_SPK_ENDPOINTS" for r in rows)} narrowed rows')


if __name__ == '__main__':
    build()
