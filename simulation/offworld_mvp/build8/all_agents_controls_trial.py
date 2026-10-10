"""Five narrow, non-governed controls for the authored country/Sponsor trial."""
from decimal import Decimal as D
from .all_agents_country_trial import run, ROOT, PREFERENCES, ROUNDING_TOLERANCE
from .opening import build_country_opening
from .sponsor_executor_network_trial import PUBLIC, PRIVATE
from offworld_kernel.model import AccountKind, TxPurpose, NodeKind
from offworld_kernel.kernel import InvariantError

def controls():
    base=run()
    zero=run(appetites={'USA':D(0)})
    full=run(appetites={'USA':D(1)})
    assert D(zero[7]) < D(base[7]) < D(full[7])
    print('PASS appetite 0%, 100%: aggregate allocation decreases/increases; per-country reconciliation runs')
    equal={**PREFERENCES,'USA':{s:1 for s,homes in {**PUBLIC,**PRIVATE}.items() if 'USA' in homes}}
    even,by_country=run(preferences=equal,inspect=True)
    shares=by_country["USA"][2]
    assert max(shares.values())-min(shares.values())<ROUNDING_TOLERANCE
    assert sum(shares.values(),D(0))==by_country["USA"][1]
    print("PASS equal weights: every USA Sponsor share equal within decimal precision; exact sum")
    # Existing kernel transfer enforces the available balance: the second
    # claimant cannot spend money already transferred to the first.
    k,h,capacities,_=build_country_opening(ROOT)
    rec=k.mobilize_country_capital(1,'USA',capacities['USA',2026],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
    pool='b8_funds:USA';budget=rec.mobilized_cash*D('.5')
    for name in ('FIRST','SECOND'):
        k.add_account('control:'+name,name,'EARTH:USA',AccountKind.FUNDS,D(0))
    k.transfer(1,pool,'control:FIRST',budget,TxPurpose.OTHER_INVESTMENT)
    first=k.state.accounts['control:FIRST'].balance
    cost=budget*D('.75')
    k.add_node('OFF:COMPETITION',NodeKind.OFFWORLD)
    for name in ('FIRST','SECOND'):
        cash='control:cash:'+name
        project='control:project:'+name
        k.add_account(cash,name,'OFF:COMPETITION',AccountKind.PROJECT_CASH,D(0))
        k.add_project(project,'OFF:COMPETITION',cash,{name:D(1)})
        k.add_commitment('control:commit:'+name,name,project,cost)
    assert first>=cost
    k.disburse(1,'control:commit:FIRST','control:FIRST',cost)
    before=k.fingerprint()
    try:
        k.disburse(1,'control:commit:SECOND','control:SECOND',cost)
    except InvariantError:
        pass
    else:
        raise AssertionError('Unfunded second disbursement succeeded')
    assert k.fingerprint()==before
    assert k.state.accounts['control:cash:FIRST'].balance==cost
    assert k.state.accounts['control:cash:SECOND'].balance==0
    k.assert_invariants()
    print('PASS competition: both commitments exist; first disburses; second rejected without mutation')
    _,base_countries=run(inspect=True)
    without,without_countries=run(excluded_sponsors=('Interlune',),inspect=True)
    for country in base_countries:
        if country!='USA':
            assert base_countries[country]==without_countries[country],country
    print('PASS removal: all 79 unaffected economies have identical allocations and pool balances')
    print('CONTROL_SUMMARY',base[:8],zero[:8],full[:8],even[:8],without[:8])
if __name__=='__main__':controls()
