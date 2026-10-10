"""Disposable Build 8 sponsor/executor economic experiment. Authored scenario, not canon."""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.prospecting import derive_mobilization
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from .opening import build_country_opening

PUBLIC = {
 'NASA':('USA',), 'CNSA':('CHN',), 'Roscosmos':('RUS',),
 'ISRO':('IND',), 'JAXA':('JPN',),
 'ESA':('DEU','FRA','ITA','GBR','ESP','NLD','BEL','SWE','CHE','AUT','NOR','POL'),
 'CNES':('FRA',), 'DLR':('DEU',), 'CSA':('CAN',),
 'KASA':('KOR',), 'Australian Space Agency':('AUS',), 'UAE Space Agency':('ARE',)
}
PRIVATE = {
 'SpaceX':('USA',), 'Blue Origin':('USA',),
 'Axiom':('USA','SAU','QAT','KOR','HUN','JPN'), 'ispace':('JPN',),
 'Interlune':('USA',), 'Isar Aerospace':('DEU','GBR','USA'),
 'Starlab':('USA','DEU','FRA','JPN','CAN'), 'LandSpace':('CHN',)
}
# Authored weights within ONE national envelope, not ownership shares.
PREFERENCES = {
 'USA':{'NASA':5,'SpaceX':3,'Blue Origin':2,'Axiom':1,'Interlune':1,'Starlab':1,'Isar Aerospace':1},
 'CHN':{'CNSA':5,'LandSpace':2}, 'JPN':{'JAXA':5,'ispace':2,'Axiom':1,'Starlab':1},
 'DEU':{'ESA':3,'DLR':3,'Isar Aerospace':2,'Starlab':1},
 'FRA':{'ESA':3,'CNES':4,'Starlab':1}, 'CAN':{'CSA':5,'Starlab':2},
 'KOR':{'KASA':5,'Axiom':1}, 'GBR':{'ESA':3,'Isar Aerospace':2}
}
# Fixed economic domicile and coarse delivery capability.
EXECUTORS = {
 'Astrobotic':('USA',('LAND','BUILD')), 'CASC':('CHN',('BUILD','LAUNCH','LAND')),
 'RKK Energia':('RUS',('BUILD','LAUNCH')), 'HAL / L&T':('IND',('BUILD','LAUNCH')),
 'Mitsubishi Heavy Industries':('JPN',('BUILD','LAUNCH')),
 'Thales Alenia Space':('FRA',('BUILD','RUN')),
 'Airbus Defence and Space':('FRA',('BUILD','RUN')),
 'OHB':('DEU',('BUILD',)), 'MDA Space':('CAN',('BUILD','RUN')),
 'Hanwha Aerospace':('KOR',('BUILD','LAUNCH')),
 'Toyota':('JPN',('BUILD','RUN')), 'SpaceX':('USA',('BUILD','LAUNCH','RUN')),
 'Blue Origin':('USA',('BUILD','LAUNCH','LAND')),
 'ispace':('JPN',('LAND','RUN')), 'Northrop Grumman':('USA',('BUILD','RUN')),
 'Isar Aerospace':('DEU',('LAUNCH',))
}
# Motivation selects an authored objective and cost. All numbers fictional model units.
PROJECTS = {
 'NASA':('STRATEGIC','LAND',D('.045')), 'CNSA':('STRATEGIC','LAND',D('.045')),
 'Roscosmos':('STRATEGIC','LAUNCH',D('.030')),
 'ISRO':('SCIENTIFIC','BUILD',D('.015')),
 'JAXA':('SCIENTIFIC','LAND',D('.030')),
 'ESA':('SCIENTIFIC','BUILD',D('.030')),
 'CNES':('SCIENTIFIC','BUILD',D('.015')),
 'DLR':('SCIENTIFIC','BUILD',D('.015')),
 'CSA':('SCIENTIFIC','RUN',D('.015')),
 'KASA':('STRATEGIC','LAUNCH',D('.030')),
 'Australian Space Agency':('SCIENTIFIC','BUILD',D('.015')),
 'UAE Space Agency':('STRATEGIC','BUILD',D('.045')),
 'SpaceX':('COMMERCIAL','LAUNCH',D('.090')),
 'Blue Origin':('COMMERCIAL','LAUNCH',D('.090')),
 'Axiom':('COMMERCIAL','RUN',D('.045')),
 'ispace':('COMMERCIAL','LAND',D('.045')),
 'Interlune':('COMMERCIAL','BUILD',D('.090')),
 'Isar Aerospace':('COMMERCIAL','LAUNCH',D('.045')),
 'Starlab':('COMMERCIAL','RUN',D('.090')),
 'LandSpace':('COMMERCIAL','LAUNCH',D('.045'))
}

