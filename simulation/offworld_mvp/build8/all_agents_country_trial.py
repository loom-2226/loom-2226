"""One disposable Build 8 experiment: all authored Sponsors and Executors over all 80 country envelopes.

Unlisted countries retain funds; no fictional Sponsors are manufactured.
"""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, TxPurpose
from .opening import build_country_opening
from .sponsor_executor_network_trial import PUBLIC, PRIVATE, EXECUTORS, PREFERENCES
from .two_economy_source_finance_trial import ROOT

EXCLUSIONS = {("Axiom", "QAT"): "No 2026 capacity record in Earth v4"}
DEFAULT_APPETITE = D("0.5")
COUNTRY_APPETITE = {}  # Optional country-specific overrides, fractions in [0,1].
ROUNDING_TOLERANCE = D("1e-24")

def run(root=ROOT,year=2026,report=False,appetites=None,preferences=None,excluded_sponsors=(),inspect=None):
    k,h,capacities,_=build_country_opening(root)
    roster={s:homes for s,homes in {**PUBLIC,**PRIVATE}.items() if s not in excluded_sponsors}
    assert roster
    executors={name:(country,caps) for name,(country,caps) in EXECUTORS.items()}
    assert len(executors)==16
    # Sponsors and executors can overlap; these are roles, not duplicate people.
    unique_agents=set(roster)|set(executors)
    countries=sorted(c for c,y in capacities if y==year)
    assert len(countries)==80
    pairs={(s,c) for s,homes in roster.items() for c in homes}
    active_exclusions={pair:reason for pair,reason in EXCLUSIONS.items() if pair[0] in roster}
    unknown_exclusions=set(active_exclusions)-pairs
    if unknown_exclusions:
        raise ValueError(f"Exclusions not in Sponsor roster: {sorted(unknown_exclusions)}")
    missing=sorted({country for sponsor,country in pairs if (sponsor,country) not in active_exclusions and (country,year) not in capacities})
    if report:
        for (sponsor,country),reason in sorted(active_exclusions.items()):
            print(f"EXCLUDED {sponsor} / {country}: {reason}")
        print(f"DEFAULT_APPETITE {DEFAULT_APPETITE}")
        print(f"ROUNDING_TOLERANCE {ROUNDING_TOLERANCE}")
    if missing:
        raise ValueError(f"Sponsor economies without {year} capital pools: {missing}")
    allocation_count=0;mobilized=D(0);allocated=D(0);idle=0;executor_count=0;zero_allocations=0
    observed={}
    # Executors are suppliers, not capital recipients. Register their existing
    # country domiciles and capabilities without manufacturing demand.
    for name,(country,caps) in sorted(executors.items()):
        assert country in countries and caps
        key=f"b8:executor:revenue:{name}"
        k.add_account(key,name,"EARTH:"+country,AccountKind.FUNDS,D(0))
        executor_count+=1
    for country in countries:
        rec=k.mobilize_country_capital(year-2025,country,capacities[country,year],D(1),h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
        mobilized+=rec.mobilized_cash
        pool=f'b8_funds:{country}'
        eligible=sorted(s for s,homes in roster.items() if country in homes and (s,country) not in active_exclusions)
        appetite=D((appetites if appetites is not None else COUNTRY_APPETITE).get(country,DEFAULT_APPETITE))
        if not D(0)<=appetite<=D(1):
            raise ValueError(f"Invalid appetite {country}: {appetite}")
        if not eligible:
            idle+=1
        weights={s:D((preferences if preferences is not None else PREFERENCES).get(country,{}).get(s,1)) for s in eligible}
        if any(w<=0 for w in weights.values()):
            raise ValueError(f"Nonpositive Sponsor weight in {country}")
        total=sum(weights.values(),D(0))
        # Explicit trial allocation: national appetite times mobilized envelope.
        budget=rec.mobilized_cash*appetite if total else D(0)
        remaining_budget=budget
        shares={}
        for index,sponsor in enumerate(eligible):
            share=remaining_budget if index==len(eligible)-1 else budget*weights[sponsor]/total
            remaining_budget-=share
            shares[sponsor]=share
            dest=f'b8:sourcebacked:{country}:{sponsor}'
            k.add_account(dest,sponsor,'EARTH:'+country,AccountKind.FUNDS,D(0))
            if share:
                k.transfer(year-2025,pool,dest,share,TxPurpose.OTHER_INVESTMENT,parent_ids=(rec.transaction_id,))
                allocated+=share;allocation_count+=1
            else:
                zero_allocations+=1
            assert k.capital_coupling[country]['F']==rec.mobilized_cash
            assert k.capital_coupling[country]['X']==0
        assert abs(sum(shares.values(),D(0))-budget)<ROUNDING_TOLERANCE,(country,sum(shares.values(),D(0)),budget)
        observed[country]=(rec.mobilized_cash,budget,shares.copy(),k.state.accounts[pool].balance)
        held=k.state.accounts[pool].balance+sum(a.balance for name,a in k.state.accounts.items() if name.startswith(f'b8:sourcebacked:{country}:'))
        assert abs(held-rec.mobilized_cash)<ROUNDING_TOLERANCE,(country,held,rec.mobilized_cash)
    k.assert_invariants()
    if report:
        print(f"ZERO_ALLOCATIONS {zero_allocations}")
        print(f"NO_ELIGIBLE_SPONSOR_ECONOMIES {idle}")
    result=(len(countries),len(roster),executor_count,len(unique_agents),allocation_count,idle,str(mobilized),str(allocated),k.fingerprint())
    return (result,observed) if inspect else result

if __name__=='__main__':
    a=run(report=True);b=run();assert a==b
    print('ALL_AGENTS_80_COUNTRIES_PASS',a)
