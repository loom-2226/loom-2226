"""Frozen screened snapshots: semantic comparison independent of audit order."""
import json
import unittest
from collections import Counter
from pathlib import Path

from .baselines.pre_cast_migration.capture import capture

BASELINES = Path(__file__).resolve().parent / 'baselines' / 'pre_cast_migration'
SCENARIOS = ('screen_default', 'screen_sub', 'screen_sub_failure')


def _semantic_event(event):
    """Exclude generated transaction references, never substantive amounts/parties."""
    return {k: v for k, v in event.items()
            if k not in ('seq', 'transaction_id', 'transaction_ids', 'tx_id', 'tx_ids')}


def event_multiset(events):
    return Counter(json.dumps(_semantic_event(event), sort_keys=True) for event in events)


def transaction_multiset(transactions):
    """Compare economic transfers, independent of generated IDs and insertion order."""
    def fields(t):
        if isinstance(t, dict):
            return (str(t['year']), t['source'], t['destination'], str(t['amount']),
                    t['purpose'], t['supplier_location'], t['asset_location'])
        return (str(t.year), t.source_account, t.destination_account, str(t.amount),
                t.purpose.value, t.supplier_location, t.asset_location)
    return Counter(fields(t) for t in transactions)


def differences(actual, expected, actual_transactions=None, expected_transactions=None):
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
    if actual_transactions is not None and expected_transactions is not None:
        old_tx, new_tx = transaction_multiset(expected_transactions), transaction_multiset(actual_transactions)
        if old_tx != new_tx:
            problems['transactions_missing'] = dict(old_tx - new_tx)
            problems['transactions_extra'] = dict(new_tx - old_tx)
    return problems


class YearlyMatchRuleTests(unittest.TestCase):
    def test_frozen_screened_baselines_match_existing_experiments(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                baseline = json.loads((BASELINES / (scenario + '.json')).read_text())
                actual = json.loads(capture(scenario))
                self.assertEqual(differences(actual, baseline), {})
                self.assertEqual(actual[2]['fingerprint'], baseline[2]['fingerprint'])
                from .screened_delivery import run_screened
                opts = {'screen_default': {}, 'screen_sub': {'subcontract': True, 'capacity_slots': 1},
                        'screen_sub_failure': {'subcontract': True, 'capacity_slots': 1,
                                               'sub_failure': True, 'resource_on_failure': True}}[scenario]
                transactions = run_screened(**opts)[2].state.transactions
                frozen = json.loads((BASELINES / (scenario + '_transactions.json')).read_text())
                self.assertEqual(transaction_multiset(transactions), transaction_multiset(frozen))

    def test_transaction_multiset_is_order_and_id_independent(self):
        from .screened_delivery import run_screened
        _, _, kernel, _ = run_screened()
        from dataclasses import replace
        transactions = kernel.state.transactions
        changed = [replace(t, id='renumbered-' + str(i)) for i, t in enumerate(reversed(transactions))]
        self.assertEqual(transaction_multiset(transactions), transaction_multiset(changed))
        changed[0] = replace(changed[0], amount=changed[0].amount + 1)
        self.assertNotEqual(transaction_multiset(transactions), transaction_multiset(changed))

    def test_order_only_is_permitted(self):
        baseline = json.loads((BASELINES / 'screen_default.json').read_text())
        changed = json.loads(json.dumps(baseline))
        changed[2]['events'].reverse()
        self.assertEqual(differences(changed, baseline), {})
        changed[2]['events'][0]['transaction_id'] = 'tx-renumbered'
        self.assertEqual(differences(changed, baseline), {})
        changed[2]['events'][0]['year'] += 1
        self.assertIn('events_missing', differences(changed, baseline))


if __name__ == '__main__':
    unittest.main()
