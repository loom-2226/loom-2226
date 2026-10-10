"""Small authored sponsor-routing experiment from the 80-country Earth investment boundary.

Country investment is a proxy, not an agency budget or ownership audit.
No admission to the persistent campaign.
"""
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.prospecting import derive_mobilization
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from .country_capital_input import load_investment_capacity
from .opening import build_country_opening

# Explicit approximate source weights, not purported historical equity stakes.
ROUTES = {
    'NASA': ('PUBLIC', {'USA': '1'}, 'SCIENCE/STRATEGY'),
    'CNSA': ('PUBLIC', {'CHN': '1'}, 'RESOURCES/STRATEGY'),
    'ESA': ('PUBLIC', {'DEU': '1', 'FRA': '1', 'ITA': '1', 'GBR': '1'}, 'SCIENCE/ALLIANCE'),
    'SpaceX': ('PRIVATE', {'USA': '.75'}, 'VISION/RETURN'),
    'Axiom': ('PRIVATE', {'USA': '.25', 'JPN': '.25', 'KOR': '1', 'SAU': '1', 'QAT': '1'}, 'ACCESS/CONTRACT'),
    'ispace': ('PRIVATE', {'JPN': '.75'}, 'RESOURCES/RETURN'),
}
COST = D('.05')


def run_named_sponsors(root: Path, year=2026):
    kernel, _, capacities, _ = build_country_opening(root)
    scenario = load_prospecting_scenario()
    strategic = replace(scenario, base_salience=D('.2'), race_pressure=D(0))
    # Mobilize separate 10% proxy slices once per country and type.
    source = {}
    for country in sorted({c for _, (_, weights, _) in ROUTES.items() for c in weights if (c,year) in capacities}):
        investment = capacities[country, year]
        for kind in ('PUBLIC', 'PRIVATE'):
            amount = derive_mobilization(
                investment_proxy=investment * D('.1'),
                commercial_opportunity=D(1) if kind == 'PRIVATE' else D(0),
                scenario=scenario if kind == 'PRIVATE' else strategic)[3]
            origin = f'trial_origin:{kind}:{country}'
            kernel.add_account(origin, country, 'EARTH:'+country,
                               AccountKind.EARTH_BOUNDARY, amount)
            source[kind, country] = (origin, amount)

    # Each country's weights within each capital class sum to at most one.
    for kind, country in source:
        weight = sum((D(weights.get(country, '0')) for k, weights, _ in ROUTES.values()
                      if k == kind), D(0))
        assert weight <= 1

    output = []
    for sponsor, (kind, weights, motivation) in ROUTES.items():
        home = next(iter(weights))
        budget = 'trial_budget:'+sponsor
        kernel.add_account(budget, sponsor, 'EARTH:'+home, AccountKind.FUNDS, D(0))
        for country, weight in weights.items():
            if (kind, country) not in source:
                continue
            origin, amount = source[kind, country]
            kernel.transfer(year, origin, budget, amount*D(weight), TxPurpose.OTHER_INVESTMENT)
        before = kernel.state.accounts[budget].balance
        outcome = 'WAIT'
        if before >= COST:
            project = 'trial_project:'+sponsor
            location = 'OFF:TRIAL:'+sponsor
            cash = 'trial_project_cash:'+sponsor
            kernel.add_node(location, NodeKind.OFFWORLD)
            kernel.add_account(cash, sponsor, location, AccountKind.PROJECT_CASH, D(0))
            kernel.add_project(project, location, cash, {sponsor:D(1)})
            commitment = 'trial_commit:'+sponsor
            kernel.add_commitment(commitment, sponsor, project, COST)
            kernel.disburse(year, commitment, budget, COST)
            outcome = 'FUNDED'
        output.append(dict(sponsor=sponsor, kind=kind, motivation=motivation,
                           opening=str(before), outcome=outcome,
                           closing=str(kernel.state.accounts[budget].balance)))
    kernel.assert_invariants()
    for kind, country in source:
        origin, amount = source[kind, country]
        routed = sum((D(weights.get(country, '0'))*amount
                      for k, weights, _ in ROUTES.values() if k == kind), D(0))
        assert kernel.state.accounts[origin].balance == amount-routed
    return output, kernel.fingerprint()
