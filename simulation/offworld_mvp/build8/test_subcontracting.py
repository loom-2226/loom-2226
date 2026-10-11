import unittest
from decimal import Decimal as D
from .screened_delivery import run_screened
from .trial_knowledge import who_knows

class SubcontractTests(unittest.TestCase):
    def test_default_bit_identical(self):
        a,da,ka,oa=run_screened()
        b,db,kb,ob=run_screened(subcontract=False)
        self.assertEqual((a,da,oa,ka.fingerprint(),ka.build8_knowledge),
                         (b,db,ob,kb.fingerprint(),kb.build8_knowledge))

    def test_shared_capacity_money_and_visibility(self):
        rows,_,k,occupied=run_screened(subcontract=True,capacity_slots=1)
        subs=[e for e in k.event_log if e.get('kind')=='BUILD8_SUBCONTRACT']
        self.assertEqual(len(subs),2)
        for s in subs:
            self.assertEqual(s['depth'],1)
            self.assertEqual(occupied[('LAND',s['start'])],1)
            fact='subcontract:'+s['project']+':BUILD:'+s['prime']+':'+s['sub']
            self.assertEqual({x[1] for x in who_knows(k,fact)},{s['prime'],s['sub']})
            self.assertNotIn(s['project'],{x[1] for x in who_knows(k,fact)})
        sub_total=sum((D(s['price']) for s in subs),D(0))
        self.assertEqual(sum((D(e['amount']) for e in k.event_log if e.get('kind')=='BUILD8_SUB_PAYMENT'),D(0)),sub_total)
        # All prime customer revenue is unchanged; subcontract transfers are internal.
        direct,_,kd,_=run_screened(capacity_slots=1)
        self.assertEqual(sum((r.revenue for r in rows),D(0)),sum((r.revenue for r in direct),D(0)))
        self.assertEqual(k.state.accounts['screen:expense:BUILD'].balance+sub_total,
                         kd.state.accounts['screen:expense:BUILD'].balance)
        k.assert_invariants()

    def test_failure_never_accelerates_with_one_slot_and_holdback(self):
        success,_,ks,_=run_screened(subcontract=True,capacity_slots=1)
        recovered,_,kr,_=run_screened(subcontract=True,capacity_slots=1,
                                      sub_failure=True,resource_on_failure=True)
        for row in recovered:
            reference=next(x for x in success if x.project==row.project and x.category==row.category)
            self.assertGreaterEqual(row.finish,reference.finish)
        self.assertEqual([r.finish for r in recovered if r.category=='LAND'],[2032,2034])
        payments=[e for e in kr.event_log if e.get('kind')=='BUILD8_SUB_PAYMENT']
        self.assertEqual(len(payments),2)
        self.assertEqual(sum((D(e['amount']) for e in payments),D(0)),D('.36'))
        self.assertEqual(sum((D(e['withheld']) for e in payments),D(0)),D('.04'))
        self.assertEqual(sum((D(e['quoted']) for e in payments),D(0)),D('.40'))
        self.assertEqual(kr.state.accounts['screen:expense:BUILD'].balance,D('.60'))
        self.assertEqual(ks.state.accounts['screen:expense:BUILD'].balance,D('.60'))
        kr.assert_invariants()

    def test_failure_propagates_and_prime_can_self_perform(self):
        failed,_,kf,_=run_screened(subcontract=True,sub_failure=True)
        self.assertTrue(all(r.outcome=='FAILED' for r in failed if r.category=='BUILD'))
        self.assertTrue(all(r.outcome=='BLOCKED_UPSTREAM' for r in failed if r.category=='LAND'))
        recovered,_,kr,_=run_screened(subcontract=True,sub_failure=True,resource_on_failure=True)
        self.assertTrue(all(r.outcome=='DELIVERED' for r in recovered))
        baseline,_,_,_=run_screened(subcontract=True)
        for r in recovered:
            counterpart=next(x for x in baseline if x.project==r.project and x.category==r.category)
            self.assertGreaterEqual(r.finish,counterpart.finish+1)
        self.assertEqual(len([e for e in kr.event_log if e.get('kind')=='BUILD8_SUB_RESOURCED']),2)
        kf.assert_invariants();kr.assert_invariants()
