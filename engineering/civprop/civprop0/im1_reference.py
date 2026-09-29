"""One completed Intuitive Machines provider precedent, then unchanged Roo-ver screen."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date
import hashlib
import json
from pathlib import Path

from .blue_ghost_1_reference import ObservedSegment, _hours, _instant, _validated_context
from .roover_service import RooVerRequest
from .roover_transport import SolarContext, assess_roover_transport, capture_live_solar_context


FIXTURE = Path(__file__).with_name('im1_reference.json')
SAMPLED_EVENTS = ('launch', 'landing')


def assess_im1(contexts: dict[str, SolarContext]) -> dict:
    """Reuse the completed-mission timing/geometry checks, with IM-1 evidence only."""
    raw = FIXTURE.read_bytes()
    fixture = json.loads(raw)
    if fixture['id'] != 'IM1_CLPS_TO2IM_COMPLETED_PROVIDER_REFERENCE_V1':
        raise ValueError('wrong provider reference fixture')
    sources = {source['id'] for source in fixture['sources']}
    events = {event['id']: event for event in fixture['events']}
    if len(events) != len(fixture['events']) or any(event['source'] not in sources
                                                   for event in events.values()):
        raise ValueError('duplicate event or missing source')
    launch = _instant(events['launch']['epoch_utc'])
    separation = _instant(events['lander_separation']['epoch_utc'])
    landing = _instant(events['landing']['epoch_utc'])
    loi = events['lunar_orbit_insertion']
    end = events['surface_end']
    if (loi['precision'] != 'REPORTED_DATE_ONLY_TIMEZONE_UNSPECIFIED' or
            end['precision'] != 'REPORTED_DATE_ONLY_TIMEZONE_UNSPECIFIED' or
            not launch < separation < landing or
            not separation.date() < date.fromisoformat(loi['reported_calendar_date'])
                < landing.date() < date.fromisoformat(end['reported_calendar_date'])):
        raise ValueError('IM-1 phase evidence is out of order or over-precise')
    geometry = {}
    for name in SAMPLED_EVENTS:
        if name not in contexts:
            raise ValueError(f'missing Solar context for {name}')
        geometry[name] = _validated_context(contexts[name], events[name]['epoch_utc'])
    segments = (
        ObservedSegment('launch', 'OBSERVED_COMPLETE', ('launch', 'lander_separation')),
        ObservedSegment('transfer', 'OBSERVED_COMPLETE', ('lunar_orbit_insertion',)),
        ObservedSegment('lunar_delivery', 'OBSERVED_COMPLETE', ('landing',)),
        ObservedSegment('site_operations', 'OBSERVED_LIMITED', ('landing', 'surface_end')),
    )
    return {
        'reference_id': fixture['id'],
        'fixture_sha256': hashlib.sha256(raw).hexdigest(),
        'authority_class': 'RETROSPECTIVE_PROVIDER_SPECIFIC_COMPLETED_MISSION',
        'provider': fixture['delivery_provider'],
        'lander': fixture['lander'],
        'segments': [asdict(segment) for segment in segments],
        'derived_intervals': {
            'launch_to_approx_separation_hours': _hours(launch, separation),
            'launch_to_landing_hours': _hours(launch, landing),
            'loi_to_landing_hours': None,
            'landing_to_surface_end_hours': None,
            'lien': 'LOI and surface end are date-only; separation minute is approximate',
        },
        'solar_geometry': geometry,
        'does_not_establish': fixture['limits'],
    }


def rerun_roover(context: SolarContext) -> dict:
    """Use the promoted Roo-ver assessor unchanged; IM-1 is not its input."""
    return asdict(assess_roover_transport(RooVerRequest(required_surface_days=14), context))


def main() -> None:
    fixture = json.loads(FIXTURE.read_text())
    events = {event['id']: event for event in fixture['events']}
    contexts = {name: capture_live_solar_context(epoch_utc=events[name]['epoch_utc'])
                for name in SAMPLED_EVENTS}
    result = {
        'im1_reference': assess_im1(contexts),
        'roover_rerun': rerun_roover(capture_live_solar_context()),
        'boundary': 'IM-1 observed outcomes are not passed to the IM-5/Roo-ver assessor',
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
