"""One named Roo-ver service-envelope check, not transport physics.

The result qualifies participation and published targets. It never returns a
trajectory or upgrades planned service to executed mission feasibility.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

from .actor_access import CAPABILITY, resolve_actor_capability


ENVELOPE_PATH = Path(__file__).with_name('roover_service_envelope.json')


@dataclass(frozen=True)
class RooVerRequest:
    actor_id: str = 'AUS'
    mission_id: str = 'ROO_VER_CLPS_CT4_IM5'
    payload_id: str = 'ROO_VER_WITH_NASA_MNP'
    landing_year: int = 2030
    destination_scope: str = 'LUNAR_SOUTH_POLE_REGION'
    exact_site_id: str | None = None
    launch_utc: str | None = None
    payload_mass_kg: float | None = None
    required_surface_days: float | None = None


@dataclass(frozen=True)
class RooVerServiceAssessment:
    status: str
    actor_access_status: str
    transport_feasibility: str
    matched: tuple[str, ...]
    unresolved: tuple[str, ...]
    quantities: dict
    evidence_id: str
    evidence_sha256: str
    authority_class: str = 'EMPIRICAL_SERVICE_SCOPE_ASSESSMENT'


def _envelope():
    raw = ENVELOPE_PATH.read_bytes()
    value = json.loads(raw)
    if value['authority_class'] != 'EMPIRICAL_MISSION_ENVELOPE_WITH_PLANNED_TARGETS':
        raise ValueError('invalid service-envelope authority class')
    return value, hashlib.sha256(raw).hexdigest()


def assess_roover_service(request: RooVerRequest) -> RooVerServiceAssessment:
    """Match one requested mission to the published CT-4/IM-5 envelope.

    CONDITIONAL means the named mission is manifested and broadly in scope;
    exact execution remains unqualified. OUT_OF_SCOPE applies only to this
    named path and says nothing about other providers or missions.
    """
    for value in (request.payload_mass_kg, request.required_surface_days):
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError('mass and duration must be finite nonnegative quantities')
    e, sha = _envelope()
    quantities = {key: e[key] for key in ('rover_mass_kg_approx',
                  'manifested_suite_mass_kg_approx', 'surface_operations_days_expected',
                  'delivery_capacity_kg', 'delta_v_km_s', 'transfer_duration_days',
                  'launch_vehicle', 'target_launch_period')}
    access = resolve_actor_capability(request.actor_id, CAPABILITY, e['as_of'])
    base = dict(actor_access_status=access.status, transport_feasibility='UNKNOWN',
                quantities=quantities, evidence_id=e['id'], evidence_sha256=sha)
    if request.actor_id != e['actor_id'] or access.status != 'USABLE':
        return RooVerServiceAssessment('UNKNOWN', **base, matched=(),
                                       unresolved=('no matching actor-owned Roo-ver access',))
    mismatches = tuple(name for name, actual, expected in (
        ('mission identity', request.mission_id, e['mission_id']),
        ('payload identity', request.payload_id, e['payload_id']),
        ('landing target year', request.landing_year, e['target_landing_year']),
        ('destination region', request.destination_scope, e['destination_scope'])
    ) if actual != expected)
    if mismatches:
        return RooVerServiceAssessment('OUT_OF_SCOPE', **base, matched=(),
                                       unresolved=mismatches)
    matched = (e['service_path'], 'named Roo-ver with NASA MNP is manifested',
               '2030 target and South Pole region match',
               'NASA buys delivery; Intuitive Machines delivers; ELO2 operates rover')
    unresolved = ['exact launch window', 'final landing coordinates',
                  'final rover and deployer mass acceptance',
                  'rover-specific deployment, power, data and operations terms',
                  'launch vehicle, transfer duration and delta-v',
                  'surface operations duration guarantee']
    if request.exact_site_id is not None:
        unresolved.append('exact landing site match')
    if request.launch_utc is not None:
        unresolved.append('requested departure slot')
    if request.payload_mass_kg is not None:
        unresolved.append('requested payload mass acceptance')
    if request.required_surface_days is not None:
        unresolved.append('requested surface duration guarantee')
    return RooVerServiceAssessment('CONDITIONAL', **base, matched=matched,
                                   unresolved=tuple(unresolved))


def main():
    result = assess_roover_service(RooVerRequest())
    print(json.dumps(asdict(result), sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
