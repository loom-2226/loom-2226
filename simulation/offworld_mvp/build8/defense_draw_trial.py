"""Authored USA/China defense-capital response sweep, no simulated war."""
from dataclasses import replace
from decimal import Decimal as D
from offworld_kernel.model import AccountKind
from simulation.offworld_mvp.defense_capital import DefenseDials, Crisis, draw, CODE_VERSION
from .opening import build_country_opening, EARTH_V4_ROOT

# SINGLE AUTHORING TABLE. Fraction of investment, not military expenditure.
DIALS = {(country,year): DefenseDials(D('1'),D('1'),D('2'),D('.01'))
         for country in ('USA','CHN') for year in range(2026,2036)}
EXAMPLE_CRISIS = Crisis('USA_CHINA_SPACE_CRISIS',('USA','CHN'),2027,2029,D('.4'))
SEED = 'BUILD8-DEFENSE-DRAW-V1'


def run(*, enabled=False, pressure=D('.3'), overall_scale=None, crises=(), root=EARTH_V4_ROOT):
    k,h,capacities,_=build_country_opening(root,world_seed=SEED)
    results=[]
    for year in range(2026,2031):
        for country in ('USA','CHN'):
            # Same civilian draw in every scenario; never subtract defense from it.
            civil=k.mobilize_country_capital(year-2025,country,capacities[country,year],D(1),
                h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
            defense=D(0);names=()
            dials=DIALS[country,year]
            if overall_scale is not None:dials=replace(dials,overall_scale=D(overall_scale))
            if enabled:
                account=f'defense:funds:{country}'
                if account not in k.state.accounts:
                    k.add_account(account,'DEFENSE:'+country,'EARTH:'+country,AccountKind.FUNDS)
                receipt=draw(k,year,country,capacities[country,year],D(pressure),dials,h['prospecting_scenario'].investment_proxy_units_per_model_currency,
                             f'b8_source:{country}',account,crises=crises,seed=SEED)
                defense=receipt.amount;names=receipt.crises
            results.append({'year':year,'country':country,'civilian':str(civil.mobilized_cash),
                            'defense':str(defense),'crises':','.join(names),'seed':SEED,
                            'code_version':CODE_VERSION,'overall_scale':str(dials.overall_scale),
                            'country_scale':str(dials.country_scale),'steepness':str(dials.steepness),
                            'cap':str(dials.cap)})
    k.assert_invariants()
    return results,k


def sweep(scales=('0','.25','.5','1','2'),*,crises=(),root=EARTH_V4_ROOT):
    return [dict(scale=str(scale),**row) for scale in scales
            for row in run(enabled=True,overall_scale=D(scale),crises=crises,root=root)[0]]
