"""Disposable explicit country-to-Sponsor allocation. Not a policy authorization."""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import TxPurpose
from .opening import build_country_opening


def run_allocation(root: Path, allocation=D('2')):
    k,h,capacities,_=build_country_opening(root)
    country='USA'
    rec=k.mobilize_country_capital(1,country,capacities[country,2026],D(1),
        h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
    amount=D(allocation)
    if amount<0 or amount>rec.mobilized_cash:
        raise ValueError('allocation exceeds available USA country capital')
    # This is an explicit authored scenario choice, not an inferred government decision.
    k.transfer(1,'b8_funds:USA','sponsor_funds',amount,TxPurpose.OTHER_INVESTMENT)
    pool=k.state.accounts['b8_funds:USA'].balance
    sponsor=k.state.accounts['sponsor_funds'].balance
    assert pool+sponsor==rec.mobilized_cash
    assert k.capital_coupling[country]['F']==rec.mobilized_cash
    assert k.capital_coupling[country]['X']==0
    assert not k.state.projects
    k.assert_invariants()
    return (str(pool),str(sponsor),str(k.capital_coupling[country]['F']),
            str(k.capital_coupling[country]['X']),k.fingerprint())
