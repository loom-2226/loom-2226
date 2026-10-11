"""Opt-in, fictional one-project BUILD-only yearly experiment; never legacy execution."""
from decimal import Decimal as D
from hashlib import sha256
from .opening import build_country_opening
from .master_cast import actor
from .competitive_delivery import Work
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose


def run_esa_build(chosen, root, seed, tiers, slots, prices):
    assert chosen['stages'] == {'ESA': ('BUILD',)}
    offers = chosen['quotes']['BUILD']
    ceiling = chosen['ceiling']
    feasible = sorted(((price, name) for name, price in offers.items()
                       if price <= ceiling and actor(name, 'executor', 'BUILD')))
    if not feasible:
        raise ValueError('no feasible ESA BUILD quote')
    quote, winner = feasible[0]
    loser = next(name for name in offers if name != winner)
    k, history, capacities, _ = build_country_opening(root)
    mobilized = k.mobilize_country_capital(1, 'DEU', capacities['DEU', 2026], D(1),
        history['prospecting_scenario'], 'b8_source:DEU', 'b8_funds:DEU')
    # The chosen BUILD stage alone sizes financing. No network-trial cash is imported.
    if mobilized.mobilized_cash < quote:
        raise ValueError('ESA yearly financier lacks cash for selected BUILD stage')
    k.add_account('esa:fund', 'ESA_TRIAL_FINANCIER', 'EARTH:DEU', AccountKind.FUNDS)
    k.add_account('esa:sponsor', 'ESA', 'EARTH:DEU', AccountKind.FUNDS)
    k.add_node('esa:moon', NodeKind.OFFWORLD)
    k.add_account('esa:cash', 'ESA', 'esa:moon', AccountKind.PROJECT_CASH)
    k.add_project('esa:project', 'esa:moon', 'esa:cash', {'ESA':D(1)})
    k.add_account('esa:revenue', winner, 'EARTH:'+actor(winner)['home_country'], AccountKind.SUPPLIER)
    k.transfer(1, 'b8_funds:DEU', 'esa:fund', quote, TxPurpose.OTHER_INVESTMENT,
               parent_ids=(mobilized.transaction_id,))
    opening = k.state.accounts['esa:sponsor'].balance
    k.transfer(1, 'esa:fund', 'esa:sponsor', quote, TxPurpose.OTHER_INVESTMENT)
    k.add_commitment('esa:commit', 'ESA_TRIAL_FINANCIER', 'esa:project', quote)
    k.disburse(1, 'esa:commit', 'esa:sponsor', quote)
    k.audit('ESA_BUILD_FINANCING', 2026, opening_cash=opening, committed=quote,
            project_ceiling=ceiling, pre_payment_cash=k.state.accounts['esa:cash'].balance,
            financing_source='DEU_YEARLY_MOBILIZATION_NOT_NETWORK_TRIAL')
    k.audit('ESA_BUILD_QUOTES', 2026, winner=winner, winner_quote=quote,
            loser=loser, loser_quote=offers[loser], fictional=True,
            price_fallback_used=False, slots_fallback_used=False)
    if tiers:
        from .capacity_options import descriptive_tier
        tier = descriptive_tier(winner, 'BUILD', tiers=True)
        if tier:
            k.audit('BUILD8_DESCRIPTIVE_TIER', 2026, executor=winner, category='BUILD', **tier)
    # One draw per run, no retries or tuning. Uniform 256-bit deterministic draw.
    digest = sha256(f'ESA_BUILD_READY|{seed}|ESA|BUILD|2026'.encode()).hexdigest()
    draw = D(int(digest, 16)) / D(2**256)
    probability = chosen['readiness_probability']  # authored, uncalibrated
    ready = draw < probability
    k.audit('ESA_BUILD_READINESS', 2026, seed=seed, draw=draw,
            probability=probability, ready=ready, method='SHA256_UNIFORM_AUTHORED')
    start = 2026 if ready else 2027
    finish = start + 2  # existing BUILD duration; no competing work in this scenario
    k.audit('ESA_BUILD_SCHEDULE', start, project='ESA', category='BUILD',
            executor=winner, start=start, finish=finish, readiness_deferred=not ready)
    before = k.state.accounts['esa:cash'].balance
    tx = k.transfer(finish-2025, 'esa:cash', 'esa:revenue', quote, TxPurpose.CAPEX,
                    parent_ids=('esa:commit',))
    k.audit('ESA_BUILD_DELIVERY', finish, project='ESA', category='BUILD',
            executor=winner, outcome='DELIVERED', paid=quote,
            pre_payment_cash=before, transaction_id=tx.id)
    k.assert_invariants()
    work = (Work('ESA', 'BUILD', start, finish, 'DELIVERED', 'COMMISSION:ESA',
                 'BUILT:ESA', quote, quote, D(0)),)
    decisions = (('ESA', 'AUTHORED_BUILD_ONLY', 'FUNDED', str(quote), 2026),)
    return work, decisions, k, {('BUILD', y):1 for y in range(start, finish)}
