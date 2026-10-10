"""Build 8 80-country pre-epoch opening. Experimental, not persistent WA genesis."""
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.causal_trace import canonical, content_hash
from offworld_kernel.boundary import validate_opening
from simulation.offworld_mvp.build7.generated_campaign import _build_kernel, load_config
from .country_capital_input import load_investment_capacity
from .two_country_trial import WORLD


def build_country_opening(root: Path, *, world=None, world_seed='BUILD8-80-COUNTRY-10-YEAR'):
    capacities, provenance = load_investment_capacity(root)
    kernel, history = _build_kernel(None, load_config(), world_seed=world_seed, world=WORLD if world is None else world)
    template = next(a for a in kernel.boundary_manifest.assertions
                    if a.subject_id == 'USA' and a.concept == 'investment' and a.valid_from == '2026')
    countries = tuple(sorted({c for c, _ in capacities}))
    originals = tuple(a for a in kernel.boundary_manifest.assertions
                      if not (a.concept == 'investment' and a.world_context == 'REAL'
                              and a.subject_id in countries and 2026 <= int(a.valid_from) <= 2035))
    assertions = tuple(replace(template, assertion_id=f'B8:{country}:{year}:investment',
                               subject_id=country, scope=f'COUNTRY:{country}',
                               value=str(capacities[country,year]), valid_from=str(year), valid_to=str(year),
                               source_refs=(provenance['designation'],f'{country}:{year}'),
                               source_hashes=tuple(s['sha256'] for s in provenance['sources']),
                               authorization_ref='BUILD8_EXPERIMENT_A_OPENING_TRIAL',
                               warrant_refs=('BUILD8_EXPERIMENT_A_LOCAL_PROJECTION',))
                       for country in countries for year in range(2026,2036))
    scenario_template = next(a for a in kernel.boundary_manifest.assertions
                             if a.subject_id == 'USA' and a.concept == 'investment'
                             and a.world_context == 'SCENARIO' and a.valid_from == '1')
    scenario_assertions = tuple(replace(scenario_template,
        assertion_id=f'B8:{country}:{year}:scenario_investment',
        subject_id=country,scope=f'COUNTRY:{country}',value=str(capacities[country,year]),
        valid_from=str(year-2025),valid_to=str(year-2025),
        available_from=str(year-2025),source_time=str(year-2025),
        source_refs=(provenance['designation'],f'{country}:{year}'),
        source_hashes=tuple(s['sha256'] for s in provenance['sources']))
        for country in countries if country != 'USA' for year in (2026,))
    usa_contract = next(c for c in kernel.boundary_manifest.allowed_use_contracts
                        if c[0] == 'SYS:mobilize_country_capital' and c[2] == 'investment'
                        and c[3] == 'COUNTRY:USA')
    extra_contracts = tuple((c[0], c[1], c[2], f'COUNTRY:{country}', *c[4:])
                            for country in countries if country != 'USA' for c in (usa_contract,))
    kernel.boundary_manifest = replace(kernel.boundary_manifest, assertions=originals+assertions+scenario_assertions,
                                       allowed_use_contracts=(*kernel.boundary_manifest.allowed_use_contracts,*extra_contracts))
    for country in countries:
        node=f'EARTH:{country}'
        if node not in kernel.state.nodes:
            kernel.add_node(node,NodeKind.EARTH)
        kernel.add_account(f'b8_source:{country}',f'COUNTRY:{country}',node,AccountKind.EARTH_BOUNDARY,Decimal(0))
        kernel.add_account(f'b8_funds:{country}',f'CAPITAL_POOL:{country}',node,AccountKind.FUNDS,Decimal(0))
        kernel.capital_coupling.setdefault(country,dict.fromkeys(('F','X','R','S'),Decimal(0)))
    old=kernel.boundary_manifest
    input_id='BUILD8_INPUT:'+content_hash((old.input_snapshot_id,provenance,tuple((c,y,str(v)) for (c,y),v in sorted(capacities.items())),extra_contracts,content_hash(scenario_assertions)))
    sources=(*old.real_source_refs,('BUILD8_EARTH_V4_COUNTRY_INVESTMENT',content_hash(provenance)))
    opening=tuple((key,canonical(kernel._boundary_opening_value(key)))
                  for key in ('accounts','agents','resources','constraints','population','earth_admission_receipts'))
    kernel.run_identity=replace(kernel.run_identity,input_snapshot_id=input_id,universe_version='BUILD8_EXPERIMENT_A')
    build8_run_id=old.run_id+':B8:'+content_hash((input_id,old.run_id))[:12]
    kernel.boundary_manifest=replace(old,run_id=build8_run_id,input_snapshot_id=input_id,real_source_refs=sources,
                                     opening_bindings=opening,
                                     opening_state_hash=content_hash(kernel._boundary_projection()))
    validate_opening(kernel)
    return kernel,history,capacities,provenance
