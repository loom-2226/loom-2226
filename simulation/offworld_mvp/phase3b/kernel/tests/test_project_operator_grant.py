"""Project-scoped operator access, without conflating legal ownership."""
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'build6/qualification'))
from build6d_fixture import make_kernel

from offworld_kernel.boundary import ConsumptionRequest, query_context
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import Asset, AssetKind, AccountKind
from offworld_kernel.mvp_state import ActionKind
from offworld_kernel.operating import ExtractionResolutionRecord
from offworld_kernel.policy import FactState


class ProjectOperatorGrantTests(unittest.TestCase):
    def setUp(self):
        self.k, _ = make_kernel()
        self.k.state.assets['MINE-P'] = Asset(
            'MINE-P', 'P', 'OFF:T1', AssetKind.PRODUCTIVE, D('10'), D('5'))
        self.k.state.projects['P'].status = 'OPERATING'

    def permit(self, actor, project='P'):
        self.k.agents[actor].capabilities.add('OPERATE_PROJECT:' + project)

    def request(self, actor, concept, subject='P', scope='PROJECT:P',
                unit='STATUS_CATEGORY'):
        return ConsumptionRequest(
            'operator-test:' + actor + ':' + concept, actor, 'POLICY', subject,
            concept, scope, 'SIM_TIME', '9', '9', 'REALIZED',
            self.k.boundary_manifest.run_id, 'AGENT', actor, 'ADMITTED',
            unit, 'ADMITTED_INFORMATION')

    def fact(self, actor, concept='project.STATUS'):
        mapping = {
            'project.STATUS': ('P', 'PROJECT:P', 'STATUS_CATEGORY'),
            'project.CASH_BALANCE': ('P', 'PROJECT:P', 'MODEL_CURRENCY'),
            'asset.CAPACITY': ('P', 'PROJECT:P', 'MODEL_RESOURCE_UNIT_PER_CYCLE'),
        }
        return query_context(self.k, self.request(actor, concept, *mapping[concept]))

    def executed_output(self, actor):
        # Explicit test fixture: a recorded extraction event, matching actor
        # and history. The test targets access, not physical extraction physics.
        event = self.k.event(9, actor, ActionKind.EXTRACT, 'FULL_OUTPUT', ('P',))
        self.k.extraction_resolution_records.append(ExtractionResolutionRecord(
            9, actor, 'OP-DEC-' + actor, 'P', 'MINE-P', 'RES',
            D(2), D(2), D(20), D(18), D(0), D(2), event.id))
        return event.id

    def output_fact(self, actor, event_id):
        return query_context(self.k, self.request(
            actor, 'cycle.ACTUAL_OUTPUT', event_id, 'SITE:OFF:T1',
            'MODEL_RESOURCE_UNIT_BY_FAMILY'))

    def test_legal_owner_keeps_fact_and_output_access(self):
        for concept in ('project.STATUS', 'project.CASH_BALANCE', 'asset.CAPACITY'):
            with self.subTest(concept=concept):
                self.assertEqual(self.fact('SPN', concept).value_state, FactState.KNOWN)
        event_id = self.executed_output('SPN')
        self.k.admit_realized_output_observation(9, 'SPN', event_id)
        fact = self.output_fact('SPN', event_id)
        self.assertEqual((fact.value_state, fact.value), (FactState.KNOWN, '2'))

    def test_authorized_nonowner_can_admit_own_output_and_read_project(self):
        original_fp = self.k.mvp_fingerprint()
        self.permit('PUB')
        self.assertNotEqual(self.k.mvp_fingerprint(), original_fp)
        self.assertNotIn('PUB', self.k.state.projects['P'].owners)
        for concept in ('project.STATUS', 'project.CASH_BALANCE', 'asset.CAPACITY'):
            with self.subTest(concept=concept):
                self.assertEqual(self.fact('PUB', concept).value_state, FactState.KNOWN)
        event_id = self.executed_output('PUB')
        self.k.admit_realized_output_observation(9, 'PUB', event_id)
        self.assertEqual((self.output_fact('PUB', event_id).value_state,
                          self.output_fact('PUB', event_id).value),
                         (FactState.KNOWN, '2'))

    def test_unauthorized_nonowner_remains_blocked(self):
        for concept in ('project.STATUS', 'project.CASH_BALANCE', 'asset.CAPACITY'):
            with self.subTest(concept=concept):
                self.assertEqual(self.fact('FIN', concept).reason_code,
                                 'BLOCKED_POSSESSION')
        event_id = self.executed_output('FIN')
        with self.assertRaisesRegex(InvariantError, 'BLOCKED_POSSESSION'):
            self.k.admit_realized_output_observation(9, 'FIN', event_id)
        # Information possession alone cannot waive project authorization.
        self.k.agents['FIN'].information.add(event_id)
        self.assertEqual(self.output_fact('FIN', event_id).reason_code,
                         'BLOCKED_POSSESSION')

    def test_grant_is_exact_project_only_and_not_hidden_truth(self):
        self.permit('PUB', 'P')
        self.k.add_account('Q-cash', 'SPN', 'OFF:T1', AccountKind.PROJECT_CASH)
        self.k.add_project('Q', 'OFF:T1', 'Q-cash', {'SPN': D(1)})
        # Same method but outside the existing author's exact use bindings:
        # add a test-scoped source binding for the second project.
        from dataclasses import replace
        m = self.k.boundary_manifest
        self.k.boundary_manifest = replace(
            m,
            allowed_use_contracts=(*m.allowed_use_contracts,
                ('PUB','POLICY','project.Q_STATUS','PROJECT:Q','REALIZED',
                 'AGENT','STATUS_CATEGORY','ADMITTED_INFORMATION'),
                ('PUB','POLICY','R_RECOVERABLE','SITE:OFF:T1','REALIZED',
                 'AGENT','MODEL_RESOURCE_UNIT_BY_FAMILY','ADMITTED_INFORMATION')),
            source_resolver_bindings=(*m.source_resolver_bindings,
                ('PUB','project.Q_STATUS','PROJECT:Q:STATUS'),
                ('PUB','R_RECOVERABLE','RESOURCE')))
        other = self.request('PUB','project.Q_STATUS','Q','PROJECT:Q',
                             'STATUS_CATEGORY')
        self.assertEqual(query_context(self.k, other).reason_code,
                         'BLOCKED_POSSESSION')
        # No operator grant widens the existing forbidden Agent truth view.
        truth = self.request('PUB','R_RECOVERABLE','RES','SITE:OFF:T1',
                             'MODEL_RESOURCE_UNIT_BY_FAMILY')
        with self.assertRaisesRegex(InvariantError,'physical truth'):
            query_context(self.k, truth)

    def test_recorded_actor_and_history_still_required(self):
        self.permit('PUB')
        event_id = self.executed_output('PUB')
        with self.assertRaisesRegex(InvariantError, 'BLOCKED_POSSESSION'):
            self.k.admit_realized_output_observation(9, 'SPN', event_id)
        self.k.agents['PUB'].history.remove(event_id)
        with self.assertRaisesRegex(InvariantError, 'BLOCKED_POSSESSION'):
            self.k.admit_realized_output_observation(9, 'PUB', event_id)
        self.k.agents['PUB'].history.append(event_id)
        self.k.admit_realized_output_observation(9, 'PUB', event_id)
        self.assertIn(event_id, self.k.agents['PUB'].information)

    def test_grant_without_admitted_output_does_not_reveal_output(self):
        self.permit('PUB')
        event_id = self.executed_output('PUB')
        self.assertEqual(self.output_fact('PUB', event_id).reason_code,
                         'BLOCKED_POSSESSION')


if __name__ == '__main__':
    unittest.main()
