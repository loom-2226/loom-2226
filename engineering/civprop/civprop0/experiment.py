"""One experiment, canonical JSON serialization and execution-based replay.

Replay and normal execution are offline. No consumer opens PostgreSQL/SQLite.
The full artifact includes evaluator-only diagnostics and must not be an actor API.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from .model import (Actor, Scenario, Economics, KnowledgeState, Mission, Event,
                    CapitalTransaction, InfrastructureChange, Run)
from .actor import prospect, continuation, update
from .observation import Instrument
from .transport import assess_mission

HERE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def load_inputs():
    raw = (HERE / 'inputs.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != (HERE / 'inputs.sha256').read_text().strip():
        raise ValueError('frozen input checksum mismatch')
    return json.loads(raw)


def implementation_hashes():
    return {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ('model.py', 'actor.py', 'observation.py', 'transport.py', 'experiment.py')}


def execute(inputs: dict, scenario: Scenario = Scenario(), seed: int = 0) -> dict:
    scenario.validate()
    if type(seed) is not int or seed < 0:
        raise ValueError('seed must be a nonnegative integer')
    # This experiment accepts only the exact captured authority bundle. General
    # intake/version negotiation is deliberately outside CIVPROP-0.
    if inputs != load_inputs():
        raise ValueError('unsupported or modified frozen authority input')
    inputs = json.loads(canonical(inputs))
    s = scenario
    code = implementation_hashes()
    run_id = 'civprop0:' + digest([digest(inputs), asdict(s), seed, code])[:24]
    a = inputs['records']['earth_actor'][0]
    actor = Actor(a['iso3'], a['display_name'], int(s.departure[:4]), a['snapshot_id'])
    e = Economics(s.mission_cost, s.continuation_cost, s.success_value,
                  s.threshold, s.sensitivity, s.false_positive)
    k = KnowledgeState(s.site_id, s.prior, s.prior_version, s.departure)
    initial = k
    instrument = Instrument(seed, s, digest(inputs['resource']))
    events, transactions, infrastructure, observations, decisions = [], [], [], [], []
    balance, mission = s.capital, None

    def emit(kind, time, payload):
        # Internal append only; payload is detached from caller-owned objects.
        events.append(Event(f'{run_id}:event:{len(events):02}', run_id, actor.actor_id,
                            kind, time, events[-1].event_id if events else None,
                            json.loads(canonical(payload))))

    def spend(amount, purpose, time):
        nonlocal balance
        if amount > balance:
            raise ValueError('insufficient capital')
        transaction = CapitalTransaction(f'{run_id}:capital:{len(transactions)}', amount, purpose, s.money_unit)
        transactions.append(transaction)
        balance -= amount
        emit('CAPITAL_COMMITTED', time, {**asdict(transaction), 'remaining_capital': balance})
        return transaction.transaction_id

    def install(kind, transaction_id, time):
        change = InfrastructureChange(f'{run_id}:asset:{len(infrastructure)}', s.site_id, transaction_id, kind)
        infrastructure.append(change)
        emit('INFRASTRUCTURE_CHANGED', time, asdict(change))

    emit('RUN_INITIALIZED', s.departure, {'actor': asdict(actor), 'capital': balance,
                                        'capital_authority': 'SCENARIO_ONLY_NOT_EARTH_WITHDRAWAL',
                                        'input_sha256': digest(inputs), 'knowledge': asdict(k)})
    opportunity = assess_mission(inputs, s)
    emit('OPPORTUNITY_EVALUATED', s.departure, asdict(opportunity))
    first = prospect(k, e, balance, opportunity.status)
    decisions.append(first)
    emit('DECISION_MADE', s.departure, {**asdict(first), 'economics': asdict(e)})
    if first.action == 'PROSPECT':
        mission = Mission(f'mission:{actor.actor_id}:{s.site_id}:{s.departure}', actor.actor_id,
                          s.site_id, s.departure, s.arrival)
        funding = spend(s.mission_cost, 'robotic prospecting mission and survey instrument', s.departure)
        emit('MISSION_LAUNCHED', s.departure, asdict(mission))
        emit('MISSION_EXECUTED', s.arrival, {**asdict(mission), 'execution_basis': 'SCENARIO_SUCCESS_CONDITIONAL_ON_FEASIBILITY'})
        install('SURVEY_INSTRUMENT', funding, s.arrival)
        observation = instrument.observe(mission.mission_id, s.arrival)
        observations.append(observation)
        emit('OBSERVATION_PRODUCED', s.arrival, asdict(observation))
        emit('OBSERVATION_RECEIVED', s.arrival, {'observation_id': observation.observation_id, 'visibility': 'PRIVATE'})
        k = update(k, observation)
        emit('KNOWLEDGE_UPDATED', s.arrival, asdict(k))
        second = continuation(k, e, balance)
        decisions.append(second)
        emit('DECISION_REEVALUATED', s.arrival, asdict(second))
        if second.action == 'CONTINUE':
            funding = spend(s.continuation_cost, 'fund existing instrument site-analysis continuation', s.arrival)
            install('FUNDED_SITE_ANALYSIS_CAPACITY', funding, s.arrival)
        else:
            emit('CAPITAL_PRESERVED', s.arrival, {'remaining_capital': balance})
    final_time = s.arrival if mission else s.departure
    emit('RUN_COMPLETED', final_time, {'ending_capital': balance, 'action': decisions[-1].action})
    if balance != s.capital - sum(t.amount for t in transactions):
        raise AssertionError('capital reconciliation failed')
    result = Run(run_id, seed, asdict(s), inputs, digest(inputs), code, actor, opportunity,
                 initial, k, tuple(decisions), mission, tuple(observations), tuple(transactions),
                 tuple(infrastructure), balance, tuple(events), instrument.audit())
    return json.loads(canonical(asdict(result)))


def replay(artifact: dict) -> dict:
    if artifact['implementation_sha256'] != implementation_hashes():
        raise ValueError('replay requires the pinned implementation')
    actual = execute(artifact['inputs'], Scenario(**artifact['scenario']), artifact['seed'])
    if canonical(actual) != canonical(artifact):
        raise ValueError('re-executed causal trace differs from artifact')
    return actual


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args()
    run = replay(json.loads(args.replay.read_text())) if args.replay else execute(load_inputs(), seed=args.seed)
    if args.output:
        args.output.write_text(json.dumps(run, sort_keys=True, indent=2, allow_nan=False) + '\n')
    print(canonical({'run_id': run['run_id'], 'decisions': run['decisions'],
                     'belief': run['final_knowledge']['probability'], 'ending_capital': run['ending_capital']}))


if __name__ == '__main__':
    main()
