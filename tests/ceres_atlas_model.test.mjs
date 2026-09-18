import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateManifest, filterFacilities, findFacility, parseRoute, routeHash, listSnapshot} from '../web/ceres-atlas/model.mjs';

const raw = readFileSync(new URL('../docs/ceres/manifest.json', import.meta.url));
const original = JSON.parse(raw);
const fixture = () => ({schema_version: 1, source: 'docs/ceres/manifest.json',
  source_sha256: createHash('sha256').update(raw).digest('hex'), facilities: structuredClone(original)});
const records = validateManifest(fixture());

test('all five verified identities survive the explicit projection', () => {
  assert.deepEqual(records.map(r => r.id), ['CER-P01', 'CER-P02', 'CER-P03', 'CER-P04', 'CER-P05']);
  for (const row of original) {
    const record = findFacility(records, row.node_id);
    assert.equal(record.nounId, row.noun_id);
    assert.equal(record.assetId, row.asset_id);
    assert.equal(record.image, `images/${row.filename}`);
    assert.equal(record.hash, row.sha256);
    assert.equal(record.bytes, row.byte_length);
    assert.equal(record.name, row.name);
    assert.ok(Object.isFrozen(record));
    assert.ok(!('civstate_zones' in record));
    assert.ok(!('population' in record));
  }
});

test('no invented placement is derived from strategic port', () => {
  const anchorage = findFacility(records, 'CER-P05');
  assert.equal(anchorage.typeLabel, 'Strategic port');
  assert.ok(!('placement' in anchorage));
});

test('case-insensitive search supports name, ID and readable type', () => {
  assert.deepEqual(filterFacilities(records, {query: '  OCCATOR ', type: ''}).map(r => r.id), ['CER-P01']);
  assert.deepEqual(filterFacilities(records, {query: 'cer-p04', type: ''}).map(r => r.id), ['CER-P04']);
  assert.equal(filterFacilities(records, {query: 'orbital', type: ''}).length, 2);
  assert.equal(filterFacilities(records, {query: 'surface resource', type: ''})[0].id, 'CER-P02');
});

test('type filter and search intersect; empty and unknown states stay empty', () => {
  assert.deepEqual(filterFacilities(records, {query: 'ceres', type: 'ORBITAL_SHIPYARD'}).map(r => r.id), ['CER-P04']);
  assert.equal(filterFacilities(records, {query: 'missing', type: ''}).length, 0);
  assert.equal(filterFacilities(records, {query: '', type: 'INVENTED'}).length, 0);
  assert.equal(findFacility(records, 'CER-P99'), null);
  assert.equal(findFacility(records, '<script>'), null);
});

test('route preserves filters and facility through serialization and return', () => {
  const list = {query: 'Ceres & port + α', type: 'STRATEGIC_PORT', facilityId: ''};
  const detail = {...list, facilityId: 'CER-P05'};
  assert.deepEqual(parseRoute(routeHash(detail)), detail);
  assert.deepEqual(parseRoute(routeHash({...detail, facilityId: ''})), list);
  assert.deepEqual(parseRoute(''), {query: '', type: '', facilityId: ''});
});

test('unknown and malformed URL values remain data, never another selected facility', () => {
  assert.equal(parseRoute('#facility=CER-P99').facilityId, 'CER-P99');
  assert.equal(findFacility(records, parseRoute('#facility=%E0%A4%A').facilityId), null);
  assert.equal(parseRoute('#q=' + 'a'.repeat(300)).query.length, 200);
  assert.equal(parseRoute('#q=%3Cscript%3E').query, '<script>');
});

test('return snapshots retain focus, scroll and last viewed identity; invalid scroll is reset', () => {
  assert.deepEqual(listSnapshot({scroll: 845, focus: 'open-CER-P04', lastId: 'CER-P04'}),
    {scroll: 845, focus: 'open-CER-P04', lastId: 'CER-P04'});
  assert.equal(listSnapshot({scroll: -1}).scroll, 0);
  assert.equal(listSnapshot({scroll: Infinity}).scroll, 0);
  assert.equal(listSnapshot({scroll: '845'}).scroll, 0);
});

for (const [name, change] of [
  ['unsupported schema', p => { p.schema_version = 2; }],
  ['missing source hash', p => { delete p.source_sha256; }],
  ['wrong count', p => { p.facilities.pop(); }],
  ['duplicate facility', p => { p.facilities[1].node_id = p.facilities[0].node_id; }],
  ['unknown facility', p => { p.facilities[0].node_id = 'CER-P99'; }],
  ['unapproved image', p => { p.facilities[0].review_status = 'PENDING'; }],
  ['noncurrent image', p => { p.facilities[0].is_current = 0; }],
  ['nonhero image', p => { p.facilities[0].role = 'OTHER'; }],
  ['unverified export', p => { p.facilities[0].export_status = 'UNKNOWN'; }],
  ['duplicate asset', p => { p.facilities[1].asset_id = p.facilities[0].asset_id; }],
  ['traversal filename', p => { p.facilities[0].filename = '../private.png'; }],
  ['external asset', p => { p.facilities[0].filename = 'https://example.com/image.png'; }],
  ['missing name', p => { p.facilities[0].name = ''; }],
  ['invalid hash', p => { p.facilities[0].sha256 = 'not-a-hash'; }],
  ['invalid size', p => { p.facilities[0].byte_length = 0; }],
]) test(`rejects ${name}`, () => {
  const payload = fixture(); change(payload);
  assert.throws(() => validateManifest(payload));
});
