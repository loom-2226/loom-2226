from .mvp_kernel import MVPKernel
from .mvp_state import *
from .model import *

def full_causal_loop_fixture(universe='SPARSE'):
    if universe not in {'NULL','SPARSE','RICH'}: raise ValueError(universe)
    k=MVPKernel()
    k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
    # Synthetic country-neutral fixture accounts.
    for args in [
      ('public_funds','PUB','EARTH:X',AccountKind.FUNDS,'1000'),
      ('private_funds','FIN','EARTH:X',AccountKind.FUNDS,'1000'),
      ('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,'100'),
      ('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,'0'),
      ('earth_market','MARKET','EARTH:X',AccountKind.EARTH_BOUNDARY,'100000'),
      ('project_cash','PRJ','OFF:T1',AccountKind.PROJECT_CASH,'0'),
      ('local_funds','LOCAL','OFF:T1',AccountKind.FUNDS,'0'),
      ('local_supplier','LSUP','OFF:T1',AccountKind.SUPPLIER,'0')]:
        k.add_account(args[0],args[1],args[2],args[3],D(args[4]))
    k.add_project('PRJ','OFF:T1','project_cash',{'SPN':D('0.25'),'FIN':D('0.75')})
    k.add_agent(AgentState('PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',{'EXPLORE','FINANCE','MIGRATE'},('CAPABILITY','PUBLIC_INFORMATION')))
    k.add_agent(AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',{'EXPLORE','EXTRACT','SELL'},('RETURN',)))
    k.add_agent(AgentState('FIN',AgentKind.PRIVATE_FINANCIER,'EARTH:X','private_funds',{'FINANCE'},('RETURN',)))
    k.add_agent(AgentState('LOCAL',AgentKind.LOCAL_FINANCIER,'OFF:T1','local_funds',{'FINANCE'},('LOCAL_REINVESTMENT',)))
    qty={'NULL':'0','SPARSE':'20','RICH':'100'}[universe]
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',D(qty),D(qty),D(qty),D(qty)))
    for a in k.agents.values(): a.beliefs['RES']=D('0.20')
    k.colonies['OFF:T1']=ColonyState('OFF:T1'); k.population=PopulationLedger(earth=1000,offworld={'OFF:T1':0})

    # 1 public exploration -> public observation. Same pre-observation actions in all universes.
    obs=k.observe(1,'PUB','RES','REMOTE',public=True)
    # 2 sponsor requests development finance based only on information now held.
    req=k.request_finance(1,'SPN','PRJ',D('60'),'DEVELOPMENT',(obs.id,))
    positive=(obs.signal=='POSITIVE')
    k.decide_finance(req.id,'FIN',positive,'SCRIPTED_BELIEF_GATE')
    if not positive:
        k.assert_mvp_invariants()
        return k

    # 3 financed project buys Earth capital good -> offworld FCF -> productive asset.
    k.spend_capex(1,'PRJ','earth_supplier',D('60'),'MINE','OFF:T1',financing_origin_nodes=('EARTH:X',))
    k.capitalize('MINE',D('10'))
    # 4 public settlement support migrates people; migration conserves population.
    k.migrate(2,'PUB','OFF:T1',10)
    # 5 operator extracts against hidden fixed scenario stock, then sells to explicit Earth market.
    q=min(D('5'),k.resources['RES'].remaining)
    k.extract(2,'SPN','RES',q)
    revenue=k.sell(2,'SPN','RES',q,D('20'),'earth_market')
    # 6 sponsor moves realized proceeds into local-financier funds, creating explicit local financing capacity.
    k.transfer(2,'sponsor_funds','local_funds',revenue,TxPurpose.LOCAL_RETENTION,parent_ids=('RES',))
    # 7 local financier funds a local service-capital project.
    k.add_account('service_cash','SERVICE','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_project('SERVICE','OFF:T1','service_cash',{'LOCAL':D('1')})
    local_amount=min(D('40'),k.state.accounts['local_funds'].balance)
    lreq=FinancingRequest(k._id('req'),3,'SPN','SERVICE',local_amount,'LOCAL_REINVESTMENT',(obs.id,))
    k.financing_requests[lreq.id]=lreq
    k.decide_finance(lreq.id,'LOCAL',True,'SCRIPTED_LOCAL_REINVEST')
    k.spend_capex(3,'SERVICE','local_supplier',local_amount,'HABITAT','OFF:T1',financing_origin_nodes=('OFF:T1',))
    k.capitalize('HABITAT',local_amount)
    c=k.colonies['OFF:T1']; c.productive_capital=k.productive_capital('OFF:T1'); c.infrastructure=local_amount; c.production_capacity=k.state.assets['MINE'].capacity
    c.stage='DEPENDENT_SETTLEMENT'
    k.assert_mvp_invariants(); return k
