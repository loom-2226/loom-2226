"""AUS-ACCESS-1: government ownership and narrow Roo-ver scope."""
import unittest
from unittest.mock import patch

from . import actor_access
from .actor_access import (MissionRequirements, resolve_actor_capability,
                           execute_with_actor_access, replay_with_actor_access)
from .experiment import load_inputs


class GovernmentAccessTests(unittest.TestCase):
    def test_fleet_only_evidence_never_grants_country_access(self):
        fleet_case = actor_access._evidence()[0][0]
        with patch.object(actor_access, '_evidence', return_value=((fleet_case,), 'fleet-only')):
            result = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS',
                                              '2026-09-28')
        self.assertEqual(result.status, 'UNKNOWN')

    def test_aus_has_named_government_mission_path(self):
        result = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-09-28')
        self.assertEqual(result.status, 'USABLE')
        self.assertEqual(result.evidence_status, 'OBSERVED_ACCESS')
        self.assertEqual(result.provider_id, 'INTUITIVE_MACHINES')
        self.assertEqual(result.access_basis, 'GOVERNMENT_MISSION_PARTNERSHIP_VIA_NASA_CLPS')
        self.assertIn('Roo-ver', result.supported_scope)

    def test_aus_exact_civprop_mission_is_conditional(self):
        result = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS',
                                          '2026-09-28', MissionRequirements(
                                              '2026-09-28T00:00:00Z',
                                              'SCENARIO:MOON_POLAR_PSR:SITE_0'))
        self.assertEqual(result.status, 'CONDITIONAL')
        self.assertIn('documented pathway targets 2030, not requested departure',
                      result.unresolved_requirements)
        self.assertIn('payload accommodation', result.unresolved_requirements)

    def test_no_clps_award_before_publication(self):
        result = resolve_actor_capability('AUS', 'LUNAR_PAYLOAD_DELIVERY_ACCESS', '2026-03-26')
        self.assertEqual(result.status, 'UNKNOWN')

    def test_civprop_waits_and_replays(self):
        artifact = execute_with_actor_access(load_inputs(), seed=0)
        self.assertEqual(artifact['assessment']['status'], 'CONDITIONAL')
        self.assertEqual(artifact['run']['opportunity']['status'], 'UNKNOWN')
        self.assertEqual(artifact['run']['decisions'][0]['action'], 'WAIT')
        self.assertEqual(artifact['run']['transactions'], [])
        self.assertEqual(replay_with_actor_access(artifact), artifact)


if __name__ == '__main__':
    unittest.main()
