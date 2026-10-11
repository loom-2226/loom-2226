"""Reproduce Build 8's recorded pre-cast outputs. Run as a module from repo root."""
import argparse
import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from pathlib import Path

from simulation.offworld_mvp.build8.opening import EARTH_V4_ROOT
from simulation.offworld_mvp.build8.sponsor_executor_network_trial import run_network
from simulation.offworld_mvp.build8.named_sponsor_trial import run_named_sponsors
from simulation.offworld_mvp.build8.executor_quotes import evaluate_quotes
from simulation.offworld_mvp.build8.screened_delivery import run_screened

HERE = Path(__file__).resolve().parent


def normalize(value):
    if isinstance(value, Decimal):
        return str(value)
    if is_dataclass(value):
        return normalize(asdict(value))
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if hasattr(value, 'fingerprint'):
        return {
            'fingerprint': value.fingerprint(),
            'knowledge': normalize(getattr(value, 'build8_knowledge', None)),
            'events': normalize(getattr(value, 'event_log', [])),
            'balances': normalize({k: str(a.balance) for k, a in value.state.accounts.items()}),
        }
    return value


def capture(name):
    if name == 'network':
        value = run_network(EARTH_V4_ROOT)
    elif name == 'named_sponsors':
        value = run_named_sponsors(EARTH_V4_ROOT)
    elif name == 'quotes':
        value = [asdict(row) for row in evaluate_quotes()]
    elif name == 'screen_default':
        value = normalize(run_screened())
    elif name == 'screen_sub':
        value = normalize(run_screened(subcontract=True, capacity_slots=1))
    elif name == 'screen_sub_failure':
        value = normalize(run_screened(subcontract=True, capacity_slots=1, sub_failure=True, resource_on_failure=True))
    else:
        raise ValueError(name)
    return json.dumps(value, sort_keys=True, default=str, indent=2) + '\n'


NAMES = ('network', 'named_sponsors', 'quotes', 'screen_default', 'screen_sub', 'screen_sub_failure')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Regenerate snapshot files explicitly')
    parser.add_argument('names', nargs='*', choices=NAMES)
    args = parser.parse_args()
    for name in args.names or NAMES:
        result = capture(name)
        target = HERE / (name + '.json')
        if args.write:
            target.write_text(result)
            print('RECORDED', name)
        else:
            expected = target.read_text()
            if result != expected:
                raise SystemExit(f'MISMATCH: {name} (snapshot differs; do not overwrite baseline)')
            print('EXACT', name)


if __name__ == '__main__':
    main()
