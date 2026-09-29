"""CIVPROP-0E: one evidence-backed readiness gate and unchanged replay harness.

The CIVPROP-0 run remains its synthetic 2026 mission. The Roo-ver assessment
tests the same actor decision gate; it is not substituted for that mission.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import unittest

from src.loom_spatial_state_authority import SpatialState

from .actor import prospect
from .actor_access import (CAPABILITY, execute_with_actor_access,
                           replay_with_actor_access, resolve_actor_capability)
from .experiment import canonical, load_inputs
from .model import Economics, KnowledgeState, Scenario
from .roover_service import RooVerRequest, assess_roover_service
from .roover_transport import SolarContext, assess_roover_transport


HERE = Path(__file__).resolve().parent
SOLAR_SNAPSHOT = HERE / 'runs/roover_transport_mid2030_v1.json'
PROBE_ARTIFACT = HERE / 'runs/civprop0e_readiness_v1.json'


def _solar_context() -> SolarContext:
    # Re-evaluate the promoted assessment against its pinned, disposable state
    # snapshot. No fresh transport research or live database is needed here.
    record = json.loads(SOLAR_SNAPSHOT.read_text())['assessment']['solar_context']
    return SolarContext(record['reference_epoch_utc'], SpatialState(**record['earth']),
                        SpatialState(**record['moon']), record['registry_sha256'],
                        record['manifest_sha256'])


def readiness_probe(seed: int = 0) -> dict:
    inputs = load_inputs()
    scenario = Scenario()
    actor = inputs['records']['earth_actor'][0]['iso3']
    request = RooVerRequest(actor_id=actor, required_surface_days=14)
    access = resolve_actor_capability(actor, CAPABILITY, scenario.departure)
    service = assess_roover_service(request)
    transport = assess_roover_transport(request, _solar_context())

    # This is the existing CIVPROP decision function with the actual Roo-ver
    # transport status. Scenario credits remain a test fixture, not a Roo-ver
    # mission price or Australian public expenditure.
    knowledge = KnowledgeState(scenario.site_id, scenario.prior,
                               scenario.prior_version, scenario.departure)
    economics = Economics(scenario.mission_cost, scenario.continuation_cost,
                          scenario.success_value, scenario.threshold,
                          scenario.sensitivity, scenario.false_positive)
    decision = prospect(knowledge, economics, scenario.capital, transport.status)

    # The original synthetic 2026 run demonstrates the same UNKNOWN gate with
    # its own mission identity and append-only accounting. It is not Roo-ver.
    reference = execute_with_actor_access(inputs, scenario, seed)
    run = reference['run']
    if (run['opportunity']['status'] != transport.status or
            run['decisions'][0] != asdict(decision)):
        raise ValueError('CIVPROP-0 reference gate diverges from readiness decision')
    result = {
        'version': 'CIVPROP0E_READINESS_PROBE_V1',
        'actor_access': {'status': access.status, 'evidence_id': access.evidence_id,
                         'evidence_sha256': access.evidence_sha256},
        'service_scope': {'status': service.status, 'evidence_id': service.evidence_id,
                          'evidence_sha256': service.evidence_sha256,
                          'unresolved': service.unresolved},
        'transport': {'status': transport.status,
                      'segments': [(segment.name, segment.status) for segment in transport.segments],
                      'unresolved': {segment.name: segment.unresolved
                                     for segment in transport.segments if segment.unresolved},
                      'evidence_sha256': transport.service_evidence_sha256,
                      'solar_registry_sha256': transport.solar_context.registry_sha256},
        'decision': asdict(decision),
        'civprop0_reference': {
            'scope': 'SYNTHETIC_2026_HARNESS_NOT_ROO_VER_EXECUTION',
            'run_id': run['run_id'], 'seed': seed,
            'mission_access_status': reference['assessment']['status'],
            'opportunity_status': run['opportunity']['status'],
            'action': run['decisions'][0]['action'],
            'starting_capital': scenario.capital,
            'ending_capital': run['ending_capital'],
            'transactions': run['transactions'],
            'mission': run['mission'],
            'event_types': [event['event_type'] for event in run['events']],
            'replay_verified': replay_with_actor_access(reference) == reference,
        },
        'source_snapshot_sha256': hashlib.sha256(SOLAR_SNAPSHOT.read_bytes()).hexdigest(),
        'precedent_use': 'Blue Ghost 1 and IM-1 are observed references only; neither is a transport qualifier for IM-5',
    }
    return json.loads(canonical(result))


class ReadinessIntegrationTests(unittest.TestCase):
    def test_readiness_chain_and_wait_accounting(self):
        result = readiness_probe()
        self.assertEqual(result['actor_access']['status'], 'USABLE')
        self.assertEqual(result['service_scope']['status'], 'CONDITIONAL')
        self.assertEqual(result['transport']['status'], 'UNKNOWN')
        self.assertEqual(result['decision']['action'], 'WAIT')
        run = result['civprop0_reference']
        self.assertEqual(run['action'], 'WAIT')
        self.assertEqual(run['opportunity_status'], 'UNKNOWN')
        self.assertEqual(run['starting_capital'], run['ending_capital'])
        self.assertEqual(run['transactions'], [])
        self.assertIsNone(run['mission'])
        self.assertTrue(run['replay_verified'])

    def test_unknown_is_not_infeasible_or_provider_success(self):
        result = readiness_probe()
        self.assertNotEqual(result['transport']['status'], 'INFEASIBLE')
        self.assertEqual(dict(result['transport']['segments'])['transfer'], 'UNKNOWN')
        self.assertIn('IM-5', result['precedent_use'])
        self.assertIn('exact launch window', result['service_scope']['unresolved'])

    def test_pinned_probe_replays(self):
        self.assertEqual(readiness_probe(), json.loads(PROBE_ARTIFACT.read_text()))
        self.assertEqual(readiness_probe(), readiness_probe())


if __name__ == '__main__':
    print(json.dumps(readiness_probe(), sort_keys=True, indent=2, allow_nan=False))
