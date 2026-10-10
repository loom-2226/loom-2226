"""Illustrative Build 7 investment economics, not a source of physical truth.

Scenario labels are for offline experiments; never expose them to Agents.
Only realized recovery/sales may enter the simulation's actual ledgers.
"""
from decimal import Decimal
import json
from pathlib import Path
from .mission_costs import public_mission_cost

TABLE = Path(__file__).resolve().parent / 'inputs/BUILD7_RESOURCE_RETURN_SCENARIOS_V1.json'
D = Decimal


def compare_returns(*, scenario, body_id, year=2026, years=10,
                    mission_types=('LANDING_PROSPECTING', 'CARGO_DELIVERY'),
                    annual_revenue=None, annual_opex=None,
                    prospecting_capital=None, development_capital=None):
    """Ten-operating-year illustrative net return; no state mutation.

    Actual revenue/cost overrides allow future use with realized cash flows.
    Unknown mission trajectory stays unknown rather than becoming free.
    """
    if not 0 <= years <= 10:
        raise ValueError('illustrative horizon must be 0..10 operating years')
    doc = json.loads(TABLE.read_text())
    s = doc['scenarios'][scenario]
    revenue = D(str(s['annual_gross_revenue'] if annual_revenue is None else annual_revenue))
    opex = D(str(s['annual_operating_cost'] if annual_opex is None else annual_opex))
    if revenue < 0 or opex < 0:
        raise ValueError('negative revenue or operating cost')
    # When NULL is established by landing/prospecting, avoid an unnecessary cargo mission.
    if scenario == 'NULL':
        mission_types = tuple(m for m in mission_types if m != 'CARGO_DELIVERY')
    costs = [public_mission_cost(year, body_id, mission_type) for mission_type in mission_types]
    if any(c is None for c in costs):
        return None
    mission = sum((c.model_currency for c in costs), D(0))
    prospecting = D(str(doc['capital_assumptions']['prospecting_capital'] if prospecting_capital is None else prospecting_capital))
    development = D(str(doc['capital_assumptions']['development_capital'] if development_capital is None else development_capital))
    if prospecting < 0 or development < 0:
        raise ValueError('negative capital')
    # NULL should be abandoned once identified; never charge phantom operating years.
    if scenario == 'NULL':
        revenue = D(0)
        years = 0
        development = D(0)
    operating = (revenue - opex) * years
    invested = prospecting + development + mission
    return {'scenario': scenario, 'body_id': body_id, 'years': years,
            'annual_gross_revenue': revenue, 'annual_opex': opex,
            'annual_net': revenue - opex, 'mission_cost': mission,
            'invested': invested, 'operating_cash_flow': operating,
            'net_return': operating - invested}
