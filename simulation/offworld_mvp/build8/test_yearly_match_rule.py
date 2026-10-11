"""Frozen screened snapshots: semantic comparison independent of audit order."""
import json
import unittest
from collections import Counter
from pathlib import Path

from .baselines.pre_cast_migration.capture import capture

BASELINES = Path(__file__).resolve().parent / 'baselines' / 'pre_cast_migration'
SCENARIOS = ('screen_default', 'screen_sub', 'screen_sub_failure')


def event_multiset(events):
    """Ignore only sequence and ordering; retain every substantive event field."""
    return Counter(json.dumps({k: v for k, v in event.items() if k != 'seq'}, sort_keys=True)
                   for event in events)


def differences(actual, expected):
    """Return precise semantic differences; IDs and fingerprint are separately reported."""
    problems = {}
    for field, index in (('work_outcomes_and_dates', 0), ('screening_outcomes', 1),
                         ('occupied_capacity', 3)):
        if actual[index] != expected[index]:
            problems[field] = (expected[index], actual[index])
    a, b = actual[2], expected[2]
    for field in ('balances', 'knowledge'):
        if a[field] != b[field]:
            problems[field] = (b[field], a[field])
    old, new = event_multiset(b['events']), event_multiset(a['events'])
    if old != new:
        problems['events_missing'] = dict(old - new)
        problems['events_extra'] = dict(new - old)
    return problems


class YearlyMatchRuleTests(unittest.TestCase):
    def test_frozen_screened_baselines_match_existing_experiments(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                baseline = json.loads((BASELINES / (scenario + '.json')).read_text())
                actual = json.loads(capture(scenario))
                self.assertEqual(differences(actual, baseline), {})
                self.assertEqual(actual[2]['fingerprint'], baseline[2]['fingerprint'])

    def test_order_only_is_permitted(self):
        baseline = json.loads((BASELINES / 'screen_default.json').read_text())
        changed = json.loads(json.dumps(baseline))
        changed[2]['events'].reverse()
        self.assertEqual(differences(changed, baseline), {})
        changed[2]['events'][0]['year'] += 1
        self.assertIn('events_missing', differences(changed, baseline))


if __name__ == '__main__':
    unittest.main()
