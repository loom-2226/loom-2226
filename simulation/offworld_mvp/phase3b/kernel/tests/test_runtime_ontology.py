import unittest
from decimal import Decimal as D
from offworld_kernel.mvp_state import *
from offworld_kernel.mvp_kernel import MVPKernel
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import *

class RuntimeOntologyTests(unittest.TestCase):
    def kernel(self):
        k=MVPKernel(); k.add_node('E',NodeKind.EARTH); k.add_node('O',NodeKind.OFFWORLD)
        k.add_account('cash','X','E',AccountKind.FUNDS,D('10')); k.add_account('pcash','P','O',AccountKind.PROJECT_CASH,D('0'))
        k.add_project('P','O','pcash',{'X':D('1')}); return k

    def test_non_agent_cannot_enter_agent_registry(self):
        for cls in (RuntimeObjectClass.SYSTEM,RuntimeObjectClass.AGGREGATE,RuntimeObjectClass.ENTITY_ASSET):
            k=self.kernel()
            with self.assertRaises(InvariantError):
                k.add_agent(AgentState('X',AgentKind.PRIVATE_SPONSOR,'E','cash',runtime_class=cls))

    def test_agent_class_admitted(self):
        k=self.kernel(); a=AgentState('X',AgentKind.PRIVATE_SPONSOR,'E','cash')
        k.add_agent(a); self.assertEqual(k.agents['X'].runtime_class,RuntimeObjectClass.AGENT)

    def test_earth_market_is_not_agent(self):
        # Market is represented by clearing/boundary state, not AgentState.
        k=self.kernel(); k.add_account('market','EARTH_MARKET_v0','E',AccountKind.EARTH_BOUNDARY,D('0'))
        self.assertNotIn('EARTH_MARKET_v0',k.agents)

    def test_resolution_change_not_silent(self):
        # Runtime class is explicit state. Registry admission rejects type masquerading.
        k=self.kernel(); aggregate=AgentState('X',AgentKind.PRIVATE_SPONSOR,'E','cash',runtime_class=RuntimeObjectClass.AGGREGATE)
        with self.assertRaises(InvariantError): k.add_agent(aggregate)

if __name__=='__main__': unittest.main()
