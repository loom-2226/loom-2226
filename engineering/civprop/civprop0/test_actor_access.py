"""AUS-CAP-0: bounded service-access qualification and CIVPROP-0 seam."""
import json
import unittest

from .actor_access import (MissionRequirements, resolve_actor_capability,
                           execute_with_actor_access, replay_with_actor_access)
from .experiment import load_inputs
from .model import Scenario
from .transport import assess_mission


class ActorAccessTests(unittest.TestCase):
    def test_fleet_has_documented_service_path(self):
        a = resolve_actor_capability('FLEET_SPACE_TECHNOLOGIES',
                                     'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-09-28')
        self.assertEqual(a.status, 'USABLE')
        self.assertEqual(a.access_basis, 'PROVIDER_AGREEMENT')
        self.assertEqual(a.provider_id, 'FIREFLY_AEROSPACE')
        self.assertEqual(a.evidence_status, 'OBSERVED_ACCESS')
        self.assertFalse(a.actor_possesses_transport)

    def test_exact_fleet_mission_is_conditional(self):
        a = resolve_actor_capability('FLEET_SPACE_TECHNOLOGIES',
                                     'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-09-28',
                                     MissionRequirements('2026-09-28T00:00:00Z',
                                                         'SCENARIO:MOON_POLAR_PSR:SITE_0'))
        self.assertEqual(a.status, 'CONDITIONAL')
        self.assertIn('mission-specific provider slot and schedule', a.unresolved_requirements)
        self.assertIn('landing site coverage for SCENARIO:MOON_POLAR_PSR:SITE_0',
                      a.unresolved_requirements)

    def test_country_actor_does_not_inherit_firm_contract(self):
        a = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-09-28')
        self.assertEqual(a.status, 'UNKNOWN')
        self.assertIsNone(a.provider_id)

    def test_missing_evidence_is_unknown_not_unusable(self):
        for actor, capability in [('ZZZ', 'LUNAR_PAYLOAD_DELIVERY_ACCESS'),
                                  ('AUS', 'SOVEREIGN_LUNAR_TRANSPORT')]:
            self.assertEqual(resolve_actor_capability(actor, capability, '2026-09-28').status,
                             'UNKNOWN')

    def test_milestone_does_not_grant_access(self):
        a = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2040-01-01')
        self.assertEqual(a.status, 'UNKNOWN')

    def test_no_anachronistic_access(self):
        a = resolve_actor_capability('FLEET_SPACE_TECHNOLOGIES',
                                     'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2023-01-01')
        self.assertEqual(a.status, 'UNKNOWN')

    def test_country_experiment_waits_without_transport_claim(self):
        artifact = execute_with_actor_access(load_inputs(), Scenario(), 0)
        self.assertEqual(artifact['assessment']['status'], 'UNKNOWN')
        self.assertEqual(artifact['run']['opportunity']['status'], 'UNKNOWN')
        self.assertEqual(artifact['run']['decisions'][0]['action'], 'WAIT')
        self.assertEqual(artifact['run']['transactions'], [])
        self.assertIsNone(artifact['run']['scenario']['technology'])

    def test_access_replay_is_deterministic_and_tamper_aware(self):
        artifact = execute_with_actor_access(load_inputs(), Scenario(), 2)
        self.assertEqual(replay_with_actor_access(json.loads(json.dumps(artifact))), artifact)
        self.assertEqual(execute_with_actor_access(load_inputs(), Scenario(), 2), artifact)
        artifact['assessment']['status'] = 'USABLE'
        with self.assertRaises(ValueError):
            replay_with_actor_access(artifact)

    def test_capability_is_not_transport_feasibility(self):
        a = resolve_actor_capability('FLEET_SPACE_TECHNOLOGIES',
                                     'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-09-28')
        self.assertEqual(a.status, 'USABLE')
        self.assertEqual(assess_mission(load_inputs(), Scenario(technology=None)).status,
                         'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
