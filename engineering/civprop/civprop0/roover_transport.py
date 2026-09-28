"""One Roo-ver transport screen using live Solar states and a named service path.

FEASIBLE means the requested *segment scope* is supported by the admitted
service evidence. It is not a prediction of mission success or a trajectory.
INFEASIBLE is limited to a known conflict with this named service envelope.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import subprocess

from src.loom_spatial_state_authority import CANONICAL_FRAME, SpatialState
from src.loom_spice_ephemeris_adapter import (
    BodyIdentifier, EphemerisCoverage, EphemerisSource, KernelAsset,
    SolarBody, SolarEphemerisRegistry, SpiceEphemerisAdapter,
)

from .roover_service import RooVerRequest, _envelope, assess_roover_service


ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = Path('/home/ubuntu/loom_solar_assets')
REFERENCE_EPOCH = '2030-07-01T00:00:00Z'  # Scenario sample, not a booked launch or arrival.
SEGMENT_NAMES = ('launch', 'transfer', 'lunar_delivery', 'site_operations')


@dataclass(frozen=True)
class SolarContext:
    reference_epoch_utc: str
    earth: SpatialState
    moon: SpatialState
    registry_sha256: str
    manifest_sha256: str


@dataclass(frozen=True)
class Segment:
    name: str
    status: str
    basis: str
    unresolved: tuple[str, ...] = ()


@dataclass(frozen=True)
class TransportAssessment:
    mission_id: str
    status: str
    segments: tuple[Segment, ...]
    service_evidence_id: str
    service_evidence_sha256: str
    actor_access_status: str
    documented_rover_mass_kg_approx: float
    documented_manifested_suite_mass_kg_approx: float
    documented_surface_plan_max_days: float
    reference_epoch_utc: str
    reference_epoch_role: str
    earth_moon_distance_km: float | None
    earth_moon_relative_speed_km_s: float | None
    solar_context: SolarContext
    authority_class: str = 'BOUNDED_MISSION_TRANSPORT_SCREEN'


def _typed(cls, row):
    from dataclasses import fields
    names = {field.name for field in fields(cls)}
    return cls(**{key: value for key, value in row.items() if key in names})


def capture_live_solar_context(database: str = 'loom_dev',
                               asset_root: Path = ASSET_ROOT,
                               epoch_utc: str = REFERENCE_EPOCH) -> SolarContext:
    """Read registry metadata in one read-only transaction; resolve fresh states.

    The date is a context sample in the reported mid-2030 target. It is never
    passed to a transfer solver or interpreted as a scheduled mission epoch.
    """
    queries = {
        'bodies': "SELECT * FROM loom_solar.body WHERE body_id IN ('EARTH','MOON') ORDER BY body_id",
        'identifiers': "SELECT * FROM loom_solar.body_identifier WHERE body_id IN ('EARTH','MOON') AND authority='NAIF' AND status='ACTIVE' ORDER BY body_id",
        'sources': "SELECT * FROM loom_solar.ephemeris_source WHERE ephemeris_source_id='DE440'",
        'coverage': "SELECT * FROM loom_solar.ephemeris_coverage WHERE body_id IN ('EARTH','MOON') AND ephemeris_source_id='DE440' ORDER BY body_id",
    }
    sql = 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n'
    sql += '\n'.join(
        f"SELECT json_build_object('key','{key}','rows',COALESCE(json_agg(t),'[]'))::jsonb::text FROM ({query}) t;"
        for key, query in queries.items()
    )
    sql += '\nCOMMIT;'
    output = subprocess.check_output(
        ['psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-d', database, '-c', sql], text=True,
    )
    records = {item['key']: item['rows'] for item in map(json.loads, output.splitlines())}
    if len(records['bodies']) != 2 or len(records['identifiers']) != 2 or len(records['sources']) != 1:
        raise ValueError('live Solar Earth/Moon DE440 registry is incomplete')

    manifest_raw = (ROOT / 'manifests/solar/SOLAR_PHASE4B_AUTHORITY_V1.json').read_bytes()
    manifest = json.loads(manifest_raw)
    expected = next(source for source in manifest['registry']['sources']
                    if source['ephemeris_source_id'] == 'DE440')
    source = records['sources'][0]
    if source['sha256'] != expected['sha256'] or source['status'] != 'QUALIFIED':
        raise ValueError('live DE440 source does not match promoted Solar manifest')
    assets = tuple(KernelAsset(asset_root / asset['local_path'], asset['sha256'], asset['byte_count'])
                   for asset in manifest['assets'] if asset['asset_id'] in ('LSK', 'DE440'))
    registry = SolarEphemerisRegistry(
        [_typed(SolarBody, row) for row in records['bodies']],
        [_typed(BodyIdentifier, row) for row in records['identifiers']],
        [_typed(EphemerisSource, {**source, 'kernel_assets': assets})],
        [_typed(EphemerisCoverage, row) for row in records['coverage']],
    )
    service = SpiceEphemerisAdapter(registry).service()
    earth, moon = (service.resolve(body, epoch_utc) for body in ('EARTH', 'MOON'))
    registry_hash = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
    return SolarContext(epoch_utc, earth, moon, registry_hash,
                        hashlib.sha256(manifest_raw).hexdigest())


def assess_roover_transport(request: RooVerRequest, context: SolarContext) -> TransportAssessment:
    """Screen the named mission; unknown quantitative limits never become zero."""
    envelope, envelope_hash = _envelope()
    service = assess_roover_service(request)
    nominal = (request.mission_id == envelope['mission_id'] and
               request.payload_id == envelope['payload_id'])
    landing_year_matches = request.landing_year == envelope['target_landing_year']
    region_matches = request.destination_scope == envelope['destination_scope']
    solar_valid = (context.earth.entity_id == 'EARTH' and context.moon.entity_id == 'MOON' and
                   context.earth.epoch_utc == context.moon.epoch_utc == context.reference_epoch_utc and
                   all(state.reference_frame == CANONICAL_FRAME and state.navigation_grade is True and
                       state.provenance.get('units') == 'km,km/s' and
                       state.provenance.get('ephemeris_source_id') == 'DE440' and
                       state.provenance.get('state_source') == 'LOCAL_SPICE'
                       for state in (context.earth, context.moon)))
    distance = speed = None
    if solar_valid:
        distance = math.dist(context.earth.position_km, context.moon.position_km)
        speed = math.dist(context.earth.velocity_km_s, context.moon.velocity_km_s)

    launch = Segment('launch', 'UNKNOWN',
                     'Initial mid-2030 target; no booked launch epoch, vehicle or mass allocation.',
                     ('launch date/window', 'launch vehicle', 'payload integration and mass margin'))
    transfer = Segment('transfer', 'UNKNOWN',
                       'Qualified Earth/Moon states provide geometry context only.' if solar_valid else
                       'Qualified Earth/Moon context is unavailable.',
                       ('departure and arrival epochs', 'trajectory and propulsion performance',
                        'transfer duration and delta-v'))
    if not region_matches:
        delivery = Segment('lunar_delivery', 'INFEASIBLE',
                           'Requested destination is outside the contracted South Pole regional service scope.',
                           ('Another service path would need separate assessment.',))
    elif not nominal or not landing_year_matches or service.actor_access_status != 'USABLE':
        delivery = Segment('lunar_delivery', 'UNKNOWN',
                           'Requested actor, payload or year is not qualified by the named Roo-ver service evidence.',
                           ('Matching mission-specific access and schedule evidence',))
    elif request.exact_site_id is not None or request.payload_mass_kg is not None:
        delivery = Segment('lunar_delivery', 'UNKNOWN',
                           'The named rover is manifested for a South Pole regional delivery, but an exact site or flight-mass requirement is unqualified.',
                           ('final landing coordinates', 'final accepted flight mass and delivery margin'))
    else:
        delivery = Segment('lunar_delivery', 'FEASIBLE',
                           'NASA awarded Intuitive Machines end-to-end delivery of the named Roo-ver/MNP payload to the South Pole region; this is a planned service-scope result, not demonstrated flight success.',
                           ('final landing coordinates', 'flight performance and landing outcome'))

    planned_max = envelope['surface_operations_days_planned_max']
    if request.required_surface_days is not None and request.required_surface_days > planned_max:
        operations = Segment('site_operations', 'INFEASIBLE',
                             'Requested duration exceeds the Agency-described up-to-14-day Roo-ver plan; this is a plan limit, not a physical limit.',
                             ('A revised operations plan would require new evidence.',))
    else:
        operations = Segment('site_operations', 'UNKNOWN',
                             'ELO2 is the planned rover operator, but deployment, site conditions and duration are not guaranteed.',
                             ('final site and terrain', 'deployment, power and data terms',
                              'operational duration assurance'))
    segments = (launch, transfer, delivery, operations)
    status = ('INFEASIBLE' if any(item.status == 'INFEASIBLE' for item in segments) else
              'FEASIBLE' if all(item.status == 'FEASIBLE' for item in segments) else 'UNKNOWN')
    return TransportAssessment(request.mission_id, status, segments, envelope['id'], envelope_hash,
                               service.actor_access_status, envelope['rover_mass_kg_approx'],
                               envelope['manifested_suite_mass_kg_approx'], planned_max,
                               context.reference_epoch_utc,
                               'MID_2030_GEOMETRY_SAMPLE_NOT_MISSION_EPOCH', distance, speed, context)


def main() -> None:
    request = RooVerRequest(required_surface_days=14)
    result = assess_roover_transport(request, capture_live_solar_context())
    print(json.dumps({'request': asdict(request), 'assessment': asdict(result)},
                     indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
