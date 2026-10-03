import unittest
from decimal import Decimal as D
from offworld_kernel.build4_fixture import *
from offworld_kernel.kernel import InvariantError

class Build4Tests(unittest.TestCase):
    def test_hard_accounting(self):
        k,held,dep,amort,res=hard_accounting_fixture()
        self.assertEqual(held,D('60')); self.assertEqual(k.state.assets['A1'].book_value,D('45'))
        self.assertEqual(dep,D('5')); self.assertEqual(k.state.assets['K1'].book_value,D('8')); self.assertEqual(amort,D('2'))
        self.assertEqual(res,D('40')); self.assertEqual(k.carry_reservations['R1'].spent,D('15')); self.assertEqual(k.carry_reservations['R1'].lapsed,D('25'))
    def test_many_to_many_and_lapse(self):
        k,blocked=many_to_many_fixture(); self.assertTrue(blocked)
        self.assertEqual(k.state.accounts['p1cash'].balance,D('60'))
        self.assertEqual(k.state.commitments['P2C'].outstanding,D('30')); self.assertEqual(k.state.commitments['P2C'].lapsed,D('20'))
    def test_owner_claims_conserved(self):
        k=ownership_fixture(); shares={s.owner_id:s.share for s in k.ownership_stakes}
        self.assertEqual(shares,{'F1':D('0.6'),'F2':D('0.4')}); self.assertEqual(sum(shares.values()),D('1'))
        self.assertEqual(k.state.accounts['fin1'].balance,D('470')); self.assertEqual(k.state.accounts['fin2'].balance,D('480'))
        self.assertEqual(k.state.accounts['local_vehicle'].balance,D('50'))
    def test_boundary_signed_position_and_consumption(self):
        k=boundary_fixture(); self.assertEqual(k.state.accounts['boundary'].balance,D('-100'))
        self.assertEqual(k.boundary_net['boundary'],D('-100')); self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('3'))
    def test_local_supply_bound(self):
        k=build4_base(); k.create_wip('W','P1','OFF:T1'); k.state.accounts['p1cash'].balance=D('60')
        k.add_wip_expenditure(1,'W','local_supplier',D('50'))
        with self.assertRaises(InvariantError): k.add_wip_expenditure(1,'W','local_supplier',D('0.01'))
    def test_property_valid_sequences(self):
        a=property_sequence(2226,250); b=property_sequence(2226,250)
        self.assertEqual(a.fingerprint(),b.fingerprint())
    def test_invalid_transition_atomic(self):
        k=build4_base(); before=k.fingerprint()
        with self.assertRaises(InvariantError): k.transfer(1,'p1cash','fin1',D('1'),TxPurpose.OPEX)
        self.assertEqual(before,k.fingerprint())
    def test_event_log_changes_replay_fingerprint(self):
        a=build4_base('LOG'); b=build4_base('LOG'); a.audit('MARK',1,value='x')
        self.assertNotEqual(a.build4_fingerprint(),b.build4_fingerprint())
    def test_keyed_draw_uniformity(self):
        k=build4_base('UNIFORM'); mean,lo,hi=k.uniformity_sample(10000)
        self.assertGreater(mean,0.49); self.assertLess(mean,0.51); self.assertLess(lo,0.001); self.assertGreater(hi,0.999)

if __name__=='__main__': unittest.main()
