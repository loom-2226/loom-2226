"""Frozen semantic acceptance plus explicit expected chronological relabelling."""
import json
import unittest
from collections import Counter, defaultdict
from .screened_yearly import run_yearly
from .baselines.pre_cast_migration.capture import normalize
from .test_yearly_match_rule import BASELINES, differences

OPTIONS = {'screen_default': {},
           'screen_sub': {'subcontract': True, 'capacity_slots': 1},
           'screen_sub_failure': {'subcontract': True, 'capacity_slots': 1,
                                  'sub_failure': True, 'resource_on_failure': True}}
EXPECTED_FINGERPRINTS = {
    'screen_default': '7d42fe980ffba611d970465cd0571cbf6666c44e8a2138680ab15f9fee5ad051',
    'screen_sub': 'd9b04d05ebc5ad2478e588943674adcbbbce84368966a06c1d3b47f904116e27',
    'screen_sub_failure': '6f939cb778c2fe1779af350dc134bd8dee87a98003067579e8ba2dbe0da92bd1',
}
# The exact ID-to-economic-identity reassignment is checked, not waived.
EXPECTED_REASSIGNED_IDS = {
    'screen_default': (), 'screen_sub': (),
    'screen_sub_failure': ('tx-000055', 'tx-000056', 'tx-000057', 'tx-000058', 'tx-000059'),
}
EXPECTED_PARENT_ID_CHANGES = {
    'screen_default': (), 'screen_sub': (),
    'screen_sub_failure': ('tx-000055', 'tx-000057', 'tx-000058', 'tx-000059'),
}


def identity(t):
    if isinstance(t, dict):
        return (str(t['year']), t['source'], t['destination'], str(t['amount']),
                t['purpose'], t['supplier_location'], t['asset_location'])
    return (str(t.year), t.source_account, t.destination_account, str(t.amount),
            t.purpose.value, t.supplier_location, t.asset_location)


def parent_graph(transactions):
    """Map economic identities to multisets of parent economic identities/references."""
    ids = {(t['id'] if isinstance(t, dict) else t.id): identity(t) for t in transactions}
    result = defaultdict(Counter)
    for t in transactions:
        parents = t['parent_ids'] if isinstance(t, dict) else t.parent_ids
        normalized = tuple(('transaction', ids[p]) if p in ids else ('external', p)
                           for p in parents)
        result[identity(t)][normalized] += 1
    return dict(result)


class FrozenYearlyAcceptance(unittest.TestCase):
    def test_all_three_frozen_replays(self):
        for scenario, opts in OPTIONS.items():
            with self.subTest(scenario=scenario):
                actual_run = run_yearly(**opts)
                actual = normalize(actual_run)
                expected = json.loads((BASELINES / (scenario + '.json')).read_text())
                frozen_tx = json.loads((BASELINES / (scenario + '_transactions.json')).read_text())
                new_tx = actual_run[2].state.transactions
                self.assertEqual(differences(actual, expected, new_tx, frozen_tx), {})
                self.assertEqual(parent_graph(new_tx), parent_graph(frozen_tx))
                years = [record[0] for record in actual[2]['knowledge']]
                self.assertEqual(years, sorted(years))
                # Explicit exception: generated at epoch 2 but authored as 2026.
                self.assertIn([2026, 'obs-000037', 'Axiom', 'OBSERVED',
                               'WATER_BEARING_MATERIAL_PRESENT:NEGATIVE'], actual[2]['knowledge'])
                old_by_id = {t['id']: t for t in frozen_tx}
                new_by_id = {t.id: t for t in new_tx}
                self.assertEqual(set(old_by_id), set(new_by_id))
                reassigned = tuple(sorted(tid for tid in old_by_id
                                          if identity(old_by_id[tid]) != identity(new_by_id[tid])))
                self.assertEqual(reassigned, EXPECTED_REASSIGNED_IDS[scenario])
                parent_changed = tuple(sorted(tid for tid in old_by_id
                                              if tuple(old_by_id[tid]['parent_ids']) != new_by_id[tid].parent_ids))
                self.assertEqual(parent_changed, EXPECTED_PARENT_ID_CHANGES[scenario])
                self.assertEqual(actual[2]['fingerprint'], EXPECTED_FINGERPRINTS[scenario])

if __name__ == '__main__':
    unittest.main()
