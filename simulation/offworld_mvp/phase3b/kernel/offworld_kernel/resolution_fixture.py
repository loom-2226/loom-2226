from decimal import Decimal as D

from .build3 import RunIdentity
from .build4 import OwnershipStake
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind, TxPurpose
from .mvp_state import AggregateState, AgentKind, AgentState, RuntimeObjectClass, SystemState
from .resolution import (
    ExposureAllocationBasis,
    ExposureSelectionBasis,
    ResolutionExposurePlan,
    resolution_invariant_totals,
)
from .runtime import ScheduledSimulationRuntime
from .scheduler import CouplingSpec, Phase, ScheduledEvent


def resolution_invariance_fixture(split: bool, horizon: int=5):
    rid=RunIdentity(
        'RESOLUTION_EQUIVALENCE',
        'v1',
        'SYNTH_RESOLUTION_EQUIVALENCE',
        'BUILD4_MVP_METHODOLOGY_R1',
        (('per_member_revenue','4'),('horizon',str(horizon))),
    )
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)

    k.add_account('revenue_source','FLOW_SYSTEM','EARTH:X',AccountKind.FUNDS,D('1000'))
    k.add_account('sector_cash','FIRM_SECTOR','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('firm_cash','FIRM_01','EARTH:X',AccountKind.FUNDS,D('0'))

    k.add_aggregate(AggregateState(
        'FIRM_SECTOR',
        'EARTH:X',
        'sector_cash',
        4,
        set(),
        {'RESOURCE_X':D('40')},
        {'VEH':D('1')},
        ['HIST:COMMON'],
    ))
    k.ownership_stakes.append(OwnershipStake('VEH','FIRM_SECTOR','EARTH:X',D('1')))

    k.add_system(SystemState(
        'REPRESENTATION_FLOW_SYSTEM',
        'EQUIVALENT_PER_MEMBER_FLOW',
        {'accounts','transactions'},
    ))
    if split:
        k.add_system(SystemState(
            'RESOLUTION_SYSTEM',
            'RUNTIME_RESOLUTION',
            {'aggregate','accounts','agent_registry','resolution','ownership'},
        ))

    k.scheduler.register_coupling(CouplingSpec(
        'REPRESENTATION_FLOW_SYSTEM',
        'v1',
        RuntimeObjectClass.SYSTEM,
        ('accounts','transactions'),
        ('aggregate','agent_registry','resolution'),
        ('accounts','transactions'),
        'ANNUAL',
        Phase.OPERATIONS,
    ))
    if split:
        k.scheduler.register_coupling(CouplingSpec(
            'RESOLUTION_SYSTEM',
            'v1',
            RuntimeObjectClass.SYSTEM,
            ('aggregate','accounts','agent_registry','resolution','ownership'),
            ('aggregate','accounts','ownership'),
            ('aggregate','accounts','agent_registry','resolution','ownership'),
            'ONCE',
            Phase.EXOGENOUS_INPUTS,
        ))
        k.scheduler.schedule(ScheduledEvent(
            'resolve-firm-01',
            D('0'),
            Phase.EXOGENOUS_INPUTS,
            0,
            'FIRM_01',
            'RESOLUTION_SYSTEM',
        ))

    for year in range(1,horizon+1):
        k.scheduler.schedule(ScheduledEvent(
            f'flow-{year}',
            D(year),
            Phase.OPERATIONS,
            0,
            f'FLOW-{year:04d}',
            'REPRESENTATION_FLOW_SYSTEM',
            payload=(('year',str(year)),),
        ))

    plan=ResolutionExposurePlan(
        plan_id='RESOLUTION_EQUIVALENCE_PLAN_001',
        aggregate_id='FIRM_SECTOR',
        selected_agent_id='FIRM_01',
        members_exposed=1,
        selection_basis=ExposureSelectionBasis.VALIDATION_FIXTURE_STABLE_ID,
        selection_ref='FIXTURE:RESOLUTION_EQUIVALENCE:FIRM_01',
        allocation_basis=ExposureAllocationBasis.EQUAL_MEMBER_PRO_RATA,
        allocation_ref='MODEL:EQUAL_MEMBER_PRO_RATA',
        explicit_share=None,
    )

    trajectory=[]
    rt=ScheduledSimulationRuntime(k)

    if split:
        def resolution_handler(kernel,event):
            agent=AgentState(
                'FIRM_01',
                AgentKind.PRIVATE_SPONSOR,
                'EARTH:X',
                'firm_cash',
                objectives=('FOLLOW_AGGREGATE_EQUIVALENCE_RULE',),
            )
            rec=kernel.expose_agent_by_plan(0,plan,agent)
            return f'{rec.plan_id}:{rec.allocation_fraction}'

        rt.register_handler('RESOLUTION_SYSTEM',resolution_handler)

    def flow_handler(kernel,event):
        year=int(dict(event.payload)['year'])
        per_member=D('4')
        agg=kernel.aggregates['FIRM_SECTOR']

        aggregate_amount=per_member*D(agg.member_count)
        if aggregate_amount:
            kernel.transfer(
                year,
                'revenue_source',
                agg.account_id,
                aggregate_amount,
                TxPurpose.REVENUE,
            )

        for rec in kernel.resolution_exposure_records:
            if rec.aggregate_id!='FIRM_SECTOR':
                continue
            agent=kernel.agents[rec.agent_id]
            agent_amount=per_member*D(rec.members_exposed)
            if agent_amount:
                kernel.transfer(
                    year,
                    'revenue_source',
                    agent.account_id,
                    agent_amount,
                    TxPurpose.REVENUE,
                )

        totals=resolution_invariant_totals(kernel,'FIRM_SECTOR','revenue_source')
        trajectory.append((year,totals))
        return f'YEAR:{year}:PAID:{totals.value_paid_to_representation}'

    rt.register_handler('REPRESENTATION_FLOW_SYSTEM',flow_handler)
    rt.seal()
    result=rt.run()

    terminal=resolution_invariant_totals(k,'FIRM_SECTOR','revenue_source')
    return k,result,tuple(trajectory),terminal,plan


def paired_resolution_invariance_fixture(horizon: int=5):
    aggregate_only=resolution_invariance_fixture(False,horizon)
    exposed_agent=resolution_invariance_fixture(True,horizon)
    return aggregate_only,exposed_agent
