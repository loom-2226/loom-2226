from __future__ import annotations
from decimal import Decimal as D

from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind, TxPurpose
from .mvp_state import AgentKind, AgentState, PopulationLedger, ScenarioResource


def earth_shadow_kernel(universe_id='RICH_PUBLIC_3',stock='20'):
    rid=RunIdentity(
        universe_id,'v1','EARTH_REFERENCE_TEST013A_v1','BUILD5_EARTH_SHADOW_TEST013A',
        (('earth_shadow_fixture','TEST_ONLY_NOT_CALIBRATED'),))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('earth_finance','FIN','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('earth_return','OWNER','EARTH:X',AccountKind.FUNDS,D('0'))
    k.add_account('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,D('0'))
    k.add_account('earth_market','EARTH_MARKET_v0','EARTH:X',AccountKind.EARTH_BOUNDARY,D('100'))
    k.add_account('project_cash','SPN','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_account('local_cash','LOCAL','OFF:T1',AccountKind.FUNDS,D('10'))
    k.add_project('P','OFF:T1','project_cash',{'SPN':D('1')})
    k.add_agent(AgentState(
        'PUB',AgentKind.PUBLIC,'EARTH:X','earth_finance',
        capabilities={'MIGRATE'},objectives=('PUBLIC_SETTLEMENT',)))
    q=D(stock)
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',q,q,q,q))
    k.population=PopulationLedger(1000,{'OFF:T1':0})
    k.set_resource_constraint('EARTH:X',1,D('100'),D('1'))
    return k


def realize_shadow_flows(k):
    # Earth -> offworld financing: capital diverted.
    k.add_commitment('C','FIN','P',D('40'))
    k.disburse(1,'C','earth_finance',D('40'))

    # Offworld project -> Earth supplier: purchase from Earth and existing FCF displacement view.
    k.reserve_earth_supply('EARTH:X',1,D('20'))
    k.create_wip('WIP-013A','P','OFF:T1')
    k.add_wip_expenditure(1,'WIP-013A','earth_supplier',D('20'),('EARTH:X',))

    # Earth boundary -> offworld project: Earth purchase from offworld venture.
    k.boundary_purchase(2,'earth_market','project_cash',D('10'),'RES',D('1'))

    # Offworld project -> Earth owner: capital returned.
    k.transfer(2,'project_cash','earth_return',D('5'),TxPurpose.RETURN_TO_EARTH)

    # Existing direct aggregate migration path: migration shadow only, no invented return transition.
    k.migrate(2,'PUB','OFF:T1',3)
    return k
