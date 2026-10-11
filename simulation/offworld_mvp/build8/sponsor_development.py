"""Build 8 only: authorize funded Sponsor projects using recorded authored decisions.

An award is a reporting outcome, not a kernel project status. This trial
records an explicit Sponsor decision before the existing lifecycle transition.
No physical delivery or executor payment occurs here.
"""
from offworld_kernel.mvp_state import AgentKind, AgentState, ActionKind
from offworld_kernel.kernel import InvariantError


def authorize_funded_projects(kernel, rows, budgets, year):
    """Apply recorded Sponsor decisions to already-funded Build 8 projects."""
    decisions = {}
    for row in rows:
        if row['outcome'] != 'AWARDED_PENDING_PLAN':
            continue
        sponsor = row['sponsor']
        project_id = 'network:project:' + sponsor
        project = kernel.state.projects[project_id]
        if project.status not in ('PROPOSED', 'EXPLORING'):
            raise InvariantError('Build 8 project cannot enter DEVELOPMENT from ' + project.status)
        budget = budgets[sponsor]
        kernel.add_agent(AgentState(sponsor, AgentKind.PRIVATE_SPONSOR,
                                    kernel.state.accounts[budget].node_id, budget,
                                    {'DEVELOP'}, ('RETURN',)))
        # An authored Sponsor decision is recorded in the causal event log
        # before transition, rather than invented as a conductor-side reason.
        decision = kernel.event(year, sponsor, ActionKind.AUTHORIZE_ACTIVITY,
                                'AUTHORIZE_DEVELOPMENT',
                                (project_id, 'AUTHORED_BUILD8_SPONSOR_DECISION'))
        kernel.transition_project_status(year, sponsor, project_id,
                                         'DEVELOPMENT', decision.id)
        decisions[sponsor] = decision.id
    return decisions
