"""Build 8 Experiment B: an award must not masquerade as physical delivery."""
from .opening import EARTH_V4_ROOT
import unittest
from pathlib import Path
from decimal import Decimal as D
from .sponsor_executor_network_trial import run_network
from .sponsor_development import authorize_funded_projects
from offworld_kernel.mvp_state import AgentKind, ActionKind
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import AccountKind, NodeKind
from .opening import build_country_opening

ROOT=EARTH_V4_ROOT

@unittest.skipUnless(ROOT.exists(),'Earth v4 baseline absent')
class SponsorExecutorNetworkTests(unittest.TestCase):
    def test_awards_hold_cash_until_physical_plan(self):
        rows,revenue,fingerprint=run_network(ROOT)
        awards=[r for r in rows if r['outcome']=='AWARDED_PENDING_PLAN']
        self.assertEqual([r['sponsor'] for r in awards],['CNSA','ISRO','ESA'])
        self.assertEqual(len(rows),20)
        self.assertEqual(len(awards),3)
        self.assertTrue(all(v==str(D(0)) for v in revenue.values()))
        self.assertEqual(sum(D(r['cost']) for r in awards),D('.090'))
        self.assertEqual((rows,revenue,fingerprint),run_network(ROOT))

    def test_development_requires_recorded_sponsor_decision(self):
        kernel, _, _, _ = build_country_opening(ROOT)
        sponsor = 'Interlune'
        budget = 'network:budget:' + sponsor
        project = 'network:project:' + sponsor
        kernel.add_account(budget, sponsor, 'EARTH:USA', AccountKind.FUNDS, D(0))
        kernel.add_node('OFF:NETWORK:' + sponsor, NodeKind.OFFWORLD)
        kernel.add_account('network:cash:' + sponsor, sponsor, 'OFF:NETWORK:' + sponsor, AccountKind.PROJECT_CASH, D(0))
        kernel.add_project(project, 'OFF:NETWORK:' + sponsor, 'network:cash:' + sponsor, {sponsor: D(1)})
        self.assertEqual(kernel.state.projects[project].status, 'PROPOSED')
        rows = [dict(sponsor=sponsor, outcome='AWARDED_PENDING_PLAN')]
        decisions = authorize_funded_projects(kernel, rows, {sponsor: budget}, 2026)
        self.assertEqual(kernel.state.projects[project].status, 'DEVELOPMENT')
        self.assertEqual(kernel.agents[sponsor].kind, AgentKind.PRIVATE_SPONSOR)
        decision = next(e for e in kernel.events if e.id == decisions[sponsor])
        self.assertEqual(decision.action, ActionKind.AUTHORIZE_ACTIVITY)
        transition = next(e for e in kernel.events if e.action == ActionKind.DEVELOP and project in e.inputs)
        self.assertIn(decision.id, transition.parent_ids)
        kernel.assert_invariants()

    def test_invalid_starting_status_is_rejected(self):
        kernel, _, _, _ = build_country_opening(ROOT)
        sponsor = 'Interlune'
        budget = 'network:budget:' + sponsor
        project = 'network:project:' + sponsor
        kernel.add_account(budget, sponsor, 'EARTH:USA', AccountKind.FUNDS, D(0))
        kernel.add_node('OFF:NETWORK:' + sponsor, NodeKind.OFFWORLD)
        kernel.add_account('network:cash:' + sponsor, sponsor, 'OFF:NETWORK:' + sponsor, AccountKind.PROJECT_CASH, D(0))
        kernel.add_project(project, 'OFF:NETWORK:' + sponsor, 'network:cash:' + sponsor, {sponsor: D(1)})
        kernel.state.projects[project].status = 'AWARDED_PENDING_PLAN'
        with self.assertRaisesRegex(InvariantError, 'cannot enter DEVELOPMENT'):
            authorize_funded_projects(kernel, [dict(sponsor=sponsor, outcome='AWARDED_PENDING_PLAN')], {sponsor: budget}, 2026)
