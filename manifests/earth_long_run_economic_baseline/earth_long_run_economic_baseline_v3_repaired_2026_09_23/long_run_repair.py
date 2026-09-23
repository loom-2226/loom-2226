"""Universal post-2060 economic transition and active-sector boundary repair.

The OECD 2025 long-run scenario uses a one-third capital share and a 3.4
capital/output target. Transition speeds below are explicit experiment assumptions.
"""
import json
import math
from pathlib import Path

OECD_ALPHA = 1.0 / 3.0
OECD_KY = 3.4
ALPHA_HALF_LIFE = 20.0
INVESTMENT_HALF_LIFE = 20.0
KY_ADJUSTMENT = 0.05


def transition_weight(years, half_life):
    return 1.0 - 2.0 ** (-years / half_life)


def effective_alpha(alpha_2060, year):
    return alpha_2060 + transition_weight(year - 2060, ALPHA_HALF_LIFE) * (OECD_ALPHA - alpha_2060)


def rebase_A(A, old_alpha, new_alpha, capital, labor):
    if A <= 0 or capital <= 0 or labor <= 0:
        return A, 1.0
    factor = math.exp((old_alpha - new_alpha) * math.log(capital / labor))
    return A * factor, factor


def investment_budget(year, national_rate, va, prior_va, capital, depreciation_need):
    """Blend the 2060 national rate into a capital/output feedback rule.

    K[t+1] = K[t] - depreciation + I[t]. The growth term moves the target
    capital stock with output; the gap term closes 5% of the remaining gap.
    """
    target = max(0.0, depreciation_need + OECD_KY * (va - prior_va)
                 + KY_ADJUSTMENT * (OECD_KY * va - capital))
    weight = transition_weight(year - 2060, INVESTMENT_HALF_LIFE)
    return max(0.0, (1.0 - weight) * national_rate * va + weight * target)


def read_ndjson(path):
    return [json.loads(line) for line in Path(path).open()]


