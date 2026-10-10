"""Two competing prospecting proposals, one existing Sponsor, finite cash.

Disposable kernel experiment. No new Agents or financial machinery.
"""
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.prospecting import SponsorProspectingOutcome, SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner as workers
from .opening import build_country_opening


def run_finite_capital_trial(root: Path):
    kernel, history, capacities, _ = build_country_opening(root)
    country = 'USA'
    capital = kernel.mobilize_country_capital(1,country,capacities[country,2026],D(1),
        history['prospecting_scenario'],'earth_capital_source','sponsor_funds').mobilized_cash
    # Identical independently submitted economics, distinct project identities.
    amount = D(3)
    results=[]
    for index in (1,2):
        available=kernel.state.accounts['sponsor_funds'].balance
        project=f'B8_PROSPECT_{index}'
        request=SponsorProspectingRequest(f'B8_REQUEST_{index}',1,'SPN',f'B8_OPPORTUNITY_{index}',
            project,f'B8_BODY_{index}',f'B8_REGION_{index}',f'B8_LOCATION_{index}',
            tuple(f'B8_OBS_{index}_{n}' for n in range(1,5)),
            tuple(f'B8_BELIEF_{index}_{n}' for n in range(1,5)),amount,D(5)).validate_protocol()
        snapshot=DecisionSnapshot('SPN','PRIVATE_SPONSOR','EARTH:USA',f'B8_{index}','1',D(0),
            ('REQUEST_FINANCE',),('RETURN',),request.observation_ids,
            tuple((key,D('.8')) for key in request.belief_keys),
            tuple((key,D('.5')) for key in request.belief_keys),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(amount),'SCENARIO'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'5','SCENARIO'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,str(available),'CAPITAL')))
        decision=workers.run_sponsor_prospecting_policy(snapshot,request,f'B8_PROPOSAL_{index}').decision
        if decision.outcome==SponsorProspectingOutcome.INITIATE_PROJECT:
            kernel.create_prospecting_project(1,'SPN',request,decision,
                f'OFF:B8:{index}',f'b8_project_cash:{index}')
            kernel.add_commitment(f'B8_COMMIT_{index}','SPN',project,decision.amount)
            kernel.disburse_country_capital(1,country,f'B8_COMMIT_{index}',
                'sponsor_funds',decision.amount,request,decision)
        results.append((project,decision.outcome.value,str(available),
                        str(kernel.state.accounts['sponsor_funds'].balance)))
    assert kernel.capital_coupling[country]['F']==kernel.state.accounts['sponsor_funds'].balance
    assert capital==kernel.capital_coupling[country]['F']+kernel.capital_coupling[country]['X']
    return tuple(results),str(capital),str(kernel.capital_coupling[country]['X'])
