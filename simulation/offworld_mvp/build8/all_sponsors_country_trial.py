"""One disposable Build 8 experiment: all authored Sponsors over all 80 country envelopes.

Unlisted countries retain funds; no fictional Sponsors are manufactured.
"""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, TxPurpose
from .opening import build_country_opening
from .sponsor_executor_network_trial import PUBLIC, PRIVATE, PREFERENCES
from .two_economy_source_finance_trial import ROOT

def run(root=ROOT,year=2026):
    k,h,capacities,_=build_country_opening(root)
    roster={**PUBLIC,**PRIVATE}
    assert len(roster)==20
    countries=sorted(c for c,y in capacities if y==year)
    assert len(countries)==80
    allocation_count=0;mobilized=D(0);allocated=D(0);idle=0
    for country in countries:
        rec=k.mobilize_country_capital(year-2025,country,capacities[country,year],D(1),h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
        mobilized+=rec.mobilized_cash
        pool=f'b8_funds:{country}'
        eligible=sorted(s for s,homes in roster.items() if country in homes)
        if not eligible:
            idle+=1
        weights={s:D(PREFERENCES.get(country,{}).get(s,1)) for s in eligible}
        total=sum(weights.values(),D(0))
        # Explicit trial allocation: reserve half the mobilized envelope for eligible Sponsors.
        budget=rec.mobilized_cash/D(2) if total else D(0)
        for sponsor in eligible:
            share=budget*weights[sponsor]/total
            dest=f'b8:sourcebacked:{country}:{sponsor}'
            k.add_account(dest,sponsor,'EARTH:'+country,AccountKind.FUNDS,D(0))
            if share:
                k.transfer(year-2025,pool,dest,share,TxPurpose.OTHER_INVESTMENT,parent_ids=(rec.transaction_id,))
                allocated+=share;allocation_count+=1
            assert k.capital_coupling[country]['F']==rec.mobilized_cash
            assert k.capital_coupling[country]['X']==0
        held=k.state.accounts[pool].balance+sum(a.balance for name,a in k.state.accounts.items() if name.startswith(f'b8:sourcebacked:{country}:'))
        assert abs(held-rec.mobilized_cash)<D('0.000000000000000000000001'),(country,held,rec.mobilized_cash)
    k.assert_invariants()
    return (len(countries),len(roster),allocation_count,idle,str(mobilized),str(allocated),k.fingerprint())

if __name__=='__main__':
    a=run();b=run();assert a==b
    print('ALL_SPONSORS_80_COUNTRIES_PASS',a)
