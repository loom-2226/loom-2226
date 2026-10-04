import unittest
from decimal import Decimal as D
from offworld_kernel.edge_fixtures import staged_multiyear_wip_fixture,genuine_multirate_fixture
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind,NodeKind,TxPurpose
from offworld_kernel.kernel import InvariantError

class AccountingEdgeTests(unittest.TestCase):
    def test_signed_boundary_mirror_reconciles_account_and_ledger(self):
        k=MethodologyHardenedBuild4Kernel(RunIdentity('B','v1','S','C',()))
        k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
        k.add_account('boundary','MKT','EARTH:X',AccountKind.EARTH_BOUNDARY,D('0'))
        k.add_account('project','P','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
        k.boundary_purchase(1,'boundary','project',D('100'),'RES',D('5'))
        k.transfer(1,'project','boundary',D('30'),TxPurpose.RETURN_TO_EARTH)
        k.assert_build4_invariants()
        self.assertEqual(k.state.accounts['boundary'].balance,D('-70'))
        self.assertEqual(k.boundary_net['boundary'],D('-70'))
        ledger=sum((t.amount for t in k.state.transactions if t.destination_account=='boundary'),D('0'))-sum((t.amount for t in k.state.transactions if t.source_account=='boundary'),D('0'))
        self.assertEqual(ledger,D('-70'))
        k.boundary_net['boundary']=D('-69')
        with self.assertRaisesRegex(InvariantError,'boundary mirror reconciliation'):
            k.assert_build4_invariants()

    def test_true_staged_multiyear_wip_then_depreciation(self):
        k,result,states=staged_multiyear_wip_fixture()
        self.assertEqual(states[0],('spend-y2','20','0',None))
        self.assertEqual(states[1],('spend-y3','50','0',None))
        self.assertEqual(states[2],('commission-y4','50','50','50'))
        self.assertEqual(states[3],('depreciate-y5','50','50','45.00'))
        self.assertEqual([(e.year,str(e.amount)) for e in k.state.fcf_events],[(2,'20'),(3,'30')])
        self.assertEqual(k.state.assets['A'].book_value,D('45.00'))

    def test_genuine_multirate_synchronization(self):
        k,result,obs=genuine_multirate_fixture()
        self.assertEqual(result.execution_log,(
          'mission-day30','finance-q1','finance-q2','mission-day200','finance-q3',
          'earth-annual','mission-day365','finance-q4'))
        d=dict(obs)
        self.assertEqual(d['mission-day30'],'0')
        self.assertEqual(d['mission-day200'],'2')
        self.assertEqual(d['earth-annual'],'3')
        self.assertEqual(d['mission-day365'],'3')
        self.assertEqual(d['finance-q4'],'4')
        self.assertEqual(k.state.accounts['project'].balance,D('4'))

if __name__=='__main__': unittest.main()
