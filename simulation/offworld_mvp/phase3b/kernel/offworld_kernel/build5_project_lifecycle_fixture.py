from __future__ import annotations
from decimal import Decimal as D

from .build5_sponsor_fixture import sponsor_operator_kernel
from .mvp_state import SystemState
from .project_lifecycle import ProjectDevelopmentPlan
from .underwriting import UnderwritingInputKind

def project_lifecycle_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                             year7_earth_ceiling='100',
                             commissioned_capacity='10',
                             sponsor_capabilities=('REQUEST_FINANCE','DEVELOP')):
    values=sponsor_operator_kernel(
        universe_id,stock,sponsor_capabilities=sponsor_capabilities)
    k,pub_snapshot,pub_request,manifest,obs,wip,draw,table,sponsor_request=values

    k.add_system(SystemState(
        'CONSTRUCTION_SYSTEM','STAGED_PROJECT_CONSTRUCTION',
        {'accounts','transactions','wip','fcf','earth_impact','resource_constraints','events'}))
    k.add_system(SystemState(
        'DEVELOPMENT_RESOLUTION_SYSTEM','PROJECT_DEVELOPMENT_RESOLUTION',
        {'project_state','wip','assets','events'}))

    # Test-only Earth resource-allocation ceilings for the two construction years.
    k.set_resource_constraint('EARTH:X',6,D('1000'),D('0.10'))
    ceiling=D(year7_earth_ceiling)
    k.set_resource_constraint('EARTH:X',7,ceiling,D('1'))

    dev=table.get('GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.DEVELOPMENT_CAPEX)
    lead=table.get('GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.LEAD_TIME)
    if D(dev.value)!=D('60') or D(lead.value)!=D('2'):
        raise ValueError('Test 006A fixture expects pinned Build 5 validation underwriting values')

    plan=ProjectDevelopmentPlan(
        'DEVPLAN-006A','P','WIP-P','MINE-P','earth_supplier','OFF:T1',
        D(dev.value),((6,D('30')),(7,D('30'))),8,D(commissioned_capacity),
        f'{table.table_id}:{table.version}:{dev.input_id}:{lead.input_id}:TEST_ONLY_EXPLICIT_STAGE_SCHEDULE_30_30')
    k.register_development_plan(plan)

    holder={
        'pub_snapshot':pub_snapshot,
        'pub_request':pub_request,
        'manifest':manifest,
        'obs':obs,
        'wip':wip,
        'draw':draw,
        'table':table,
        'sponsor_request':sponsor_request,
        'development_plan':plan,
    }
    return k,holder
