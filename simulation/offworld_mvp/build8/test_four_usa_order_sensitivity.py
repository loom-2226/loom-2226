"""Exhaust all 24 funding orders, holding evidence and capital fixed."""
from collections import Counter
from itertools import permutations
import unittest
from .test_four_usa_agents import NAMES,trial


def sweep():
    orders=tuple(permutations(NAMES))
    results={}
    for positive in (False,True):
        rows=[]
        for order in orders:
            outcome,_,mobilized,remaining=trial(positive,order)
            funded=frozenset(name for name in NAMES if outcome[name][2]=='FUNDED')
            decisions=tuple((name,outcome[name][0:2]) for name in NAMES)
            rows.append((order,funded,decisions,mobilized,remaining))
        results[positive]=rows
    return results

class FourUSAOrderSensitivity(unittest.TestCase):
    def test_all_orders_and_information_effect(self):
        results=sweep()
        for positive,rows in results.items():
            self.assertEqual(len(rows),24)
            self.assertEqual(len({r[0] for r in rows}),24)
            self.assertEqual(len({r[2] for r in rows}),1)
            self.assertEqual(len({r[3:] for r in rows}),1)
            self.assertTrue(all(len(r[1])==2 for r in rows))
            counts=Counter(name for r in rows for name in r[1])
            sets=Counter(tuple(sorted(r[1])) for r in rows)
            print('ORDER_SWEEP', 'POSITIVE' if positive else 'NEGATIVE', 'FUNDING_COUNTS',dict(counts),'FUNDED_SETS',dict(sets))
        changed=sum(results[False][i][1]!=results[True][i][1] for i in range(24))
        print('CROSS_SCENARIO_CHANGED_FUNDED_SET',changed,'OF',24)
        self.assertEqual(changed,12)
        # The original fixed-order result must be included, not replaced.
        self.assertEqual(results[False][0][1],frozenset(('Blue Origin','Interlune')))
        self.assertEqual(results[True][0][1],frozenset(('SpaceX','Blue Origin')))
