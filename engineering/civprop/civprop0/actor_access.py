"""Dated, scoped Fleet and Australian-government access assertions.

The fixtures admit one firm provider agreement and one government mission path.
They are not trajectories, completed landings, owned lunar transport, or a
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
GOVERNMENT_EVIDENCE_PATH = Path(__file__).with_name('aus_government_access_evidence.json')
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
    raws = (EVIDENCE_PATH.read_bytes(), GOVERNMENT_EVIDENCE_PATH.read_bytes())
    packets = tuple(json.loads(raw) for raw in raws)
    if any(packet['authority_class'] != 'EMPIRICAL_ACTOR_ACCESS_ASSERTION' for packet in packets):
        raise ValueError('invalid evidence authority class')
    return tuple(packet['case'] for packet in packets), hashlib.sha256(b''.join(raws)).hexdigest()


def _date(value: str) -> date:
    return date.fromisoformat(value[:10])


def resolve_actor_capability(actor: str, capability: str, epoch: str,
                             mission_requirements: MissionRequirements | None = None
                             ) -> CapabilityAssessment:
    """Resolve two bounded 2026 access relationships; missing evidence is UNKNOWN.

    USABLE means the named actor has a documented path for *one* mission of
    this service class. It does not mean any requested mission is qualified
    or that the transport has already flown.
    """
    _date(epoch)
    if mission_requirements is not None:
        _date(mission_requirements.departure)
    cases, sha = _evidence()
    case = next((item for item in cases if item['actor_id'] == actor and
                 item['capability'] == capability and
                 _date(epoch) >= _date(item['observed_from']) and _date(epoch).year == 2026), None)
    base = dict(actor_id=actor, capability=capability, epoch=epoch,
                evidence_sha256=sha, actor_possesses_transport=False)
    if case is None:
        return CapabilityAssessment(**base, status='UNKNOWN', evidence_status='UNKNOWN',
                                    evidence_id=None, provider_id=None, access_basis=None,
                                    supported_scope=None, unresolved_requirements=())

    unresolved = []
    if mission_requirements is not None:
        # Both paths are for named payloads. Neither establishes a right to
        # substitute CIVPROP-0's separate synthetic prospecting instrument.
        unresolved = ['mission-specific provider slot and schedule',
                      f'landing site coverage for {mission_requirements.site_id}', 'payload accommodation',
                      'mission-specific price and contract',
                      'operations support for requested payload']
        target_year = case.get('target_landing_year')
        if target_year is not None and _date(mission_requirements.departure).year != target_year:
            unresolved.insert(0, f'documented pathway targets {target_year}, not requested departure')
    return CapabilityAssessment(**base, status='CONDITIONAL' if unresolved else 'USABLE',
                                evidence_status=case['evidence_status'],
                                evidence_id=case['sources'][0]['id'],
                                provider_id=case['provider_id'],
                                access_basis=case['access_basis'],
                                supported_scope=case['scope'],
                                unresolved_requirements=tuple(unresolved))


def execute_with_actor_access(inputs: dict, scenario: Scenario = Scenario(), seed: int = 0) -> dict:
    """Evidence-backed entrypoint; original CIVPROP-0 replay stays frozen."""
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
