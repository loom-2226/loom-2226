import unittest
from decimal import Decimal as D
from offworld_kernel.build3_fixture import *
from offworld_kernel.kernel import InvariantError

class Build3Tests(unittest.TestCase):
    def test_paid_exploration_and_knowledge_asset(self):
        k,o,w,d=paid_exploration_fixture('SPARSE',D('20'),D('0'),D('0'))
        self.assertEqual(k.state.accounts['public_funds'].balance,D('990'))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('10'))
        self.assertEqual(k.state.assets[w].kind,AssetKind.EXPLORATION_WIP)
        self.assertEqual(k.resolve_exploration(w,True),'KNOWLEDGE_ASSET')
        self.assertEqual(k.state.assets[w].kind,AssetKind.KNOWLEDGE)
    def test_stock_binding(self):
        k,q=stock_binding_fixture(); self.assertEqual(q,D('2')); self.assertEqual(k.resources['RES'].remaining,D('0'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('2'))
    def test_keyed_false_positive_and_writeoff(self):
        k,draw,q=false_positive_writeoff_fixture()
        self.assertLess(draw,D('0.20')); self.assertEqual(q,D('0')); self.assertEqual(k.resources['RES'].remaining,D('0'))
        self.assertNotIn('MINE',k.state.assets); self.assertIn('WRITE_OFF',k.exploration_resolution.values())
    def test_market_matched_resource_inventory(self):
        k,q,value=market_conservation_fixture()
        self.assertEqual(q,D('5')); self.assertEqual(value,D('100'))
        self.assertEqual(k.market_resource_inventory[('EARTH:X','RES')],D('5'))
        self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D('0'))
    def test_disposition_can_say_no_to_local_reinvestment(self):
        e,er=disposition_fixture('ENCLAVE'); s,sr=disposition_fixture('SETTLEMENT')
        self.assertEqual(er,'EARTH_RETURN'); self.assertEqual(sr,'LOCAL_REINVESTMENT')
        self.assertEqual(e.state.accounts['local_funds'].balance,D('0')); self.assertEqual(s.state.accounts['local_funds'].balance,D('80'))
    def test_earth_reference_proxy_ceiling(self):
        k=build3_base(); k.reserve_earth_supply('EARTH:X',1,D('100'))
        with self.assertRaises(InvariantError): k.reserve_earth_supply('EARTH:X',1,D('0.01'))
    def test_fingerprint_includes_run_identity_and_parameters(self):
        a=build3_base('A'); b=build3_base('B')
        self.assertNotEqual(a.build3_fingerprint(),b.build3_fingerprint())
        self.assertEqual(a.build3_fingerprint(),build3_base('A').build3_fingerprint())

if __name__=='__main__': unittest.main()
