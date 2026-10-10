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


def build_country_opening(root: Path):
    capacities, provenance = load_investment_capacity(root)
    kernel, history = _build_kernel(None, load_config(), world_seed='BUILD8-80-COUNTRY-10-YEAR', world=WORLD)
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
    kernel.boundary_manifest = replace(kernel.boundary_manifest, assertions=originals+assertions)
    for country in countries:
        node=f'EARTH:{country}'
        if node not in kernel.state.nodes:
            kernel.add_node(node,NodeKind.EARTH)
        kernel.add_account(f'b8_source:{country}',f'COUNTRY:{country}',node,AccountKind.EARTH_BOUNDARY,Decimal(0))
        kernel.add_account(f'b8_funds:{country}',f'CAPITAL_POOL:{country}',node,AccountKind.FUNDS,Decimal(0))
        kernel.capital_coupling.setdefault(country,dict.fromkeys(('F','X','R','S'),Decimal(0)))
    old=kernel.boundary_manifest
    input_id='BUILD8_INPUT:'+content_hash((old.input_snapshot_id,provenance,tuple((c,y,str(v)) for (c,y),v in sorted(capacities.items()))))
    sources=(*old.real_source_refs,('BUILD8_EARTH_V4_COUNTRY_INVESTMENT',content_hash(provenance)))
    opening=tuple((key,canonical(kernel._boundary_opening_value(key)))
                  for key in ('accounts','agents','resources','constraints','population','earth_admission_receipts'))
    kernel.run_identity=replace(kernel.run_identity,input_snapshot_id=input_id)
    kernel.boundary_manifest=replace(old,input_snapshot_id=input_id,real_source_refs=sources,
                                     opening_bindings=opening,
                                     opening_state_hash=content_hash(kernel._boundary_projection()))
    kernel.run_identity=replace(kernel.run_identity,input_snapshot_id=input_id)
    validate_opening(kernel)
    return kernel,history,capacities,provenance
