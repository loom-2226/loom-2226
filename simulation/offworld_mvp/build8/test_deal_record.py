import unittest
from .deal_record import evidence_routes, deal_records
from .screened_delivery import run_screened

class DealRecordTests(unittest.TestCase):
    def test_private_flip_and_share_custody(self):
        base=evidence_routes()
        flipped=evidence_routes('POSITIVE')
        shared=evidence_routes(share_private=True)
        self.assertNotEqual(base,flipped)  # same access, different observed signal
        self.assertEqual(tuple(r[:3] for r in base),tuple(r[:3] for r in flipped))
        self.assertFalse(any(r[1]=='Interlune' and r[2]=='SHARED' for r in base))
        self.assertTrue(any(r[1]=='Interlune' and r[2]=='SHARED' for r in shared))
        self.assertTrue(any(r[1]=='Axiom' and r[2]=='OBSERVED' for r in base))
        self.assertTrue(any(r[1]=='SCREEN_FINANCIER' and r[2].startswith('DISCLOSED_BELIEF') for r in base))

    def test_deals_reconcile_to_trial(self):
        work,decisions,_,_=run_screened()
        deals=deal_records(work,decisions)
        self.assertEqual(len(deals),2)
        self.assertEqual({d['sponsor'] for d in deals},{'Interlune','Axiom'})
        self.assertTrue(all(len(d['work'])==2 for d in deals))
        self.assertTrue(all(len(d['executors'])==2 for d in deals))
