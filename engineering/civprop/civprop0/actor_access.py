"""AUS-CAP-0: one dated, scoped actor/provider access assertion.

The fixture is an admitted empirical claim about a provider agreement.
It is not a trajectory, completed landing, country-owned capability, or a
general capability database. CIVPROP-0's original replay path stays frozen.
"""
from dataclasses import asdict, dataclass, replace
from datetime import date
import hashlib
import json
from pathlib import Path

from .experiment import canonical, execute, load_inputs
from .model import Scenario


EVIDENCE_PATH = Path(__file__).with_name('actor_access_evidence.json')
CAPABILITY = 'LUNAR_PAYLOAD_DELIVERY_ACCESS'


@dataclass(frozen=True)
class MissionRequirements:
    departure: str
    site_id: str


@dataclass(frozen=True)
class CapabilityAssessment:
    actor_id: str
    capability: str
    epoch: str
    status: str
    evidence_status: str
    evidence_id: str | None
    evidence_sha256: str
    provider_id: str | None
    access_basis: str | None
    actor_possesses_transport: bool
    supported_scope: str | None
    unresolved_requirements: tuple[str, ...]
    authority_class: str = 'EMPIRICAL_ACCESS_ASSESSMENT'


def _evidence():
    raw = EVIDENCE_PATH.read_bytes()
    packet = json.loads(raw)
    if packet['authority_class'] != 'EMPIRICAL_ACTOR_ACCESS_ASSERTION':
        raise ValueError('invalid evidence authority class')
    return packet, hashlib.sha256(raw).hexdigest()


def _date(value: str) -> date:
    return date.fromisoformat(value[:10])


def resolve_actor_capability(actor: str, capability: str, epoch: str,
                             mission_requirements: MissionRequirements | None = None
                             ) -> CapabilityAssessment:
    """Resolve only Fleet's dated SPIDER agreement; missing evidence is UNKNOWN.

    USABLE means the named actor has a documented access agreement for *one*
    mission of this service class. It does not mean any requested mission is
    qualified or that the transport has already flown.
    """
    _date(epoch)
    if mission_requirements is not None:
        _date(mission_requirements.departure)
    packet, sha = _evidence()
    case = packet['case']
    base = dict(actor_id=actor, capability=capability, epoch=epoch,
                evidence_sha256=sha, actor_possesses_transport=False)
    if (actor != case['actor_id'] or capability != case['capability'] or
            _date(epoch) < _date(case['observed_from']) or _date(epoch).year != 2026):
        return CapabilityAssessment(**base, status='UNKNOWN', evidence_status='UNKNOWN',
                                    evidence_id=None, provider_id=None, access_basis=None,
                                    supported_scope=None, unresolved_requirements=())

    unresolved = []
    if mission_requirements is not None:
        # The public agreement concerns SPIDER on a named far-side mission.
        # None of these terms are established for CIVPROP-0's separate polar
        # instrument, date and site. A supplied mass is not a provider limit.
        unresolved = ['mission-specific provider slot and schedule',
                      f'landing site coverage for {mission_requirements.site_id}', 'payload accommodation',
                      'mission-specific price and contract',
                      'operations support for requested payload']
    return CapabilityAssessment(**base, status='CONDITIONAL' if unresolved else 'USABLE',
                                evidence_status=case['evidence_status'],
                                evidence_id=case['sources'][0]['id'],
                                provider_id=case['provider_id'],
                                access_basis=case['access_basis'],
                                supported_scope=case['scope'],
                                unresolved_requirements=tuple(unresolved))


def execute_with_actor_access(inputs: dict, scenario: Scenario = Scenario(), seed: int = 0) -> dict:
    """Versioned evidence-backed entrypoint; old CIVPROP-0 artifacts stay valid.

    The pinned Earth actor is AUS. Fleet's agreement cannot be assigned to
    that actor, so its access status is UNKNOWN and transport is not cleared.
    """
    actor = inputs['records']['earth_actor'][0]['iso3']
    requirements = MissionRequirements(scenario.departure, scenario.site_id)
    assessment = resolve_actor_capability(actor, CAPABILITY, scenario.departure, requirements)
    technology = True if assessment.status == 'USABLE' else (False if assessment.status == 'UNUSABLE' else None)
    run = execute(inputs, replace(scenario, technology=technology), seed)
    return {'version': 'AUS_CAP_0_ADAPTER_V1',
            'requested_scenario': asdict(scenario),
            'assessment': asdict(assessment), 'run': run,
            'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def replay_with_actor_access(artifact: dict) -> dict:
    if artifact.get('adapter_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise ValueError('replay requires the pinned access adapter')
    actual = execute_with_actor_access(artifact['run']['inputs'],
                                       Scenario(**artifact['requested_scenario']),
                                       artifact['run']['seed'])
    if canonical(actual) != canonical(artifact):
        raise ValueError('re-executed access assessment or causal trace differs')
    return actual


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args()
    artifact = (replay_with_actor_access(json.loads(args.replay.read_text())) if args.replay
                else execute_with_actor_access(load_inputs(), seed=args.seed))
    if args.output:
        args.output.write_text(json.dumps(artifact, sort_keys=True, indent=2) + '\n')
    print(canonical({'run_id': artifact['run']['run_id'],
                     'access': artifact['assessment']['status'],
                     'transport': artifact['run']['opportunity']['status'],
                     'decision': artifact['run']['decisions'][0]['action']}))


if __name__ == '__main__':
    main()
