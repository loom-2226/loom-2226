"""Opt-in shared-kernel defense draw: conservation, counterfactual, crisis, replay."""
import unittest
from decimal import Decimal as D
from simulation.offworld_mvp.defense_capital import draw, DefenseDials, Crisis
from .defense_draw_trial import run, sweep, EXAMPLE_CRISIS
from .opening import EARTH_V4_ROOT

@unittest.skipUnless(EARTH_V4_ROOT.exists(),'Earth v4 missing')
class DefenseDrawTests(unittest.TestCase):
    def test_off_is_identical_and_no_crisis_is_identical(self):
        a,k=run()
        b,j=run(enabled=False,crises=(EXAMPLE_CRISIS,))
        self.assertEqual((a,k.fingerprint()),(b,j.fingerprint()))
        self.assertFalse(hasattr(k,'defense_draw_records'))
        c,l=run(enabled=True)
        d,m=run(enabled=True,crises=())
        self.assertEqual((c,l.fingerprint()),(d,m.fingerprint()))
        self.assertEqual([r['civilian'] for r in a],[r['civilian'] for r in c])
        self.assertEqual(len(l.defense_draw_records),10)
        self.assertEqual(len([x for x in l.event_log if x.get('kind')=='DEFENSE_CAPITAL_DRAW']),10)
        for country in ('USA','CHN'):
            self.assertEqual(l.state.accounts['defense:funds:'+country].balance,
                             sum((r.amount for r in l.defense_draw_records if r.country==country),D(0)))

    def test_crisis_and_sweep(self):
        normal,_=run(enabled=True)
        crisis,k=run(enabled=True,crises=(EXAMPLE_CRISIS,))
        for a,b in zip(normal,crisis):
            self.assertEqual(a['civilian'],b['civilian'])
            if 2027<=a['year']<=2029:
                self.assertGreater(D(b['defense']),D(a['defense']))
                self.assertEqual(b['crises'],EXAMPLE_CRISIS.name)
            else:self.assertEqual(a['defense'],b['defense'])
        rows=sweep(scales=('0','1','2'))
        self.assertEqual(len(rows),30)
        self.assertTrue(all(D(r['defense'])==0 for r in rows if r['scale']=='0'))
        self.assertTrue(all(D(r['defense'])>=0 for r in rows))
        k.assert_invariants()

    def test_duplicate_rejected(self):
        _,k=run(enabled=True)
        r=k.defense_draw_records[0]
        with self.assertRaises(Exception):
            draw(k,2026,'USA',D('4958025335469.291'),D('.3'),DefenseDials(D(1),D(1),D(2),D('.01')),
                 D('1000000000'),'b8_source:USA','defense:funds:USA')
