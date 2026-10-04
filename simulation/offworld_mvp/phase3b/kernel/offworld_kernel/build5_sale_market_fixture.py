from __future__ import annotations
from decimal import Decimal as D

from .build5_operating_extraction_fixture import operating_extraction_kernel
from .market import CommodityMarketEnvelope
from .market_protocol import build_sale_decision_request
from .model import AccountKind
from .mvp_state import SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot


RESEARCH_ADVISORY_REF=(
    'loom-2226/loom-research-lab@80085a254be53bb46e290cd5ec802fc600e77bc2:'
    'projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md'
)

def sale_market_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                       unit_price='20',demand_quantity='4',
                       sponsor_capabilities=(
                           'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL')):
    k,h=operating_extraction_kernel(
        universe_id,stock,sponsor_capabilities=sponsor_capabilities)

    k.add_account(
        'earth_market','EARTH_MARKET_v0','EARTH:X',
        AccountKind.EARTH_BOUNDARY,D('0'))
    k.add_system(SystemState(
        'SALE_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState(
        'EARTH_MARKET_v0','EXTERNAL_COMMODITY_CLEARING',
        {'accounts','transactions','colonies','market_resource_inventory',
         'market_clearing_records','boundary_net','events'}))

    envelope=CommodityMarketEnvelope(
        'MARKET-009A-1',10,'RES','earth_market',
        D(unit_price),D(demand_quantity),
        'MODEL_CURRENCY','MODEL_RESOURCE_UNIT_BY_FAMILY',
        'TEST_ONLY:BUILD5_TEST009A_EXOGENOUS_MARKET_ENVELOPE|ADVISORY_RESEARCH:'+RESEARCH_ADVISORY_REF,
        'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
    k.register_market_envelope(envelope)
    h['market_envelope']=envelope
    return k,h

def sale_snapshot_facts(k,envelope,project_id='P',
                        price_unknown=False,demand_unknown=False,
                        status_override=None,inventory_override=None,
                        price_override=None,demand_override=None):
    p=k.state.projects[project_id]
    resource=k.resources[envelope.resource_id]
    colony=k.colonies.get(resource.node_id)
    inventory=D('0') if colony is None else D(colony.resource_inventory)
    if inventory_override is not None:
        inventory=D(inventory_override)
    status=p.status if status_override is None else str(status_override)
    price=D(envelope.unit_price) if price_override is None else D(price_override)
    demand=k.market_remaining_demand(envelope.id)
    if demand_override is not None:
        demand=D(demand_override)
    return (
        SnapshotFact(
            'project.STATUS',FactState.KNOWN,status,
            f'PROJECT:{project_id}:STATUS'),
        SnapshotFact(
            'inventory.AVAILABLE',FactState.KNOWN,str(inventory),
            f'COLONY:{resource.node_id}:RESOURCE_INVENTORY:{envelope.resource_id}'),
        SnapshotFact(
            'market.UNIT_PRICE',
            FactState.UNKNOWN if price_unknown else FactState.KNOWN,
            None if price_unknown else str(price),
            f'MARKET:{envelope.id}:UNIT_PRICE:{envelope.source_ref}'),
        SnapshotFact(
            'market.REMAINING_DEMAND',
            FactState.UNKNOWN if demand_unknown else FactState.KNOWN,
            None if demand_unknown else str(demand),
            f'MARKET:{envelope.id}:REMAINING_DEMAND:{envelope.source_ref}'),
    )

def sale_snapshot(k,envelope,period_key='SALE-10',effective_time='10',**kw):
    return build_decision_snapshot(
        k,'SPN',period_key,D(str(effective_time)),
        sale_snapshot_facts(k,envelope,**kw))

def sale_request(observation_id,market_state_id='MARKET-009A-1',
                 resource_id='RES',request_id='SALEREQ-009A-1',year=10):
    return build_sale_decision_request(
        request_id,year,'P',resource_id,market_state_id,observation_id)
