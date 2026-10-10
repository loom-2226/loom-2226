"""Disposable continuation of actual replayed lunar opportunity, with Sponsor policy."""
from decimal import Decimal as D
from offworld_kernel.model import TxPurpose
from offworld_kernel.prospecting import SponsorProspectingRequest, SponsorProspectingOutcome
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner as workers
from .replay_lunar_allocation_trial import replay_observed

def run_trial(country_id="USA"):
    country_id=str(country_id).upper()
    k,h,choice,opportunities=replay_observed(country_id)
    opportunity=sorted(opportunities,key=lambda o:o.opportunity_id)[0]
    amount=opportunity.required_capital
    original=k.state.accounts['sponsor_funds'].balance
    project='PROSPECT:'+opportunity.body_key+':'+opportunity.region_key
    request=SponsorProspectingRequest(
        'B8_LUNAR:'+opportunity.opportunity_id,1,'SPN',opportunity.opportunity_id,
        project,opportunity.body_key,opportunity.region_key,opportunity.location_id,
        opportunity.observation_ids,opportunity.belief_keys,amount,
        opportunity.prospective_information_value).validate_protocol()
    sponsor=k.agents['SPN']
    if not set(request.observation_ids).issubset(sponsor.information):
        raise AssertionError('Sponsor missing lunar observations')
    snapshot=DecisionSnapshot('SPN','PRIVATE_SPONSOR','EARTH:USA','B8_LUNAR','1',D(0),
        ('REQUEST_FINANCE',),('RETURN',),request.observation_ids,
        tuple((key,sponsor.beliefs.get(key,D('.5'))) for key in request.belief_keys),
        tuple((key,sponsor.priors.get(key,D('.5'))) for key in request.belief_keys),
        (),(),(),(
            SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(amount),'SCENARIO'),
            SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,str(opportunity.prospective_information_value),'SCENARIO'),
            SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,str(amount),'CAPITAL')))
    from simulation.offworld_mvp.build7.generated_campaign import _execute_annual_prospecting_investment
    from simulation.offworld_mvp.build7.generated_campaign import _agent_logins
    h['agent_logins'].update(_agent_logins(('agent_pub','agent_spn','agent_fin')))
    decision,creation=_execute_annual_prospecting_investment(k,h,2026,opportunity,
        'runtime',h['named_binding'])
    k.assert_invariants()
    remaining=k.capital_coupling[country_id]['F']
    sponsor_cash=k.state.accounts['sponsor_funds'].balance
    spent=k.capital_coupling[country_id]['X']
    assert original==remaining+spent
    assert original==sponsor_cash+spent
    assert (project in k.state.projects)==(decision.outcome==SponsorProspectingOutcome.INITIATE_PROJECT)
    return (opportunity.opportunity_id,decision.outcome.value,str(original),
        str(remaining),str(sponsor_cash),str(spent),
        str(k.state.projects[project].status) if project in k.state.projects else 'NO_PROJECT')

if __name__=='__main__':
    first=run_trial()
    print('FIRST',first,flush=True)
    second=run_trial()
    print('SECOND',second,flush=True)
    assert first==second,'NONDETERMINISTIC_LUNAR_CONSEQUENCE'
    print('DETERMINISTIC_PASS',flush=True)
