"""Disposable Build 8 two-Sponsor project experiment, not admitted policy or WA runtime.

Uses existing Kernel accounts, projects, commitments and transfers. Public choice is
an explicit experimental rule; no claim of qualified public prospecting policy.
"""
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AgentState, AgentKind
from .opening import build_country_opening
from .public_private_comparison import run_public_private_comparison


def run_two_sponsor_projects(root: Path, *, commercial=False, strategic=False,
                             pooled_public=True):
    k,h,capacities,_=build_country_opening(root)
    amounts=run_public_private_comparison(root)[bool(commercial),bool(strategic)]
    cost=D(2)
    # Explicit pooled 80-country scenario. Do not treat an unpooled Australian
    # budget as though it can spend all 80 countries' resources.
    public_funds=amounts['public_total'] if pooled_public else amounts['public_country']
    private_funds=amounts['private_total']
    k.add_account('b8_public_budget','PUBLIC_CONSORTIUM','EARTH:USA',
                  AccountKind.FUNDS,D(0))
    # Existing SPN is the private sponsor; its existing account starts empty.
    k.add_agent(AgentState('B8_PUBLIC',AgentKind.PUBLIC,'EARTH:USA',
                          'b8_public_budget',{'REQUEST_FINANCE'},('SCIENCE','STRATEGIC')))
    # This is a disposable accounting scenario, not a country mobilization
    # record or qualified Earth-source admission. Record explicit input origin.
    k.add_account('b8_trial_public_origin','TRIAL_PUBLIC_ORIGIN','EARTH:USA',
                  AccountKind.EARTH_BOUNDARY,public_funds)
    k.add_account('b8_trial_private_origin','TRIAL_PRIVATE_ORIGIN','EARTH:USA',
                  AccountKind.EARTH_BOUNDARY,private_funds)
    from offworld_kernel.model import TxPurpose
    k.transfer(1,'b8_trial_public_origin','b8_public_budget',public_funds,
               TxPurpose.OTHER_INVESTMENT)
    k.transfer(1,'b8_trial_private_origin','sponsor_funds',private_funds,
               TxPurpose.OTHER_INVESTMENT)
    results=[]
    for actor,source,motivation in (
            ('B8_PUBLIC','b8_public_budget',bool(strategic)),
            ('SPN','sponsor_funds',bool(commercial))):
        available=k.state.accounts[source].balance
        if not motivation or available<cost:
            results.append((actor,'WAIT',str(available),str(available)))
            continue
        # Two separate region opportunities from the same observed body are
        # represented here by distinct experimental project IDs, not claims
        # about a particular discovered deposit.
        project='B8_PROJECT_'+actor
        node='OFF:B8:'+actor
        cash='b8_cash:'+actor
        k.add_node(node,NodeKind.OFFWORLD)
        k.add_account(cash,actor,node,AccountKind.PROJECT_CASH,D(0))
        k.add_project(project,node,cash,{actor:D(1)})
        k.add_commitment('B8_COMMIT_'+actor,actor,project,cost)
        k.disburse(1,'B8_COMMIT_'+actor,source,cost)
        results.append((actor,'FUNDED',str(available),str(k.state.accounts[source].balance)))
    k.assert_invariants()
    assert sum((k.state.accounts['b8_public_budget'].balance,
                k.state.accounts['sponsor_funds'].balance,
                *(k.state.accounts['b8_cash:'+a].balance
                  for a in ('B8_PUBLIC','SPN') if 'b8_cash:'+a in k.state.accounts)),D(0))==public_funds+private_funds
    return tuple(results),k.fingerprint()
