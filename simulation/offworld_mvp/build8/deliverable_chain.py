"""Noncanon Build 8 executor-chain experiment. Authored outcomes, not flight physics.

Every step consumes a predecessor's deliverable and creates its own. An
unsuccessful step produces a failure record, never a usable deliverable.
This intentionally leaves the 80-economy conductor and shared kernel alone.
"""
from dataclasses import dataclass
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening, EARTH_V4_ROOT
from .executor_quotes import EXECUTORS as QUOTED
from .master_cast import name as cast_name

CATEGORIES = ('BUILD', 'LAUNCH', 'LAND', 'TRANSPORT', 'EXTRACT', 'RUN')
# Additional operators are explicitly fictional placeholders, not researched offers.
OPERATORS = {
    'BUILD': ('Northrop Grumman', D('2.00'), D('.25'), 2, 1),
    'LAND': ('Firefly Aerospace', D('3.00'), D('.20'), 2, 1),
    'LAUNCH': ('Authored Launch Operator', D('1'), D('.20'), 1, 1),
    'TRANSPORT': ('Authored Transport Operator', D('1'), D('.20'), 2, 1),
    'EXTRACT': ('Authored Extraction Operator', D('1'), D('.20'), 2, 1),
    'RUN': ('Authored Operations Operator', D('1'), D('.20'), 1, 1),
}
assert all(OPERATORS[x][0] == q.name and OPERATORS[x][1:4] == (q.authored_cost, q.markup_rate, q.duration_years)
           for x in ('BUILD', 'LAND') for q in QUOTED if q.category == x)

@dataclass(frozen=True)
class Step:
    id: str
    category: str
    input_id: str
    output_id: str

@dataclass(frozen=True)
class Record:
    step_id: str
    category: str
    executor: str
    start_year: int | None
    finish_year: int | None
    status: str
    input_id: str
    output_id: str | None
    payment: D
    cost: D
    profit: D


