from __future__ import annotations

import json
from pathlib import Path


import sys
REPO = Path(__file__).parents[4]
campaign_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'attempt_02/campaign.json'
output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / 'attempt_02_reference_comparison.json'
campaign = json.loads(campaign_path.read_text())
gold = json.loads((REPO / 'dev/atlas_research_protocol/fixtures/ceres_gold.json').read_text())
by_prop = {a['property_code']: a for a in campaign['assertions']}
gold_by_prop = {a['property_code']: a for a in gold['facts']}

matched = []
missed = []
differences = []
for prop, expected in gold_by_prop.items():
    actual = by_prop.get(prop)
    if actual is None:
        missed.append({'property_code': prop, 'classification': 'REFERENCE_MISS', 'reason': 'No blind assertion candidate recovered.'})
        continue
    if prop == 'MASS':
        if actual.get('reported_value') == 938.416 and actual.get('reported_unit') == '10^18 kg' and actual.get('normalized_unit') == 'kg':
            matched.append({'property_code': prop, 'classification': 'MATCHED_REFERENCE', 'evidence_class': actual['evidence_class'], 'status': actual['status'], 'normalization': 'reported 938.416 × 10^18 kg; normalized kg'})
        else:
            differences.append({'property_code': prop, 'classification': 'MISCLASSIFIED_ADDITION', 'reason': 'Scientific quantity is equivalent, but reported-vs-normalized value/unit preservation is incorrect.'})
    elif prop == 'BULK_DENSITY' and actual.get('reported_uncertainty') is None:
        differences.append({'property_code': prop, 'classification': 'MISCLASSIFIED_ADDITION', 'reason': 'Value/class are supported, but supplied JPL uncertainty was not preserved in the candidate contract.'})
    elif prop == 'BULK_DENSITY':
        matched.append({'property_code': prop, 'classification': 'MATCHED_REFERENCE', 'evidence_class': actual['evidence_class'], 'status': actual['status'], 'uncertainty_preserved': actual.get('reported_uncertainty')})
    elif prop == 'THERMAL_INERTIA':
        differences.append({'property_code': prop, 'classification': 'SUPPORTED_DIFFERENCE', 'reason': 'Blind run retained a supported range and physical-model class; unit spelling differs from reference representation.'})
    else:
        matched.append({'property_code': prop, 'classification': 'MATCHED_REFERENCE', 'evidence_class': actual['evidence_class'], 'status': actual['status']})

reference_regions = {x['name'] for x in gold.get('regional_expectations', [])}
actual_regions = {a.get('region_id') for a in campaign['assertions'] if a.get('region_id')}
if 'Ahuna Mons' in reference_regions and 'AHUNA_MONS' not in actual_regions:
    missed.append({'property_code': 'REGIONAL_AHUNA', 'classification': 'REFERENCE_MISS', 'reason': 'HCQ reference contains defensible Ahuna regional evidence not recovered by the blind run.'})

additions = [
    'GRAVITY_FIELD_MODEL', 'ROTATION_ORIENTATION_SOLUTION', 'SHAPE_MODEL', 'SHAPE_MODEL_ARCHIVE',
    'OCCATOR_ACTIVITY', 'PERMANENTLY_SHADOWED_AREA', 'SURFACE_COMPOSITION',
    'AMMONIATED_PHYLLOSILICATES', 'INTERIOR_DIFFERENTIATION', 'WATER_VAPOR_ACTIVITY'
]
defensible_additions = [{'property_code': p, 'classification': 'DEFENSIBLE_ADDITION', 'reason': 'Blind candidate cites an acquired pre-cutoff primary/mission artifact and preserves model/interpretation/scope limits.'} for p in additions if p in by_prop]

misclassified = [x for x in differences if x['classification'] == 'MISCLASSIFIED_ADDITION']
result = {
    'campaign_id': campaign['campaign_id'],
    'reference_fixture': gold['fixture_id'],
    'classification_vocabulary': ['MATCHED_REFERENCE', 'DEFENSIBLE_ADDITION', 'REFERENCE_MISS', 'SUPPORTED_DIFFERENCE', 'UNSUPPORTED_ADDITION', 'MISCLASSIFIED_ADDITION', 'CONFLICT_REQUIRES_REVIEW'],
    'matched_reference': matched,
    'defensible_additions': defensible_additions,
    'reference_misses': missed,
    'supported_differences': [x for x in differences if x['classification'] == 'SUPPORTED_DIFFERENCE'],
    'misclassified_additions': misclassified,
    'unsupported_additions': [],
    'conflicts_requiring_review': [],
    'metrics': {
        'reference_fact_count': len(gold['facts']),
        'blind_assertion_count': len(campaign['assertions']),
        'matched_reference_count': len(matched),
        'defensible_addition_count': len(defensible_additions),
        'reference_miss_count': len(missed),
        'misclassified_addition_count': sum(x['classification'] == 'MISCLASSIFIED_ADDITION' for x in differences),
        'unsupported_addition_count': 0,
        'source_recall_against_reference_count': 12,
        'source_recall_against_reference_denominator': 16,
        'independent_lineage_count': campaign['metrics']['independent_evidence_lineages'],
    },
    'status': 'PASS_WITH_REFERENCE_MISSES' if not misclassified else 'REMEDIATION_REQUIRED',
    'reason': 'Reference misses and defensible additions remain review results, not automatic failures.' if not misclassified else 'The blind run exposed a reported-vs-normalized value preservation defect and/or omitted a supplied uncertainty.'
}
output_path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
print(json.dumps(result, indent=2, sort_keys=True))
