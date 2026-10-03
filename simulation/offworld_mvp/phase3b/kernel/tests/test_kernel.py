import unittest
from decimal import Decimal
from offworld_kernel.fixtures import four_route_fixture, recursive_fixture
from offworld_kernel.kernel import Kernel, InvariantError
from offworld_kernel.model import AccountKind, D, NodeKind

class FourRouteTests(unittest.TestCase):
    def test_routes_and_locality(self):
        k=four_route_fixture()
        self.assertEqual(k.realized_fcf('OFF:C1',1),D('40')); self.assertEqual(k.realized_fcf('OFF:C1',2),D('20'))
        self.assertEqual(k.realized_fcf('OFF:C1',3),D('15')); self.assertEqual(k.realized_fcf('OFF:M1',4),D('10'))
        self.assertEqual(k.state.earth_impact.terrestrial_fcf_delta[('EARTH:X',1)],D('-40'))
        self.assertEqual(k.state.earth_impact.terrestrial_fcf_delta[('EARTH:Y',3)],D('-15'))
        self.assertEqual(k.productive_capital('EARTH:X'),D('0')); self.assertEqual(k.productive_capital('EARTH:Y'),D('0'))
    def test_replay(self): self.assertEqual(four_route_fixture().fingerprint(),four_route_fixture().fingerprint())

class RecursiveTests(unittest.TestCase):
    def test_divergence(self):
        e=recursive_fixture('ENCLAVE',50); s=recursive_fixture('SETTLEMENT',50)
        self.assertEqual(e['productive_capital'],D('100')); self.assertEqual(e['local_fcf'],D('0'))
        self.assertGreater(s['productive_capital'],e['productive_capital']); self.assertGreater(s['local_fcf'],D('0')); self.assertNotEqual(s['fingerprint'],e['fingerprint'])
    def test_replay(self): self.assertEqual(recursive_fixture('SETTLEMENT',20)['fingerprint'],recursive_fixture('SETTLEMENT',20)['fingerprint'])

class GuardrailTests(unittest.TestCase):
    def test_ownership(self):
        k=Kernel(); k.add_node('OFF:X',NodeKind.OFFWORLD); k.add_account('cash','p','OFF:X',AccountKind.PROJECT_CASH)
        with self.assertRaises(InvariantError): k.add_project('p','OFF:X','cash',{'a':Decimal('0.6'),'b':Decimal('0.5')})

if __name__=='__main__': unittest.main()