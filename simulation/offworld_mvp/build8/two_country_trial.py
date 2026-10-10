"""Isolated two-country transaction trial, not a qualified Build 8 runtime."""
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind
from simulation.offworld_mvp.build7.generated_campaign import _build_kernel, load_config
from .country_capital_input import load_investment_capacity

WORLD = {'scenario_id':'00000000-0000-0000-0000-000000000001',
         'scenario_key':'BUILD8_TWO_COUNTRY_TRIAL','body_count':90,
         'sealed_world_digest':'0'*64}


def run_two_country_trial(root: Path, countries=('USA','AUS')):
    """Exercise the real kernel transfer on isolated state, never the DB campaign."""
    capacities, provenance = load_investment_capacity(root)
    kernel, history = _build_kernel(None, load_config(), world_seed='BUILD8-TWO-COUNTRY', world=WORLD)
    template = next(a for a in kernel.boundary_manifest.assertions
                    if a.subject_id == 'USA' and a.concept == 'investment' and a.valid_from == '2026')
    records = []
    for country in countries:
        if country not in {c for c, year in capacities if year == 2026}:
            raise ValueError(f'country absent: {country}')
        investment = capacities[country, 2026]
        assertion = replace(template, assertion_id=f'B8:{country}:2026:investment',
                            subject_id=country, scope=f'COUNTRY:{country}',
                            value=str(investment),
                            source_refs=(provenance['designation'], f'{country}:2026'),
                            source_hashes=tuple(s['sha256'] for s in provenance['sources']),
                            authorization_ref='BUILD8_TWO_COUNTRY_ISOLATED_TRIAL',
                            warrant_refs=('BUILD8_EXPERIMENT_A_LOCAL_PROJECTION',))
        # Replace USA's inherited projection for the trial; retain other countries' records.
        assertions=tuple(a for a in kernel.boundary_manifest.assertions
                         if not (a.subject_id == country and a.concept == 'investment'
                                 and a.valid_from == '2026'))
        kernel.boundary_manifest=replace(kernel.boundary_manifest,
                                         assertions=(*assertions, assertion))
        node=f'EARTH:{country}'
        if node not in kernel.state.nodes:
            kernel.add_node(node, NodeKind.EARTH)
        source=f'b8_source:{country}'
        destination=f'b8_funds:{country}'
        kernel.add_account(source, f'COUNTRY:{country}', node, AccountKind.EARTH_BOUNDARY, Decimal(0))
        kernel.add_account(destination, f'CAPITAL_POOL:{country}', node, AccountKind.FUNDS, Decimal(0))
        kernel.capital_coupling.setdefault(country, dict.fromkeys(('F','X','R','S'), Decimal(0)))
        result=kernel.mobilize_country_capital(1,country,investment,Decimal(1),
                                               history['prospecting_scenario'],source,destination)
        amount=result.mobilized_cash
        assert kernel.state.accounts[source].balance == -amount
        assert kernel.state.accounts[destination].balance == amount
        assert kernel.capital_coupling[country]['F'] == amount
        records.append({'country':country,'investment':str(investment),
                        'mobilized':str(amount),'transaction_id':result.transaction_id})
    assert len(kernel.capital_mobilization_records)==len(countries)
    return records