def repair_active_boundary(root, countries, base, state, asset_state, sector_rows,
                           asset_rows, labor_shares, investment_shares, base_go60,
                           base_compute_enabling_per_worker,
                           base_automation_per_worker, base_energy_go_per_worker,
                           current_tfp, sectors, assets):
    """Restore active non-positive-VA nodes without changing country totals.

    A positive previous-year-price VA/output ratio identifies positive real
    activity despite non-positive current-price accounting VA. The 2026 sector
    gross output and employment supply the activity scale. Country growth from
    2026 to the qualified 2060 boundary advances that scale; capital uses the
    same country's 2060 capital/VA ratio. Other sectors surrender proportional
    shares, so the qualified 2060 country accounts remain exact.
    """
    oecd = Path(root) / 'oecd_ten_sector_2024'
    stage = Path(root) / 'earth_repair_successor_2026_09_22' / 'stage_2026_2031'
    def source(name, field):
        return {(r['country'], r['sector']): r[field] for r in read_ndjson(oecd / name)}
    current_va = source('current_country_sector_value_added_2024.ndjson', 'value_added')
    current_go = source('current_country_sector_gross_output_2024.ndjson', 'gross_output')
    pyp_va = source('pyp_country_sector_value_added_2024.ndjson', 'value_added')
    pyp_go = source('pyp_country_sector_gross_output_2024.ndjson', 'gross_output')
    seed_sectors = {(r['iso3'], r['sector']): r for r in read_ndjson(stage / 'country_sectors_2026_2031.ndjson') if r['year'] == 2026}
    seed_countries = {r['iso3']: r for r in read_ndjson(stage / 'countries_2026_2031.ndjson') if r['year'] == 2026}
    repairs = []
    sector_index = {(r['iso3'], r['sector']): r for r in sector_rows if r['year'] == 2060}
    asset_index = {(r['iso3'], r['sector'], r['asset_class']): r for r in asset_rows if r['year'] == 2060}
    for iso in sorted(countries):
        for sector in sectors:
            node = (iso, sector)
            seed = seed_sectors[node]
            if not (current_va[node] <= 0 and current_go[node] > 0
                    and pyp_va[node] > 0 and pyp_go[node] > 0
                    and seed['gross_output'] > 0 and seed['employment'] > 0
                    and state[node]['value_added'] <= 0):
                continue
            country = countries[iso]
            seed_country = seed_countries[iso]
            va = (seed['gross_output'] * pyp_va[node] / pyp_go[node]
                  * country['value_added'] / seed_country['value_added'])
            go = va * pyp_go[node] / pyp_va[node]
            cap = va * country['capital'] / country['value_added']
            emp = (seed['employment'] / seed_country['employment']
                   * country['employment'])
            inv = va / country['value_added'] * country['investment']
            if min(va, go, cap, emp, inv) <= 0:
                raise ValueError(f'invalid active-boundary reconstruction {node}')
            old = state[node]
            if any(value >= country[key] for value, key in ((va, 'value_added'),
                  (go, 'gross_output'), (cap, 'capital'), (emp, 'employment'),
                  (inv, 'investment'))):
                raise ValueError(f'active-boundary reconstruction exceeds country {node}')
            others = [s for s in sectors if s != sector]
            old_totals = {key: sum(state[(iso,s)][key] for s in others)
                          for key in ('value_added','gross_output','capital','employment','investment')}
            new_values = {'value_added':va,'gross_output':go,'capital':cap,
                          'employment':emp,'investment':inv}
            multipliers = {key:(country[key]-value)/old_totals[key]
                           for key,value in new_values.items()}
            if min(multipliers.values()) <= 0:
                raise ValueError(f'negative residual allocation {node}')
            for s in others:
                item = state[(iso,s)]
                row = sector_index[(iso,s)]
                for key,mult in multipliers.items():
                    item[key] *= mult
                    row[key] = item[key]
                item['go_va_ratio'] = item['gross_output'] / item['value_added']
                for a in assets:
                    asset_state[(iso,s,a)]['capital'] *= multipliers['capital']
                    asset_state[(iso,s,a)]['investment'] *= multipliers['investment']
                    asset_index[(iso,s,a)]['capital'] = asset_state[(iso,s,a)]['capital']
                    asset_index[(iso,s,a)]['investment'] = asset_state[(iso,s,a)]['investment']
            prior_asset_cap = sum(asset_state[(iso,sector,a)]['capital'] for a in assets)
            prior_asset_inv = sum(asset_state[(iso,sector,a)]['investment'] for a in assets)
            for a in assets:
                ac = asset_state[(iso,sector,a)]
                ac['capital'] = cap * ac['capital'] / prior_asset_cap
                ac['investment'] = inv * ac['investment'] / prior_asset_inv
                asset_index[(iso,sector,a)]['capital'] = ac['capital']
                asset_index[(iso,sector,a)]['investment'] = ac['investment']
            old.update(new_values, go_va_ratio=go/va)
            sector_index[node].update(new_values)
            for s in sectors:
                item = state[(iso,s)]
                item['A'] = item['value_added'] / (current_tfp[iso]
                    * item['capital'] ** base[iso]['alpha']
                    * item['employment'] ** (1-base[iso]['alpha']))
                sector_index[(iso,s)]['A'] = item['A']
                base_go60[(iso,s)] = item['gross_output']
            labor_total = sum(state[(iso,s)]['employment'] for s in sectors)
            inv_total = sum(state[(iso,s)]['investment'] for s in sectors)
            labor_shares[iso] = {s:state[(iso,s)]['employment']/labor_total for s in sectors}
            investment_shares[iso] = {s:state[(iso,s)]['investment']/inv_total for s in sectors}
            base_energy_go_per_worker[iso] = state[(iso,'ENERGY')]['gross_output']/country['employment']
            compute = asset_state[(iso,'COMPUTE','machinery')]['capital'] + asset_state[(iso,'COMPUTE','other_assets')]['capital']
            base_compute_enabling_per_worker[iso] = compute/country['employment']
            for s in sectors:
                auto = asset_state[(iso,s,'machinery')]['capital'] + asset_state[(iso,s,'transport_equipment')]['capital']
                base_automation_per_worker[(iso,s)] = auto/state[(iso,s)]['employment']
            repairs.append({'iso3':iso,'sector':sector,'source_va_2024_current_usd_million':current_va[node],
                            'source_go_2024_current_usd_million':current_go[node],
                            'source_va_2024_pyp_usd_million':pyp_va[node],
                            'source_go_2024_pyp_usd_million':pyp_go[node],
                            'seed_go_2026':seed['gross_output'],'seed_employment_2026':seed['employment'],
                            'reconstructed_va_2060':va,'reconstructed_go_2060':go,
                            'reconstructed_capital_2060':cap,'reconstructed_employment_2060':emp,
                            'method':'PYP_VA_GO_RATIO_X_2026_GO_X_COUNTRY_2026_2060_GROWTH; COUNTRY_2060_ACCOUNTING_PRESERVED'})
    return repairs
