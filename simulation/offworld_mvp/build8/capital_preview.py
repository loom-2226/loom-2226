"""Non-mutating 80-country capital activation preview using Build 7's exact rule."""
from decimal import Decimal
from pathlib import Path
from offworld_kernel.prospecting import derive_mobilization
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from .country_capital_input import load_investment_capacity


def preview_country_capital(baseline_root: Path, commercial_opportunity: bool):
    capacities, provenance = load_investment_capacity(baseline_root)
    scenario = load_prospecting_scenario()
    rows = []
    for (country, year), investment in sorted(capacities.items()):
        normalized, pressure, fraction, potential = derive_mobilization(
            investment_proxy=investment,
            commercial_opportunity=Decimal(int(commercial_opportunity)),
            scenario=scenario)
        rows.append({'country': country, 'year': year,
                     'investment_proxy': str(investment),
                     'normalized_capacity': str(normalized),
                     'strategic_pressure': str(pressure),
                     'activation_fraction': str(fraction),
                     'potential_mobilization': str(potential)})
    return rows, {**provenance, 'commercial_opportunity': bool(commercial_opportunity),
                  'standing': 'COUNTERFACTUAL_PREVIEW_NOT_DISBURSEMENT'}
