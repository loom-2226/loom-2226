"""Four-family REMOTE signals use one paid existing observation transition."""
import unittest
from decimal import Decimal as D

from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.build3 import Build3Kernel, RunIdentity
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.mvp_state import (
    AgentKind, AgentState, BODY_MATERIAL_FAMILIES, BODY_MATERIAL_QUESTIONS,
)
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.model import AccountKind, NodeKind


class MaterialCharacterizationTests(unittest.TestCase):
    def kernel(self):
        k=Build3Kernel(RunIdentity('MATERIAL','v1','SYNTHETIC','BUILD7_I3',()))
        k.add_node('EARTH:X',NodeKind.EARTH)
        k.add_account('public_funds','PUB','EARTH:X',AccountKind.FUNDS,D(100))
        k.add_account('supplier','SUP','EARTH:X',AccountKind.SUPPLIER,D(0))
        k.add_agent(AgentState('PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',{'EXPLORE'}))
        return k

    def test_one_payment_four_noisy_family_signals_without_project(self):
        k=self.kernel()
        truth=dict(zip(BODY_MATERIAL_FAMILIES,(True,False,True,False)))
        draws={'VOLATILES':D('.5'),'METALS':D('.5'),
               'SILICATES_ROCK':D('.1'),'CARBONACEOUS_ORGANICS':D('.1')}
        k.keyed_draw=lambda *keys:draws[keys[3].rsplit(':',1)[1]]
        observations,asset,used_draws=k.explore_paid(1,'PUB','','','supplier',D(10),
            channel='REMOTE',public=False,false_positive=D('.2'),false_negative=D('.2'),
            update_belief=False,body_id='UNNAMED_BODY',
            question_ref='BODY_MATERIAL_CHARACTERIZATION',body_truth=truth)
        self.assertIsNone(asset)
        self.assertEqual(tuple(o.question_ref for o in observations),BODY_MATERIAL_QUESTIONS)
        self.assertEqual(tuple(o.signal for o in observations),
                         ('POSITIVE','NEGATIVE','NEGATIVE','POSITIVE'))
        self.assertEqual(used_draws,tuple(draws.values()))
        self.assertEqual(k.state.accounts['public_funds'].balance,D(90))
        self.assertEqual(k.state.accounts['supplier'].balance,D(10))
        self.assertEqual(len(k.state.transactions),1)
        self.assertFalse(k.state.projects)
        self.assertFalse(k.resources)
        self.assertFalse(k.state.assets)
        self.assertEqual(k.agents['PUB'].information,{o.id for o in observations})


if __name__=='__main__':unittest.main()
