"""Disposable inspection data. All coordinates come through the governed service."""
from dataclasses import asdict
from datetime import timedelta
from functools import lru_cache
import hashlib
import json

from src.loom_spatial_state_authority import CANONICAL_FRAME, CelestialStateError, _epoch, _iso
from src.loom_spice_ephemeris_adapter import SpiceEphemerisAdapter
from src.loom_solar_postgres import load_authority


def relative_state(state, center):
    if state['epoch_utc'] != center['epoch_utc'] or state['reference_frame'] != center['reference_frame']:
        raise CelestialStateError('relative states must share epoch and frame')
    return {
        'reference_center': center['entity_id'],
        'position_km': [a-b for a, b in zip(state['position_km'], center['position_km'])],
        'velocity_km_s': [a-b for a, b in zip(state['velocity_km_s'], center['velocity_km_s'])],
        'presentation_only': True,
    }


class Inspector:
    def __init__(self, ledger, registry, service, manifest_hashes=None):
        self.ledger, self.registry, self.service = ledger, registry, service
        self.bodies = {r['body_id']: r for r in ledger['body']}
        self.metadata = {r['body_id']: r for r in ledger['object_metadata']}
        self.cohorts = {}
        for row in ledger['curated_cohort_member']:
            self.cohorts.setdefault(row['body_id'], []).append(row)
        identifiers = {}
        for identifier in registry.identifiers:
            identifiers.setdefault(identifier.body_id, []).append(asdict(identifier))
        coverage_rows = [(coverage.body_id, asdict(coverage)) for coverage in registry.coverage]
        # Trajectory sampling revisits each identity at many epochs. Share the
        # immutable startup-ledger projection; only resolver state varies.
        self.record_metadata = {
            body_id: {**body, 'identifiers': identifiers.get(body_id, []),
                      'metadata': self.metadata.get(body_id), 'cohorts': self.cohorts.get(body_id, []),
                      'known_coverage': [row for covered_body, row in coverage_rows if covered_body in (None, body_id)]}
            for body_id, body in self.bodies.items()
        }
        self.authority = {
            'catalog_source': 'PostgreSQL loom_solar; read-only startup snapshot',
            'ledger_sha256': hashlib.sha256(json.dumps(ledger, sort_keys=True).encode()).hexdigest(),
            'manifest_sha256': manifest_hashes or {},
        }

    @classmethod
    def connect(cls, database, asset_root):
        ledger, registry, hashes = load_authority(database, asset_root)
        return cls(ledger, registry, SpiceEphemerisAdapter(registry).service(), hashes)

    @lru_cache(maxsize=8192)
    def record(self, body_id, epoch):
        epoch = _iso(_epoch(epoch))
        if body_id not in self.bodies:
            raise ValueError(f'unknown catalog object: {body_id}')
        row = {**self.record_metadata[body_id], 'epoch_utc': epoch}
        try:
            state = self.service.resolve(body_id, epoch)
            if state.reference_frame != CANONICAL_FRAME or state.provenance.get('units') != 'km,km/s':
                raise CelestialStateError('noncanonical resolver frame/units')
            row.update(resolution='RESOLVED', state=asdict(state),
                       authority_class=('PROPAGATED' if state.provenance['state_capability'].startswith('EMPIRICAL_PROPAGATED')
                                        else 'DIRECT'))
        except CelestialStateError as exc:
            reasons = []
            while exc is not None:
                reasons.append(str(exc))
                exc = exc.__cause__
            row.update(resolution='UNRESOLVED', reason='; caused by: '.join(reasons))
        return row

    def at(self, body_id, epoch, center_id):
        row = dict(self.record(body_id, epoch))
        center = self.record(center_id, epoch)
        if row['resolution'] == 'RESOLVED' and center['resolution'] == 'RESOLVED':
            row['relative'] = relative_state(row['state'], center['state'])
        else:
            row['presentation_reason'] = ('object unresolved' if row['resolution'] == 'UNRESOLVED'
                                          else f'reference center unresolved: {center["reason"]}')
        return row

    def catalog(self, epoch=None):
        """Stable governed identity for selectors; no ephemeris evaluation."""
        if epoch is not None:
            epoch = _iso(_epoch(epoch))
        def identity(row):
            item = {key: row.get(key) for key in ('body_id', 'canonical_name', 'body_class', 'parent_body_id', 'status')}
            if epoch:
                try:
                    source, _ = self.registry.source_for(row['body_id'], epoch)
                    item['source_asset_bytes'] = sum(asset.byte_count or 0 for asset in source.kernel_assets)
                except CelestialStateError:
                    item['source_asset_bytes'] = None
            return item
        return {'authority': self.authority, 'objects': [
            identity(row) for row in sorted(self.bodies.values(), key=lambda row: row['body_id'])
        ]}

    def preview_ids(self, epoch, center_id='SUN', limit=5):
        """Prioritize low-cost governed sources for the first scene paint."""
        epoch = _iso(_epoch(epoch))
        if center_id not in self.bodies:
            raise ValueError(f'unknown catalog object: {center_id}')
        candidates = []
        for row in self.bodies.values():
            if row['body_class'] not in ('PLANET', 'NATURAL_SATELLITE'):
                continue
            try:
                source, _ = self.registry.source_for(row['body_id'], epoch)
            except CelestialStateError:
                continue
            candidates.append((sum(asset.byte_count or 0 for asset in source.kernel_assets), row['body_id']))
        return tuple([center_id] + [body for _, body in sorted(candidates) if body != center_id][:limit-1])

    def scene_row(self, row):
        """Transport projection of an exact resolver row, never a new state source."""
        keys = ('body_id', 'canonical_name', 'body_class', 'parent_body_id', 'resolution',
                'authority_class', 'relative', 'reason', 'presentation_reason')
        return {**{key: row[key] for key in keys if key in row},
                'catalog_only': not any(c['status'] == 'QUALIFIED' and self.registry.sources[c['ephemeris_source_id']].status == 'QUALIFIED'
                                        for c in row['known_coverage']),
                'partial_catalog': any(c['final_outcome'] == 'PARTIAL' for c in row['cohorts'])}

    @lru_cache(maxsize=8)
    def scene_snapshot(self, epoch, center_id='SUN', body_ids=None):
        epoch = _iso(_epoch(epoch))
        ids = tuple(sorted(self.bodies)) if body_ids is None else tuple(dict.fromkeys(body_ids))
        if not ids or any(body not in self.bodies for body in ids):
            raise ValueError('scene requires known catalog body IDs')
        rows = [self.at(body, epoch, center_id) for body in ids]
        scene_rows = [self.scene_row(row) for row in rows]
        resolved = sum(row['resolution'] == 'RESOLVED' for row in rows)
        direct = sum(row.get('authority_class') == 'DIRECT' for row in rows)
        return {
            'epoch_utc': epoch, 'reference_center': center_id, 'reference_frame': CANONICAL_FRAME,
            'units': 'km,km/s', 'authority': self.authority, 'objects': scene_rows,
            'complete': body_ids is None, 'catalog_total': len(self.bodies),
            'counts': {'catalog': len(rows), 'resolved': resolved, 'direct': direct,
                       'propagated': resolved-direct, 'unresolved': len(rows)-resolved,
                       'catalog_only': sum(row['catalog_only'] for row in scene_rows),
                       'partial_catalog': sum(row['partial_catalog'] for row in scene_rows),
                       'renderable': sum('relative' in row for row in scene_rows)},
        }

    def path(self, body_id, start, end, center_id='SUN', samples=96):
        """Compact display geometry from the same exact trajectory and seam logic."""
        result = self.trajectory(body_id, start, end, center_id, samples)
        return {**{key: result[key] for key in ('body_id', 'reference_center', 'reference_frame',
                                                'start', 'end', 'segments', 'gap_indices', 'closed_by_renderer')},
                'points': [{key: point[key] for key in ('epoch_utc', 'resolution', 'authority_class', 'relative') if key in point}
                           for point in result['points']]}

    @lru_cache(maxsize=8)
    def snapshot(self, epoch, center_id='SUN'):
        epoch = _iso(_epoch(epoch))
        rows = [self.at(body, epoch, center_id) for body in sorted(self.bodies)]
        resolved = sum(r['resolution'] == 'RESOLVED' for r in rows)
        direct = sum(r.get('authority_class') == 'DIRECT' for r in rows)
        catalog_only = sum(not any(c.status == 'QUALIFIED' and self.registry.sources[c.ephemeris_source_id].status == 'QUALIFIED'
                                  for c in self.registry.coverage if c.body_id in (None, r['body_id'])) for r in rows)
        return {
            'epoch_utc': epoch, 'reference_center': center_id, 'reference_frame': CANONICAL_FRAME,
            'units': 'km,km/s', 'authority': self.authority, 'objects': rows,
            'counts': {'catalog': len(rows), 'resolved': resolved, 'direct': direct,
                       'propagated': resolved-direct, 'unresolved': len(rows)-resolved,
                       'catalog_only': catalog_only,
                       'partial_catalog': sum(any(c['final_outcome'] == 'PARTIAL' for c in r['cohorts']) for r in rows),
                       'renderable': sum('relative' in r for r in rows)},
        }

    @staticmethod
    def source_key(row):
        return (row['state']['provenance']['ephemeris_source_id'], row['authority_class'])

    @lru_cache(maxsize=16)
    def trajectory(self, body_id, start, end, center_id='SUN', samples=96):
        first, last = _epoch(start), _epoch(end)
        if first >= last or not 2 <= samples <= 512:
            raise ValueError('trajectory requires start < end and 2–512 samples')
        times = {first+(last-first)*i/(samples-1) for i in range(samples)}
        # Sample coverage boundaries and each side, but let the SAME resolver
        # select the source. This is sampling, not a second precedence policy.
        for c in self.registry.coverage:
            if c.body_id in (None, body_id, center_id):
                for t in (_epoch(c.valid_from), _epoch(c.valid_until)):
                    for offset in (-1000000, -1, 0, 1, 1000000):
                        candidate = t + timedelta(microseconds=offset)
                        if first <= candidate <= last:
                            times.add(candidate)
        points, segments, seams, gaps = [], [], [], []
        previous_key, previous_index, interrupted = None, None, False
        for t in sorted(times):
            epoch = _iso(t)
            row = self.at(body_id, epoch, center_id)
            center = self.record(center_id, epoch)
            index = len(points)
            points.append(row)
            if 'relative' not in row:
                gaps.append(index)
                interrupted = True
                continue
            key = (self.source_key(row), self.source_key(center))
            if key != previous_key or interrupted:
                if previous_index is not None and key != previous_key:
                    seams.append({'before_index': previous_index, 'after_index': index,
                                  'time_bracket_utc': [points[previous_index]['epoch_utc'], epoch],
                                  'before_sources': previous_key, 'after_sources': key,
                                  'gap_indices': [i for i in gaps if previous_index < i < index],
                                  'before_center_state': self.record(center_id, points[previous_index]['epoch_utc'])['state'],
                                  'after_center_state': center['state']})
                segments.append({'authority_class': row['authority_class'], 'sources': key, 'indices': []})
            segments[-1]['indices'].append(index)
            previous_key, previous_index = key, index
            interrupted = False
        return {'body_id': body_id, 'reference_center': center_id, 'reference_frame': CANONICAL_FRAME,
                'start': _iso(first), 'end': _iso(last), 'points': points, 'segments': segments,
                'seams': seams, 'gap_indices': gaps, 'closed_by_renderer': False}
