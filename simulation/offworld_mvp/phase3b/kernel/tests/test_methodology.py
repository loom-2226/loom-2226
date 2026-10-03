import unittest
from decimal import Decimal as D
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.build4 import OwnershipStake
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.mvp_state import *
from offworld_kernel.model import *
from offworld_kernel.kernel import InvariantError

class MethodologyTests(unittest.TestCase):
    def kernel(self):
        rid=RunIdentity('METH','v1','SYNTH','BUILD4_MVP_METHODOLOGY_R1',())
        k=MethodologyHardenedBuild4Kernel(rid)
        k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
        k.add_account('agg_cash','FIRM_SECTOR','EARTH:X',AccountKind.FUNDS,D('100'))
        k.add_account('agent_cash','FIRM_01','EARTH:X',AccountKind.FUNDS,D('0'))
        k.add_account('market','EARTH_MARKET_v0','EARTH:X',AccountKind.EARTH_BOUNDARY,D('0'))
        k.add_aggregate(AggregateState('FIRM_SECTOR','EARTH:X','agg_cash',10,{'A1','A2'},{'R':D('50')},{'VEH':D('1')},['H1','H2']))
        k.ownership_stakes.append(OwnershipStake('VEH','FIRM_SECTOR','EARTH:X',D('1')))
        k.add_system(SystemState('EARTH_MARKET_v0','EXTERNAL_CLEARING',{'market'}))
        return k

    def test_aggregate_to_agent_reconciliation(self):
        k=self.kernel()
        a=AgentState('FIRM_01',AgentKind.PRIVATE_SPONSOR,'EARTH:X','agent_cash',{'EXTRACT'},('RETURN',))
        rec=k.expose_agent_from_aggregate(1,'FIRM_SECTOR',a,D('20'),1,('A1',),{'R':D('5')},{'VEH':D('0.2')},('H1',))
        agg=k.aggregates['FIRM_SECTOR']; ag=k.agents['FIRM_01']
        self.assertEqual(k.state.accounts['agg_cash'].balance,D('80')); self.assertEqual(k.state.accounts['agent_cash'].balance,D('20'))
        self.assertEqual(agg.member_count,9); self.assertEqual(agg.asset_refs,{'A2'}); self.assertEqual(ag.asset_refs,{'A1'})
        self.assertEqual(agg.resource_holdings['R'],D('45')); self.assertEqual(ag.resource_holdings['R'],D('5'))
        self.assertEqual(agg.claim_holdings['VEH'],D('0.8')); self.assertEqual(ag.claim_holdings['VEH'],D('0.2'))
        self.assertIn('H1',ag.lineage_refs); self.assertIn(rec.resolution_id,ag.lineage_refs)
        self.assertEqual(rec.transaction_count_before,rec.transaction_count_after)
        self.assertEqual(rec.cash_total_before,rec.cash_total_after)
        k.assert_methodology_invariants()

    def test_invalid_resolution_atomic(self):
        k=self.kernel(); before=k.methodology_fingerprint()
        a=AgentState('FIRM_01',AgentKind.PRIVATE_SPONSOR,'EARTH:X','agent_cash')
        with self.assertRaises(InvariantError):
            k.expose_agent_from_aggregate(1,'FIRM_SECTOR',a,D('20'),1,(),{'R':D('500')},{},())
        self.assertEqual(before,k.methodology_fingerprint()); self.assertNotIn('FIRM_01',k.agents)

    def test_market_boundary_is_system_and_cannot_generic_fund(self):
        k=self.kernel()
        self.assertIn('EARTH_MARKET_v0',k.systems); self.assertNotIn('EARTH_MARKET_v0',k.agents)
        with self.assertRaises(InvariantError): k.transfer(1,'market','agent_cash',D('1'),TxPurpose.DISBURSE)

if __name__=='__main__': unittest.main()
