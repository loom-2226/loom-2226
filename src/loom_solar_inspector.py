"""Disposable inspection data. All coordinates come through the governed service."""
from dataclasses import asdict
from functools import lru_cache
import hashlib
import json
import math

from src.loom_spatial_state_authority import CelestialStateError
from src.loom_spice_ephemeris_adapter import SPICE_FRAME, SpiceEphemerisAdapter
from src.loom_solar_time import codec_from_registry
from src.loom_solar_postgres import load_authority


def relative_state(state, center):
    if state['epoch_et'] != center['epoch_et'] or state['reference_frame'] != center['reference_frame']:
        raise CelestialStateError('relative states must share epoch and frame')
    return {
        'reference_center': center['entity_id'],
        'position_km': [a-b for a, b in zip(state['position_km'], center['position_km'])],
        'velocity_km_s': [a-b for a, b in zip(state['velocity_km_s'], center['velocity_km_s'])],
        'presentation_only': True,
    }


class Inspector:
    def __init__(self, ledger, registry, service, manifest_hashes=None, max_orbit_years=100, time_codec=None):
        if not 1 <= max_orbit_years <= 500:
            raise ValueError('maximum orbit horizon must be 1–500 Julian years')
        self.max_orbit_years = max_orbit_years
        self.ledger, self.registry, self.service = ledger, registry, service
        self.time = time_codec or (service.adapter.time if hasattr(service, 'adapter') else codec_from_registry(registry))
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
            'physical_time': 'SPICE ET/TDB seconds past J2000',
            'coverage_time': 'numeric SPICE ET from pinned SPK target windows and explicit qualification intersections',
            'utc_input_policy': 'explicit LSK projection at interface only; future UTC is not known authority',
            'utc_projection_lsk_sha256': self.time.lsk_sha256,
        }

    @classmethod
    def connect(cls, database, asset_root, max_orbit_years=100):
        ledger, registry, hashes = load_authority(database, asset_root)
        return cls(ledger, registry, SpiceEphemerisAdapter(registry).service(), hashes, max_orbit_years)

    @lru_cache(maxsize=8192)
    def record(self, body_id, epoch):
        et = self.time.parse(epoch)
        if body_id not in self.bodies:
            raise ValueError(f'unknown catalog object: {body_id}')
        row = {**self.record_metadata[body_id], 'epoch_et': et, 'epoch_tdb': self.time.label(et)}
        try:
            state = self.service.resolve_et(body_id, et)
            if state.epoch_et != et or state.reference_frame != SPICE_FRAME or state.provenance.get('units') != 'km,km/s':
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
        et = self.time.parse(epoch)
        row = dict(self.record(body_id, et))
        row['input_representation'] = self.time.representation(epoch)
        center = self.record(center_id, et)
        if row['resolution'] == 'RESOLVED' and center['resolution'] == 'RESOLVED':
            row['relative'] = relative_state(row['state'], center['state'])
        else:
            row['presentation_reason'] = ('object unresolved' if row['resolution'] == 'UNRESOLVED'
                                          else f'reference center unresolved: {center["reason"]}')
        return row

    def catalog(self, epoch=None):
        """Stable governed identity for selectors; no ephemeris evaluation."""
        if epoch is not None:
            epoch = self.time.parse(epoch)
        def identity(row):
            item = {key: row.get(key) for key in ('body_id', 'canonical_name', 'body_class', 'parent_body_id', 'status')}
            if epoch is not None:
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
        epoch = self.time.parse(epoch)
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
        input_representation = self.time.representation(epoch)
        epoch = self.time.parse(epoch)
        ids = tuple(sorted(self.bodies)) if body_ids is None else tuple(dict.fromkeys(body_ids))
        if not ids or any(body not in self.bodies for body in ids):
            raise ValueError('scene requires known catalog body IDs')
        rows = [self.at(body, epoch, center_id) for body in ids]
        scene_rows = [self.scene_row(row) for row in rows]
        resolved = sum(row['resolution'] == 'RESOLVED' for row in rows)
        direct = sum(row.get('authority_class') == 'DIRECT' for row in rows)
        return {
            'epoch_et': epoch, 'epoch_tdb': self.time.label(epoch), 'input_representation': input_representation,
            'reference_center': center_id, 'reference_frame': SPICE_FRAME,
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
                                                'start', 'end', 'start_et', 'end_et', 'segments', 'gap_indices', 'closed_by_renderer')},
                'points': [{key: point[key] for key in ('epoch_et', 'epoch_tdb', 'resolution', 'authority_class', 'relative') if key in point}
                           for point in result['points']]}

    def orbital_center(self, body_id):
        """Choose a governed state reference for display-horizon planning."""
        body = self.bodies[body_id]
        if body['body_class'] != 'NATURAL_SATELLITE':
            return 'SUN'
        if body_id == 'MOON':
            return 'EARTH'
        parent = body.get('parent_body_id')
        if parent in self.bodies and self.bodies[parent]['body_class'] == 'BARYCENTER':
            primaries = [row['body_id'] for row in self.bodies.values()
                         if row.get('parent_body_id') == parent and
                         row['body_class'] in ('PLANET', 'DWARF_PLANET')]
            if len(primaries) == 1:
                return primaries[0]
        return parent if parent in self.bodies else 'SUN'

    @lru_cache(maxsize=512)
    def automatic_plan(self, body_id, epoch):
        """Find a future revolution using resolver states only; never generate an orbit."""
        input_representation = self.time.representation(epoch)
        first = self.time.parse(epoch)
        start = self.time.label(first)
        body = self.bodies[body_id]
        orbital_center = self.orbital_center(body_id)
        common = {'body_id': body_id, 'start': start, 'start_et': first,
                  'start_input_representation': input_representation,
                  'orbital_reference_center': orbital_center,
                  'max_orbit_years': self.max_orbit_years, 'period_source': 'governed resolver phase search'}
        if body['body_class'] in ('SPACECRAFT', 'INTERSTELLAR_OBJECT'):
            return {**common, 'end': self.time.label(first + 365.25*86400), 'end_et': first + 365.25*86400,
                    'horizon_kind': 'OPEN_ONE_EARTH_YEAR', 'status': 'OPEN_YEAR',
                    'revolution_complete': False, 'phase_covered_degrees': None}
        limit = first + 365.25 * self.max_orbit_years * 86400
        start_row = self.at(body_id, first, orbital_center)
        if 'relative' not in start_row:
            return {**common, 'end': self.time.label(limit), 'end_et': limit, 'horizon_kind': 'BOUND_REVOLUTION',
                    'status': 'UNRESOLVED_AT_T0', 'revolution_complete': False,
                    'phase_covered_degrees': None}
        initial = start_row['relative']
        r0, v0 = initial['position_km'], initial['velocity_km_s']
        cross = lambda a, b: (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        dot = lambda a, b: sum(x*y for x, y in zip(a, b))
        norm = lambda a: math.sqrt(dot(a, a))
        angular_momentum = cross(r0, v0)
        if not norm(r0) or not norm(angular_momentum):
            return {**common, 'end': self.time.label(limit), 'end_et': limit, 'horizon_kind': 'BOUND_REVOLUTION',
                    'status': 'PHASE_UNDETERMINED', 'revolution_complete': False,
                    'phase_covered_degrees': None}
        x_axis = [x/norm(r0) for x in r0]
        normal = [x/norm(angular_momentum) for x in angular_momentum]
        y_axis = cross(normal, x_axis)
        def angle(position):
            return math.atan2(dot(position, y_axis), dot(position, x_axis))
        def advance(previous, current):
            return math.atan2(math.sin(current-previous), math.cos(current-previous))
        current, previous_angle, phase, row = first, 0.0, 0.0, start_row
        for _ in range(2048):
            if current >= limit:
                break
            r, v = row['relative']['position_km'], row['relative']['velocity_km_s']
            omega = norm(cross(r, v)) / max(dot(r, r), 1.0) * 86400.0
            step_days = min(365.25, max(.05, (2*math.pi / max(omega, 1e-12)) / 24))
            following = min(limit, current + step_days*86400)
            next_row = self.at(body_id, following, orbital_center)
            if 'relative' not in next_row:
                return {**common, 'end': self.time.label(limit), 'end_et': limit, 'horizon_kind': 'BOUND_REVOLUTION',
                        'status': 'UNRESOLVED_BEFORE_COMPLETION', 'revolution_complete': False,
                        'phase_covered_degrees': round(math.degrees(phase), 2),
                        'first_unresolved_et': following, 'first_unresolved_epoch': self.time.label(following)}
            next_angle = angle(next_row['relative']['position_km'])
            delta = advance(previous_angle, next_angle)
            if delta < -0.05:
                return {**common, 'end': self.time.label(limit), 'end_et': limit, 'horizon_kind': 'BOUND_REVOLUTION',
                        'status': 'PHASE_AMBIGUOUS', 'revolution_complete': False,
                        'phase_covered_degrees': round(math.degrees(phase), 2)}
            if phase + delta >= 2*math.pi:
                low, high = current, following
                for _ in range(12):
                    mid = low + (high-low)/2
                    mid_row = self.at(body_id, mid, orbital_center)
                    if 'relative' not in mid_row:
                        break
                    mid_phase = phase + advance(previous_angle, angle(mid_row['relative']['position_km']))
                    if mid_phase < 2*math.pi:
                        low = mid
                    else:
                        high = mid
                return {**common, 'end': self.time.label(high), 'end_et': high, 'horizon_kind': 'BOUND_REVOLUTION',
                        'status': 'REVOLUTION_COMPLETE', 'revolution_complete': True,
                        'phase_covered_degrees': 360.0}
            current, previous_angle, phase, row = following, next_angle, phase + max(0.0, delta), next_row
        return {**common, 'end': self.time.label(limit), 'end_et': limit, 'horizon_kind': 'BOUND_REVOLUTION',
                'status': 'MAX_HORIZON_TRUNCATED', 'revolution_complete': False,
                'phase_covered_degrees': round(math.degrees(phase), 2)}

    def automatic_path(self, body_id, epoch, center_id='SUN'):
        plan = self.automatic_plan(body_id, epoch)
        days = (plan['end_et'] - plan['start_et']) / 86400
        samples = min(192, max(24, round(32 + 8 * math.log1p(days / 365.25))))
        probes = (plan['first_unresolved_et'],) if 'first_unresolved_et' in plan else ()
        result = self.trajectory(body_id, plan['start_et'], plan['end_et'], center_id, samples,
                                 adaptive=True, extra_epochs=probes)
        return {**{key: result[key] for key in ('body_id', 'reference_center', 'reference_frame',
                                                'start', 'end', 'start_et', 'end_et', 'segments', 'seams', 'gap_indices', 'closed_by_renderer')},
                'points': [{key: point[key] for key in ('epoch_et', 'epoch_tdb', 'resolution', 'authority_class', 'relative') if key in point}
                           for point in result['points']],
                'horizon': plan, 'sampling': {'nominal': samples, 'actual': len(result['points']),
                                             'method': 'uniform plus resolver midpoint curvature refinement'}}

    @lru_cache(maxsize=8)
    def snapshot(self, epoch, center_id='SUN'):
        input_representation = self.time.representation(epoch)
        epoch = self.time.parse(epoch)
        rows = [self.at(body, epoch, center_id) for body in sorted(self.bodies)]
        resolved = sum(r['resolution'] == 'RESOLVED' for r in rows)
        direct = sum(r.get('authority_class') == 'DIRECT' for r in rows)
        catalog_only = sum(not any(c.status == 'QUALIFIED' and self.registry.sources[c.ephemeris_source_id].status == 'QUALIFIED'
                                  for c in self.registry.coverage if c.body_id in (None, r['body_id'])) for r in rows)
        return {
            'epoch_et': epoch, 'epoch_tdb': self.time.label(epoch), 'input_representation': input_representation,
            'reference_center': center_id, 'reference_frame': SPICE_FRAME,
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
    def trajectory(self, body_id, start, end, center_id='SUN', samples=96, adaptive=False, extra_epochs=()):
        start_representation, end_representation = self.time.representation(start), self.time.representation(end)
        first, last = self.time.parse(start), self.time.parse(end)
        if first >= last or not 2 <= samples <= 512:
            raise ValueError('trajectory requires start < end and 2–512 samples')
        times = {first+(last-first)*i/(samples-1) for i in range(samples)}
        times.update(self.time.parse(epoch) for epoch in extra_epochs)
        if adaptive:
            # Refine only from exact resolver positions. Midpoints never become
            # a physical model or bridge an unresolved interval.
            for _ in range(3):
                additions = []
                ordered = sorted(times)
                for a, b in zip(ordered, ordered[1:]):
                    if len(times) + len(additions) >= 512:
                        break
                    mid = a + (b-a)/2
                    rows = [self.at(body_id, t, center_id) for t in (a, mid, b)]
                    if 'relative' not in rows[1]:
                        additions.append(mid)
                        continue
                    if any('relative' not in row for row in rows):
                        continue
                    p, m, q = [row['relative']['position_km'] for row in rows]
                    scale = max(*(math.dist(point, (0, 0, 0)) for point in (p, m, q)), 1.0)
                    deviation = math.dist(m, [(x+y)/2 for x, y in zip(p, q)]) / scale
                    if deviation > .005:
                        additions.append(mid)
                if not additions:
                    break
                times.update(additions)
        # Sample coverage boundaries and each side, but let the SAME resolver
        # select the source. This is sampling, not a second precedence policy.
        for c in self.registry.coverage:
            if c.body_id in (None, body_id, center_id):
                if c.coverage_start_et is None or c.coverage_end_et is None:
                    continue
                for t in (c.coverage_start_et, c.coverage_end_et):
                    for candidate in (t-1, math.nextafter(t, -math.inf), t,
                                      math.nextafter(t, math.inf), t+1):
                        if first <= candidate <= last:
                            times.add(candidate)
        points, segments, seams, gaps = [], [], [], []
        previous_key, previous_index, interrupted = None, None, False
        for t in sorted(times):
            row = self.at(body_id, t, center_id)
            center = self.record(center_id, t)
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
                                  'time_bracket_et': [points[previous_index]['epoch_et'], t],
                                  'time_bracket_tdb': [points[previous_index]['epoch_tdb'], row['epoch_tdb']],
                                  'before_sources': previous_key, 'after_sources': key,
                                  'gap_indices': [i for i in gaps if previous_index < i < index],
                                  'before_center_state': self.record(center_id, points[previous_index]['epoch_et'])['state'],
                                  'after_center_state': center['state']})
                segments.append({'authority_class': row['authority_class'], 'sources': key, 'indices': []})
            segments[-1]['indices'].append(index)
            previous_key, previous_index = key, index
            interrupted = False
        return {'body_id': body_id, 'reference_center': center_id, 'reference_frame': SPICE_FRAME,
                'start': self.time.label(first), 'end': self.time.label(last), 'start_et': first, 'end_et': last,
                'start_input_representation': start_representation,
                'end_input_representation': end_representation,
                'points': points, 'segments': segments,
                'seams': seams, 'gap_indices': gaps, 'closed_by_renderer': False}
