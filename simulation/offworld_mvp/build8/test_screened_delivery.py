"""Build 8 screened funding, deterministic queue, and physical handoffs."""
import unittest
from decimal import Decimal as D
from .screened_delivery import run_screened, SPONSORS
from .opening import EARTH_V4_ROOT

@unittest.skipUnless(EARTH_V4_ROOT.exists(), 'Earth v4 missing')
class ScreenedDeliveryTests(unittest.TestCase):
    def test_policy_rank_defer_retry_and_shuffled_inputs(self):
        rows, decisions, k, capacity = run_screened()
        shuffled, other_decisions, other, other_capacity = run_screened(tuple(reversed(SPONSORS)))
        self.assertEqual((rows,decisions,capacity),(shuffled,other_decisions,other_capacity))
        self.assertEqual(k.fingerprint(),other.fingerprint())
        self.assertEqual([(d[0],d[1],d[2],d[4]) for d in decisions],
            [('Interlune','INITIATE_PROJECT','APPROVE',2026),
             ('Axiom','INITIATE_PROJECT','APPROVE',2027)])
        self.assertGreater(D(decisions[0][3]),D(decisions[1][3]))
        self.assertEqual([(r.project,r.category,r.start,r.finish) for r in rows],
            [('Interlune','BUILD',2026,2028),('Axiom','BUILD',2027,2029),
             ('Interlune','LAND',2028,2030),('Axiom','LAND',2029,2031)])
        self.assertTrue(all(r.outcome=='DELIVERED' for r in rows))
        self.assertEqual(sum((r.revenue for r in rows),D(0)),D('3.05'))
        self.assertEqual(sum((r.cost for r in rows),D(0)),D('2.50'))
        self.assertEqual(sum((r.profit for r in rows),D(0)),D('.55'))
        self.assertEqual(k.state.accounts['screen:revenue:BUILD'].balance,D('.25'))
        self.assertEqual(k.state.accounts['screen:revenue:LAND'].balance,D('.30'))
        self.assertEqual(len(k.financing_decisions),2)
        k.assert_invariants()

    def test_failed_build_blocks_landing_and_preserves_cash(self):
        rows,_,k,_=run_screened(failure=('Interlune','BUILD'))
        first=[r for r in rows if r.project=='Interlune']
        self.assertEqual([r.outcome for r in first],['FAILED','BLOCKED_UPSTREAM'])
        self.assertFalse(any(r.produced=='ON_MOON:Interlune' for r in rows))
        self.assertEqual(k.state.accounts['screen:cash:Interlune'].balance,D('.90'))
        k.assert_invariants()

    def test_failed_landing_is_not_delivery(self):
        rows,_,k,_=run_screened(failure=('Interlune','LAND'))
        self.assertEqual(next(r.outcome for r in rows if r.project=='Interlune' and r.category=='LAND'),'FAILED')
        self.assertFalse(any(r.produced=='ON_MOON:Interlune' for r in rows))
        k.assert_invariants()

    def test_funding_delay_is_real_when_capacity_available(self):
        rows,decisions,k,occupied=run_screened(capacity_slots=2)
        axiom=next(r for r in rows if r.project=='Axiom' and r.category=='BUILD')
        self.assertEqual(axiom.start,2027)
        self.assertEqual(axiom.finish,2029)
        # In 2026 Northrop had a second unused slot: this is financing delay,
        # not an executor bottleneck hidden behind the finance queue.
        self.assertEqual(occupied[('BUILD',2026)],1)
        self.assertEqual(next(d[4] for d in decisions if d[0]=='Axiom'),2027)
        k.assert_invariants()

    def test_cost_difference_not_named_belief_and_pressure_audit(self):
        rows,decisions,k,_=run_screened()
        self.assertGreater(D(decisions[0][3]),D(decisions[1][3]))
        records=[e for e in k.event_log if e.get('kind')=='BUILD8_FINANCE_SCREEN']
        self.assertEqual(len(records),2)
        for e in records:
            self.assertEqual(D(e['pressure']),D(0))
            self.assertEqual(D(e['pressure_contribution']),D(0))
            self.assertEqual(str(e['economic_score']),next(d[3] for d in decisions if d[0]==e['sponsor']))
        # Zero-pressure case preserves the constrained ranking and funding order.
        self.assertEqual([d[4] for d in decisions],[2026,2027])
        self.assertEqual([r.finish for r in rows if r.category=='LAND'],[2030,2031])

    def test_failure_contract_comparison(self):
        full,_,kf,_=run_screened(failure=('Interlune','LAND'),contract='FULL_ON_FAILURE')
        held,_,kh,_=run_screened(failure=('Interlune','LAND'),contract='ACCEPTANCE_HOLDBACK')
        a=next(r for r in full if r.project=='Interlune' and r.category=='LAND')
        b=next(r for r in held if r.project=='Interlune' and r.category=='LAND')
        self.assertEqual((a.outcome,b.outcome),('FAILED','FAILED'))
        self.assertEqual((a.revenue,b.revenue),(D('.9'),D('.81')))
        self.assertEqual((a.cost,b.cost),(D('.75'),D('.75')))
        self.assertEqual((a.profit,b.profit),(D('.15'),D('.06')))
        self.assertEqual(kf.state.accounts['screen:cash:Interlune'].balance,D(0))
        self.assertEqual(kh.state.accounts['screen:cash:Interlune'].balance,D('.09'))
        self.assertFalse(any(r.produced=='ON_MOON:Interlune' for r in held))
        kf.assert_invariants();kh.assert_invariants()

    def test_private_evidence_flip_share_and_both_counterfactuals(self):
        for signal in ('NEGATIVE','POSITIVE'):
            constrained, decisions, k, _ = run_screened(private_signal=signal)
            immediate, controls, kc, _ = run_screened(private_signal=signal, immediate_funding=True)
            self.assertEqual({r.project for r in constrained},{'Interlune','Axiom'})
            for name in ('Interlune','Axiom'):
                funded=next(d[4] for d in decisions if d[0]==name)
                baseline=next(d[4] for d in controls if d[0]==name)
                self.assertEqual(baseline,2026)
                actual=next(r for r in constrained if r.project==name and r.category=='LAND')
                hypothetical=next(r for r in immediate if r.project==name and r.category=='LAND')
                self.assertEqual(actual.finish-hypothetical.finish,funded-baseline)
                self.assertEqual(sum(r.revenue for r in constrained if r.project==name),
                                 sum(r.revenue for r in immediate if r.project==name))
            k.assert_invariants();kc.assert_invariants()
        negative=run_screened(private_signal='NEGATIVE')[1]
        positive=run_screened(private_signal='POSITIVE')[1]
        self.assertEqual([d[4] for d in negative],[2026,2027])
        self.assertEqual([d[4] for d in positive],[2027,2026])
        shared=run_screened(private_signal='NEGATIVE',share_private=True)[1]
        self.assertEqual(D(shared[0][3]),D(shared[1][3]))

    def test_reversed_input_replay_under_both_evidence_signals(self):
        for signal in ('NEGATIVE','POSITIVE'):
            a,da,ka,ca=run_screened(private_signal=signal)
            b,db,kb,cb=run_screened(tuple(reversed(SPONSORS)),private_signal=signal)
            self.assertEqual((a,da,ca),(b,db,cb))
            self.assertEqual(ka.fingerprint(),kb.fingerprint())
