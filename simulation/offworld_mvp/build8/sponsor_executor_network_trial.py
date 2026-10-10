"""Disposable Build 8: 20 sponsors, 16 executor roles, country-routed capital.
Proxies from the three October 2026 research tables; no historical budget claims.
"""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening

# One row per organization. The first country is its home economy.
PUBLIC = {
 'NASA':('USA',), 'CNSA':('CHN',), 'Roscosmos':('RUS',),
 'ISRO':('IND',), 'JAXA':('JPN',),
 'ESA':('DEU','FRA','ITA','GBR','ESP','NLD','BEL','SWE','CHE','AUT','NOR','POL'),
 'CNES':('FRA',), 'DLR':('DEU',), 'CSA':('CAN',),
 'KASA':('KOR',), 'Australian Space Agency':('AUS',),
 'UAE Space Agency':('ARE',)
}
PRIVATE = {
 'SpaceX':('USA',), 'Blue Origin':('USA',),
 'Axiom':('USA','SAU','QAT','KOR','HUN','JPN'),
 'ispace':('JPN',), 'Interlune':('USA',),
 'Isar Aerospace':('DEU','GBR','USA'),
 'Starlab':('USA','DEU','FRA','JPN','CAN'),
 'LandSpace':('CHN',)
}
# Project's executor; an executor can serve several sponsors and need not be a sponsor.
CONTRACTORS = {
 'NASA':'Astrobotic', 'CNSA':'CASC', 'Roscosmos':'RKK Energia',
 'ISRO':'HAL / L&T', 'JAXA':'Mitsubishi Heavy Industries',
 'ESA':'Thales Alenia Space', 'CNES':'Airbus Defence and Space',
 'DLR':'OHB', 'CSA':'MDA Space', 'KASA':'Hanwha Aerospace',
 'Australian Space Agency':'Toyota', 'UAE Space Agency':'Thales Alenia Space',
 'SpaceX':'SpaceX', 'Blue Origin':'Blue Origin', 'Axiom':'Thales Alenia Space',
 'ispace':'ispace', 'Interlune':'Northrop Grumman',
 'Isar Aerospace':'Isar Aerospace', 'Starlab':'MDA Space',
 'LandSpace':'CASC'
}
# Equal shares among a sponsor's listed countries are deliberately authored,
# not claims about real ownership. Divide each country's capital pool across
# ALL participating sponsors to prevent duplicate national allocations.
COST = D('.015')

def run_network(root: Path, year=2026):
    kernel, _, capacities, _ = build_country_opening(root)
    sponsors = {**{s:('PUBLIC',c) for s,c in PUBLIC.items()},
                **{s:('PRIVATE',c) for s,c in PRIVATE.items()}}
    weights = {}
    for sponsor,(kind,countries) in sponsors.items():
        present = tuple(c for c in countries if (c,year) in capacities)
        for country in present:
            weights[sponsor,country] = D(1)/D(len(present))
    by_country = {}
    for (s,c),weight in weights.items():
        kind=sponsors[s][0]
        by_country.setdefault((kind,c),[]).append((s,weight))
    origins={}
    for kind,c in sorted(by_country):
        # 10% of reference investment is the experimental mobilization envelope.
        amt=capacities[c,year]*D('.1')
        key=f'network:origin:{kind}:{c}'
        kernel.add_account(key,'COUNTRY:'+c,'EARTH:'+c,AccountKind.EARTH_BOUNDARY,amt)
        origins[kind,c]=(key,amt)
    budgets={}
    for sponsor,(kind,countries) in sponsors.items():
        home=countries[0]
        key='network:budget:'+sponsor
        kernel.add_account(key,sponsor,'EARTH:'+home,AccountKind.FUNDS,D(0))
        budgets[sponsor]=key
    for (kind,c),entries in sorted(by_country.items()):
        origin,amt=origins[kind,c]
        total=sum((w for _,w in entries),D(0))
        for sponsor,w in entries:
            kernel.transfer(year,origin,budgets[sponsor],amt*w/total,TxPurpose.OTHER_INVESTMENT)
    executor_accounts={}
    rows=[]
    for sponsor,(kind,countries) in sponsors.items():
        budget=budgets[sponsor]
        opening=kernel.state.accounts[budget].balance
        executor=CONTRACTORS[sponsor]
        outcome='WAIT'
        if opening>=COST:
            location='OFF:NETWORK:'+sponsor
            project='network:project:'+sponsor
            cash='network:cash:'+sponsor
            kernel.add_node(location,NodeKind.OFFWORLD)
            kernel.add_account(cash,sponsor,location,AccountKind.PROJECT_CASH,D(0))
            kernel.add_project(project,location,cash,{sponsor:D(1)})
            kernel.add_commitment('network:commit:'+sponsor,sponsor,project,COST)
            kernel.disburse(year,'network:commit:'+sponsor,budget,COST)
            if executor not in executor_accounts:
                ek='network:revenue:'+executor
                # Contractor's domicile is an accounting label, not extra funding.
                kernel.add_account(ek,executor,'EARTH:'+countries[0],AccountKind.FUNDS,D(0))
                executor_accounts[executor]=ek
            kernel.transfer(year,cash,executor_accounts[executor],COST,TxPurpose.OTHER_INVESTMENT)
            outcome='CONTRACTED'
        rows.append(dict(sponsor=sponsor,kind=kind,executor=executor,
                         opening=str(opening),outcome=outcome,
                         remaining=str(kernel.state.accounts[budget].balance)))
    kernel.assert_invariants()
    return rows,{e:str(kernel.state.accounts[a].balance) for e,a in executor_accounts.items()},kernel.fingerprint()