def run_chain(steps, failure=None, root=EARTH_V4_ROOT, eligible_executors=None, selected_executors=None):
    """One commissioned chain, one capacity slot per operator, integer-year clock.

    Failure is an authored step id. Payment is for work attempted, not a claim
    that a failed delivery arrived. No implicit salvage/refund is assumed.
    """
    # Authored pool and selected actor are separate. No quote/bidding selection.
    selected_executors = {} if selected_executors is None else dict(selected_executors)
    eligible_executors = {} if eligible_executors is None else dict(eligible_executors)
    operators = dict(OPERATORS)
    for category, candidates in eligible_executors.items():
        if category not in CATEGORIES or not candidates:
            raise ValueError('invalid executor candidate pool')
        candidates = tuple(cast_name(n, 'executor', category) for n in candidates)
        chosen = selected_executors.get(category, OPERATORS[category][0])
        if chosen not in candidates:
            raise ValueError('selected executor not in eligible pool')
        operators[category] = (cast_name(chosen, 'executor', category), *OPERATORS[category][1:])
    if set(selected_executors) - set(eligible_executors):
        raise ValueError('selection requires explicit eligible pool')
    steps = tuple(steps)
    if not steps or len({s.id for s in steps}) != len(steps):
        raise ValueError('chain needs distinct steps')
    if failure is not None and failure not in {s.id for s in steps}:
        raise ValueError('unknown failure step')
    if any(s.category not in CATEGORIES or not s.id or not s.output_id for s in steps):
        raise ValueError('invalid step/category')
    if len({s.output_id for s in steps}) != len(steps):
        raise ValueError('duplicate deliverable identity')
    # The first input is the Sponsor's recorded commissioning authorization.
    if steps[0].input_id != 'SPONSOR_COMMISSION':
        raise ValueError('first step needs commission')
    if any(b.input_id != a.output_id for a, b in zip(steps, steps[1:])):
        raise ValueError('missing predecessor deliverable dependency')
    k, _, _, _ = build_country_opening(root)
    k.add_node('B8:MOON', NodeKind.OFFWORLD)
    k.add_account('chain:sponsor', 'CHAIN_SPONSOR', 'EARTH:USA', AccountKind.FUNDS)
    k.add_account('chain:cash', 'CHAIN_PROJECT', 'B8:MOON', AccountKind.PROJECT_CASH)
    k.add_project('chain:project', 'B8:MOON', 'chain:cash', {'CHAIN_SPONSOR': D(1)})
    # Fund from the existing Earth-v4-backed pool, never mint new money.
    total = sum((operators[s.category][1] * (1 + operators[s.category][2]) for s in steps), D(0))
    source = 'public_funds'  # Existing seeded USA funds; not the empty country mobilization account.
    if k.state.accounts[source].balance < total:
        raise ValueError('seeded Sponsor pool cannot fund chain')
    k.transfer(2026, source, 'chain:cash', total, TxPurpose.OTHER_INVESTMENT,
               parent_ids=('SPONSOR_COMMISSION',))
    for category in {s.category for s in steps}:
        name, _, _, _, _ = operators[category]
        if name == 'CHAIN_SPONSOR':
            raise ValueError('self-payment is not executor revenue')
        k.add_account('chain:executor:' + category, name, 'EARTH:USA', AccountKind.SUPPLIER)
    records = []
    delivered = {'SPONSOR_COMMISSION'}
    year = 2026
    capacity = {}  # (category, year) -> units reserved while a job is active
    for step in steps:
        name, cost, markup, duration, slots = operators[step.category]
        if step.input_id not in delivered:
            records.append(Record(step.id, step.category, name, None, None, 'BLOCKED_UPSTREAM',
                                  step.input_id, None, D(0), D(0), D(0)))
            k.audit('BUILD8_EXECUTOR_STEP', year, step=step.id, category=step.category,
                    executor=name, input=step.input_id, output='', status='BLOCKED_UPSTREAM',
                    payment=D(0), cost=D(0), profit=D(0))
            continue
        if any(capacity.get((step.category, y), 0) >= slots for y in range(year, year + duration)):
            raise ValueError('executor capacity exhausted')
        for y in range(year, year + duration):
            capacity[step.category, y] = capacity.get((step.category, y), 0) + 1
        finish = year + duration
        price = cost * (1 + markup)
        # Record an actual cash transfer to an independent supplier account.
        k.transfer(finish, 'chain:cash', 'chain:executor:' + step.category, price,
                   TxPurpose.CAPEX, parent_ids=('chain:project', step.id, step.input_id))
        status = 'FAILED' if step.id == failure else 'DELIVERED'
        if status == 'DELIVERED':
            delivered.add(step.output_id)
        k.audit('BUILD8_EXECUTOR_STEP', finish, step=step.id, category=step.category,
                executor=name, input=step.input_id, output=step.output_id if status == 'DELIVERED' else '',
                status=status, payment=price, cost=cost, profit=price-cost)
        records.append(Record(step.id, step.category, name, year, finish, status,
                              step.input_id, step.output_id if status == 'DELIVERED' else None,
                              price, cost, price - cost))
        year = finish
    k.assert_invariants()
    spent = sum((r.payment for r in records), D(0))
    assert spent + k.state.accounts['chain:cash'].balance == total
    assert spent == sum((k.state.accounts['chain:executor:' + c].balance
                         for c in {s.category for s in steps}), D(0))
    return tuple(records), frozenset(delivered), k, capacity


BUILD_LAND = (Step('build', 'BUILD', 'SPONSOR_COMMISSION', 'PAYLOAD_BUILT'),
              Step('land', 'LAND', 'PAYLOAD_BUILT', 'PAYLOAD_ON_MOON'))
LAND_EXTRACT_TRANSPORT = (
    Step('site', 'LAND', 'SPONSOR_COMMISSION', 'LANDING_SITE_DELIVERED'),
    Step('mine', 'EXTRACT', 'LANDING_SITE_DELIVERED', 'MATERIAL_EXTRACTED'),
    Step('ship', 'TRANSPORT', 'MATERIAL_EXTRACTED', 'MATERIAL_TRANSPORTED'))
