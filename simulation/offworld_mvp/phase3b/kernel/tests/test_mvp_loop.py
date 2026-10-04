import unittest
from decimal import Decimal as D
from offworld_kernel.mvp_fixture import full_causal_loop_fixture

class FullLoopTests(unittest.TestCase):
    def test_sparse_full_loop(self):
        k=full_causal_loop_fixture('SPARSE')
        self.assertEqual(k.resources['RES'].remaining,D('15'))
        self.assertEqual(k.population.earth,990); self.assertEqual(k.population.offworld['OFF:T1'],10)
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('0'))
        self.assertEqual(k.productive_capital('OFF:T1'),D('100'))
        self.assertEqual(k.realized_fcf('OFF:T1',1),D('60')); self.assertEqual(k.realized_fcf('OFF:T1',3),D('40'))
        self.assertEqual(k.state.accounts['earth_market'].balance,D('99900'))
        self.assertTrue(k.agents['FIN'].information)
        self.assertGreater(k.agents['FIN'].beliefs['RES'],D('0.20'))
    def test_null_blocks_development(self):
        k=full_causal_loop_fixture('NULL')
        self.assertEqual(k.resources['RES'].remaining,D('0')); self.assertEqual(len(k.state.fcf_events),0)
        self.assertEqual(k.population.offworld['OFF:T1'],0)
        self.assertEqual(next(iter(k.financing_decisions.values())).approved,False)
    def test_pre_observation_action_identity(self):
        n=full_causal_loop_fixture('NULL'); s=full_causal_loop_fixture('SPARSE'); r=full_causal_loop_fixture('RICH')
        self.assertEqual(n.events[0].action,s.events[0].action); self.assertEqual(s.events[0].action,r.events[0].action)
        self.assertEqual(n.events[0].inputs[0],s.events[0].inputs[0]); self.assertEqual(s.events[0].inputs[0],r.events[0].inputs[0])
    def test_deterministic_replay(self):
        self.assertEqual(full_causal_loop_fixture('SPARSE').mvp_fingerprint(),full_causal_loop_fixture('SPARSE').mvp_fingerprint())
    def test_epistemic_separation(self):
        k=full_causal_loop_fixture('RICH')
        self.assertNotEqual(k.agents['SPN'].beliefs['RES'],k.resources['RES'].remaining)
        self.assertTrue(all('100' not in e.inputs for e in k.events[:2]))
if __name__=='__main__': unittest.main()
