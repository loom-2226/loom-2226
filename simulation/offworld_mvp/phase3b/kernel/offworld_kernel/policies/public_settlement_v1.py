from decimal import Decimal

D=Decimal

POLICY_ID='PUBLIC_SETTLEMENT_V1'
SEMANTIC_VERSION='0.1'
POLICY_SEMANTICS='BOUNDED_CAPACITY_AND_FUNDING_LIMITED_PUBLIC_SETTLEMENT_SUPPORT_V1'
POLICY_CONTRACT={
    'contract_id':'BUILD5_TEST011A_PUBLIC_SETTLEMENT_CONTRACT_V0_1',
    'required_agent_kind':'PUBLIC',
    'required_objective':'PUBLIC_SETTLEMENT',
    'required_capabilities':['MIGRATE','SETTLEMENT_SUPPORT'],
    'eligible_stage':'EXTRACTION_ENCLAVE',
    'stage_fact':'settlement.STAGE',
    'headroom_fact':'settlement.HABITAT_HEADROOM',
    'requested_fact':'settlement.REQUESTED_RESIDENTS',
    'earth_population_fact':'population.EARTH_AVAILABLE',
    'support_cost_fact':'settlement.PUBLIC_SUPPORT_COST',
    'numeric_policy_parameters':[],
}

def _d(x):
    return D(str(x))

def _facts(snapshot):
    return {f['key']:f for f in snapshot['admitted_facts']}

def evaluate(snapshot,request,contract,decision_key):
    if contract!=POLICY_CONTRACT:
        raise ValueError('public settlement contract mismatch')
    facts=_facts(snapshot)
    stage=str(facts[contract['stage_fact']]['value'])
    headroom=int(facts[contract['headroom_fact']]['value'])
    requested=int(facts[contract['requested_fact']]['value'])
    earth_available=int(facts[contract['earth_population_fact']]['value'])
    support_cost=_d(facts[contract['support_cost_fact']]['value'])
    if support_cost!=_d(request['support_cost']):
        raise ValueError('settlement support cost/request mismatch')
    if min(headroom,requested,earth_available)<0 or support_cost<0:
        raise ValueError('negative admitted settlement-support input')

    metrics={
        'stage':stage,'habitat_headroom':str(headroom),
        'requested_residents':str(requested),
        'earth_population_available':str(earth_available),
        'support_cost':str(support_cost),
        'public_balance':str(snapshot['account_balance']),
        'decision_key_hash_material':str(decision_key),
    }
    if snapshot['agent_kind']!=contract['required_agent_kind'] or contract['required_objective'] not in snapshot['objectives']:
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'authorized_residents':0,'support_amount':'0',
                'reason':'public Agent class or settlement objective is not admitted','metrics':metrics}
    if not set(contract['required_capabilities']).issubset(set(snapshot['capabilities'])):
        return {'outcome':'DEFER','reason_code':'CAPABILITY_OR_OBJECTIVE_BLOCK',
                'authorized_residents':0,'support_amount':'0',
                'reason':'public Agent lacks admitted migration/settlement-support capability','metrics':metrics}
    if stage!=contract['eligible_stage']:
        return {'outcome':'DEFER','reason_code':'STAGE_BLOCK',
                'authorized_residents':0,'support_amount':'0',
                'reason':'current settlement stage is not an extraction enclave','metrics':metrics}
    if requested<=0:
        return {'outcome':'DEFER','reason_code':'NO_REQUESTED_RESIDENTS',
                'authorized_residents':0,'support_amount':'0',
                'reason':'no positive resident movement requested','metrics':metrics}
    if headroom<requested:
        return {'outcome':'DEFER','reason_code':'HABITAT_CAPACITY_LIMIT',
                'authorized_residents':0,'support_amount':'0',
                'reason':'requested residents exceed admitted habitat headroom','metrics':metrics}
    if earth_available<requested:
        return {'outcome':'DEFER','reason_code':'ORIGIN_POPULATION_LIMIT',
                'authorized_residents':0,'support_amount':'0',
                'reason':'requested residents exceed admitted Earth population','metrics':metrics}
    if _d(snapshot['account_balance'])<support_cost:
        return {'outcome':'DEFER','reason_code':'INSUFFICIENT_PUBLIC_FUNDS',
                'authorized_residents':0,'support_amount':'0',
                'reason':'public funds do not cover admitted settlement-support cost','metrics':metrics}
    return {'outcome':'AUTHORIZE','reason_code':'SETTLEMENT_SUPPORT_AUTHORIZED',
            'authorized_residents':requested,'support_amount':str(support_cost),
            'reason':'admitted enclave headroom, origin population and public funding authorize settlement support',
            'metrics':metrics}
