"""Explicit isolated World Authority Build 8 country-capital epoch experiment."""
from decimal import Decimal
from pathlib import Path
from simulation.offworld_mvp.build7.generated_campaign import (
    _world_from_run, _attach_persistence, _record_empty_year)
from simulation.offworld_mvp.build7 import runtime_flow
from .opening import build_country_opening


def run_persistent_trial(root: Path, control_run_id: str, countries=('AUS',),
                         reference_service='reference_reader',runtime_service='runtime'):
    world,seed=_world_from_run(reference_service,runtime_service,control_run_id)
    kernel,history,capacities,_=build_country_opening(root,world=world,world_seed=seed)
    _attach_persistence(history,None,runtime_service,{})
    _record_empty_year(kernel,history,2026)
    results=[]
    for country in countries:
        if (country,2026) not in capacities:
            raise ValueError('unknown country')
        runtime_flow.system_epoch(kernel,history,'mobilize_country_capital','1',
            (1,country,capacities[country,2026],Decimal(1),history['prospecting_scenario'],
             f'b8_source:{country}',f'b8_funds:{country}'))
        results.append((country,history['epoch_commits'][-1][1],
                        str(kernel.state.accounts[f'b8_funds:{country}'].balance)))
    return kernel.boundary_manifest.run_id,tuple(results)
