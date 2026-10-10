"""Shared authored setup for disposable Build 8 Sponsor trials; no new behavior."""
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening
from .two_economy_source_finance_trial import ROOT

SPONSORS=('Axiom','Blue Origin','Interlune','SpaceX')
# Fictional model-unit cost tiers; same public candidate list for everyone.
OPTIONS=(('HEAVY',D('.40')),('MEDIUM',D('.25')),('LIGHT',D('.10')))
EXECUTORS={'Axiom':'Thales Alenia Space','Blue Origin':'Blue Origin',
           'Interlune':'Northrop Grumman','SpaceX':'SpaceX'}
HOMES={'Thales Alenia Space':'FRA','Blue Origin':'USA',
       'Northrop Grumman':'USA','SpaceX':'USA'}
# Distinct objectives rank different cost tiers first. Identical control overrides these.
RANKS={'Axiom':('LIGHT','MEDIUM','HEAVY'),
       'Blue Origin':('HEAVY','MEDIUM','LIGHT'),
       'Interlune':('MEDIUM','LIGHT','HEAVY'),
       'SpaceX':('HEAVY','LIGHT','MEDIUM')}

def episode_setup():
    k,h,capacities,_=build_country_opening(ROOT,world_seed='B8_EPISODE_A')
    rec=k.mobilize_country_capital(1,'USA',capacities['USA',2026],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
    # The episode's deliberately scarce envelope is separate from the 80-country trial.
    envelope=D('.60'); assert rec.mobilized_cash>envelope
    k.add_account('episode:budget','EPISODE','EARTH:USA',AccountKind.FUNDS,D(0))
    k.transfer(1,'b8_funds:USA','episode:budget',envelope,TxPurpose.OTHER_INVESTMENT)
    for sponsor in SPONSORS:
        k.add_account('episode:funds:'+sponsor,sponsor,'EARTH:USA',AccountKind.FUNDS,D(0))
    for executor,home in sorted(HOMES.items()):
        node='EARTH:'+home
        if node not in k.state.nodes:k.add_node(node,NodeKind.EARTH)
        k.add_account('episode:revenue:'+executor,executor,node,AccountKind.FUNDS,D(0))
    return k,h,capacities,envelope,rec
