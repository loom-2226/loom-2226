"""Pure Build 7 prospective mission surface from admitted public Solar inputs.

These immutable records describe possible destinations. They cause no mission,
project, binding, resource observation, or actor decision.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / 'inputs/BUILD7_SOLAR_BODY_CATALOG_V1.json'
REFERENCE = ROOT / 'inputs/BUILD7_SOLAR_ACCESSIBILITY_REFERENCE_V1.json'
SCREEN = ROOT / 'inputs/BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1.json'
ACTION = 'REMOTE_EXPLORATION'


@dataclass(frozen=True)
class MissionCandidate:
    candidate_id: str
    actor_id: str
    calendar_year: int
    action: str
    origin_body_id: str
    destination_body_id: str
    canonical_name: str
    body_class: str
    accessibility_status: str
    sampled_departure_utc: str | None
    sampled_time_of_flight_days: int | None
    departure_vinf_km_s: float | None
    arrival_vinf_km_s: float | None
    transfer_burden_km_s: float | None
    capability_status: str
    qualification_state: str
    public_authority_refs: tuple[str, ...]
    accessibility_method_id: str


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_visible_inputs() -> tuple[dict, dict]:
    """Load pinned catalog and compiled screen; never opens generated WORLD."""
    catalog = json.loads(CATALOG.read_text())
    reference = json.loads(REFERENCE.read_text())
    screen = json.loads(SCREEN.read_text())
    catalog_ref = next(ref for ref in reference['source_artifacts']
                       if ref['path'].endswith('/BUILD7_SOLAR_BODY_CATALOG_V1.json'))
    bodies = catalog['bodies']
    expected = {record['body_id']: record for record in reference['records']}
    if (catalog['schema'] != 'BUILD7_SOLAR_BODY_CATALOG_V1'
            or catalog['eligible_count'] != 90 or len(expected) != 90
            or screen['schema'] != 'BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1'
            or screen['authority_map_sha256'] != _digest(REFERENCE)
            or screen['origin_body_id'] != 'EARTH'
            or catalog_ref['sha256'] != _digest(CATALOG)
            or screen['counts'] != {'eligible_bodies': 90, 'screened': 83, 'unknown': 7, 'years': 10}
            or {body['semantic_key'] for body in bodies} != set(expected)):
        raise ValueError('Build 7 public opportunity authority drift')
    if (len(screen['rows']) != 900
            or {(row['body_id'], row['year']) for row in screen['rows']}
            != {(body_id, year) for body_id in expected for year in range(2026, 2036)}):
        raise ValueError('Build 7 accessibility screen incomplete')
    for row in screen['rows']:
        body_id = row['body_id']
        status = row['accessibility_status']
        if (body_id not in expected or row['year'] not in range(2026, 2036)
                or (expected[body_id]['accessibility_status'] == 'UNKNOWN') != (status == 'UNKNOWN')
                or status not in ('UNKNOWN', 'SCREENED')):
            raise ValueError('Build 7 accessibility status drift')
    return catalog, screen


def derive_mission_candidates(*, actor_id: str, capabilities: Iterable[str],
                              calendar_year: int, public_bodies: Iterable[Mapping],
                              accessibility_rows: Iterable[Mapping]) -> tuple[MissionCandidate, ...]:
    """Derive every destination through one visible-input path, without ranking."""
    if not actor_id or calendar_year not in range(2026, 2036):
        raise ValueError('actor or year outside Build 7 opportunity scope')
    public_bodies = tuple(public_bodies)
    accessibility_rows = tuple(accessibility_rows)
    rows = {(row['body_id'], row['year']): row for row in accessibility_rows}
    bodies = {body['semantic_key']: body for body in public_bodies}
    if len(bodies) != len(public_bodies) or len(rows) != len(accessibility_rows):
        raise ValueError('duplicate public body or accessibility row')
    if {(body_id, calendar_year) for body_id in bodies} - set(rows):
        raise ValueError('missing public accessibility row')
    can_explore = 'EXPLORE' in frozenset(capabilities)
    candidates = []
    for body_id in sorted(bodies):
        body = bodies[body_id]
        row = rows[(body_id, calendar_year)]
        status = row['accessibility_status']
        if status not in ('SCREENED', 'UNKNOWN'):
            raise ValueError('unrecognized accessibility status')
        screened = status == 'SCREENED'
        candidates.append(MissionCandidate(
            candidate_id=f'MISSION_CANDIDATE_V1:{actor_id}:{calendar_year}:{ACTION}:{body_id}',
            actor_id=actor_id, calendar_year=calendar_year, action=ACTION,
            origin_body_id='EARTH',
            destination_body_id=body_id, canonical_name=body['canonical_name'],
            body_class=body['body_class'], accessibility_status=status,
            sampled_departure_utc=row['sampled_departure_utc'] if screened else None,
            sampled_time_of_flight_days=row['sampled_time_of_flight_days'] if screened else None,
            departure_vinf_km_s=row['departure_vinf_km_s'] if screened else None,
            arrival_vinf_km_s=row['arrival_vinf_km_s'] if screened else None,
            transfer_burden_km_s=row['transfer_burden_km_s'] if screened else None,
            capability_status='AVAILABLE' if can_explore else 'UNAVAILABLE',
            qualification_state=('ACCESS_UNKNOWN' if not screened else
                                 'PRELIMINARY_COMPARABLE' if can_explore else 'CAPABILITY_UNAVAILABLE'),
            public_authority_refs=('BUILD7_SOLAR_BODY_CATALOG_V1',
                                   'BUILD7_SOLAR_ACCESSIBILITY_SCREEN_V1'),
            accessibility_method_id=row['method_id']))
    return tuple(candidates)


def candidate_digest(candidates: Iterable[MissionCandidate]) -> str:
    payload = [asdict(candidate) for candidate in candidates]
    return sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
