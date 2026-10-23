"""Run the immutable portfolio campaign with genuine strict-boundary inputs.

This opt-in adapter registers every candidate as a real kernel Box3 activity,
binds typed kernel state into the existing boundary manifest, admits those
facts through admit_for_use, and lets strict snapshot validation verify the
resulting receipts. All report output is redirected to /tmp.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'simulation/offworld_mvp/phase3b/kernel'))
sys.path.insert(0, str(ROOT / 'src'))

from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022 import run_multi_project as m
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022 import run_with_boundary_accounting as accounting
from simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022.general_project import _total_money
from offworld_kernel.boundary import (
    ConsumptionRequest, ContextValue, admit_for_use, snapshot_facts,
)
from offworld_kernel.project_activity import (
    ProjectActivity, build_sponsor_portfolio_request,
)
from offworld_kernel.model import (
    AccountKind, NodeKind,
)
from offworld_kernel.policy import (
    FactState, build_decision_snapshot,
)
from offworld_kernel.policy_runner import run_sponsor_portfolio_policy


OUT = Path('/tmp/loom_multi_project_boundary_kt_20261022')
OUT.mkdir(parents=True, exist_ok=True)
D = Decimal


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()


def _assertion(k, *, sponsor, concept, scope, value, year, source_ref, source_value, unit, role):
    source_hash = _digest(source_value)
    return ContextValue(
        assertion_id=f"MP-BOUNDARY:{year}:{sponsor}:{_digest((concept, source_ref))[:20]}",
        subject_id=sponsor if concept.startswith('agent.') or concept == 'portfolio.AVAILABLE_CAPITAL' else source_ref,
        concept=concept, scope=scope, world_context='REALIZED', context_id=k.boundary_manifest.run_id,
        perspective='AGENT', perspective_actor_id=sponsor, value_state=FactState.KNOWN,
        value=str(value), unit=unit, reason_code='ADMITTED', proposition_kind='KERNEL_TYPED_STATE',
        proposition_role=role, epistemic_mode='ADMITTED_INFORMATION', admission_state='ADMITTED',
        uncertainty_state='DECLARED', uncertainty_ref='', valid_from=str(year), valid_to=str(year),
        time_basis='SIM_TIME', available_from=str(year), source_refs=(source_ref,), source_hashes=(source_hash,),
        warrant_refs=('REGISTERED_BOX3_ACTIVITY_OR_LIVE_SPONSOR_ACCOUNT',), support_conflict_refs=(),
        dependency_refs=(), transformation_ref='', transformation_version='',
        authorization_ref=k.boundary_manifest.authorization_ref, reference_role='KERNEL_STATE',
        exception_flags=(), record_version='CONTEXT_VALUE_V1', source_time=str(year))


def _contract(sponsor, concept, scope, unit, role):
    return (sponsor, 'POLICY', concept, scope, 'REALIZED', 'AGENT', unit, role)


class AdmittedPortfolioCampaign(accounting.BoundaryAwareCampaign):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registered_candidates = {}
        self.boundary_receipt_counts = []

    def _register_candidate(self, k, candidate, year, priority):
        aid = f"MP:{year}:{candidate['sponsor']}:{candidate['body']}"
        key = (candidate['sponsor'], candidate['body'])
        if key not in self._registered_candidates:
            # The kernel's policy activity is a separate governance object;
            # its project identity must not occupy the lifecycle project ID,
            # which EconomicLifecycle creates only after selection.
            pid = 'POLICY_PROJECT:' + _digest(candidate['state'].project)[:24]
            node = 'OFF:POLICY:' + _digest(pid)[:24]
            cash = 'POLICY:CASH:' + _digest(pid)[:24]
            if node not in k.state.nodes:
                k.add_node(node, NodeKind.OFFWORLD)
            if cash not in k.state.accounts:
                k.add_account(cash, candidate['sponsor'], node, AccountKind.PROJECT_CASH)
            if pid not in k.state.projects:
                k.add_project(pid, node, cash, {candidate['sponsor']: D(1)})
            activity = ProjectActivity(aid, pid, 'CAPITAL_ALLOCATION', candidate['sponsor'],
                priority, D(year), D(1), D(candidate['commitment']), 'PROJECT_FUNDING_RESULT')
            k.register_project_activity(activity)
            self._registered_candidates[key] = aid
        else:
            aid = self._registered_candidates[key]
            pid = k.project_activities[aid].project_id
            k.project_activities[aid].priority = priority
        return aid

    def _policy_filter(self, k, candidates, year):
        selected = []
        self.last_policy_decisions = []
        all_receipts = []
        for sponsor in self.requesters:
            group = [c for c in candidates if c['sponsor'] == sponsor]
            if not group:
                continue
            group.sort(key=lambda c: (D(c['commitment']), c['eligibility_year'], c['roster_index']))
            activities = {self._register_candidate(k, c, year, rank): c for rank, c in enumerate(group, 1)}
            account_id = k.agents[sponsor].account_id
            account = k.state.accounts[account_id]
            agent = k.agents[sponsor]
            assertions = []
            requests = []
            specs = (
                ('agent.STATE', 'AGENT:' + sponsor, 'TYPED_AGENT_STATE', 'ADMITTED_INFORMATION',
                 {'account_id': account_id, 'balance': str(account.balance), 'kind': account.kind.value,
                  'capabilities': sorted(agent.capabilities), 'objectives': list(agent.objectives)}),
                ('agent.BELIEF', 'AGENT:' + sponsor, 'PROBABILITY', 'ACTOR_BELIEF',
                 {key: str(value) for key, value in sorted(agent.beliefs.items())}),
                ('agent.PRIOR', 'AGENT:' + sponsor, 'PROBABILITY', 'AGENT_PRIOR',
                 {key: str(value) for key, value in sorted(agent.priors.items())}),
                ('portfolio.AVAILABLE_CAPITAL', 'SPONSOR:' + sponsor, 'MODEL_CURRENCY', 'ADMITTED_INFORMATION',
                 str(k.project_activity_available_capital(sponsor))),
            )
            for concept, scope, unit, role, source_value in specs:
                assertion = _assertion(k, sponsor=sponsor, concept=concept, scope=scope,
                    value=json.dumps(source_value, sort_keys=True) if isinstance(source_value, dict) else source_value,
                    year=year, source_ref='KERNEL:' + concept + ':' + sponsor,
                    source_value=source_value, unit=unit, role=role)
                assertions.append(assertion)
                requests.append(ConsumptionRequest(
                    f"MP:{year}:{sponsor}:{concept}", sponsor, 'POLICY', sponsor, concept,
                    scope, 'SIM_TIME', str(year), str(year), 'REALIZED', k.boundary_manifest.run_id,
                    'AGENT', sponsor, 'ADMITTED', unit, role))
            for activity_id, candidate in activities.items():
                activity = k.project_activities[activity_id]
                project = k.state.projects[activity.project_id]
                fields = (
                    ('PROJECT_ID', project.id), ('PROJECT_STATUS', project.status),
                    ('STATUS', activity.status.value), ('COMMITMENT', str(activity.capital_commitment)),
                    ('PRIORITY', str(activity.priority)), ('WINDOW_VALID', '1'),
                )
                for name, value in fields:
                    concept = f'activity.{activity_id}.{name}'
                    scope = 'PROJECT:' + project.id
                    unit = 'MODEL_CURRENCY' if name == 'COMMITMENT' else 'ADMITTED_INFORMATION'
                    role = 'CAPITAL_COMMITMENT' if name == 'COMMITMENT' else 'ADMITTED_INFORMATION'
                    source_value = {'project_id': project.id,
                                    'lifecycle_project_id': candidate['state'].project,
                                    'status': project.status,
                                    'activity_id': activity.id, 'activity_status': activity.status.value,
                                    'commitment': str(activity.capital_commitment),
                                    'priority': activity.priority, 'window_valid': True}
                    assertions.append(_assertion(k, sponsor=sponsor, concept=concept, scope=scope,
                        value=value, year=year, source_ref='KERNEL:PROJECT_ACTIVITY:' + activity.id,
                        source_value=source_value, unit=unit, role=role))
                    requests.append(ConsumptionRequest(
                        f"MP:{year}:{sponsor}:{activity_id}:{name}", sponsor, 'POLICY',
                        activity_id, concept, scope, 'SIM_TIME', str(year), str(year), 'REALIZED',
                        k.boundary_manifest.run_id, 'AGENT', sponsor, 'ADMITTED', unit, role))
            contracts = tuple(_contract(sponsor, q.concept, q.scope, q.required_unit, q.required_role) for q in requests)
            manifest = k.boundary_manifest
            k.boundary_manifest = replace(manifest,
                allowed_use_contracts=manifest.allowed_use_contracts + tuple(x for x in contracts if x not in manifest.allowed_use_contracts),
                assertions=manifest.assertions + tuple(assertions))
            receipts = []
            for request in requests:
                value, receipt = admit_for_use(k, request)
                if value.value_state != FactState.KNOWN:
                    raise RuntimeError(f'BOX3 boundary admission did not resolve: {request.concept}:{value.reason_code}')
                receipts.append(receipt)
            all_receipts.extend(receipts)
            facts = snapshot_facts(k, tuple(receipts))
            snap = build_decision_snapshot(k, sponsor, f'MULTI_PROJECT:{year}:{sponsor}', year,
                                           facts, admission_receipts=tuple(receipts))
            request = build_sponsor_portfolio_request(
                f'MULTI_PROJECT:PORTFOLIO:{year}:{sponsor}', year, tuple(activities))
            decision = run_sponsor_portfolio_policy(snap, request, 'MULTI_PROJECT:SPONSOR_POLICY').decision
            chosen = activities.get(decision.selected_activity_id)
            self.last_policy_decisions.append(dict(year=year, sponsor=sponsor,
                outcome=decision.outcome.value, reason=decision.reason_code.value,
                selected_activity_id=decision.selected_activity_id,
                selected_body=chosen['body'] if chosen else None,
                available_capital=str(snap.account_balance), policy_version=decision.policy_version,
                admission_receipt_count=len(receipts)))
            if chosen:
                selected.append(chosen)
            else:
                self.project_rows.append(dict(year=year, sponsor=sponsor,
                    outcome='DEFERRED_BY_SPONSOR_PORTFOLIO_POLICY', policy_reason=decision.reason_code.value,
                    eligible_candidates=[c['body'] for c in group], retry='REATTEMPT_NEXT_ANNUAL_POLICY_CALLBACK'))
        self.boundary_receipt_counts.append(dict(year=year, receipts=len(all_receipts)))
        return selected


def _main():
    # The already-qualified Ceres projection is consumed as an input; it is not rerun.
    ceres = json.loads((m.HERE / 'ceres_equivalence_report.json').read_text())
    if ceres.get('result') != 'PASS' or ceres.get('transaction_counts') != [8798, 8798] or ceres.get('event_count') != 290:
        raise RuntimeError('Existing Ceres equivalence evidence is not the stated exact PASS')
    original_write = m.write
    original_ceres = m.ceres_equivalence
    m.PortfolioCampaign = AdmittedPortfolioCampaign
    m.write = lambda name, obj: (OUT / name).write_text(json.dumps(m.jsonable(obj), sort_keys=True, indent=2) + '\n')
    m.ceres_equivalence = lambda scenario, prices: ceres
    try:
        m.main()
    finally:
        m.write = original_write
        m.ceres_equivalence = original_ceres
    for name in ('full_clock_report.json', 'zero_conversion_control_report.json', 'a1_flyby_comparison_report.json'):
        report = json.loads((OUT / name).read_text())
        report['boundary_adapter'] = 'GENUINE_KERNEL_ACTIVITY_REGISTRATION_AND_ADMISSION_RECEIPTS'
        (OUT / name).write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    _main()
