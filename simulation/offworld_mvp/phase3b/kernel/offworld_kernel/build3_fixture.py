from .build3 import *
from .mvp_state import *
from .model import *

def build3_base(universe_id='SPARSE',stock=D('20'),fp=D('0.20'),fn=D('0.10')):
    rid=RunIdentity(universe_id,'v1','SYNTHETIC_EARTH_REFERENCE_FIXTURE_v1','PHASE3B_BUILD3_v1',
        (('false_positive',str(fp)),('false_negative',str(fn)),('lambda_displacement','1'),('allocation_fraction','0.10')))
    k=Build3Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
    for aid,owner,node,kind,balance in [
      ('public_funds','PUB','EARTH:X',AccountKind.FUNDS,'1000'),('private_funds','FIN','EARTH:X',AccountKind.FUNDS,'1000'),
      ('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,'0'),('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,'0'),
      ('earth_market','MARKET','EARTH:X',AccountKind.EARTH_BOUNDARY,'100000'),('explore_cash','EXP','OFF:T1',AccountKind.PROJECT_CASH,'0'),
      ('develop_cash','DEV','OFF:T1',AccountKind.PROJECT_CASH,'0'),('local_funds','LOCAL','OFF:T1',AccountKind.FUNDS,'0')]:
        k.add_account(aid,owner,node,kind,D(balance))
    k.add_project('EXP','OFF:T1','explore_cash',{'PUB':D('1')}); k.add_project('DEV','OFF:T1','develop_cash',{'SPN':D('0.25'),'FIN':D('0.75')})
    k.add_agent(AgentState('PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',{'EXPLORE','FINANCE','MIGRATE'}))
    k.add_agent(AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',{'EXTRACT','SELL'}))
    k.add_agent(AgentState('FIN',AgentKind.PRIVATE_FINANCIER,'EARTH:X','private_funds',{'FINANCE'}))
    k.add_agent(AgentState('LOCAL',AgentKind.LOCAL_FINANCIER,'OFF:T1','local_funds',{'FINANCE'}))
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',stock,stock,stock,stock))
    for a in k.agents.values(): a.beliefs['RES']=D('0.20')
    k.colonies['OFF:T1']=ColonyState('OFF:T1'); k.population=PopulationLedger(1000,{'OFF:T1':0})
    # Synthetic reference FCF exercises reservation/ceiling logic without claiming governed Earth ingestion.
    k.set_resource_constraint('EARTH:X',1,D('1000'),D('0.10'))
    return k

def paid_exploration_fixture(universe_id='SPARSE',stock=D('20'),fp=D('0.20'),fn=D('0.10')):
    k=build3_base(universe_id,stock,fp,fn)
    # Public financing -> explicit exploration project cash -> supplier expenditure.
    k.add_commitment('PUB-EXP','PUB','EXP',D('10')); k.disburse(1,'PUB-EXP','public_funds',D('10'))
    obs,wip,draw=k.explore_paid(1,'PUB','RES','EXP','earth_supplier',D('10'),'REMOTE',True,fp,fn)
    return k,obs,wip,draw

def false_positive_writeoff_fixture():
    k,obs,wip,draw=paid_exploration_fixture('NULL_FP_1',D('0'),D('0.20'),D('0.10'))
    assert obs.signal=='POSITIVE'
    # Scripted financier acts on disclosed observation, not hidden truth.
    req=k.request_finance(1,'SPN','DEV',D('60'),'DEVELOPMENT',(obs.id,)); k.decide_finance(req.id,'FIN',True,'SCRIPTED_POSITIVE_OBSERVATION')
    k.reserve_earth_supply('EARTH:X',1,D('60'))
    k.spend_reserved_capex(1,'DEV','earth_supplier',D('60'),'MINE','OFF:T1',financing_origin_nodes=('EARTH:X',)); k.capitalize('MINE',D('10'))
    extracted=k.extract_bounded(2,'SPN','RES',D('5'))
    # Surface resolution discovers no usable deposit: exploration knowledge and failed development are written off.
    k.resolve_exploration(wip,False); del k.state.assets['MINE']
    k.assert_mvp_invariants()
    return k,draw,extracted

def stock_binding_fixture():
    k,obs,wip,draw=paid_exploration_fixture('TINY_STOCK',D('2'),D('0'),D('0'))
    k.resolve_exploration(wip,True)
    q=k.extract_bounded(2,'SPN','RES',D('5'))
    return k,q

def market_conservation_fixture():
    k,obs,wip,draw=paid_exploration_fixture('MARKET_STOCK',D('10'),D('0'),D('0'))
    k.resolve_exploration(wip,True); q=k.extract_bounded(2,'SPN','RES',D('5'))
    value=k.sell_to_market(2,'SPN','RES',q,D('20'),'earth_market')
    return k,q,value

def disposition_fixture(mode):
    k=build3_base('DISPOSITION_'+mode,D('20'),D('0'),D('0'))
    k.state.accounts['sponsor_funds'].balance=D('100')
    result=k.dispose_surplus(1,'SPN','sponsor_funds',D('80'),mode,earth_account='public_funds',local_account='local_funds')
    return k,result
