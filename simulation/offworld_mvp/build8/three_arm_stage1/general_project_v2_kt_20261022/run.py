"""Step 2–4 runner. Writes every generated result beside this module."""
import argparse
import csv
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
import hashlib
import json
from pathlib import Path
import time

from simulation.offworld_mvp.build8.ceres_downstream import (
    A as CERES_INPUTS, CeresDownstream, T as CERES_T,
)
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.sponsor_executor_network_trial import EXECUTORS
from simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022.general_project import (
    GeneralProjectCampaign, scenario_identity,
)

HERE = Path(__file__).resolve().parent
STAGE1 = HERE.parent
SCENARIO_PATH = HERE / 'scenario.json'
PRICE_PATH = STAGE1 / 'A_VEHICLE_MISSION_PAIRS.csv'
MAX_RUN_SECONDS = 3600


def load_inputs():
    scenario_bytes = SCENARIO_PATH.read_bytes()
    scenario = json.loads(scenario_bytes)
    price_bytes = PRICE_PATH.read_bytes()
    price_sha = hashlib.sha256(price_bytes).hexdigest()
    if price_sha != scenario['price_inputs']['sha256']:
        raise RuntimeError('saved mission price table SHA mismatch')
    with PRICE_PATH.open(newline='') as stream:
        prices = list(csv.DictReader(stream))
    identities = {row['run_identity'] for row in prices}
    if identities != {scenario['price_inputs']['source_run_identity']}:
        raise RuntimeError('saved mission table run identity mismatch')
    if scenario['run_identity'] != scenario_identity(scenario, price_bytes):
        raise RuntimeError('scenario run identity mismatch')
    return scenario, prices, scenario_bytes, price_bytes


def jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return jsonable(asdict(value))
    if hasattr(value, '_asdict'):
        return jsonable(value._asdict())
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [jsonable(v) for v in value]
    if hasattr(value, '__dict__'):
        return jsonable(vars(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def write_json(name, data):
    path = HERE / name
    path.write_text(json.dumps(jsonable(data), sort_keys=True, indent=2) + '\n')
    return path


def run_campaign(campaign, run_name, share, start_year, end_year):
    campaign.record_states(start_year)
    started = time.perf_counter()
    result = run_cast_payments(share=share, end_year=end_year,
        run_setting={'name': 'general_project_campaign' if run_name != 'reference' else 'ceres_downstream',
                     'campaign': campaign})
    elapsed = time.perf_counter() - started
    if elapsed > MAX_RUN_SECONDS:
        raise RuntimeError(f'{run_name} exceeded 60-minute runtime ceiling: {elapsed:.3f}s')
    campaign_result = campaign.report()
    return result, campaign_result, elapsed


def ordered_projection(kernel):
    transactions = [jsonable(tx) for tx in kernel.state.transactions]
    event_collections = {}
    for label, obj in (('kernel', kernel), ('state', kernel.state)):
        values = getattr(obj, '__dict__', {})
        for key, value in values.items():
            low = key.lower()
            if ('event' in low or 'audit' in low) and isinstance(value, (list, tuple)):
                event_collections[f'{label}.{key}'] = jsonable(value)
    if not event_collections:
        raise RuntimeError('cannot locate ordered kernel event projection')
    # The kernel may expose audit and domain-event lists separately; retain all
    # discovered collections, their names and their source order.
    return dict(transactions=transactions, events=event_collections)


def first_difference(left, right, path='$'):
    if type(left) is not type(right):
        return dict(path=path, reference=left, generic=right)
    if isinstance(left, dict):
        keys = list(dict.fromkeys([*left.keys(), *right.keys()]))
        for key in keys:
            if key not in left or key not in right:
                return dict(path=f'{path}.{key}', reference=left.get(key), generic=right.get(key))
            mismatch = first_difference(left[key], right[key], f'{path}.{key}')
            if mismatch:
                return mismatch
        return None
    if isinstance(left, list):
        if len(left) != len(right):
            return dict(path=path + '.length', reference=len(left), generic=len(right))
        for index, (a, b) in enumerate(zip(left, right)):
            mismatch = first_difference(a, b, f'{path}[{index}]')
            if mismatch:
                return mismatch
        return None
    return None if left == right else dict(path=path, reference=left, generic=right)


def equivalence(scenario):
    reference = CeresDownstream()
    start_year = int(scenario['full_clock']['start_year'])
    end_year = int(scenario['full_clock']['end_year'])
    reference_result, reference_campaign, reference_seconds = run_campaign(
        reference, 'reference', CERES_T('share'), start_year, end_year)
    generic = GeneralProjectCampaign(scenario, _read_prices(),
        project_override=scenario['project'])
    generic_result, generic_campaign, generic_seconds = run_campaign(
        generic, 'generic', CERES_T('share'), start_year, end_year)
    reference_projection = ordered_projection(reference_result['kernel'])
    generic_projection = ordered_projection(generic_result['kernel'])
    mismatch = first_difference(reference_projection, generic_projection)
    exact = mismatch is None
    summary = dict(result='PASS' if exact else 'FAIL_FIRST_MISMATCH',
        reference_class='CeresDownstream', generic_class='GeneralProjectCampaign',
        transaction_counts=(len(reference_projection['transactions']),
                            len(generic_projection['transactions'])),
        event_collections=(list(reference_projection['events']),
                           list(generic_projection['events'])),
        ordered_projection_exact=exact, first_mismatch=mismatch,
        allowed_id_rename_mapping={}, reference_runtime_seconds=reference_seconds,
        generic_runtime_seconds=generic_seconds,
        comparison='ordered transactions and ordered kernel event projections; zero tolerance',
        equivalence_evidence_boundary=('Exact replay includes the legacy Ceres kernel realized-output '
            'admission call to preserve event identity. This equivalence fixture is TEST_ONLY and '
            'does not qualify synthetic extraction as scientific evidence. The general full-clock '
            'run does not admit synthetic extraction observations and records PLACEHOLDER only.'),
        run_identity=scenario_identity(scenario, PRICE_PATH.read_bytes()))
    write_json('equivalence_report.json', summary)
    write_json('equivalence_reference_projection.json', reference_projection)
    write_json('equivalence_generic_projection.json', generic_projection)
    if not exact:
        raise RuntimeError('exact Ceres equivalence failed; first mismatch is in equivalence_report.json')
    return summary


def _read_prices():
    with PRICE_PATH.open(newline='') as stream:
        return list(csv.DictReader(stream))


def full_clock(scenario, prices, scenario_bytes, price_bytes, conversion_enabled):
    mode = 'full_clock' if conversion_enabled else 'conversion_zero_control'
    campaign = GeneralProjectCampaign(scenario, prices, conversion_enabled=conversion_enabled)
    start_year = int(scenario['full_clock']['start_year'])
    end_year = int(scenario['full_clock']['end_year'])
    result, campaign_report, elapsed = run_campaign(campaign, mode, CERES_T('share'),
                                                      start_year, end_year)
    annual = campaign_report['year_rollup']
    if len(annual) != int(scenario['full_clock']['end_year']) - int(scenario['full_clock']['start_year']) + 1:
        raise RuntimeError(f'full-clock annual coverage is incomplete: {len(annual)} rows; '
            f'first/last={annual[:1]}/{annual[-1:]}; '
            f'lifecycle_rows={len(campaign_report["yearly_lifecycle"])}')
    state = campaign.project_state
    placeholder_count = len(state.realized_outputs)
    generic_project = campaign_report['generic_project']
    mission_settlement = next((row for row in campaign_report['yearly_lifecycle']
                               if row.get('mission_price_transaction')), None)
    mission_tx = None if mission_settlement is None else mission_settlement['mission_price_transaction']
    trace = dict(project_id=state.project_id, body=state.body, sponsor=state.sponsor,
        executor=state.executor, study_receipt=(generic_project['physical'][0].get('study_receipt')
            if generic_project['physical'] else None), mission_price_transaction=mission_tx,
        mission_price_settlement=mission_settlement,
        financing=next((row for row in generic_project['physical'] if row['stage'] == 'FINANCE'), None),
        construction=tuple(row for row in generic_project['physical'] if row['stage'] == 'CONSTRUCTION'),
        extractions=tuple(row for row in generic_project['physical'] if row['stage'] == 'EXTRACTED'),
        sales=generic_project['sales'], returns=generic_project['returns'],
        appropriations=generic_project['appropriations'])
    report = dict(run_name=mode,
        run_identity=scenario_identity(scenario, price_bytes) + (':conversion=1' if conversion_enabled else ':conversion=0'),
        scenario_sha256=hashlib.sha256(scenario_bytes).hexdigest(),
        mission_price_table_sha256=hashlib.sha256(price_bytes).hexdigest(),
        source_price_run_identity=scenario['price_inputs']['source_run_identity'],
        runtime_seconds=elapsed, year_range=[start_year, end_year], year_count=len(annual),
        campaign_sponsor_count=len(campaign.requesters), executor_count=len(EXECUTORS),
        body_count=len(campaign.bodies), per_year_rollup=annual,
        route1_campaign_annual=campaign_report['annual'],
        lifecycle_annual=campaign_report['yearly_lifecycle'],
        project=generic_project, traced_chain=trace,
        sponsor_exhaustion_by_year=tuple(dict(year=row['year'], sponsors=row['sponsor_exhausted'])
                                         for row in campaign_report['yearly_lifecycle']),
        unpriced_mission_bodies=campaign_report['unpriced_bodies'],
        unpriced_mission_count=campaign_report['unpriced_count'],
        mission_price_policy=scenario['price_inputs'],
        evidence_status_table=[
            dict(status='REAL', count=0, meaning='No synthetic extraction is admitted as a REAL observation in general mode.'),
            dict(status='PLACEHOLDER', count=placeholder_count, meaning='Synthetic lifecycle extraction outputs; not observations or scientific evidence.'),
            dict(status='TEST_ONLY_STUDY', count=len(campaign.studies), meaning='Paid A1/A2 study outcomes remain analytically separate from physical missions.')],
        physical_mission_funded=sum(row['funded'] for row in campaign_report['year_rollup']),
        physical_projects_completed=sum(row['completed'] for row in campaign_report['year_rollup']),
        sales=sum(row['sales'] for row in campaign_report['year_rollup']),
        returns=sum(row['returns'] for row in campaign_report['year_rollup']),
        kernel_transaction_count=len(result['kernel'].state.transactions),
        zero_conversion_control=not conversion_enabled)
    write_json(mode + '_report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('equivalence', 'full', 'control', 'all'), default='all')
    args = parser.parse_args()
    scenario, prices, scenario_bytes, price_bytes = load_inputs()
    run_id = scenario_identity(scenario, price_bytes)
    write_json('input_identity.json', dict(run_identity=run_id,
        scenario_sha256=hashlib.sha256(scenario_bytes).hexdigest(),
        mission_price_table_sha256=hashlib.sha256(price_bytes).hexdigest(),
        mission_price_run_identity=scenario['price_inputs']['source_run_identity']))
    if args.mode in ('equivalence', 'all'):
        equivalence(scenario)
    if args.mode in ('full', 'all'):
        full_clock(scenario, prices, scenario_bytes, price_bytes, True)
    if args.mode in ('control', 'all'):
        full_clock(scenario, prices, scenario_bytes, price_bytes, False)


if __name__ == '__main__':
    main()
