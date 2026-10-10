"""Build 8 disposable public/private capital and strategic-pressure comparison.

No new Agent policies, runtime wiring, or authoritative campaign changes.
"""
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.prospecting import derive_mobilization
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from .country_capital_input import load_investment_capacity


def run_public_private_comparison(root: Path, *, public_share=D('0.1'),
                                  private_share=D('0.1'), pressure=D('0.2'),
                                  public_country='AUS', project_cost=D(2)):
    """Counterfactual allocations, NOT public Sponsor decisions or spending."""
    capacities, _ = load_investment_capacity(root)
    scenario = load_prospecting_scenario()
    if (public_share < 0 or private_share < 0 or public_share+private_share > 1
            or pressure < 0 or project_cost <= 0):
        raise ValueError('invalid split, pressure, or project cost')
    if (public_country,2026) not in capacities:
        raise ValueError('country absent')
    public_scenario=replace(scenario,base_salience=pressure,race_pressure=D(0))
    # Existing mobilization ceiling, with mutually exclusive funding shares.
    # Private responds to commercial opportunity; public to strategic salience.
    results={}
    for commercial,strategic in ((False,False),(False,True),(True,False),(True,True)):
        public_total=D(0);private_total=D(0)
        public_country_amount=D(0)
        for (country,year),investment in capacities.items():
            if year!=2026:continue
            public=derive_mobilization(investment_proxy=investment*public_share,
                commercial_opportunity=D(0),
                scenario=public_scenario if strategic else scenario)[3]
            private=derive_mobilization(investment_proxy=investment*private_share,
                commercial_opportunity=D(int(commercial)),scenario=scenario)[3]
            public_total+=public;private_total+=private
            if country==public_country:public_country_amount=public
        results[(commercial,strategic)]={
            'public_total':public_total,'private_total':private_total,
            'public_country':public_country_amount,
            'public_country_affordable':public_country_amount>=project_cost,
            'public_aggregate_affordable':public_total>=project_cost,
            'private_aggregate_affordable':private_total>=project_cost}
    return results
