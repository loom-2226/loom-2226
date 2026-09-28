"""Behavioral acceptance tests; no database or network writes."""
import ast
from dataclasses import replace
import inspect
import json
from pathlib import Path
import unittest

from . import actor
from .model import KnowledgeState, Observation, Scenario
from .experiment import execute, replay, load_inputs, canonical
from .observation import Instrument
from .transport import assess_mission


class Civprop0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_inputs()

    def run_seed(self, seed=0, **changes):
        return execute(self.inputs, replace(Scenario(), **changes), seed)

    def test_replay_is_identical(self):
        self.assertEqual(self.run_seed(), self.run_seed())

    def test_seed_changes_stochastic_state_not_site_or_actor(self):
        runs = [self.run_seed(i) for i in range(20)]
        self.assertGreater(len({r['audit']['truth'] for r in runs}), 1)
        self.assertEqual({r['actor']['actor_id'] for r in runs}, {'AUS'})
        self.assertEqual({r['scenario']['site_id'] for r in runs}, {Scenario().site_id})
        self.assertEqual(len({r['run_id'] for r in runs}), 20)

    def test_actor_firewall(self):
        tree = ast.parse(inspect.getsource(actor))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertEqual(imports, ['dataclasses', 'model'])
        self.assertNotIn('truth', inspect.getsource(actor).lower())
        self.assertEqual(list(inspect.signature(actor.update).parameters), ['knowledge', 'observation'])
        self.assertNotIn('seed', inspect.getsource(actor))

    def test_observation_mediation_and_bayes(self):
        k = KnowledgeState('site', .3, 'scenario prior', '2026-09-28T00:00:00Z')
        o = Observation('o1', 'm1', 'site', True, .85, .15, '2026-10-03T00:00:00Z')
        revised = actor.update(k, o)
        self.assertAlmostEqual(revised.probability, .255 / .36)
        self.assertEqual(k.probability, .3)
        self.assertEqual(revised.observation_ids, ('o1',))
        with self.assertRaises(ValueError):
            actor.update(k, replace(o, site_id='elsewhere'))
        with self.assertRaises(ValueError):
            actor.update(revised, o)

    def test_favourable_and_adverse_paths(self):
        runs = [self.run_seed(i) for i in range(20)]
        self.assertEqual({r['decisions'][-1]['action'] for r in runs}, {'CONTINUE', 'REJECT'})
        for r in runs:
            self.assertEqual(r['decisions'][0]['action'], 'PROSPECT')
            self.assertEqual(len(r['observations']), 1)
            self.assertEqual(r['decisions'][-1]['action'],
                             'CONTINUE' if r['observations'][0]['detected'] else 'REJECT')

    def test_accounting_and_funded_infrastructure(self):
        for seed in range(20):
            r = self.run_seed(seed)
            self.assertEqual(r['ending_capital'], 100 - sum(t['amount'] for t in r['transactions']))
            self.assertGreaterEqual(r['ending_capital'], 0)
            for change in r['infrastructure']:
                self.assertIn(change['transaction_id'], {t['transaction_id'] for t in r['transactions']})

    def test_rational_wait(self):
        for changes in ({'capital': 2}, {'mission_cost': 40}, {'technology': False}):
            r = self.run_seed(**changes)
            self.assertEqual(r['decisions'][0]['action'], 'WAIT')
            self.assertEqual(r['observations'], [])
            self.assertEqual(r['transactions'], [])
            self.assertEqual(r['ending_capital'], r['scenario']['capital'])

    def test_evidence_not_promoted_or_mutated(self):
        before = canonical(self.inputs)
        r = self.run_seed()
        self.assertEqual(canonical(self.inputs), before)
        self.assertEqual(r['inputs']['resource']['status'], 'CANDIDATE')
        self.assertIsNone(r['inputs']['resource']['site_abundance'])
        self.assertEqual(r['inputs']['resource']['site_status'], 'UNKNOWN')

    def test_transport_three_states(self):
        s = Scenario()
        self.assertEqual(assess_mission(self.inputs, s).status, 'FEASIBLE')
        self.assertEqual(assess_mission(self.inputs, replace(s, technology=False)).status, 'INFEASIBLE')
        self.assertEqual(assess_mission(self.inputs, replace(s, technology=None)).status, 'UNKNOWN')
        self.assertEqual(assess_mission(self.inputs, replace(s, departure='2027-01-01T00:00:00Z')).status, 'UNKNOWN')

    def test_serialization_reexecutes_and_rejects_tamper(self):
        artifact = json.loads(canonical(self.run_seed()))
        self.assertEqual(replay(artifact), artifact)
        artifact['ending_capital'] += 1
        with self.assertRaises(ValueError):
            replay(artifact)

    def test_discovery_order_independent(self):
        s = Scenario()
        a = Instrument(7, s, 'evidence-id')
        original = a.audit()
        Instrument(7, replace(s, site_id='SCENARIO:MOON_POLAR_PSR:UNRELATED'), 'evidence-id').audit()
        self.assertEqual(original, Instrument(7, s, 'evidence-id').audit())

    def test_measurement_is_not_perfect(self):
        pairs = []
        s = Scenario()
        for seed in range(100):
            i = Instrument(seed, s, 'evidence-id')
            o = i.observe('m', s.arrival)
            pairs.append((i.audit()['truth'], o.detected))
        self.assertIn((True, False), pairs)
        self.assertIn((False, True), pairs)

    def test_complete_causal_trace(self):
        r = self.run_seed()
        events = r['events']
        kinds = [e['event_type'] for e in events]
        for kind in ('RUN_INITIALIZED', 'OPPORTUNITY_EVALUATED', 'DECISION_MADE',
                     'CAPITAL_COMMITTED', 'MISSION_LAUNCHED', 'MISSION_EXECUTED',
                     'OBSERVATION_PRODUCED', 'OBSERVATION_RECEIVED', 'KNOWLEDGE_UPDATED',
                     'DECISION_REEVALUATED', 'INFRASTRUCTURE_CHANGED', 'RUN_COMPLETED'):
            self.assertIn(kind, kinds)
        for index, event in enumerate(events):
            self.assertEqual(event['parent_id'], events[index-1]['event_id'] if index else None)
            self.assertEqual(event['run_id'], r['run_id'])
        self.assertEqual([e['time'] for e in events], sorted(e['time'] for e in events))

    def test_pinned_authority_and_code(self):
        import hashlib
        root = Path(__file__).resolve().parents[3]
        for path, expected in self.inputs['source_hashes'].items():
            self.assertEqual(hashlib.sha256((root / path).read_bytes()).hexdigest(), expected)
        altered = json.loads(canonical(self.inputs))
        altered['resource']['status'] = 'OBSERVED'
        with self.assertRaises(ValueError):
            execute(altered)

    def test_actor_decision_has_no_oracle_dependency(self):
        from .model import Economics
        k = KnowledgeState('site', .3, 'prior', '2026-09-28T00:00:00Z')
        e = Economics(5, 50, 100, 0, .85, .15)
        baseline = actor.prospect(k, e, 100, 'FEASIBLE')
        for seed in range(5):
            Instrument(seed, Scenario(), 'unused').audit()
            self.assertEqual(actor.prospect(k, e, 100, 'FEASIBLE'), baseline)
        self.assertAlmostEqual(baseline.expected_net_value, 2.5)
        self.assertEqual(actor.continuation(k, e, 100).action, 'REJECT')

    def test_invalid_observation_rejected(self):
        o = Observation('o', 'm', 'site', True, .85, .15, '2026-10-03T00:00:00Z')
        for fields in ({'sensitivity': float('nan')}, {'false_positive': -1},
                       {'detected': 'yes'}, {'authority_class': 'EMPIRICAL'},
                       {'units': 'wt%'}):
            with self.assertRaises(ValueError):
                replace(o, **fields)

    def test_invalid_parameters_fail_closed(self):
        for args in ({'prior': -1}, {'sensitivity': 1.1}, {'capital': -1}, {'mission_cost': 0},
                     {'prior': float('nan')}, {'arrival': '2020-01-01T00:00:00Z'}):
            with self.assertRaises(ValueError):
                self.run_seed(**args)


class PortableFunctionalTests(unittest.TestCase):
    def test_committed_runs_reexecute(self):
        here = Path(__file__).resolve().parent
        for name in ('adverse.json', 'favourable.json'):
            artifact = json.loads((here / 'runs' / name).read_text())
            self.assertEqual(replay(artifact), artifact)

    def test_cli_file_roundtrip(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.json'
            command = [sys.executable, '-m', 'engineering.civprop.civprop0.experiment']
            original = subprocess.check_output(command + ['--seed', '1', '--output', str(path)], text=True)
            repeated = subprocess.check_output(command + ['--replay', str(path)], text=True)
            self.assertEqual(original, repeated)


if __name__ == '__main__':
    unittest.main()
