"""Read-only independent review of the three PR427 campaign result files."""
import json
from collections import Counter
from pathlib import Path
from decimal import Decimal

HERE = Path(__file__).resolve().parent
LABEL = 'SELECTION: Box 3 rule re-implemented. Boundary admission NOT used. Firewall checked by tripwire test only.'
CASES = ('full_clock', 'a1_flyby_comparison', 'zero_conversion_control')

def review():
    results = {}
    for case in CASES:
        d = json.loads((HERE / (case + '_report.json')).read_text())
        annual = d['per_year']
        years = [int(r['year']) for r in annual]
        assert years == list(range(2026, 2227)), (case, 'clock')
        assert d['report_label'] == LABEL
        starts = d['project_start_events']
        completed = d['project_completion_events']
        assert sum(int(r['projects_started']) for r in annual) == len(starts)
        assert sum(int(r['projects_completed']) for r in annual) == len(completed)
        assert all(x['body'] != 'CERES' for x in d['non_ceres_chain'])
        assert all(x['eligibility_year'] <= x['year'] for x in starts)
        assert all(x.get('study_receipt') for x in starts)
        project_ids = [x['project_id'] for x in starts]
        assert len(project_ids) == len(set(project_ids))
        projects = d['projects']
        sales = sum(len(x.get('sales', [])) for x in projects)
        returns = sum(len(x.get('returns', [])) for x in projects)
        # These compare event counts, not monetary totals, which have differing source fields.
        assert sum(int(r['sales']) for r in annual) == sales
        assert sum(int(r['returns']) for r in annual) == returns
        results[case] = {
            'year_count': len(years), 'roster_bodies': d['bodies'],
            'roster_sponsors': d['campaign_sponsors'],
            'starts': len(starts), 'completed': len(completed),
            'bodies_ever_started': len({x['body'] for x in starts}),
            'sponsors_ever_started': len({x['sponsor'] for x in starts}),
            'sales': sales, 'return_events': returns,
            'ties': d['tie_count'],
            'ties_dominate': d['tie_count'] > len(starts),
            'unpriced_bodies': len(d['all_unpriced_reasons']),
            'non_ceres_chain': bool(d['non_ceres_chain']),
            'eligible_study_receipts': 'PASS_FOR_STARTED_PROJECTS',
            'per_year_event_count_reconciliation': 'PASS',
            'monetary_conservation': 'KERNEL_INVARIANTS_USED; NOT INDEPENDENTLY RECONCILED AGAINST_BOUNDARY_INFLOWS',
            'limitations': ['Selection currently picks at most one candidate per sponsor per annual callback.',
                            'Family extraction support is scenario PLACEHOLDER, not observed geology.',
                            'No Box3 boundary admission: tripwire protects the selector projection only.']
        }
    control = json.loads((HERE / 'route1_control_report.json').read_text())
    assert control['pass_exact'] and control['actual_sha256'] == control['expected_sha256']
    tripwire = json.loads((HERE / 'selection_firewall_tripwire_report.json').read_text())
    assert tripwire['check']['clean_input'] == 'PASS'
    assert tripwire['check']['deliberate_hidden_field'] == 'REJECTED'
    return {'report_label': LABEL, 'cases': results,
            'route1_exact_control': 'PASS', 'selection_tripwire': 'PASS_WITH_DELIBERATE_LEAK_REJECTED',
            'audit_scope': 'Read-only consistency checks on saved run reports; not an independent kernel replay.'}

if __name__ == '__main__':
    result = review()
    (HERE / 'independent_case_audit_report.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    for case, d in result['cases'].items():
        print(case, 'starts', d['starts'], 'completed', d['completed'], 'bodies', d['bodies_ever_started'], 'sponsors', d['sponsors_ever_started'], 'ties', d['ties'], 'sales', d['sales'], 'returns', d['return_events'])
    print('Route1', result['route1_exact_control'], 'tripwire', result['selection_tripwire'])
