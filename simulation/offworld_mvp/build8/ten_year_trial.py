"""Build 8 disposable ten-year country-capital trial, no persistent genesis."""
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind
from simulation.offworld_mvp.build7.generated_campaign import _build_kernel, load_config
from .country_capital_input import load_investment_capacity
from .two_country_trial import WORLD


def run_ten_year_trial(root: Path, opportunity=True):
    capacities, provenance = load_investment_capacity(root)
    kernel, history = _build_kernel(None, load_config(), world_seed='BUILD8-80-COUNTRY-10-YEAR', world=WORLD)
    template = next(a for a in kernel.boundary_manifest.assertions
                    if a.subject_id == 'USA' and a.concept == 'investment' and a.valid_from == '2026')
    # Build 8-only Earth projection admission for a disposable kernel, not an authoritative genesis.
    country_codes = sorted({c for c, _ in capacities})
    originals = tuple(a for a in kernel.boundary_manifest.assertions
                      if not (a.concept == 'investment' and a.world_context == 'REAL'
                              and a.subject_id in country_codes and 2026 <= int(a.valid_from) <= 2035))
    assertions = tuple(replace(template, assertion_id=f'B8:{country}:{year}:investment',
                               subject_id=country, scope=f'COUNTRY:{country}',
                               value=str(capacities[country,year]), valid_from=str(year), valid_to=str(year),
                               source_refs=(provenance['designation'],f'{country}:{year}'),
                               source_hashes=tuple(s['sha256'] for s in provenance['sources']),
                               authorization_ref='BUILD8_DISPOSABLE_TEN_YEAR_TRIAL',
                               warrant_refs=('BUILD8_EXPERIMENT_A_LOCAL_PROJECTION',))
                       for country in country_codes for year in range(2026,2036))
    kernel.boundary_manifest=replace(kernel.boundary_manifest, assertions=originals+assertions)
    for country in country_codes:
        node=f'EARTH:{country}'
        if node not in kernel.state.nodes:
            kernel.add_node(node,NodeKind.EARTH)
        kernel.add_account(f'b8_source:{country}',f'COUNTRY:{country}',node,AccountKind.EARTH_BOUNDARY,Decimal(0))
        kernel.add_account(f'b8_funds:{country}',f'CAPITAL_POOL:{country}',node,AccountKind.FUNDS,Decimal(0))
        kernel.capital_coupling.setdefault(country,dict.fromkeys(('F','X','R','S'),Decimal(0)))
    totals={}
    for year in range(2026,2036):
        total=Decimal(0)
        for country in country_codes:
            record=kernel.mobilize_country_capital(year-2025,country,capacities[country,year],
                Decimal(int(opportunity)),history['prospecting_scenario'],
                f'b8_source:{country}',f'b8_funds:{country}')
            total+=record.mobilized_cash
        totals[year]=total
    for country in country_codes:
        total=sum((r.mobilized_cash for r in kernel.capital_mobilization_records if r.country_id==country),Decimal(0))
        assert kernel.state.accounts[f'b8_source:{country}'].balance==-total
        assert kernel.state.accounts[f'b8_funds:{country}'].balance==total
        assert kernel.capital_coupling[country]['F']==total
    assert len(kernel.capital_mobilization_records)==800
    return totals,provenance
