from decimal import Decimal

D=Decimal

POLICY_ID='PUBLIC_SETTLEMENT_TRANSPORT_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='BOUNDED_TRANSPORT_TECHNOLOGY_GATED_PUBLIC_SETTLEMENT_SUPPORT_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST012A_PUBLIC_SETTLEMENT_TRANSPORT_CONTRACT_V0_1',
    'required_agent_kind':'PUBLIC',
    'required_objective':'PUBLIC_SETTLEMENT',
    'required_capabilities':['MIGRATE','SETTLEMENT_SUPPORT'],
    'eligible_stage':'EXTRACTION_ENCLAVE',
    'stage_fact':'settlement.STAGE',
    'headroom_fact':'settlement.HABITAT_HEADROOM',
    'requested_fact':'settlement.REQUESTED_RESIDENTS',
    'earth_population_fact':'population.EARTH_AVAILABLE',
    'support_cost_fact':'settlement.PUBLIC_SUPPORT_COST',
    'transport_available_fact':'transport.AVAILABLE',
    'transport_relationship_fact':'transport.RELATIONSHIP_ID',
    'technology_state_fact':'technology.STATE_ID',
    'transport_capacity_fact':'transport.CAPACITY',
    'transport_cost_fact':'transport.COST_PER_PASSENGER',
    'transport_time_fact':'transport.TRAVEL_TIME',
    'transport_energy_fact':'transport.ENERGY_PER_PASSENGER',
    'transport_loss_risk_fact':'transport.LOSS_RISK',
    'capacity_policy':'ALL_OR_DEFER',
    'loss_policy':'ZERO_RISK_FIXTURE_ONLY',
    'numeric_policy_parameters':[],
}


def _d(x):
    return D(str(x))


def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}


def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('public transport-settlement contract mismatch')
    facts=_facts(snapshot)
    stage=str(facts[contract['stage_fact']]['value'])
    headroom=int(facts[contract['headroom_fact']]['value'])
    requested=int(facts[contract['requested_fact']]['value'])
    earth_available=int(facts[contract['earth_population_fact']]['value'])
    support_cost=_d(facts[contract['support_cost_fact']]['value'])
    available=str(facts[contract['transport_available_fact']]['value']).upper()=='TRUE'
    relationship_id=str(facts[contract['transport_relationship_fact']]['value'])
    technology_state_id=str(facts[contract['technology_state_fact']]['value'])
    capacity=int(facts[contract['transport_capacity_fact']]['value'])
    cost_per_passenger=_d(facts[contract['transport_cost_fact']]['value'])
    travel_time=_d(facts[contract['transport_time_fact']]['value'])
    energy_per_passenger=_d(facts[contract['transport_energy_fact']]['value'])
    loss_risk=_d(facts[contract['transport_loss_risk_fact']]['value'])

    if support_cost!=_d(request['support_cost']):
        raise ValueError('settlement support cost/request mismatch')
    if relationship_id!=request['transport_relationship_id']:
        raise ValueError('transport relationship/request mismatch')
    if technology_state_id!=request['technology_state_id']:
        raise ValueError('technology state/request mismatch')
    if min(headroom,requested,earth_available,capacity)<0:
        raise ValueError('negative admitted settlement/transport input')
    if min(support_cost,cost_per_passenger,energy_per_passenger,loss_risk)<0:
        raise ValueError('negative admitted transport scalar')
    if travel_time<=0 or loss_risk>1:
        raise ValueError('invalid admitted transport time/risk')

    transport_amount=_d(requested)*cost_per_passenger
    total_public_cost=support_cost+transport_amount
    departure_time=_d(request['departure_time'])
    arrival_time=departure_time+travel_time
    metrics={
        'stage':stage,
        'habitat_headroom':str(headroom),
        'requested_residents':str(requested),
        'earth_population_available':str(earth_available),
        'support_cost':str(support_cost),
        'transport_available':str(available),
        'transport_relationship_id':relationship_id,
        'technology_state_id':technology_state_id,
        'transport_capacity':str(capacity),
        'transport_cost_per_passenger':str(cost_per_passenger),
        'transport_cost_total':str(transport_amount),
        'transport_travel_time':str(travel_time),
        'transport_energy_per_passenger':str(energy_per_passenger),
        'transport_loss_risk':str(loss_risk),
        'total_public_cost':str(total_public_cost),
        'public_balance':str(snapshot['account_balance']),
        'departure_time':str(departure_time),
        'arrival_time':str(arrival_time),
        'decision_key_hash_material':str(decision_key),
    }

    def defer(code,reason):
        return {
            'outcome':'DEFER','reason_code':code,
            'authorized_residents':0,'support_amount':'0','transport_amount':'0',
            'relationship_id':'','technology_state_id':'',
            'departure_time':'0','arrival_time':'0',
            'reason':reason,'metrics':metrics,
        }

    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return defer('CAPABILITY_OR_OBJECTIVE_BLOCK',
                     'public Agent class or settlement objective is not admitted')
    if not set(contract['required_capabilities']).issubset(set(snapshot['capabilities'])):
        return defer('CAPABILITY_OR_OBJECTIVE_BLOCK',
                     'public Agent lacks admitted migration/settlement-support capability')
    if stage!=contract['eligible_stage']:
        return defer('STAGE_BLOCK','current settlement stage is not an extraction enclave')
    if requested<=0:
        return defer('NO_REQUESTED_RESIDENTS','no positive resident movement requested')
    if headroom<requested:
        return defer('HABITAT_CAPACITY_LIMIT',
                     'requested residents exceed admitted habitat headroom')
    if earth_available<requested:
        return defer('ORIGIN_POPULATION_LIMIT',
                     'requested residents exceed admitted Earth population')
    if not available:
        return defer('TRANSPORT_UNAVAILABLE',
                     'required technology capability does not admit the transport relationship')
    if capacity<requested:
        return defer('TRANSPORT_CAPACITY_LIMIT',
                     'requested residents exceed admitted transport capacity')
    if loss_risk!=0:
        return defer('LOSS_RISK_UNSUPPORTED',
                     'Test 012A authorizes only zero-loss-risk structural passenger fixtures')
    if _d(snapshot['account_balance'])<total_public_cost:
        return defer('INSUFFICIENT_PUBLIC_FUNDS',
                     'public funds do not cover settlement support plus transport charge')

    return {
        'outcome':'AUTHORIZE',
        'reason_code':'SETTLEMENT_TRANSPORT_AUTHORIZED',
        'authorized_residents':requested,
        'support_amount':str(support_cost),
        'transport_amount':str(transport_amount),
        'relationship_id':relationship_id,
        'technology_state_id':technology_state_id,
        'departure_time':str(departure_time),
        'arrival_time':str(arrival_time),
        'reason':'admitted settlement state and qualified transport service authorize passenger movement',
        'metrics':metrics,
    }
