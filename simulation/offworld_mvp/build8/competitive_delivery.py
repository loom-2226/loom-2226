"""Noncanon Build 8: two funded projects competing in one kernel world.

Author-defined priority is alphabetical project ID. Not a market-clearing
claim. Whole-year capacity, named deliverables, and contractor costs are
separate from cash revenue. No shared kernel or 80-country conductor edits.
"""
from dataclasses import dataclass
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind, ActionKind
from .opening import build_country_opening, EARTH_V4_ROOT
from .deliverable_chain import OPERATORS

# Authored miniature project: preserve PI-01 price/cost proportions.
SCALE = D("0.25")

@dataclass(frozen=True)
class ProjectBid:
    sponsor: str
    project: str

@dataclass(frozen=True)
class Work:
    project: str
    category: str
    start: int
    finish: int
    outcome: str
    consumed: str
    produced: str | None
    revenue: D
    cost: D
    profit: D


def run_competition(bids=(ProjectBid('A', 'A'), ProjectBid('B', 'B')),
                    failure=None, root=EARTH_V4_ROOT):
    bids = tuple(sorted(bids, key=lambda b: b.project))
    if len(bids) != 2 or len({b.project for b in bids}) != 2 or len({b.sponsor for b in bids}) != 2:
        raise ValueError('two distinct Sponsors/projects required')
    if failure is not None and failure not in {(b.project, c) for b in bids for c in ('BUILD','LAND')}:
        raise ValueError('unknown failure')
    k, h, capacities, _ = build_country_opening(root)
    mobilized = k.mobilize_country_capital(1, 'USA', capacities['USA', 2026], D(1),
                                           h['prospecting_scenario'], 'b8_source:USA', 'b8_funds:USA')
    pool = 'b8_funds:USA'
    unit = sum((SCALE * OPERATORS[c][1] * (1 + OPERATORS[c][2]) for c in ('BUILD','LAND')), D(0))
    if k.state.accounts[pool].balance < unit * len(bids):
        raise ValueError('country capital insufficient for two funded projects')
    # Country pool -> private financier -> each Sponsor -> project commitment.
    k.add_account('comp:financier', 'COMP_FINANCIER', 'EARTH:USA', AccountKind.FUNDS)
    k.transfer(1, pool, 'comp:financier', unit * len(bids), TxPurpose.OTHER_INVESTMENT,
               parent_ids=(mobilized.transaction_id,))
    k.add_agent(AgentState('COMP_FINANCIER', AgentKind.PRIVATE_FINANCIER,
                           'EARTH:USA', 'comp:financier', {'FINANCE'}, ('RETURN',)))
    for b in bids:
        sponsor_account = 'comp:sponsor:' + b.sponsor
        cash = 'comp:cash:' + b.project
        pid = 'comp:project:' + b.project
        k.add_account(sponsor_account, b.sponsor, 'EARTH:USA', AccountKind.FUNDS)
        k.add_node('comp:moon:' + b.project, NodeKind.OFFWORLD)
        k.add_account(cash, b.sponsor, 'comp:moon:' + b.project, AccountKind.PROJECT_CASH)
        k.add_project(pid, 'comp:moon:' + b.project, cash, {b.sponsor:D(1)})
        k.add_agent(AgentState(b.sponsor, AgentKind.PRIVATE_SPONSOR,
                               'EARTH:USA', sponsor_account, {'DEVELOP','REQUEST_FINANCE'}, ('RETURN',)))
        # An authored financier decision is an actual kernel event, before funding.
        decision = k.event(1, 'COMP_FINANCIER', ActionKind.FINANCE, 'APPROVED',
                           (pid, str(unit), 'AUTHORED_BUILD8_FINANCING'))
        k.transfer(1, 'comp:financier', sponsor_account, unit,
                   TxPurpose.OTHER_INVESTMENT, parent_ids=(decision.id,))
        k.add_commitment('comp:commit:' + b.project, b.sponsor, pid, unit)
        k.disburse(1, 'comp:commit:' + b.project, sponsor_account, unit)
        authorization = k.event(1, b.sponsor, ActionKind.AUTHORIZE_ACTIVITY,
                                'AUTHORIZE_DEVELOPMENT', (pid, decision.id))
        k.transition_project_status(1, b.sponsor, pid, 'DEVELOPMENT', authorization.id)
    for category in ('BUILD','LAND'):
        operator = OPERATORS[category][0]
        if operator in {b.sponsor for b in bids}:
            raise ValueError('executor cannot pay itself')
        k.add_account('comp:executor:' + category, operator, 'EARTH:USA', AccountKind.SUPPLIER)
        k.add_account('comp:cost:' + category, operator + ' COST', 'EARTH:USA', AccountKind.SUPPLIER)
    # Schedule each next ready stage by (earliest ready year, project ID).
    # Both projects enter at 2026. Shared executor has one slot, occupied for
    # the full [start,finish) interval, regardless of success/failure.
    ready = {b.project:2026 for b in bids}
    delivered = {b.project:{'COMMISSION:' + b.project} for b in bids}
    stages = {b.project:0 for b in bids}
    occupied = {}
    work = []
    while any(stages[p] < 2 for p in stages):
        project = min((p for p in stages if stages[p] < 2), key=lambda p:(ready[p],p))
        idx = stages[project]
        category = ('BUILD','LAND')[idx]
        consumed = ('COMMISSION:' if idx == 0 else 'BUILT:') + project
        if consumed not in delivered[project]:
            work.append(Work(project, category, ready[project], ready[project], 'BLOCKED_UPSTREAM',
                             consumed, None, D(0), D(0), D(0)))
            stages[project] = 2
            continue
        operator, cost, markup, duration, slots = OPERATORS[category]
        start = ready[project]
        while any(occupied.get((category, year), 0) >= slots for year in range(start,start+duration)):
            start += 1
        finish = start + duration
        for year in range(start, finish):
            occupied[category,year] = occupied.get((category,year),0)+1
        cost = cost * SCALE
        price = cost*(1+markup)
        tx = k.transfer(finish, 'comp:cash:' + project, 'comp:executor:' + category,
                        price, TxPurpose.CAPEX, parent_ids=('comp:project:' + project, consumed))
        # Expense is paid to a separate cost sink, not booked as another sale.
        k.transfer(finish, 'comp:executor:' + category, 'comp:cost:' + category,
                   cost, TxPurpose.OTHER_INVESTMENT, parent_ids=(tx.id,))
        outcome = 'FAILED' if failure == (project,category) else 'DELIVERED'
        produced = (('BUILT:' if idx == 0 else 'ON_MOON:') + project) if outcome == 'DELIVERED' else None
        if produced:
            delivered[project].add(produced)
        k.audit('BUILD8_COMPETITIVE_DELIVERY', finish, project=project, category=category,
                consumed=consumed, produced=produced or '', outcome=outcome,
                revenue=price, cost=cost, profit=price-cost)
        work.append(Work(project, category, start, finish, outcome, consumed,
                         produced, price, cost, price-cost))
        ready[project] = finish
        stages[project] += 1
    k.assert_invariants()
    revenue = sum((w.revenue for w in work), D(0))
    costs = sum((w.cost for w in work), D(0))
    assert sum((k.state.accounts['comp:cash:' + b.project].balance for b in bids), D(0)) + revenue == unit*len(bids)
    assert sum((k.state.accounts['comp:executor:' + c].balance for c in ('BUILD','LAND')), D(0)) == revenue-costs
    assert sum((k.state.accounts['comp:cost:' + c].balance for c in ('BUILD','LAND')), D(0)) == costs
    return tuple(sorted(work,key=lambda w:(w.start,w.project,w.category))), k, occupied
