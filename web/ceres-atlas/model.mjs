/** Slice-1 contract. No inferred metrics, placement or census interpretation. */
export function typeLabel(value) {
  return value.toLowerCase().replaceAll('_', ' ').replace(/^./, c => c.toUpperCase());
}

export function validateManifest(payload) {
  if (payload?.schema_version !== 1 || payload.source !== 'docs/ceres/manifest.json' ||
      !/^[a-f0-9]{64}$/.test(payload.source_sha256 || '') ||
      !Array.isArray(payload.facilities) || payload.facilities.length !== 5) {
    throw new Error('The local collection has an unsupported format.');
  }
  const ids = new Set(), assets = new Set();
  const records = payload.facilities.map(row => {
    const strings = ['node_id', 'name', 'facility_type', 'noun_id', 'asset_id', 'media_key', 'filename', 'sha256'];
    if (strings.some(key => typeof row?.[key] !== 'string' || !row[key].trim()) ||
        !/^CER-P0[1-5]$/.test(row.node_id) || ids.has(row.node_id) || assets.has(row.asset_id) ||
        row.role !== 'HERO' || row.review_status !== 'APPROVED_REFERENCE' ||
        row.is_current !== 1 || row.export_status !== 'VERIFIED' ||
        !/^[a-f0-9-]{36}$/.test(row.asset_id) ||
        row.filename !== `${row.node_id}_${row.asset_id}.png` ||
        !/^[a-f0-9]{64}$/.test(row.sha256) || !Number.isSafeInteger(row.byte_length) || row.byte_length <= 0) {
      throw new Error('The local collection contains an invalid or unapproved facility.');
    }
    ids.add(row.node_id); assets.add(row.asset_id);
    // Explicit projection: census relations/unknown fields cannot become display data.
    return Object.freeze({
      id: row.node_id, name: row.name, type: row.facility_type, typeLabel: typeLabel(row.facility_type),
      nounId: row.noun_id, assetId: row.asset_id, mediaKey: row.media_key,
      image: `images/${row.filename}`, hash: row.sha256, bytes: row.byte_length,
      role: row.role, review: row.review_status,
    });
  });
  return Object.freeze(records.sort((a, b) => a.id.localeCompare(b.id)));
}

export function parseRoute(hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const route = {
    query: (params.get('q') || '').slice(0, 200),
    type: (params.get('type') || '').slice(0, 128),
    facilityId: (params.get('facility') || '').slice(0, 128),
  };
  if (params.has('institution')) route.institutionId = (params.get('institution') || '').slice(0, 160);
  if (params.has('domain')) route.domain = (params.get('domain') || 'people').slice(0, 64);
  if (params.has('collection')) route.collection = params.get('collection') === '1' ? '1' : '';
  return route;
}

export function routeHash(route) {
  const params = new URLSearchParams();
  if (route.query) params.set('q', route.query);
  if (route.type) params.set('type', route.type);
  if (route.facilityId) params.set('facility', route.facilityId);
  if (route.institutionId) params.set('institution', route.institutionId);
  if (route.domain && route.domain !== 'people') params.set('domain', route.domain);
  if (route.collection === '1') params.set('collection', '1');
  return params.size ? `#${params}` : '#';
}

export function facilityRoute(route, facilityId) {
  return {
    query: route.query || '',
    type: route.type || '',
    facilityId,
    domain: route.domain || 'people',
  };
}

export function institutionRoute(route, institutionId) {
  return {
    query: route.query || '',
    type: route.type || '',
    facilityId: '',
    institutionId,
    domain: route.domain || 'institutions',
  };
}

export function filterFacilities(records, {query, type}) {
  const needle = query.trim().toLowerCase();
  return records.filter(record => (!type || record.type === type) &&
    `${record.id} ${record.name} ${record.type} ${record.typeLabel}`.toLowerCase().includes(needle));
}

export function findFacility(records, id) {
  return records.find(record => record.id === id) || null;
}

export function listSnapshot(value = {}) {
  return {
    scroll: Number.isFinite(value.scroll) && value.scroll >= 0 ? value.scroll : 0,
    focus: typeof value.focus === 'string' ? value.focus : 'list-title',
    lastId: typeof value.lastId === 'string' ? value.lastId : '',
  };
}
