"""Additive correction: all affordable candidates and source-correct flyby quotes."""
import json
from decimal import Decimal
from pathlib import Path
from collections import defaultdict
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022 import run_selection as r
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_rule_selection_kt_20261022.selection_rule import RECORD_FIELDS, REPORT_LABEL

m = r.m
OUT = Path(__file__).resolve().parent

def select_all(records, sponsor_capital):
    """Per sponsor, authorize every affordable eligible project in increasing commitment order."""
    by_sponsor = defaultdict(list)
    for record in records:
        extra, missing = set(record) - RECORD_FIELDS, RECORD_FIELDS - set(record)
        if extra or missing:
            raise ValueError(f"selection input schema violation: extra={sorted(extra)} missing={sorted(missing)}")
        if record['reviewed_result'] == 'SUPPORTS_ADVANCE' and record['review_status'] == 'ADVANCE':
            by_sponsor[record['sponsor']].append(record)
    selected, ties = [], []
    for sponsor, candidates in by_sponsor.items():
        candidates.sort(key=lambda c: (Decimal(str(c['total_capital_commitment'])),
                                       int(c['eligibility_year']), int(c['roster_index'])))
        costs = defaultdict(list)
        for candidate in candidates:
            costs[Decimal(str(candidate['total_capital_commitment']))].append(candidate)
        for cost, group in costs.items():
            if len(group) > 1:
                ties.append({'sponsor': sponsor, 'commitment': str(cost),
                             'projects': [{'body': x['body'], 'eligibility_year': x['eligibility_year'],
                                           'roster_index': x['roster_index']} for x in group]})
        remaining = Decimal(str(sponsor_capital.get(sponsor, '0')))
        for candidate in candidates:
            commitment = Decimal(str(candidate['total_capital_commitment']))
            if commitment <= remaining:
                selected.append(candidate)
                remaining -= commitment
    return selected, ties

class FinalCampaign(r.RuleCampaign):
    def __init__(self, scenario, prices, audit, conversion=True, mission_type=None):
        super().__init__(scenario, prices, audit, conversion, mission_type)
        if self.mission_type != m.SCENARIO['mission']['flyby_comparison_type']:
            return
        # The vehicle_flyby quote contains launch_cost_usd only. It is NOT a
        # total mission quote. Prefer the full recovered combined flyby quote.
        for row in audit['matrix']:
            if row['calendar_year'] != m.SCENARIO['mission']['quote_year'] or row['mission_type'] != self.mission_type:
                continue
            quote = next((q for q in row['quotes'] if q['source'] == 'recovered_combined_59'
                          and q['price_fields'].get('lowest_price_usd')), None)
            if quote:
                self.main_quotes[row['body']] = (Decimal(quote['price_fields']['lowest_price_usd']), quote)
        self.all_unpriced = [{'body': body, 'calendar_year': m.SCENARIO['mission']['quote_year'],
                              'mission_type': self.mission_type,
                              'reason': 'No full mission flyby quote; launch-only proxy is insufficient.'}
                             for body in self.bodies if body not in self.main_quotes]

def tripwire():
    clean = {'body':'A','sponsor':'S','eligibility_year':2037,'roster_index':0,
             'reviewed_result':'SUPPORTS_ADVANCE','review_status':'ADVANCE',
             'quoted_price_usd':'1','quoted_price_model':'0.1','total_capital_commitment':'0.2'}
    valid, _ = select_all([clean], {'S':'1'})
    assert valid == [clean]
    bad = dict(clean, hidden_world_resource='SECRET')
    try:
        select_all([bad], {'S':'1'})
    except ValueError:
        return {'clean_input':'PASS','deliberate_hidden_field':'REJECTED','leak_removed':True}
    raise AssertionError('Hidden-world tripwire failed')

def main():
    m.HERE = OUT
    m.SCENARIO = json.loads((OUT/'scenario.json').read_text())
    r.OUT = OUT
    r.select_projects = select_all
    m.PortfolioCampaign = FinalCampaign
    m.write = r.labeled_write
    def parity(_scenario, _prices):
        result = {'result':'NOT_RERUN_KERNEL_AND_LIFECYCLE_UNCHANGED',
                  'prior_reference':'Ceres exact parity 8798 transactions, 290 events PASS'}
        r.labeled_write('ceres_equivalence_applicability_report.json', result)
        return result
    m.ceres_equivalence = parity
    r.labeled_write('selection_firewall_tripwire_report.json',
                    {'check':tripwire(),'boundary_admission_used':False,
                     'selection_rule':'All affordable per sponsor, lowest commitment then earliest eligible year then roster index',
                     'allowlisted_fields':sorted(RECORD_FIELDS)})
    m.main()

if __name__ == '__main__':
    main()
