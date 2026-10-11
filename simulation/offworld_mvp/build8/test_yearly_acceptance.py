"""Strict frozen yearly acceptance: do not silently normalize knowledge order."""
import json
import unittest
from .screened_yearly import run_yearly
from .baselines.pre_cast_migration.capture import normalize
from .test_yearly_match_rule import BASELINES, differences

OPTIONS = {'screen_default': {},
           'screen_sub': {'subcontract': True, 'capacity_slots': 1},
           'screen_sub_failure': {'subcontract': True, 'capacity_slots': 1,
                                  'sub_failure': True, 'resource_on_failure': True}}

class FrozenYearlyAcceptance(unittest.TestCase):
    def test_all_three_frozen_replays(self):
        for scenario, opts in OPTIONS.items():
            with self.subTest(scenario=scenario):
                actual_run = run_yearly(**opts)
                actual = normalize(actual_run)
                expected = json.loads((BASELINES / (scenario + '.json')).read_text())
                frozen_tx = json.loads((BASELINES / (scenario + '_transactions.json')).read_text())
                self.assertEqual(differences(actual, expected, actual_run[2].state.transactions, frozen_tx), {})

if __name__ == '__main__':
    unittest.main()
