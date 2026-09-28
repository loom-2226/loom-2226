"""Retrospective Blue Ghost 1 CLPS reference; never a Roo-ver route model."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

from .roover_transport import SolarContext, capture_live_solar_context


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / 'blue_ghost_1_reference.json'
SAMPLED_EVENTS = ('launch', 'lunar_orbit_insertion_burn_start', 'landing')


@dataclass(frozen=True)
class ObservedSegment:
    name: str
    observed_outcome: str
    supporting_events: tuple[str, ...]
    prospective_feasibility: str = 'NOT_ASSESSED'


def _instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('event epoch must include a timezone')
    return result.astimezone(timezone.utc)


def _hours(start: datetime, end: datetime) -> float:
    if end <= start:
        raise ValueError('mission milestones are out of order')
    return (end - start).total_seconds() / 3600


def _validated_context(context: SolarContext, epoch: str) -> dict:
    if context.reference_epoch_utc != epoch:
        raise ValueError('Solar context does not match the observed event epoch')
    a, b = context.earth, context.moon
    if (a.entity_id, b.entity_id) != ('EARTH', 'MOON'):
        raise ValueError('reference requires Earth and Moon states')
    for state in (a, b):
        if (state.epoch_utc != epoch or state.reference_frame != 'J2000/ECLIPTIC' or
                state.navigation_grade is not True or
                state.provenance.get('ephemeris_source_id') != 'DE440' or
                state.provenance.get('units') != 'km,km/s'):
            raise ValueError('reference requires qualified DE440 state at event epoch')
    return {
        'reference_epoch_utc': epoch,
        'earth_moon_distance_km': math.dist(a.position_km, b.position_km),
        'earth_moon_relative_speed_km_s': math.dist(a.velocity_km_s, b.velocity_km_s),
        'earth': asdict(a), 'moon': asdict(b),
        'registry_sha256': context.registry_sha256,
        'manifest_sha256': context.manifest_sha256,
        'meaning': 'simultaneous body geometry only; not spacecraft position, path, delta-v or flight speed',
    }


def assess_blue_ghost_1(contexts: dict[str, SolarContext]) -> dict:
    """Calculate only reported-event intervals and contemporaneous geometry."""
    raw = FIXTURE.read_bytes()
    fixture = json.loads(raw)
    if fixture['id'] != 'BLUE_GHOST_1_CLPS_TO19D_COMPLETED_REFERENCE_V1':
        raise ValueError('wrong completed-mission fixture')
    source_ids = {source['id'] for source in fixture['sources']}
    events = {item['id']: item for item in fixture['events']}
    if len(events) != len(fixture['events']) or any(event['source'] not in source_ids
                                                   for event in events.values()):
        raise ValueError('duplicate event or missing primary source')
    for event_id in SAMPLED_EVENTS:
        if event_id not in contexts:
            raise ValueError(f'missing Solar context for {event_id}')
    launch = _instant(events['launch']['epoch_utc'])
    separation = _instant(events['lander_separation']['epoch_utc'])
    loi = _instant(events['lunar_orbit_insertion_burn_start']['epoch_utc'])
    landing = _instant(events['landing']['epoch_utc'])
    last_data = _instant(events['last_data']['epoch_utc'])
    if not launch < separation < loi < landing < last_data:
        raise ValueError('observed mission phases are not chronological')
    if events['trans_lunar_injection']['precision'] != 'REPORTED_DATE_ONLY_TIMEZONE_UNSPECIFIED':
        raise ValueError('TLI precision must remain date-only')
    tli_day = datetime.fromisoformat(events['trans_lunar_injection']['reported_calendar_date']).date()
    if not separation.date() < tli_day < loi.date():
        raise ValueError('TLI date is outside launch-to-LOI interval')
    # The provider supplies no TLI clock time or time zone. Its calendar date
    # supports ordering but cannot support an elapsed-hour calculation.
    geometry = {event_id: _validated_context(contexts[event_id],
                events[event_id]['epoch_utc']) for event_id in SAMPLED_EVENTS}
    segments = (
        ObservedSegment('launch', 'OBSERVED_COMPLETE', ('launch', 'lander_separation')),
        ObservedSegment('transfer', 'OBSERVED_COMPLETE',
                        ('trans_lunar_injection', 'lunar_orbit_insertion_burn_start')),
        ObservedSegment('lunar_delivery', 'OBSERVED_COMPLETE', ('landing',)),
        ObservedSegment('site_operations', 'OBSERVED_COMPLETE', ('landing', 'last_data')),
    )
    return {
        'reference_id': fixture['id'],
        'fixture_sha256': hashlib.sha256(raw).hexdigest(),
        'authority_class': 'RETROSPECTIVE_COMPLETED_MISSION_CALCULATION',
        'segments': [asdict(segment) for segment in segments],
        'derived_intervals': {
            'launch_to_orbit_separation_hours': _hours(launch, separation),
            'launch_to_loi_burn_start_hours': _hours(launch, loi),
            'tli_to_loi_burn_start_hours': None,
            'tli_duration_lien': 'TLI has only a reported calendar date with unspecified time zone',
            'loi_burn_start_to_landing_hours': _hours(loi, landing),
            'launch_to_landing_hours': _hours(launch, landing),
            'landing_to_approx_last_data_hours': _hours(landing, last_data),
            'last_data_precision': 'APPROX_REPORTED_MINUTE',
        },
        'source_reported_approximate_phase_days': fixture['source_reported_approximate_phase_days'],
        'solar_geometry': geometry,
        'does_not_establish': fixture['transport_quantities_not_admitted'],
    }


def main() -> None:
    fixture = json.loads(FIXTURE.read_text())
    events = {event['id']: event for event in fixture['events']}
    contexts = {name: capture_live_solar_context(epoch_utc=events[name]['epoch_utc'])
                for name in SAMPLED_EVENTS}
    print(json.dumps(assess_blue_ghost_1(contexts), indent=2, sort_keys=True,
                     allow_nan=False))


if __name__ == '__main__':
    main()