def run_network(root: Path, year=2026):
    kernel, _, capacities, _ = build_country_opening(root)
    sponsors={**{s:('PUBLIC',c) for s,c in PUBLIC.items()},
              **{s:('PRIVATE',c) for s,c in PRIVATE.items()}}
    scenario=load_prospecting_scenario()
    by_country={}
    for sponsor,(_,countries) in sponsors.items():
        for country in countries:
            if (country,year) in capacities:
                by_country.setdefault(country,[]).append(
                    (sponsor,D(PREFERENCES.get(country,{}).get(sponsor,1))))
    origins={}
    for country in sorted(by_country):
        # Explicit opportunity assumption for this experiment, not a discovered fact.
        _,_,_,amount=derive_mobilization(
            investment_proxy=capacities[country,year],
            commercial_opportunity=D(1),scenario=scenario)
        # Only 2% of the mobilization ceiling is offered to this network trial.
        amount *= D('.02')
        key='network:origin:'+country
        kernel.add_account(key,'COUNTRY:'+country,'EARTH:'+country,
                           AccountKind.EARTH_BOUNDARY,amount)
        origins[country]=(key,amount)
    budgets={}
    for sponsor,(_,countries) in sponsors.items():
        key='network:budget:'+sponsor
        kernel.add_account(key,sponsor,'EARTH:'+countries[0],AccountKind.FUNDS,D(0))
        budgets[sponsor]=key
    for country,entries in sorted(by_country.items()):
        origin,amount=origins[country]
        total=sum((w for _,w in entries),D(0))
        for i,(sponsor,weight) in enumerate(entries):
            share=(kernel.state.accounts[origin].balance if i==len(entries)-1
                   else amount*weight/total)
            kernel.transfer(year,origin,budgets[sponsor],share,TxPurpose.OTHER_INVESTMENT)
    executor_accounts={}
    rows=[]
    for sponsor,(kind,_) in sponsors.items():
        budget=budgets[sponsor]
        opening=kernel.state.accounts[budget].balance
        motive,capability,cost=PROJECTS[sponsor]
        eligible=sorted(e for e,(_,caps) in EXECUTORS.items() if capability in caps)
        # Prefer the original relationship when capable; otherwise choose a capable supplier.
        preferred={
          'NASA':'Astrobotic','CNSA':'CASC','Roscosmos':'RKK Energia',
          'ISRO':'HAL / L&T','JAXA':'Mitsubishi Heavy Industries',
          'ESA':'Thales Alenia Space','CNES':'Airbus Defence and Space',
          'DLR':'OHB','CSA':'MDA Space','KASA':'Hanwha Aerospace',
          'Australian Space Agency':'Toyota','UAE Space Agency':'Thales Alenia Space',
          'SpaceX':'SpaceX','Blue Origin':'Blue Origin','Axiom':'Thales Alenia Space',
          'ispace':'ispace','Interlune':'Northrop Grumman',
          'Isar Aerospace':'Isar Aerospace','Starlab':'MDA Space','LandSpace':'CASC'
        }[sponsor]
        executor=preferred if preferred in eligible else eligible[0]
        outcome='WAIT'
        if opening>=cost:
            location='OFF:NETWORK:'+sponsor
            project='network:project:'+sponsor
            cash='network:cash:'+sponsor
            kernel.add_node(location,NodeKind.OFFWORLD)
            kernel.add_account(cash,sponsor,location,AccountKind.PROJECT_CASH,D(0))
            kernel.add_project(project,location,cash,{sponsor:D(1)})
            kernel.add_commitment('network:commit:'+sponsor,sponsor,project,cost)
            kernel.disburse(year,'network:commit:'+sponsor,budget,cost)
            if executor not in executor_accounts:
                ek='network:revenue:'+executor
                kernel.add_account(ek,executor,'EARTH:'+EXECUTORS[executor][0],
                                   AccountKind.FUNDS,D(0))
                executor_accounts[executor]=ek
            # Award is not delivery: retain project cash until an authorized
            # physical development plan and supply permit staged expenditure.
            outcome='AWARDED_PENDING_PLAN'
        rows.append(dict(sponsor=sponsor,kind=kind,executor=executor,
                         executor_home=EXECUTORS[executor][0],motive=motive,
                         capability=capability,cost=str(cost),opening=str(opening),
                         outcome=outcome,remaining=str(kernel.state.accounts[budget].balance)))
    kernel.assert_invariants()
    return rows,{e:str(kernel.state.accounts[a].balance)
                 for e,a in executor_accounts.items()},kernel.fingerprint()
