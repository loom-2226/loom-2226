"""Order-free, test-only financier clearing with real policy decisions."""
from itertools import permutations
import unittest
from .test_four_usa_agents import NAMES,trial

class FinancierClearing(unittest.TestCase):
    def test_all_24_orders_and_disclosure(self):
        results={}
        for positive,disclose in ((False,True),(True,False),(True,True)):
            runs=[trial(positive,order,financier_clearing=True,disclose_private=disclose)
                  for order in permutations(NAMES)]
            self.assertTrue(all(run==runs[0] for run in runs))
            results[positive,disclose]=runs[0]
            print('FINANCIER_24_ORDER',positive,disclose,runs[0][0])
            self.assertEqual(sum(row[2]=='FUNDED' for row in runs[0][0].values()),2)
            self.assertEqual(runs[0][3],'0.00')
            self.assertTrue(all(row[4]=='0' for row in runs[0][0].values()))
        neg=results[False,True][0]
        withheld=results[True,False][0]
        shared=results[True,True][0]
        self.assertEqual(neg['SpaceX'][0],'DECLINE')
        self.assertEqual(withheld['SpaceX'][0],'APPROVE')
        self.assertEqual(withheld['SpaceX'][2],'DEFERRED')
        self.assertEqual(shared['SpaceX'][2],'FUNDED')
        self.assertGreater(float(shared['SpaceX'][1]),float(withheld['SpaceX'][1]))
        self.assertNotEqual({n for n in NAMES if withheld[n][2]=='FUNDED'},
                            {n for n in NAMES if shared[n][2]=='FUNDED'})
        self.assertEqual(shared['Blue Origin'][3],'NEXT_PERIOD')
