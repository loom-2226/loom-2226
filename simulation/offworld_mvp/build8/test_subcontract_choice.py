import unittest
from decimal import Decimal as D
from .subcontract_choice import Request, allocate

class SubcontractChoiceTests(unittest.TestCase):
    def test_two_primes_one_sub_one_authored_slot(self):
        requests = (Request('CASC','Astrobotic','LAND',2026,D('.30')),
                    Request('Northrop Grumman','Astrobotic','LAND',2026,D('.25')))
        capacity = {('Astrobotic','LAND',2026):1}  # AUTHORED, not cast capacity index
        results, used = allocate(requests, capacity)
        self.assertEqual(results, (
            ('Northrop Grumman','Astrobotic',2026,'ALLOCATED'),
            ('CASC','Astrobotic',2026,'DEFERRED_NO_SLOT')))
        self.assertEqual(used[('Astrobotic','LAND',2026)], 1)
        self.assertEqual((results,used), allocate(tuple(reversed(requests)),capacity))

    def test_seeded_tie_break_is_order_independent(self):
        a=Request('CASC','Astrobotic','LAND',2026,D('.25'))
        b=Request('Northrop Grumman','Astrobotic','LAND',2026,D('.25'))
        capacity={('Astrobotic','LAND',2026):1}
        self.assertEqual(allocate((a,b),capacity),allocate((b,a),capacity))
        self.assertEqual([x[3] for x in allocate((a,b),capacity)[0]].count('ALLOCATED'),1)
