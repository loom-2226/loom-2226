"""Reconstruct admitted 2026 lunar observations; stop at the allocation seam.

Isolated World Authority replay only. Never infer authorization from a pool.
"""
from .opening import EARTH_V4_ROOT
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import TxPurpose
from simulation.offworld_mvp.build7.generated_campaign import (
    _world_from_run,_attach_persistence,_record_empty_year,_execute_world_remote_choice,
    derive_world_prospecting_opportunities)
from simulation.offworld_mvp.build7 import runtime_flow as flow
from .opening import build_country_opening

CONTROL='SOLAR_MATERIAL_1cd519072074d72fe42bb2f9:44f9a944ba26d099'
ROOT=EARTH_V4_ROOT

def replay_observed(country_id="USA"):
    country_id=str(country_id).upper()
    world,seed=_world_from_run('reference_reader','runtime',CONTROL)
    k,h,capacities,_=build_country_opening(ROOT,world=world,world_seed=seed+":B8_AUTHORIZED_ALLOCATION_V2:"+country_id)
    if country_id not in {c for c,y in capacities if y==2026}:
        raise ValueError('UNKNOWN_COUNTRY:'+country_id)
    if country_id!='USA':
        raise ValueError('COUNTRY_SPONSOR_BINDING_NOT_AUTHORED:'+country_id)
    _attach_persistence(h,None,'runtime',{})
    _record_empty_year(k,h,2026)
    prefix=('AUS','USA','CAN','GBR','JPN')
    countries=prefix+tuple(c for c in sorted({c for c,y in capacities if y==2026}) if c not in prefix)
    for country in countries:
        flow.system_epoch(k,h,'mobilize_country_capital','1',
            (1,country,capacities[country,2026],D(1),h['prospecting_scenario'],
             f'b8_source:{country}',('sponsor_funds' if country==country_id else f'b8_funds:{country}')))
    choice=_execute_world_remote_choice(k,h,world,reference_service='reference_reader',
        runtime_service='runtime',agent_login_service='agent_pub',calendar_year=2026)
    if choice['choice']!='SELECT' or choice['selected_body_id']!='MOON':
        raise RuntimeError('Observed lunar selection did not replay')
    opportunities=derive_world_prospecting_opportunities(k,h,2026,'MOON')
    if len(opportunities)!=10:
        raise RuntimeError('Lunar opportunities changed')
    return k,h,choice,opportunities

if __name__=='__main__':
    k,h,choice,opps=replay_observed()
    print('REPLAYED',choice['selected_body_id'],'opportunities',len(opps))
    print('COUNTRY_POOL',k.state.accounts['sponsor_funds'].balance)
    print('SPONSOR',k.state.accounts['sponsor_funds'].balance)
    print('OPPORTUNITY',opps[0].opportunity_id,'CAPITAL',opps[0].required_capital)
